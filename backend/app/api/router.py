from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import Course, CourseCreate, ClassSession, ClassCreate, ClassUpdate
from ..services.scheduler import scheduler_service
from ..db.repository import repository
from ..db.database import get_db

router = APIRouter(prefix="/api")

# Course Endpoints
@router.get("/courses", response_model=List[Course])
async def list_courses(db: AsyncSession = Depends(get_db)):
    return await repository.list_courses(db)

@router.post("/courses", response_model=Course)
async def create_course(payload: CourseCreate, db: AsyncSession = Depends(get_db)):
    return await repository.create_course(db, payload)

# Class Endpoints
@router.get("/classes", response_model=List[ClassSession])
async def list_classes(db: AsyncSession = Depends(get_db)):
    return await scheduler_service.list_classes(db)

@router.get("/classes/{class_id}", response_model=ClassSession)
async def get_class(class_id: str, db: AsyncSession = Depends(get_db)):
    return await scheduler_service.get_class(db, class_id)

@router.post("/classes", response_model=ClassSession)
async def create_class(payload: ClassCreate, db: AsyncSession = Depends(get_db)):
    return await scheduler_service.create_class(db, payload)

@router.put("/classes/{class_id}", response_model=ClassSession)
async def update_class(class_id: str, payload: ClassUpdate, db: AsyncSession = Depends(get_db)):
    return await scheduler_service.update_class(db, class_id, payload)

@router.delete("/classes/{class_id}")
async def delete_class(class_id: str, db: AsyncSession = Depends(get_db)):
    await scheduler_service.delete_class(db, class_id)
    return {"deleted": True}
