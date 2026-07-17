import logging
from core.events import event_bus
from modules.classes.schemas import ClassSession as ClassSchema
from integrations.email.client import email_notification_service

logger = logging.getLogger(__name__)

async def handle_class_created(created_class: ClassSchema):
    if not created_class.mentor_email:
        return
    
    topic = f"{created_class.course_name} - {created_class.topic_name}"
    try:
        email_notification_service.send_class_assigned_notification(
            mentor_email=created_class.mentor_email,
            class_topic=topic,
            date=created_class.date,
            start_time=created_class.start_time,
            duration=created_class.duration_minutes,
            timezone=created_class.timezone,
            zoom_link=created_class.zoom_join_url
        )
    except Exception as e:
        logger.error(f"Email notification listener failed for creation: {e}")

async def handle_class_updated(updated_class: ClassSchema):
    if not updated_class.mentor_email:
        return
    
    topic = f"{updated_class.course_name} - {updated_class.topic_name}"
    try:
        email_notification_service.send_class_updated_notification(
            mentor_email=updated_class.mentor_email,
            class_topic=topic,
            date=updated_class.date,
            start_time=updated_class.start_time,
            duration=updated_class.duration_minutes,
            timezone=updated_class.timezone,
            zoom_link=updated_class.zoom_join_url
        )
    except Exception as e:
        logger.error(f"Email notification listener failed for update: {e}")

def register_listeners():
    event_bus.subscribe("class_created", handle_class_created)
    event_bus.subscribe("class_updated", handle_class_updated)
