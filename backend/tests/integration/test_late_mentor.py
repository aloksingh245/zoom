import asyncio
import logging
from unittest.mock import AsyncMock, patch
from integrations.google_calendar.listeners import handle_class_updated
from modules.classes.schemas import ClassSession
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

class DummyClass(BaseModel):
    id: str = "test-imported-id"
    course_id: str = "course-id"
    course_name: str = "Imported Course"
    topic_name: str = "Imported Topic"
    date: str = "2024-01-01"
    start_time: str = "10:00"
    duration_minutes: int = 90
    timezone: str = "Asia/Kolkata"
    zoom_meeting_id: str = "zoom-id"
    zoom_join_url: str = "http://zoom.us"
    # Note: calendar_event_id is None by default in schema if omitted
    mentor_email: str = "new_mentor@test.com" # Added during update
    created_at: str = "2024-01-01T10:00:00Z"
    updated_at: str = "2024-01-01T10:00:00Z"
    
async def run_test():
    updated_class = ClassSession(**DummyClass().model_dump())
    
    with patch('integrations.google_calendar.listeners.calendar_service') as mock_cal_service:
        mock_cal_service.create_event = AsyncMock(return_value="gcal_late_123")
        mock_cal_service.update_event = AsyncMock()
        
        with patch('integrations.google_calendar.listeners.async_session_factory') as mock_db_factory:
            mock_session = AsyncMock()
            mock_db_factory.return_value.__aenter__.return_value = mock_session
            
            print("--- Running handle_class_updated for Late Mentor Addition ---")
            await handle_class_updated(updated_class)
            print("--- Finished handle_class_updated ---")
            
            try:
                mock_cal_service.create_event.assert_called_once()
                print("GCal Event Created (Late Addition) called: OK")
                mock_cal_service.update_event.assert_not_called()
                print("GCal Event Update NOT called (Correct): OK - TEST PASSED")
            except AssertionError:
                print("TEST FAILED")

if __name__ == "__main__":
    asyncio.run(run_test())
