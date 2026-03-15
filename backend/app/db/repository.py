from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import schemas
from . import models


class ClassRepository:
    """Repository to handle database operations for courses and class sessions."""

    # Course Operations
    async def create_course(self, db: AsyncSession, payload: schemas.CourseCreate) -> schemas.Course:
        course_id = str(uuid4())
        db_course = models.Course(
            id=course_id, 
            name=payload.name, 
            created_at=datetime.utcnow()
        )
        db.add(db_course)
        await db.commit()
        await db.refresh(db_course)
        return schemas.Course.model_validate(db_course, from_attributes=True)

    async def get_course(self, db: AsyncSession, course_id: str) -> Optional[schemas.Course]:
        result = await db.execute(select(models.Course).where(models.Course.id == course_id))
        db_course = result.scalar_one_or_none()
        return schemas.Course.model_validate(db_course, from_attributes=True) if db_course else None

    async def find_course_by_name(self, db: AsyncSession, name: str) -> Optional[schemas.Course]:
        result = await db.execute(select(models.Course).where(models.Course.name == name))
        db_course = result.scalar_one_or_none()
        return schemas.Course.model_validate(db_course, from_attributes=True) if db_course else None

    async def list_courses(self, db: AsyncSession) -> List[schemas.Course]:
        result = await db.execute(select(models.Course))
        return [schemas.Course.model_validate(c, from_attributes=True) for c in result.scalars().all()]

    # Class Session Operations
    async def create_class(
        self, 
        db: AsyncSession,
        payload: schemas.ClassCreate, 
        course: schemas.Course, 
        zoom_id: str, 
        zoom_url: str, 
        timezone: str,
        duration: int = 90
    ) -> schemas.ClassSession:
        class_id = str(uuid4())
        now = datetime.utcnow()
        db_class = models.ClassSession(
            id=class_id,
            course_id=course.id,
            course_name=course.name,
            topic_name=payload.topic_name,
            assignment_name=payload.assignment_name,
            date=payload.date,
            start_time=payload.start_time,
            duration_minutes=duration,
            timezone=timezone,
            zoom_meeting_id=str(zoom_id),
            zoom_join_url=zoom_url,
            created_at=now,
            updated_at=now,
        )
        db.add(db_class)
        await db.commit()
        await db.refresh(db_class)
        return schemas.ClassSession.model_validate(db_class, from_attributes=True)

    async def get_class(self, db: AsyncSession, class_id: str) -> Optional[schemas.ClassSession]:
        result = await db.execute(select(models.ClassSession).where(models.ClassSession.id == class_id))
        db_class = result.scalar_one_or_none()
        return schemas.ClassSession.model_validate(db_class, from_attributes=True) if db_class else None

    async def list_classes(self, db: AsyncSession) -> List[schemas.ClassSession]:
        result = await db.execute(select(models.ClassSession))
        return [schemas.ClassSession.model_validate(c, from_attributes=True) for c in result.scalars().all()]

    async def update_class(
        self, 
        db: AsyncSession,
        class_id: str, 
        payload: schemas.ClassUpdate, 
        course: Optional[schemas.Course] = None, 
        zoom_url: Optional[str] = None, 
        timezone: Optional[str] = None
    ) -> Optional[schemas.ClassSession]:
        result = await db.execute(select(models.ClassSession).where(models.ClassSession.id == class_id))
        db_class = result.scalar_one_or_none()
        if not db_class:
            return None
            
        update_data = payload.model_dump(exclude_unset=True)
        
        if course:
            db_class.course_id = course.id
            db_class.course_name = course.name
        if zoom_url:
            db_class.zoom_join_url = zoom_url
        if timezone:
            db_class.timezone = timezone
            
        for key, value in update_data.items():
            if hasattr(db_class, key):
                setattr(db_class, key, value)
        
        db_class.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_class)
        return schemas.ClassSession.model_validate(db_class, from_attributes=True)

    async def delete_class(self, db: AsyncSession, class_id: str) -> bool:
        result = await db.execute(select(models.ClassSession).where(models.ClassSession.id == class_id))
        db_class = result.scalar_one_or_none()
        if db_class:
            await db.delete(db_class)
            await db.commit()
            return True
        return False


repository = ClassRepository()
