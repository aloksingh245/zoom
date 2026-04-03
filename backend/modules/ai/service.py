import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from groq import AsyncGroq
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from modules.ai import schemas
from modules.classes.models import ClassSession
from modules.courses.models import Course

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Using the specific Groq API key and Llama 3.1 8B model as requested
        api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        if api_key:
            self.client = AsyncGroq(api_key=api_key)
            self.model_id = 'llama-3.1-8b-instant' # Precise Groq model ID for 3.1 8B
            logger.info(f"AI Assistant initialized successfully with Groq ({self.model_id}).")
        else:
            self.client = None
            logger.error("GROQ_API_KEY not found. AI Assistant will be disabled.")

    async def get_chat_response(
        self, 
        db: AsyncSession, 
        message: str, 
        history: List[schemas.ChatMessage] = []
    ) -> schemas.ChatResponse:
        if not self.client:
            return schemas.ChatResponse(response="AI Assistant is not configured. Please add GROQ_API_KEY to your environment.")

        # 1. Fetch Context
        classes_result = await db.execute(select(ClassSession))
        classes = classes_result.scalars().all()
        
        courses_result = await db.execute(select(Course))
        courses = courses_result.scalars().all()

        # 2. Build Context
        current_date = datetime.now().strftime("%Y-%m-%d (%A)")
        classes_ctx = "\n".join([
            f"- {c.date} at {c.start_time}: {c.topic_name} (Course: {c.course_name})" 
            for c in classes
        ])
        courses_ctx = ", ".join([c.name for c in courses])

        system_prompt = f"""
You are the Zoom Scheduler AI Assistant for Vipul Pawar. 
Today's Date: {current_date}

Existing Batches: {courses_ctx}

Current Schedule:
{classes_ctx if classes_ctx else "No sessions scheduled yet."}

Goals:
1. Schedule sessions instantly if the user provides enough info (Course, Topic, Date, Time).
2. Check for conflicts (don't schedule sessions at the same time).
3. If info is missing, ask for it politely.

DIRECT SCHEDULING RULE:
If you have all details to schedule a class (Course Name, Topic, Date, Time), end your response with:
ACTION_JSON: {{"course_name": "...", "topic_name": "...", "date": "YYYY-MM-DD", "start_time": "HH:MM", "duration_minutes": 90}}
AUTO_EXECUTE: true

If you are just suggesting or drafting (info is partial), use:
ACTION_JSON: {{...}}
AUTO_EXECUTE: false
"""

        # 3. Build Messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": "user" if msg.role == "user" else "assistant", "content": msg.content})
        messages.append({"role": "user", "content": message})

        try:
            completion = await self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            text = completion.choices[0].message.content

            # 4. Parse Actions
            suggested_action = None
            force_execute = False
            
            if "ACTION_JSON:" in text:
                parts = text.split("ACTION_JSON:")
                main_text = parts[0].strip()
                action_part = parts[1].strip()
                
                if "AUTO_EXECUTE:" in action_part:
                    sub_parts = action_part.split("AUTO_EXECUTE:")
                    json_str = sub_parts[0].strip()
                    force_execute = "true" in sub_parts[1].lower()
                else:
                    json_str = action_part
                
                try:
                    # Clean up possible markdown code blocks if Llama wraps the JSON
                    if json_str.startswith("```"):
                        json_str = json_str.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                        if json_str.startswith("json"):
                            json_str = json_str[4:].strip()
                            
                    suggested_action = json.loads(json_str)
                except Exception as e:
                    logger.warning(f"Failed to parse AI JSON: {e}. JSON string was: {json_str}")
                
                text = main_text

            return schemas.ChatResponse(
                response=text,
                suggested_action=suggested_action,
                force_execute=force_execute
            )

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return schemas.ChatResponse(response=f"I encountered an error with Groq: {str(e)}")

ai_service = AIService()
