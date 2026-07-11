"""
router.py — FastAPI endpoints for the AI Agent Chat system.

Exposes a streaming endpoint:
  - `POST /api/agent/chat` (Server-Sent Events)

WHY SSE (SERVER-SENT EVENTS)?
  SSE is the industry-standard way to stream text response data from a server to a client.
  Unlike WebSockets, SSE:
  1. Runs over standard HTTP (no protocol upgrade needed)
  2. Built-in support for reconnection and client events
  3. Simpler implementation, less overhead

AUTH INTEGRATION:
  We hook directly into your existing `get_current_user` dependency from `modules.auth.dependencies`.
  This guarantees that:
  1. The user must be logged in.
  2. We have access to their email, role ('admin', 'mentor', 'student'), and ID.
  3. Security policies can be enforced before processing the request.
"""

import json
import base64
import logging
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from modules.auth.dependencies import get_current_user
from modules.auth.models import User
from .agent import run_agent_stream
from .voice.stt import transcribe_audio
from .voice.tts import synthesize_speech

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["ai-agent"])


class ChatPayload(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="The message prompt to send to the AI agent.")


@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat_with_agent(
    payload: ChatPayload,
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    Send a message to the AI Agent and receive a streamed SSE response.
    
    The response streams tokens word-by-word, ending with a '[DONE]' token.
    Each token is formatted as a Server-Sent Event (SSE):
      `data: <token_content>\n\n`
    """
    
    async def sse_generator():
        # run_agent_stream handles retrieval, memory context, and agent execution loop
        async for token in run_agent_stream(
            user_id=str(current_user.id),
            user_email=current_user.email,
            user_role=current_user.role,
            message=payload.message
        ):
            # Encode token to safely handle newlines or special characters
            yield f"data: {json.dumps(token)}\n\n"
        
        # Send a terminal packet so the frontend knows streaming is complete
        yield "data: \"[DONE]\"\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in Nginx proxies (critical for real-time streaming)
        }
    )


@router.post("/chat/voice", status_code=status.HTTP_200_OK)
async def chat_with_agent_voice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts an audio file upload, transcribes it, queries the agent,
    synthesizes the response into audio, and returns text and audio bytes.
    """
    try:
        # 1. Read raw audio bytes
        audio_bytes = await file.read()
        mime_type = file.content_type or "audio/webm"
        
        # 2. Transcribe Speech-to-Text using Gemini
        query_text = await transcribe_audio(audio_bytes, mime_type=mime_type)
        if not query_text:
            return {
                "user_text": "",
                "agent_text": "I couldn't hear what you said. Please try speaking again.",
                "audio": ""
            }
            
        # 3. Query the Agent Loop to get the text response
        response_chunks = []
        async for token in run_agent_stream(
            user_id=str(current_user.id),
            user_email=current_user.email,
            user_role=current_user.role,
            message=query_text
        ):
            response_chunks.append(token)
            
        full_response_text = "".join(response_chunks)
        
        # 4. Synthesize Text-to-Speech using gTTS
        audio_data = await synthesize_speech(full_response_text)
        
        # 5. Base64 encode the MP3 audio
        audio_base64 = base64.b64encode(audio_data).decode("utf-8") if audio_data else ""
        
        return {
            "user_text": query_text,
            "agent_text": full_response_text,
            "audio": audio_base64
        }
    except Exception as e:
        logger.error(f"Voice chat endpoint error: {e}")
        return {
            "user_text": "",
            "agent_text": f"Error processing voice request: {str(e)}",
            "audio": ""
        }
