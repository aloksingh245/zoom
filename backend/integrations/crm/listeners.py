import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from core.events import event_bus
from modules.classes.schemas import ClassSession as ClassSchema
from integrations.crm.client import crm_service

logger = logging.getLogger(__name__)

async def handle_class_sync(created_class: ClassSchema):
    """Transform the class session into a CRM-compatible payload and sync."""
    
    # Calculate end time (assuming 90 mins duration)
    tz = ZoneInfo(created_class.timezone)
    start_dt = datetime.fromisoformat(f"{created_class.date}T{created_class.start_time}:00").replace(tzinfo=tz)
    end_dt = start_dt + timedelta(minutes=created_class.duration_minutes)
    
    payload = {
        "BatchId": created_class.course_id, # Or use a mapped field if batch_id is different
        "Topic": created_class.topic_name,
        "Description": f"{created_class.course_name}: {created_class.topic_name}",
        "ZoomClassId": created_class.zoom_meeting_id,
        "ZoomClassURL": created_class.zoom_join_url,
        "ClassStartDateTime": start_dt.isoformat(),
        "ClassEndDateTime": end_dt.isoformat(),
        "IsInteractiveClass": True,
        "Active": True,
        "Deleted": False
    }

    try:
        await crm_service.sync_class(payload)
    except Exception as e:
        logger.error(f"CRM sync listener failed: {e}")

def register_listeners():
    event_bus.subscribe("class_created", handle_class_sync)
    event_bus.subscribe("class_updated", handle_class_sync)
    # We could also handle "class_deleted" if the CRM supports it.
