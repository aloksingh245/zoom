from datetime import datetime
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .models import Course, CourseCreate, ClassSession, ClassCreate, ClassUpdate
from .settings import settings
from .store import InMemoryStore
from .zoom_client import ZoomClient
from zoneinfo import ZoneInfo

app = FastAPI(title="Class Scheduler API", version="0.1.0")

origins = [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]
if not origins:
    origins = ["*"]
allow_credentials = origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = InMemoryStore()
zoom = ZoomClient()


def resolve_course_for_create(payload: ClassCreate) -> Course:
    if payload.course_id:
        course = store.get_course(payload.course_id)
        if not course:
            raise HTTPException(status_code=400, detail="course_id not found")
        return course
    if payload.course_name:
        existing = store.find_course_by_name(payload.course_name)
        if existing:
            return existing
        return store.create_course(CourseCreate(name=payload.course_name))
    raise HTTPException(status_code=400, detail="course_id or course_name required")


def resolve_course_for_update(payload: ClassUpdate) -> Course | None:
    if payload.course_id:
        course = store.get_course(payload.course_id)
        if not course:
            raise HTTPException(status_code=400, detail="course_id not found")
        return course
    if payload.course_name:
        existing = store.find_course_by_name(payload.course_name)
        if existing:
            return existing
        return store.create_course(CourseCreate(name=payload.course_name))
    return None


def validate_not_past(date_str: str, time_str: str, timezone: str) -> None:
    try:
        local_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00").replace(
            tzinfo=ZoneInfo(timezone)
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {exc}") from exc

    now_local = datetime.now(tz=ZoneInfo(timezone))
    if local_dt <= now_local:
        raise HTTPException(
            status_code=400,
            detail="Start time must be in the future. Zoom defaults to current time if start_time is past.",
        )


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "time": datetime.utcnow().isoformat()}


@app.get("/api/courses", response_model=List[Course])
async def list_courses() -> List[Course]:
    return store.list_courses()


@app.post("/api/courses", response_model=Course)
async def create_course(payload: CourseCreate) -> Course:
    return store.create_course(payload)


@app.get("/api/classes", response_model=List[ClassSession])
async def list_classes() -> List[ClassSession]:
    return store.list_classes()


@app.get("/api/classes/{class_id}", response_model=ClassSession)
async def get_class(class_id: str) -> ClassSession:
    class_item = store.get_class(class_id)
    if not class_item:
        raise HTTPException(status_code=404, detail="class not found")
    return class_item


@app.post("/api/classes", response_model=ClassSession)
async def create_class(payload: ClassCreate) -> ClassSession:
    course = resolve_course_for_create(payload)
    timezone = zoom.normalize_timezone(payload.timezone or settings.timezone_default)
    validate_not_past(payload.date, payload.start_time, timezone)
    topic = f"{course.name} - {payload.topic_name}"
    print(payload.start_time)
    try:
        meeting = await zoom.create_meeting(
            topic=topic,
            agenda=payload.assignment_name,
            date=payload.date,
            start_time=payload.start_time,
            timezone=timezone,
            duration=90,
        )
        print(meeting)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (httpx.HTTPError, ValidationError) as exc:  # type: ignore[name-defined]
        raise HTTPException(status_code=502, detail=f"Zoom create failed: {exc}")

    zoom_meeting_id = str(meeting.get("id", ""))
    zoom_join_url = meeting.get("join_url", "")
    if not zoom_meeting_id or not zoom_join_url:
        raise HTTPException(status_code=502, detail="Zoom response missing meeting id or join_url")

    return store.create_class(payload, course, zoom_meeting_id, zoom_join_url, timezone)


@app.put("/api/classes/{class_id}", response_model=ClassSession)
async def update_class(class_id: str, payload: ClassUpdate) -> ClassSession:
    existing = store.get_class(class_id)
    if not existing:
        raise HTTPException(status_code=404, detail="class not found")

    course = resolve_course_for_update(payload)
    new_course_name = course.name if course else existing.course_name
    topic_name = payload.topic_name if payload.topic_name is not None else existing.topic_name
    assignment_name = payload.assignment_name if payload.assignment_name is not None else existing.assignment_name
    date = payload.date if payload.date is not None else existing.date
    start_time = payload.start_time if payload.start_time is not None else existing.start_time
    timezone = zoom.normalize_timezone(payload.timezone if payload.timezone is not None else existing.timezone)
    validate_not_past(date, start_time, timezone)

    topic = f"{new_course_name} - {topic_name}"
    try:
        await zoom.update_meeting(
            meeting_id=existing.zoom_meeting_id,
            topic=topic,
            agenda=assignment_name,
            date=date,
            start_time=start_time,
            timezone=timezone,
            duration=90,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (httpx.HTTPError, ValidationError) as exc:  # type: ignore[name-defined]
        raise HTTPException(status_code=502, detail=f"Zoom update failed: {exc}")

    return store.update_class(class_id, payload, course, None, timezone)


@app.delete("/api/classes/{class_id}")
async def delete_class(class_id: str) -> dict:
    existing = store.get_class(class_id)
    if not existing:
        raise HTTPException(status_code=404, detail="class not found")

    try:
        await zoom.delete_meeting(meeting_id=existing.zoom_meeting_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Zoom delete failed: {exc}")

    store.delete_class(class_id)
    return {"deleted": True}
