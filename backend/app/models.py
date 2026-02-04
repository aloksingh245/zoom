from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    name: str = Field(min_length=1)


class Course(BaseModel):
    id: str
    name: str
    created_at: datetime


class ClassCreate(BaseModel):
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    topic_name: str = Field(min_length=1)
    assignment_name: Optional[str] = None
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    timezone: Optional[str] = None


class ClassUpdate(BaseModel):
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    topic_name: Optional[str] = None
    assignment_name: Optional[str] = None
    date: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    timezone: Optional[str] = None


class ClassSession(BaseModel):
    id: str
    course_id: str
    course_name: str
    topic_name: str
    assignment_name: Optional[str]
    date: str
    start_time: str
    duration_minutes: int
    timezone: str
    zoom_meeting_id: str
    zoom_join_url: str
    created_at: datetime
    updated_at: datetime
