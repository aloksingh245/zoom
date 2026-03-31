import logging
import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.events import event_bus
from modules.classes import schemas, models
from modules.courses.service import course_service
from integrations.zoom.client import zoom_service
from integrations.google_calendar.client import calendar_service

logger = logging.getLogger(__name__)

class ClassService:
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

    async def _check_conflicts(self, db: AsyncSession, date: str, start_time: str, timezone: str, duration_minutes: int, exclude_id: str | None = None) -> None:
        from datetime import timedelta
        
        classes = await self.list_classes(db)
        
        try:
            new_tz = ZoneInfo(timezone)
            new_start_dt = datetime.fromisoformat(f"{date}T{start_time}:00").replace(tzinfo=new_tz)
            new_end_dt = new_start_dt + timedelta(minutes=duration_minutes)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid date/time or timezone: {exc}")

        for cls in classes:
            if cls.id == exclude_id:
                continue
                
            try:
                cls_tz = ZoneInfo(cls.timezone)
                existing_start_dt = datetime.fromisoformat(f"{cls.date}T{cls.start_time}:00").replace(tzinfo=cls_tz)
                existing_end_dt = existing_start_dt + timedelta(minutes=cls.duration_minutes)
                
                # Check for overlap in absolute time
                if new_start_dt < existing_end_dt and new_end_dt > existing_start_dt:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Time conflict: This slot overlaps with '{cls.course_name} - {cls.topic_name}' ({cls.start_time} {cls.timezone})"
                    )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error checking conflict for class {cls.id}: {e}")
                continue

    async def _resolve_course(self, db: AsyncSession, course_id: Optional[str], course_name: Optional[str]):
        if course_id:
            course = await course_service.get_course(db, course_id)
            if not course:
                raise HTTPException(status_code=400, detail="Course ID not found")
            return course
        if course_name:
            existing = await course_service.find_course_by_name(db, course_name)
            if existing:
                return existing
            from modules.courses.schemas import CourseCreate
            return await course_service.create_course(db, CourseCreate(name=course_name))
        raise HTTPException(status_code=400, detail="course_id or course_name required")

    async def list_classes(self, db: AsyncSession) -> List[schemas.ClassSession]:
        result = await db.execute(select(models.ClassSession))
        return [schemas.ClassSession.model_validate(c, from_attributes=True) for c in result.scalars().all()]

    async def get_class(self, db: AsyncSession, class_id: str) -> schemas.ClassSession:
        result = await db.execute(select(models.ClassSession).where(models.ClassSession.id == class_id))
        db_class = result.scalar_one_or_none()
        if not db_class:
            raise HTTPException(status_code=404, detail="Class not found")
        return schemas.ClassSession.model_validate(db_class, from_attributes=True)

    async def create_class(self, db: AsyncSession, payload: schemas.ClassCreate) -> schemas.ClassSession:
        course = await self._resolve_course(db, payload.course_id, payload.course_name)
        timezone = zoom_service.normalize_timezone(payload.timezone or settings.timezone_default)
        duration_minutes = payload.duration_minutes or settings.class_duration_minutes
        
        self._validate_not_past(payload.date, payload.start_time, timezone)
        await self._check_conflicts(db, payload.date, payload.start_time, timezone, duration_minutes)
        
        topic = f"{course.name} - {payload.topic_name}"
        
        # 1. Zoom is critical - do it synchronously
        try:
            meeting = await zoom_service.create_meeting(
                topic=topic,
                agenda=payload.assignment_name,
                date=payload.date,
                start_time=payload.start_time,
                timezone=timezone,
                duration=duration_minutes,
                mentor_email=payload.mentor_email,
            )
        except Exception as exc:
            logger.error(f"Zoom creation failed: {exc}")
            raise HTTPException(status_code=502, detail=f"Zoom integration failed: {exc}")

        zoom_id = str(meeting.get("id", ""))
        zoom_url = meeting.get("join_url", "")

        # 2. Save to DB
        try:
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
                duration_minutes=duration_minutes,
                timezone=timezone,
                zoom_meeting_id=zoom_id,
                zoom_join_url=zoom_url,
                mentor_email=payload.mentor_email,
                created_at=now,
                updated_at=now,
            )
            db.add(db_class)
            await db.commit()
            await db.refresh(db_class)
            created_class = schemas.ClassSession.model_validate(db_class, from_attributes=True)
            
            # 3. Emit Event for external integrations
            await event_bus.emit("class_created", created_class)
            
            return created_class
            
        except Exception as db_exc:
            logger.error(f"DB Save failed, rolling back Zoom {zoom_id}: {db_exc}")
            try:
                await zoom_service.delete_meeting(meeting_id=zoom_id)
            except Exception:
                pass
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to save class to database.")

    async def update_class(self, db: AsyncSession, class_id: str, payload: schemas.ClassUpdate) -> schemas.ClassSession:
        existing = await self.get_class(db, class_id)
        
        course = None
        if payload.course_id or payload.course_name:
             course = await self._resolve_course(db, payload.course_id, payload.course_name)
        
        new_course_name = course.name if course else existing.course_name
        topic_name = payload.topic_name if payload.topic_name is not None else existing.topic_name
        assignment_name = payload.assignment_name if payload.assignment_name is not None else existing.assignment_name
        mentor_email = payload.mentor_email if payload.mentor_email is not None else existing.mentor_email
        date = payload.date if payload.date is not None else existing.date
        start_time = payload.start_time if payload.start_time is not None else existing.start_time
        timezone = zoom_service.normalize_timezone(payload.timezone if payload.timezone is not None else existing.timezone)
        duration_minutes = payload.duration_minutes if payload.duration_minutes is not None else existing.duration_minutes
        
        self._validate_not_past(date, start_time, timezone)
        await self._check_conflicts(db, date, start_time, timezone, duration_minutes, exclude_id=class_id)

        topic = f"{new_course_name} - {topic_name}"
        try:
            await zoom_service.update_meeting(
                meeting_id=existing.zoom_meeting_id,
                topic=topic,
                agenda=assignment_name,
                date=date,
                start_time=start_time,
                timezone=timezone,
                duration=duration_minutes,
                mentor_email=mentor_email,
            )
        except Exception as exc:
            logger.error(f"Zoom update failed: {exc}")
            raise HTTPException(status_code=502, detail=f"Zoom integration failed: {exc}")

        try:
            result = await db.execute(select(models.ClassSession).where(models.ClassSession.id == class_id))
            db_class = result.scalar_one_or_none()
            
            update_data = payload.model_dump(exclude_unset=True)
            if course:
                db_class.course_id = course.id
                db_class.course_name = course.name
            db_class.timezone = timezone
            
            for key, value in update_data.items():
                if hasattr(db_class, key):
                    setattr(db_class, key, value)
            
            db_class.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(db_class)
            updated_class = schemas.ClassSession.model_validate(db_class, from_attributes=True)
            
            await event_bus.emit("class_updated", updated_class)
            return updated_class
        except Exception as exc:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update class")

    async def delete_class(self, db: AsyncSession, class_id: str) -> None:
        existing = await self.get_class(db, class_id)
        
        try:
            await zoom_service.delete_meeting(meeting_id=existing.zoom_meeting_id)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 404:
                raise HTTPException(status_code=502, detail=f"Zoom deletion failed: {exc}")
        except Exception as exc:
            logger.error(f"Zoom deletion failed: {exc}")

        try:
            result = await db.execute(select(models.ClassSession).where(models.ClassSession.id == class_id))
            db_class = result.scalar_one_or_none()
            if db_class:
                await db.delete(db_class)
                await db.commit()
                
            await event_bus.emit("class_deleted", existing)
        except Exception:
            await db.rollback()
            raise

    async def sync_with_zoom(self, db: AsyncSession) -> dict:
        local_classes = await self.list_classes(db)
        local_zoom_ids = {c.zoom_meeting_id for c in local_classes}
        removed_count = 0
        imported_count = 0
        total_checked = len(local_classes)

        try:
            zoom_data = await zoom_service.list_meetings()
            zoom_meetings = zoom_data.get("meetings", [])
            zoom_meeting_ids = {str(m["id"]) for m in zoom_meetings}

            for cls in local_classes:
                if cls.zoom_meeting_id not in zoom_meeting_ids:
                    await self.delete_class(db, cls.id)
                    removed_count += 1

            synced_course = await course_service.find_course_by_name(db, "Synced from Zoom")
            if not synced_course:
                from modules.courses.schemas import CourseCreate
                synced_course = await course_service.create_course(db, CourseCreate(name="Synced from Zoom"))

            for zm in zoom_meetings:
                z_id = str(zm["id"])
                if z_id not in local_zoom_ids:
                    st_raw = zm.get("start_time", "")
                    try:
                        zm_timezone = zm.get("timezone", settings.timezone_default)
                        normalized_tz = zoom_service.normalize_timezone(zm_timezone)
                        tz = ZoneInfo(normalized_tz)
                        
                        dt_str = st_raw.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(dt_str)
                        
                        # Convert UTC time to the meeting's local timezone
                        if dt.tzinfo:
                            dt_local = dt.astimezone(tz)
                        else:
                            dt_local = dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)
                            
                        z_date = dt_local.strftime('%Y-%m-%d')
                        z_time = dt_local.strftime('%H:%M')
                        
                        # Creating a class internally directly bypassing the external integrations
                        class_id = str(uuid4())
                        now = datetime.utcnow()
                        db_class = models.ClassSession(
                            id=class_id,
                            course_id=synced_course.id,
                            course_name=synced_course.name,
                            topic_name=zm.get("topic", "Zoom Meeting"),
                            date=z_date,
                            start_time=z_time,
                            duration_minutes=zm.get("duration", 90),
                            timezone=normalized_tz,
                            zoom_meeting_id=z_id,
                            zoom_join_url=zm.get("join_url", ""),
                            created_at=now,
                            updated_at=now,
                        )
                        db.add(db_class)
                        await db.commit()
                        await db.refresh(db_class)
                        created_class = schemas.ClassSession.model_validate(db_class, from_attributes=True)
                        await event_bus.emit("class_created", created_class)
                        imported_count += 1
                    except Exception as e:
                        logger.warning(f"Skipping import for meeting {z_id}: {e}")
                        await db.rollback()
                        continue

            return {"strategy": "full_sync", "checked": total_checked, "removed": removed_count, "imported": imported_count}

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (400, 403, 401):
                removed_count = 0
                for cls in local_classes:
                    try:
                        await asyncio.sleep(0.2)
                        await zoom_service.get_meeting(cls.zoom_meeting_id)
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 404:
                            await self.delete_class(db, cls.id)
                            removed_count += 1
                return {"strategy": "surgical_sync", "checked": total_checked, "removed": removed_count, "imported": 0}
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    async def sync_with_calendar(self, db: AsyncSession) -> dict:
        local_classes = await self.list_classes(db)
        removed_count = 0
        updated_count = 0
        total_checked = 0

        for cls in local_classes:
            if not cls.calendar_event_id or cls.calendar_event_id.startswith("stub_gcal_"):
                continue
            
            total_checked += 1
            try:
                gcal_event = await calendar_service.get_event(event_id=cls.calendar_event_id)
                
                # If event is deleted in GCal
                if not gcal_event or gcal_event.get('status') == 'cancelled':
                    # Delete locally and from zoom
                    await self.delete_class(db, cls.id)
                    removed_count += 1
                    continue
                
                # If event exists, check if time has changed
                start_dt_str = gcal_event.get('start', {}).get('dateTime')
                if start_dt_str:
                    gcal_dt = datetime.fromisoformat(start_dt_str)
                    gcal_date = gcal_dt.strftime('%Y-%m-%d')
                    gcal_time = gcal_dt.strftime('%H:%M')
                    
                    if gcal_date != cls.date or gcal_time != cls.start_time:
                        # Time was modified in GCal manually. Update our local DB and Zoom.
                        update_payload = schemas.ClassUpdate(date=gcal_date, start_time=gcal_time)
                        await self.update_class(db, cls.id, update_payload)
                        updated_count += 1

            except Exception as e:
                logger.warning(f"Failed to sync calendar event {cls.calendar_event_id}: {e}")

        return {"checked": total_checked, "removed": removed_count, "updated": updated_count}

class_service = ClassService()
