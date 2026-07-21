from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.courses import schemas
from modules.courses.service import course_service
from modules.auth.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("", response_model=List[schemas.Course])
async def list_courses(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    return await course_service.list_courses(db, tenant_id)

@router.post("", response_model=schemas.Course)
async def create_course(payload: schemas.CourseCreate, db: AsyncSession = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    return await course_service.create_course(db, payload, current_user.tenant_id)
