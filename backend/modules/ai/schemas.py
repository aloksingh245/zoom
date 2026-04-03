from pydantic import BaseModel
from typing import List, Optional, Any

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    suggested_action: Optional[Any] = None # Could be a class creation payload
    force_execute: Optional[bool] = False # If true, frontend will auto-schedule
