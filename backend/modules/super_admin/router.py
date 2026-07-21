from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from core.database import get_db
from modules.auth.dependencies import RoleChecker
from modules.auth.models import User
from modules.settings.models import TenantSettings
from modules.classes.models import ClassSession
from modules.courses.models import Course
from typing import List, Dict, Any

router = APIRouter(prefix="/api/super-admin", tags=["super-admin"])

# Guard all routes to super_admin only
super_admin_checker = RoleChecker(["super_admin"])

@router.get("/tenants", response_model=List[Dict[str, Any]])
async def list_tenants(db: AsyncSession = Depends(get_db), current_user = Depends(super_admin_checker)):
    # 1. Fetch all tenant admins
    result = await db.execute(select(User).where(User.role == "admin"))
    admins = result.scalars().all()
    
    tenants_list = []
    for admin in admins:
        # Fetch their settings
        settings_res = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == admin.id))
        settings = settings_res.scalar_one_or_none()
        
        # Count classes
        class_count_res = await db.execute(
            select(func.count(ClassSession.id)).where(ClassSession.tenant_id == admin.id)
        )
        class_count = class_count_res.scalar() or 0
        
        # Count courses
        course_count_res = await db.execute(
            select(func.count(Course.id)).where(Course.tenant_id == admin.id)
        )
        course_count = course_count_res.scalar() or 0

        # Construct status structure
        tenants_list.append({
            "id": admin.id,
            "email": admin.email,
            "is_active": admin.is_active,
            "is_verified": admin.is_verified,
            "created_at": admin.created_at,
            "courses_count": course_count,
            "classes_count": class_count,
            "settings": {
                "zoom_configured": bool(settings and settings.zoom_client_id and settings.zoom_client_secret),
                "zoom_user_id": settings.zoom_user_id if settings else "",
                "smtp_configured": bool(settings and settings.smtp_username and settings.smtp_password),
                "smtp_from": settings.smtp_from if settings else "",
                "smtp_host": settings.smtp_host if settings else "",
                "google_sheet_id": settings.google_sheet_id if settings else "",
                "google_calendar_id": settings.google_calendar_id if settings else "",
                "gemini_configured": bool(settings and settings.gemini_api_key)
            }
        })
        
    return tenants_list

@router.post("/tenants/{tenant_id}/toggle-active")
async def toggle_tenant_active(tenant_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(super_admin_checker)):
    result = await db.execute(select(User).where(User.id == tenant_id, User.role == "admin"))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Tenant admin not found.")
        
    admin.is_active = not admin.is_active
    await db.commit()
    
    status_str = "activated" if admin.is_active else "deactivated"
    return {"message": f"Tenant account successfully {status_str}.", "is_active": admin.is_active}

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(super_admin_checker)):
    result = await db.execute(select(User).where(User.id == tenant_id, User.role == "admin"))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Tenant admin not found.")

    try:
        # Delete associated items cascadingly
        # 1. Classes
        await db.execute(delete(ClassSession).where(ClassSession.tenant_id == tenant_id))
        # 2. Courses
        await db.execute(delete(Course).where(Course.tenant_id == tenant_id))
        # 3. Settings
        await db.execute(delete(TenantSettings).where(TenantSettings.tenant_id == tenant_id))
        # 4. Users (mentors / students) belonging to this tenant
        await db.execute(delete(User).where(User.tenant_id == tenant_id, User.id != tenant_id))
        # 5. The admin user itself
        await db.delete(admin)
        
        await db.commit()
        return {"message": "Tenant and all associated data permanently deleted."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete tenant: {str(e)}")
