from datetime import datetime
from pydantic import BaseModel, Field

class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Unique name of the course")

class Course(BaseModel):
    id: str
    name: str
    created_at: datetime
