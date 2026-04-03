from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ClassCreate(BaseModel):
    course_id: Optional[str] = Field(None, description="Existing course ID")
    course_name: Optional[str] = Field(None, description="New course name if ID not provided")
    topic_name: str = Field(..., min_length=1)
    assignment_name: Optional[str] = None
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Time in HH:mm format")
    duration_minutes: Optional[int] = Field(None, description="Duration of the class in minutes")
    timezone: Optional[str] = None
    mentor_email: Optional[str] = None

class ClassUpdate(BaseModel):
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    topic_name: Optional[str] = None
    assignment_name: Optional[str] = None
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    duration_minutes: Optional[int] = None
    timezone: Optional[str] = None
    mentor_email: Optional[str] = None

class ClassSession(BaseModel):
    id: str
    course_id: str
    course_name: str
    topic_name: str
    assignment_name: Optional[str] = None
    date: str
    start_time: str
    duration_minutes: int
    timezone: str
    zoom_meeting_id: str
    zoom_join_url: str
    calendar_event_id: Optional[str] = None
    mentor_email: Optional[str] = None
    sheet_row_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
