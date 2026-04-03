from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.courses import schemas
from modules.courses.service import course_service

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("", response_model=List[schemas.Course])
async def list_courses(db: AsyncSession = Depends(get_db)):
    return await course_service.list_courses(db)

@router.post("", response_model=schemas.Course)
async def create_course(payload: schemas.CourseCreate, db: AsyncSession = Depends(get_db)):
    return await course_service.create_course(db, payload)
