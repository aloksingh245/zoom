import logging
from sqlalchemy import update
from core.database import async_session_factory
from core.events import event_bus
from modules.classes.schemas import ClassSession as ClassSchema
from modules.classes.models import ClassSession as ClassModel
from integrations.google_sheets.client import sheets_service

logger = logging.getLogger(__name__)

async def handle_class_created(created_class: ClassSchema):
    try:
        row_data = [
            created_class.course_name, 
            created_class.topic_name, 
            created_class.mentor_email or "No Mentor", 
            created_class.date, 
            created_class.zoom_join_url, 
            "Scheduled"
        ]
        sheet_row_id = await sheets_service.append_row(row_data)
        
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

def register_listeners():
    event_bus.subscribe("class_created", handle_class_created)
