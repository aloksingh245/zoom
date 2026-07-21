import logging
from core.events import event_bus
from modules.classes.schemas import ClassSession as ClassSchema
from integrations.email.client import email_notification_service

logger = logging.getLogger(__name__)

async def handle_class_created(created_class: ClassSchema):
    logger.info(f"📧 EMAIL LISTENER FIRED: class_created for '{created_class.topic_name}', mentor: {created_class.mentor_email}")
    print(f"\n📧 EMAIL LISTENER FIRED: class_created for '{created_class.topic_name}', mentor: {created_class.mentor_email}")
    if not created_class.mentor_email:
        logger.info("No mentor email assigned, skipping notification.")
        return
    
    # Load Tenant Settings
    from modules.settings.models import TenantSettings
    from sqlalchemy import select
    from core.database import async_session_factory
    tenant_settings = None
    try:
        async with async_session_factory() as db:
            ts_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == created_class.tenant_id))
            tenant_settings = ts_res.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to fetch tenant settings: {e}")

    topic = f"{created_class.course_name} - {created_class.topic_name}"
    try:
        result = email_notification_service.send_class_assigned_notification(
            class_id=created_class.id,
            mentor_email=created_class.mentor_email,
            class_topic=topic,
            date=created_class.date,
            start_time=created_class.start_time,
            duration=created_class.duration_minutes,
            timezone=created_class.timezone,
            zoom_link=created_class.zoom_join_url,
            tenant_settings=tenant_settings
        )
        logger.info(f"Email send result for class_created: {result}")
    except Exception as e:
        logger.error(f"Email notification listener failed for creation: {e}", exc_info=True)

async def handle_class_updated(updated_class: ClassSchema):
    logger.info(f"📧 EMAIL LISTENER FIRED: class_updated for '{updated_class.topic_name}', mentor: {updated_class.mentor_email}")
    print(f"\n📧 EMAIL LISTENER FIRED: class_updated for '{updated_class.topic_name}', mentor: {updated_class.mentor_email}")
    if not updated_class.mentor_email:
        logger.info("No mentor email assigned, skipping update notification.")
        return
    
    # If the mentor changed or is newly assigned, handle_class_mentor_changed will handle the notification
    if hasattr(updated_class, "_old_mentor_email"):
        old_email = getattr(updated_class, "_old_mentor_email")
        if old_email != updated_class.mentor_email:
            logger.info(f"Skipping update email for {updated_class.mentor_email} because mentor has changed or was newly assigned.")
            return

    # Load Tenant Settings
    from modules.settings.models import TenantSettings
    from sqlalchemy import select
    from core.database import async_session_factory
    tenant_settings = None
    try:
        async with async_session_factory() as db:
            ts_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == updated_class.tenant_id))
            tenant_settings = ts_res.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to fetch tenant settings: {e}")

    topic = f"{updated_class.course_name} - {updated_class.topic_name}"
    try:
        result = email_notification_service.send_class_updated_notification(
            class_id=updated_class.id,
            mentor_email=updated_class.mentor_email,
            class_topic=topic,
            date=updated_class.date,
            start_time=updated_class.start_time,
            duration=updated_class.duration_minutes,
            timezone=updated_class.timezone,
            zoom_link=updated_class.zoom_join_url,
            tenant_settings=tenant_settings
        )
        logger.info(f"Email send result for class_updated: {result}")
    except Exception as e:
        logger.error(f"Email notification listener failed for update: {e}", exc_info=True)

async def handle_class_mentor_changed(data: dict):
    logger.info(f"📧 EMAIL LISTENER FIRED: class_mentor_changed")
    print(f"\n📧 EMAIL LISTENER FIRED: class_mentor_changed")
    class_session = data["class_session"]
    old_email = data["old_mentor_email"]
    new_email = data["new_mentor_email"]
    
    # Load Tenant Settings
    from modules.settings.models import TenantSettings
    from sqlalchemy import select
    from core.database import async_session_factory
    tenant_settings = None
    try:
        async with async_session_factory() as db:
            ts_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == class_session.tenant_id))
            tenant_settings = ts_res.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to fetch tenant settings: {e}")

    topic = f"{class_session.course_name} - {class_session.topic_name}"
    
    # 1. Notify the new mentor of class assignment
    if new_email:
        try:
            email_notification_service.send_class_assigned_notification(
                class_id=class_session.id,
                mentor_email=new_email,
                class_topic=topic,
                date=class_session.date,
                start_time=class_session.start_time,
                duration=class_session.duration_minutes,
                timezone=class_session.timezone,
                zoom_link=class_session.zoom_join_url,
                tenant_settings=tenant_settings
            )
            logger.info(f"Notification: Class assigned email sent to new mentor {new_email}")
        except Exception as e:
            logger.error(f"Failed to send class assignment email to new mentor: {e}")

    # 2. Notify the old mentor of unassignment (if it was a valid email and not dummy/placeholder)
    if old_email and "@" in old_email and "test" not in old_email and "example" not in old_email:
        try:
            email_notification_service.send_class_unassigned_notification(
                class_id=class_session.id,
                mentor_email=old_email,
                class_topic=topic,
                date=class_session.date,
                start_time=class_session.start_time,
                timezone=class_session.timezone,
                tenant_settings=tenant_settings
            )
            logger.info(f"Notification: Class unassigned email sent to old mentor {old_email}")
        except Exception as e:
            logger.warning(f"Failed to send class unassigned email to old mentor {old_email}: {e}")

def register_listeners():
    event_bus.subscribe("class_created", handle_class_created)
    event_bus.subscribe("class_updated", handle_class_updated)
    event_bus.subscribe("class_mentor_changed", handle_class_mentor_changed)
    print("\n✅ EMAIL LISTENERS REGISTERED: class_created, class_updated, class_mentor_changed")
    logger.info("✅ EMAIL LISTENERS REGISTERED: class_created, class_updated, class_mentor_changed")
