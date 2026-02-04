from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

from .models import Course, CourseCreate, ClassSession, ClassCreate, ClassUpdate


@dataclass
class InMemoryStore:
    courses: Dict[str, Course] = field(default_factory=dict)
    classes: Dict[str, ClassSession] = field(default_factory=dict)

    def create_course(self, payload: CourseCreate) -> Course:
        course_id = str(uuid4())
        now = datetime.utcnow()
        course = Course(id=course_id, name=payload.name, created_at=now)
        self.courses[course_id] = course
        return course

    def get_course(self, course_id: str) -> Optional[Course]:
        return self.courses.get(course_id)

    def find_course_by_name(self, name: str) -> Optional[Course]:
        for course in self.courses.values():
            if course.name.lower() == name.lower():
                return course
        return None

    def list_courses(self) -> list[Course]:
        return list(self.courses.values())

    def create_class(self, payload: ClassCreate, course: Course, zoom_meeting_id: str, zoom_join_url: str, timezone: str) -> ClassSession:
        class_id = str(uuid4())
        now = datetime.utcnow()
        class_item = ClassSession(
            id=class_id,
            course_id=course.id,
            course_name=course.name,
            topic_name=payload.topic_name,
            assignment_name=payload.assignment_name,
            date=payload.date,
            start_time=payload.start_time,
            duration_minutes=90,
            timezone=timezone,
            zoom_meeting_id=str(zoom_meeting_id),
            zoom_join_url=zoom_join_url,
            created_at=now,
            updated_at=now,
        )
        self.classes[class_id] = class_item
        return class_item

    def get_class(self, class_id: str) -> Optional[ClassSession]:
        return self.classes.get(class_id)

    def list_classes(self) -> list[ClassSession]:
        return list(self.classes.values())

    def update_class(self, class_id: str, payload: ClassUpdate, course: Optional[Course], zoom_join_url: Optional[str], timezone: Optional[str]) -> ClassSession:
        existing = self.classes[class_id]
        now = datetime.utcnow()
        updated = existing.model_copy(update={
            "course_id": course.id if course else existing.course_id,
            "course_name": course.name if course else existing.course_name,
            "topic_name": payload.topic_name if payload.topic_name is not None else existing.topic_name,
            "assignment_name": payload.assignment_name if payload.assignment_name is not None else existing.assignment_name,
            "date": payload.date if payload.date is not None else existing.date,
            "start_time": payload.start_time if payload.start_time is not None else existing.start_time,
            "timezone": timezone if timezone is not None else existing.timezone,
            "zoom_join_url": zoom_join_url if zoom_join_url is not None else existing.zoom_join_url,
            "updated_at": now,
        })
        self.classes[class_id] = updated
        return updated

    def delete_class(self, class_id: str) -> None:
        self.classes.pop(class_id, None)
