from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.courses import schemas, models

class CourseService:
    async def create_course(self, db: AsyncSession, payload: schemas.CourseCreate, tenant_id: str) -> schemas.Course:
        try:
            course_id = str(uuid4())
            db_course = models.Course(
                id=course_id, 
                name=payload.name, 
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            db.add(db_course)
            await db.commit()
            await db.refresh(db_course)
            return schemas.Course.model_validate(db_course, from_attributes=True)
        except Exception:
            await db.rollback()
            raise

    async def get_course(self, db: AsyncSession, course_id: str, tenant_id: Optional[str] = None) -> Optional[schemas.Course]:
        query = select(models.Course).where(models.Course.id == course_id)
        if tenant_id:
            query = query.where(models.Course.tenant_id == tenant_id)
        result = await db.execute(query)
        db_course = result.scalar_one_or_none()
        return schemas.Course.model_validate(db_course, from_attributes=True) if db_course else None

    async def find_course_by_name(self, db: AsyncSession, name: str, tenant_id: Optional[str] = None) -> Optional[schemas.Course]:
        query = select(models.Course).where(models.Course.name == name)
        if tenant_id:
            query = query.where(models.Course.tenant_id == tenant_id)
        result = await db.execute(query)
        db_course = result.scalar_one_or_none()
        return schemas.Course.model_validate(db_course, from_attributes=True) if db_course else None

    async def list_courses(self, db: AsyncSession, tenant_id: Optional[str] = None) -> List[schemas.Course]:
        query = select(models.Course)
        if tenant_id:
            query = query.where(models.Course.tenant_id == tenant_id)
        result = await db.execute(query)
        return [schemas.Course.model_validate(c, from_attributes=True) for c in result.scalars().all()]

course_service = CourseService()
