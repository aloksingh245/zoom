from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.ai import schemas, service

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_with_assistant(
    payload: schemas.ChatRequest, 
    db: AsyncSession = Depends(get_db)
):
    return await service.ai_service.get_chat_response(
        db, 
        payload.message, 
        payload.history
    )
