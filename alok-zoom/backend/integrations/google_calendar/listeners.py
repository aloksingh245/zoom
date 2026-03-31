import logging
from sqlalchemy import update
from core.config import settings
from core.database import async_session_factory
from core.events import event_bus
from modules.classes.schemas import ClassSession as ClassSchema
from modules.classes.models import ClassSession as ClassModel
from integrations.google_calendar.client import calendar_service

logger = logging.getLogger(__name__)

async def handle_class_created(created_class: ClassSchema):
    logger.info(f"Listener received class_created for: {created_class.topic_name}")
    if not created_class.mentor_email:
        logger.warning(f"No mentor_email found for class {created_class.id}. Skipping calendar creation.")
        return
    
    logger.info(f"Creating GCal event for mentor: {created_class.mentor_email}")
    topic = f"{created_class.course_name} - {created_class.topic_name}"
    try:
        event_id = await calendar_service.create_event(
            mentor_email=created_class.mentor_email,
            topic=topic,
            date=created_class.date,
            start_time=created_class.start_time,
            zoom_link=created_class.zoom_join_url,
            timezone=created_class.timezone,
            duration=created_class.duration_minutes
        )
        
        if event_id:
            logger.info(f"GCal event created with ID: {event_id}")
            try:
                async with async_session_factory() as db:
                    await db.execute(
                        update(ClassModel)
                        .where(ClassModel.id == created_class.id)
                        .values(calendar_event_id=event_id)
                    )
                    await db.commit()
            except Exception as db_exc:
                logger.error(f"Database update failed after creating GCal event. Rolling back GCal event {event_id}: {db_exc}")
                try:
                    await calendar_service.delete_event(event_id=event_id)
                except Exception as rollback_exc:
                    logger.error(f"CRITICAL: Failed to delete orphaned GCal event {event_id}: {rollback_exc}")
                raise db_exc
        else:
            logger.warning("Calendar event creation returned no ID.")
    except Exception as e:
        logger.error(f"Calendar creation listener failed: {e}", exc_info=True)

async def handle_class_updated(updated_class: ClassSchema):
    topic = f"{updated_class.course_name} - {updated_class.topic_name}"
    
    if not updated_class.calendar_event_id:
        if updated_class.mentor_email:
            try:
                event_id = await calendar_service.create_event(
                    mentor_email=updated_class.mentor_email,
                    topic=topic,
                    date=updated_class.date,
                    start_time=updated_class.start_time,
                    zoom_link=updated_class.zoom_join_url,
                    timezone=updated_class.timezone,
                    duration=updated_class.duration_minutes
                )
                if event_id:
                    try:
                        async with async_session_factory() as db:
                            await db.execute(
                                update(ClassModel)
                                .where(ClassModel.id == updated_class.id)
                                .values(calendar_event_id=event_id)
                            )
                            await db.commit()
                    except Exception as db_exc:
                        logger.error(f"DB update failed after late GCal event creation. Rolling back {event_id}: {db_exc}")
                        try:
                            await calendar_service.delete_event(event_id=event_id)
                        except Exception:
                            pass
            except Exception as e:
                logger.error(f"Failed to create late GCal event: {e}")
        return

    try:
        await calendar_service.update_event(
            event_id=updated_class.calendar_event_id,
            mentor_email=updated_class.mentor_email,
            topic=topic,
            date=updated_class.date,
            start_time=updated_class.start_time,
            zoom_link=updated_class.zoom_join_url,
            timezone=updated_class.timezone,
            duration=updated_class.duration_minutes
        )
    except Exception as e:
        logger.error(f"Calendar update listener failed: {e}")

async def handle_class_deleted(deleted_class: ClassSchema):
    if not deleted_class.calendar_event_id:
        return
        
    try:
        await calendar_service.delete_event(event_id=deleted_class.calendar_event_id)
    except Exception as e:
        logger.error(f"Calendar delete listener failed: {e}")

def register_listeners():
    event_bus.subscribe("class_created", handle_class_created)
    event_bus.subscribe("class_updated", handle_class_updated)
    event_bus.subscribe("class_deleted", handle_class_deleted)
