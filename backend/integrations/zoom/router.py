from fastapi import APIRouter, Request
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks/zoom", tags=["zoom"])

@router.post("")
async def zoom_webhook(request: Request):
    """Handle Zoom webhooks (e.g., meeting.deleted)."""
    data = await request.json()
    logger.info(f"Zoom webhook received: {data}")
    return {"status": "ok"}
