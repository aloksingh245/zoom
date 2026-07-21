import pytest
from unittest.mock import patch, MagicMock
from modules.classes.schemas import ClassSession
from pydantic import BaseModel
from integrations.email.listeners import handle_class_created, handle_class_updated

class DummyClass(BaseModel):
    id: str = "test-id"
    course_name: str = "Test Course"
    topic_name: str = "Test Topic"
    date: str = "2026-07-20"
    start_time: str = "10:00"
    zoom_join_url: str = "http://zoom.us/j/123"
    timezone: str = "Asia/Kolkata"
    mentor_email: str = "mentor@test.com"
    course_id: str = "course-id"
    duration_minutes: int = 90
    zoom_meeting_id: str = "zoom-id"
    created_at: str = "2026-07-20T10:00:00Z"
    updated_at: str = "2026-07-20T10:00:00Z"

@pytest.mark.asyncio
async def test_email_listener_on_class_created():
    created_class = ClassSession(**DummyClass().model_dump())
    
    with patch('integrations.email.listeners.email_notification_service') as mock_email_svc:
        mock_email_svc.send_class_assigned_notification = MagicMock()
        
        await handle_class_created(created_class)
        
        mock_email_svc.send_class_assigned_notification.assert_called_once_with(
            class_id="test-id",
            mentor_email="mentor@test.com",
            class_topic="Test Course - Test Topic",
            date="2026-07-20",
            start_time="10:00",
            duration=90,
            timezone="Asia/Kolkata",
            zoom_link="http://zoom.us/j/123"
        )

@pytest.mark.asyncio
async def test_email_listener_on_class_updated():
    updated_class = ClassSession(**DummyClass().model_dump())
    
    with patch('integrations.email.listeners.email_notification_service') as mock_email_svc:
        mock_email_svc.send_class_updated_notification = MagicMock()
        
        await handle_class_updated(updated_class)
        
        mock_email_svc.send_class_updated_notification.assert_called_once_with(
            class_id="test-id",
            mentor_email="mentor@test.com",
            class_topic="Test Course - Test Topic",
            date="2026-07-20",
            start_time="10:00",
            duration=90,
            timezone="Asia/Kolkata",
            zoom_link="http://zoom.us/j/123"
        )
