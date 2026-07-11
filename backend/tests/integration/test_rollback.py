import asyncio
import logging
from unittest.mock import AsyncMock, patch
from integrations.google_calendar.listeners import handle_class_created
from modules.classes.schemas import ClassSession
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

class DummyClass(BaseModel):
    id: str = "test-id"
    course_name: str = "Test Course"
    topic_name: str = "Test Topic"
    date: str = "2024-01-01"
    start_time: str = "10:00"
    zoom_join_url: str = "http://zoom.us"
    timezone: str = "Asia/Kolkata"
    mentor_email: str = "mentor@test.com"
    
    # Adding extra fields needed by schema
    course_id: str = "course-id"
    duration_minutes: int = 90
    zoom_meeting_id: str = "zoom-id"
    created_at: str = "2024-01-01T10:00:00Z"
    updated_at: str = "2024-01-01T10:00:00Z"
    
async def run_test():
    created_class = ClassSession(**DummyClass().model_dump())
    
    with patch('integrations.google_calendar.listeners.calendar_service') as mock_cal_service:
        mock_cal_service.create_event = AsyncMock(return_value="gcal_1234")
        mock_cal_service.delete_event = AsyncMock()
        
        with patch('integrations.google_calendar.listeners.async_session_factory') as mock_db_factory:
            # Setup mock db to fail on commit
            mock_session = AsyncMock()
            mock_session.commit.side_effect = Exception("Simulated DB lock or failure")
            mock_db_factory.return_value.__aenter__.return_value = mock_session
            
            # Run listener
            print("--- Running handle_class_created ---")
            await handle_class_created(created_class)
            print("--- Finished handle_class_created ---")
            
            # Verify rollback was called
            mock_cal_service.create_event.assert_called_once()
            print("GCal Event Created called: OK")
            
            try:
                mock_cal_service.delete_event.assert_called_once_with(event_id="gcal_1234")
                print("GCal Event Deleted (Rollback) called: OK - TEST PASSED")
            except AssertionError:
                print("GCal Event Deleted (Rollback) was NOT called! - TEST FAILED")

if __name__ == "__main__":
    asyncio.run(run_test())
