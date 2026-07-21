from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from modules.auth.dependencies import get_current_user, RoleChecker
from modules.auth.models import User
from modules.settings.models import TenantSettings
from modules.settings import schemas

router = APIRouter(prefix="/settings", tags=["settings"])

# Restrict settings to admins only
admin_guard = RoleChecker(["admin"])

@router.get("", response_model=schemas.SettingsRead)
async def get_settings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    tenant_id = current_user.tenant_id or "super_admin"
    result = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == tenant_id))
    record = result.scalar_one_or_none()
    
    if not record:
        return schemas.SettingsRead(
            zoom_account_id="",
            zoom_client_id="",
            zoom_client_secret_set=False,
            zoom_user_id="",
            google_calendar_id="",
            google_sheet_id="",
            smtp_host="",
            smtp_port=587,
            smtp_username="",
            smtp_password_set=False,
            smtp_from="",
            app_url="",
            timezone_default="Asia/Kolkata",
            gemini_api_key_set=False,
        )
        
    return schemas.SettingsRead(
        zoom_account_id=record.zoom_account_id or "",
        zoom_client_id=record.zoom_client_id or "",
        zoom_client_secret_set=bool(record.zoom_client_secret),
        zoom_user_id=record.zoom_user_id or "",
        google_calendar_id=record.google_calendar_id or "",
        google_sheet_id=record.google_sheet_id or "",
        smtp_host=record.smtp_host or "",
        smtp_port=record.smtp_port or 587,
        smtp_username=record.smtp_username or "",
        smtp_password_set=bool(record.smtp_password),
        smtp_from=record.smtp_from or "",
        app_url=record.app_url or "",
        timezone_default=record.timezone_default or "Asia/Kolkata",
        gemini_api_key_set=bool(record.gemini_api_key),
    )

@router.post("", status_code=status.HTTP_200_OK)
async def update_settings(
    payload: schemas.SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_guard)
):
    tenant_id = current_user.tenant_id
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User does not belong to a tenant context.")

    result = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == tenant_id))
    record = result.scalar_one_or_none()
    
    if not record:
        record = TenantSettings(tenant_id=tenant_id)
        db.add(record)

    # List of properties in model
    fields = [
        "zoom_account_id", "zoom_client_id", "zoom_client_secret", "zoom_user_id",
        "google_calendar_id", "google_sheet_id", "smtp_host", "smtp_port",
        "smtp_username", "smtp_password", "smtp_from", "app_url",
        "timezone_default", "gemini_api_key"
    ]

    for field in fields:
        val = getattr(payload, field, None)
        if val is not None:
            # Skip updating secret placeholders
            if field in ["zoom_client_secret", "smtp_password", "gemini_api_key"] and val == "••••••••":
                continue
            setattr(record, field, val)

    try:
        await db.commit()
        return {"status": "success", "message": "Settings updated successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")
