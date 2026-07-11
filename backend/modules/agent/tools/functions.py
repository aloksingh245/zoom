"""
functions.py — Python functions executed by the Google ADK AI Agent.

These are standard Python functions equipped with type hints and detailed docstrings.
The Google ADK introspects these function signatures to automatically generate
tool schemas (JSON schema declarations) for the Gemini model.

All database transactions are executed cleanly using context managers
over the `async_session_factory` to guarantee correct lifecycle management.
"""

import logging
from typing import Optional, Any
from sqlalchemy import select, func
from core.database import async_session_factory

# Import existing services and models to reuse database logic and sync mechanics
from modules.classes.service import class_service
from modules.classes import models as class_models, schemas as class_schemas
from modules.courses.service import course_service
from modules.courses import schemas as course_schemas
from modules.auth import models as auth_models

logger = logging.getLogger(__name__)

# ==========================================
# 1. READ TOOLS (AVAILABLE TO STUDENT/MENTOR/ADMIN)
# ==========================================

async def get_my_classes(user_email: str, user_role: str) -> list[dict[str, Any]]:
    """Retrieves upcoming class sessions filtered by the user's role.

    Students will retrieve sessions where they are participants or general batch classes.
    Mentors will retrieve sessions where they are assigned as the mentor.
    Admins will retrieve all scheduled sessions.

    Args:
        user_email: The email of the currently authenticated user.
        user_role: The role of the user (e.g. 'admin', 'mentor', 'student').
    """
    async with async_session_factory() as db:
        if user_role == "admin":
            classes = await class_service.list_classes(db)
        elif user_role == "mentor":
            # Filter classes where mentor_email equals current user's email
            result = await db.execute(
                select(class_models.ClassSession)
                .where(class_models.ClassSession.mentor_email == user_email)
            )
            classes = [class_schemas.ClassSession.model_validate(c, from_attributes=True) 
                       for c in result.scalars().all()]
        else:
            # Students get all classes for now (can filter by student course registrations if added later)
            classes = await class_service.list_classes(db)

        # Convert schemas to clean dicts for ADK output parsing
        return [c.model_dump() for c in classes]


async def get_class_details(class_id: str) -> dict[str, Any]:
    """Retrieves full details of a specific class session including Zoom link.

    Args:
        class_id: The unique UUID of the class session.
    """
    async with async_session_factory() as db:
        session = await class_service.get_class(db, class_id)
        return session.model_dump()


# ==========================================
# 2. COORDINATOR TOOLS (AVAILABLE TO MENTOR/ADMIN)
# ==========================================

async def get_all_classes() -> list[dict[str, Any]]:
    """Retrieves all scheduled class sessions across all courses and batches."""
    async with async_session_factory() as db:
        classes = await class_service.list_classes(db)
        return [c.model_dump() for c in classes]


async def get_student_list() -> list[dict[str, Any]]:
    """Retrieves all registered students in the system."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(auth_models.User).where(auth_models.User.role == "student")
        )
        users = result.scalars().all()
        return [{"id": u.id, "email": u.email, "is_verified": u.is_verified} for u in users]


# ==========================================
# 3. ADMINISTRATIVE WRITE TOOLS (ADMIN ONLY)
# ==========================================

async def schedule_class(
    topic_name: str,
    date: str,
    start_time: str,
    course_id: Optional[str] = None,
    course_name: Optional[str] = None,
    assignment_name: Optional[str] = None,
    duration_minutes: Optional[int] = 90,
    timezone: Optional[str] = None,
    mentor_email: Optional[str] = None,
) -> dict[str, Any]:
    """Schedules a new class session, automatically creates a Zoom meeting,
    and returns details.

    Args:
        topic_name: The title/topic of the class session (e.g. 'Advanced React Hooks').
        date: The date of the session in YYYY-MM-DD format (e.g. '2026-07-10').
        start_time: Start time in HH:MM format (24-hour clock, e.g. '19:30').
        course_id: The ID of an existing course. Provide either this or course_name.
        course_name: Name of course to create if course_id is not provided.
        assignment_name: Optional description or assignment details for the class.
        duration_minutes: Duration of class in minutes. Defaults to 90.
        timezone: Timezone for the class (e.g. 'Asia/Kolkata'). Defaults to default system timezone.
        mentor_email: Email of the mentor assigned to this class session.
    """
    payload = class_schemas.ClassCreate(
        course_id=course_id,
        course_name=course_name,
        topic_name=topic_name,
        assignment_name=assignment_name,
        date=date,
        start_time=start_time,
        duration_minutes=duration_minutes,
        timezone=timezone,
        mentor_email=mentor_email,
    )
    async with async_session_factory() as db:
        new_class = await class_service.create_class(db, payload)
        return new_class.model_dump()


async def edit_class(
    class_id: str,
    topic_name: Optional[str] = None,
    date: Optional[str] = None,
    start_time: Optional[str] = None,
    course_id: Optional[str] = None,
    course_name: Optional[str] = None,
    assignment_name: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    timezone: Optional[str] = None,
    mentor_email: Optional[str] = None,
) -> dict[str, Any]:
    """Modifies an existing class session and updates the Zoom meeting.

    Args:
        class_id: The unique UUID of the class session to edit.
        topic_name: Optional new topic title.
        date: Optional new date in YYYY-MM-DD format.
        start_time: Optional new start time in HH:MM format.
        course_id: Optional new course ID.
        course_name: Optional new course name.
        assignment_name: Optional new assignment details.
        duration_minutes: Optional new duration.
        timezone: Optional new timezone.
        mentor_email: Optional new mentor email.
    """
    payload = class_schemas.ClassUpdate(
        course_id=course_id,
        course_name=course_name,
        topic_name=topic_name,
        assignment_name=assignment_name,
        date=date,
        start_time=start_time,
        duration_minutes=duration_minutes,
        timezone=timezone,
        mentor_email=mentor_email,
    )
    async with async_session_factory() as db:
        updated = await class_service.update_class(db, class_id, payload)
        return updated.model_dump()


async def delete_class(class_id: str) -> dict[str, str]:
    """Cancels and deletes an existing class session, removing it from DB,
    Zoom, and Google Calendar.

    Args:
        class_id: The unique UUID of the class session to delete.
    """
    async with async_session_factory() as db:
        await class_service.delete_class(db, class_id)
        return {"status": "success", "message": f"Class {class_id} deleted successfully."}


async def sync_with_zoom() -> dict[str, Any]:
    """Runs a synchronization check with the Zoom API, validating all meetings
    and cleaning broken links.
    """
    async with async_session_factory() as db:
        res = await class_service.sync_with_zoom(db)
        return res


async def sync_with_calendar() -> dict[str, Any]:
    """Synchronizes all class events in the database with Google Calendar."""
    async with async_session_factory() as db:
        res = await class_service.sync_calendar(db)
        return res


async def get_stats() -> dict[str, int]:
    """Fetches high-level metrics (total students, mentors, total classes)."""
    async with async_session_factory() as db:
        students = await db.execute(
            select(func.count(auth_models.User.id)).where(auth_models.User.role == "student")
        )
        student_count = students.scalar() or 0

        mentors = await db.execute(
            select(func.count(auth_models.User.id)).where(auth_models.User.role == "mentor")
        )
        mentor_count = mentors.scalar() or 0

        total_classes = await db.execute(select(func.count(class_models.ClassSession.id)))
        class_count = total_classes.scalar() or 0

        return {
            "students": student_count,
            "mentors": mentor_count,
            "classes": class_count,
        }
