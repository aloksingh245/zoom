from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.classes import schemas
from modules.classes.service import class_service

router = APIRouter(prefix="/api/classes", tags=["classes"])

@router.get("", response_model=List[schemas.ClassSession])
async def list_classes(db: AsyncSession = Depends(get_db)):
    return await class_service.list_classes(db)

@router.get("/{class_id}", response_model=schemas.ClassSession)
async def get_class(class_id: str, db: AsyncSession = Depends(get_db)):
    return await class_service.get_class(db, class_id)

@router.post("", response_model=schemas.ClassSession)
async def create_class(payload: schemas.ClassCreate, db: AsyncSession = Depends(get_db)):
    return await class_service.create_class(db, payload)

@router.put("/{class_id}", response_model=schemas.ClassSession)
async def update_class(class_id: str, payload: schemas.ClassUpdate, db: AsyncSession = Depends(get_db)):
    return await class_service.update_class(db, class_id, payload)

@router.post("/sync")
async def sync_classes(db: AsyncSession = Depends(get_db)):
    return await class_service.sync_with_zoom(db)

@router.post("/sync/calendar")
async def sync_with_calendar(db: AsyncSession = Depends(get_db)):
    return await class_service.sync_with_calendar(db)

@router.delete("/{class_id}")
async def delete_class(class_id: str, db: AsyncSession = Depends(get_db)):
    await class_service.delete_class(db, class_id)
    return {"deleted": True}
