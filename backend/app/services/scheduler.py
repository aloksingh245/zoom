import logging
from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

import httpx
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..db.repository import repository
from ..models import schemas
from .zoom import zoom_service

logger = logging.getLogger(__name__)


class SchedulerService:
    """Business logic service to manage classes and Zoom synchronization."""

    def _validate_not_past(self, date_str: str, time_str: str, timezone: str) -> None:
        try:
            local_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00").replace(
                tzinfo=ZoneInfo(timezone)
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid date/time: {exc}")

        now_local = datetime.now(tz=ZoneInfo(timezone))
        if local_dt <= now_local:
            raise HTTPException(
                status_code=400,
                detail="Start time must be in the future.",
            )

    async def _resolve_course_for_create(self, db: AsyncSession, payload: schemas.ClassCreate) -> schemas.Course:
        if payload.course_id:
            course = await repository.get_course(db, payload.course_id)
            if not course:
                raise HTTPException(status_code=400, detail="Course ID not found")
            return course
        if payload.course_name:
            existing = await repository.find_course_by_name(db, payload.course_name)
            if existing:
                return existing
            return await repository.create_course(db, schemas.CourseCreate(name=payload.course_name))
        raise HTTPException(status_code=400, detail="course_id or course_name required")

    async def _resolve_course_for_update(self, db: AsyncSession, payload: schemas.ClassUpdate) -> Optional[schemas.Course]:
        if payload.course_id:
            course = await repository.get_course(db, payload.course_id)
            if not course:
                raise HTTPException(status_code=400, detail="Course ID not found")
            return course
        if payload.course_name:
            existing = await repository.find_course_by_name(db, payload.course_name)
            if existing:
                return existing
            return await repository.create_course(db, schemas.CourseCreate(name=payload.course_name))
        return None

    async def list_classes(self, db: AsyncSession) -> List[schemas.ClassSession]:
        return await repository.list_classes(db)

    async def get_class(self, db: AsyncSession, class_id: str) -> schemas.ClassSession:
        class_item = await repository.get_class(db, class_id)
        if not class_item:
            raise HTTPException(status_code=404, detail="Class not found")
        return class_item

    async def create_class(self, db: AsyncSession, payload: schemas.ClassCreate) -> schemas.ClassSession:
        course = await self._resolve_course_for_create(db, payload)
        timezone = zoom_service.normalize_timezone(payload.timezone or settings.timezone_default)
        self._validate_not_past(payload.date, payload.start_time, timezone)
        
        topic = f"{course.name} - {payload.topic_name}"
        try:
            meeting = await zoom_service.create_meeting(
                topic=topic,
                agenda=payload.assignment_name,
                date=payload.date,
                start_time=payload.start_time,
                timezone=timezone,
                duration=settings.class_duration_minutes,
            )
        except (httpx.HTTPError, ValidationError, RuntimeError) as exc:
            logger.error(f"Zoom creation failed: {exc}")
            raise HTTPException(status_code=502, detail=f"Zoom integration failed: {exc}")

        zoom_id = str(meeting.get("id", ""))
        zoom_url = meeting.get("join_url", "")
        
        return await repository.create_class(
            db, payload, course, zoom_id, zoom_url, timezone, settings.class_duration_minutes
        )

    async def update_class(self, db: AsyncSession, class_id: str, payload: schemas.ClassUpdate) -> schemas.ClassSession:
        existing = await self.get_class(db, class_id)
        course = await self._resolve_course_for_update(db, payload)
        
        new_course_name = course.name if course else existing.course_name
        topic_name = payload.topic_name if payload.topic_name is not None else existing.topic_name
        assignment_name = payload.assignment_name if payload.assignment_name is not None else existing.assignment_name
        date = payload.date if payload.date is not None else existing.date
        start_time = payload.start_time if payload.start_time is not None else existing.start_time
        timezone = zoom_service.normalize_timezone(payload.timezone if payload.timezone is not None else existing.timezone)
        
        self._validate_not_past(date, start_time, timezone)

        topic = f"{new_course_name} - {topic_name}"
        try:
            await zoom_service.update_meeting(
                meeting_id=existing.zoom_meeting_id,
                topic=topic,
                agenda=assignment_name,
                date=date,
                start_time=start_time,
                timezone=timezone,
                duration=settings.class_duration_minutes,
            )
        except (httpx.HTTPError, ValidationError, RuntimeError) as exc:
            logger.error(f"Zoom update failed: {exc}")
            raise HTTPException(status_code=502, detail=f"Zoom integration failed: {exc}")

        return await repository.update_class(db, class_id, payload, course, None, timezone)

    async def delete_class(self, db: AsyncSession, class_id: str) -> None:
        existing = await self.get_class(db, class_id)
        try:
            await zoom_service.delete_meeting(meeting_id=existing.zoom_meeting_id)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 404:
                raise HTTPException(status_code=502, detail=f"Zoom deletion failed: {exc}")
        except Exception as exc:
            logger.error(f"Zoom deletion failed: {exc}")
            raise HTTPException(status_code=502, detail=f"Zoom integration failed: {exc}")

        await repository.delete_class(db, class_id)


scheduler_service = SchedulerService()
