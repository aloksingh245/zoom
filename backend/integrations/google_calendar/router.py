from fastapi import APIRouter, Request
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks/calendar", tags=["calendar"])

@router.post("")
async def calendar_webhook(request: Request):
    """Handle Google Calendar webhooks."""
    data = await request.json()
    logger.info(f"Calendar webhook received: {data}")
    return {"status": "ok"}
