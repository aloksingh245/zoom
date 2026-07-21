import logging
from datetime import datetime
from sqlalchemy import update
from core.database import async_session_factory
from core.events import event_bus
from modules.classes.schemas import ClassSession as ClassSchema
from modules.classes.models import ClassSession as ClassModel
from integrations.google_sheets.client import sheets_service

logger = logging.getLogger(__name__)

async def handle_class_created(created_class: ClassSchema):
    try:
        # Load Tenant Settings
        from modules.settings.models import TenantSettings
        from sqlalchemy import select
        async with async_session_factory() as db:
            ts_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == created_class.tenant_id))
            tenant_settings = ts_res.scalar_one_or_none()

        # Initialize headers if sheet is empty
        await sheets_service.initialize_headers(tenant_settings)

        row_data = [
            datetime.utcnow().isoformat() + "Z",
            created_class.id,
            created_class.course_name, 
            created_class.topic_name, 
            created_class.mentor_email or "No Mentor", 
            created_class.date, 
            created_class.start_time,
            created_class.duration_minutes,
            created_class.timezone,
            created_class.zoom_meeting_id,
            created_class.zoom_join_url, 
            created_class.assignment_name or "",
            "Scheduled"
        ]
        sheet_row_id = await sheets_service.append_row(row_data, tenant_settings)
        
        if sheet_row_id:
            async with async_session_factory() as db:
                await db.execute(
                    update(ClassModel)
                    .where(ClassModel.id == created_class.id)
                    .values(sheet_row_id=sheet_row_id)
                )
                await db.commit()
    except Exception as e:
        logger.error(f"Sheets listener failed: {e}")

async def handle_class_updated(updated_class: ClassSchema):
    if not updated_class.sheet_row_id:
        # If it doesn't have a row yet (maybe it was in STUB mode), try creating it
        await handle_class_created(updated_class)
        return

    try:
        # Load Tenant Settings
        from modules.settings.models import TenantSettings
        from sqlalchemy import select
        async with async_session_factory() as db:
            ts_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == updated_class.tenant_id))
            tenant_settings = ts_res.scalar_one_or_none()

        row_data = [
            datetime.utcnow().isoformat() + "Z",
            updated_class.id,
            updated_class.course_name, 
            updated_class.topic_name, 
            updated_class.mentor_email or "No Mentor", 
            updated_class.date, 
            updated_class.start_time,
            updated_class.duration_minutes,
            updated_class.timezone,
            updated_class.zoom_meeting_id,
            updated_class.zoom_join_url, 
            updated_class.assignment_name or "",
            "Updated"
        ]
        await sheets_service.update_row(updated_class.sheet_row_id, row_data, tenant_settings)
    except Exception as e:
        logger.error(f"Sheets update listener failed: {e}")

async def handle_class_deleted(deleted_class: ClassSchema):
    if not deleted_class.sheet_row_id:
        return
        
    try:
        # Load Tenant Settings
        from modules.settings.models import TenantSettings
        from sqlalchemy import select
        async with async_session_factory() as db:
            ts_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == deleted_class.tenant_id))
            tenant_settings = ts_res.scalar_one_or_none()

        # We don't delete the row, we mark it as cancelled
        row_data = [
            datetime.utcnow().isoformat() + "Z",
            deleted_class.id,
            deleted_class.course_name, 
            deleted_class.topic_name, 
            deleted_class.mentor_email or "No Mentor", 
            deleted_class.date, 
            deleted_class.start_time,
            deleted_class.duration_minutes,
            deleted_class.timezone,
            deleted_class.zoom_meeting_id,
            deleted_class.zoom_join_url, 
            deleted_class.assignment_name or "",
            "CANCELLED"
        ]
        await sheets_service.update_row(deleted_class.sheet_row_id, row_data, tenant_settings)
    except Exception as e:
        logger.error(f"Sheets delete listener failed: {e}")

def register_listeners():
    event_bus.subscribe("class_created", handle_class_created)
    event_bus.subscribe("class_updated", handle_class_updated)
    event_bus.subscribe("class_deleted", handle_class_deleted)
