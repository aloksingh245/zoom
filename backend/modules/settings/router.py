from fastapi import APIRouter, Depends, HTTPException, status
from modules.auth.dependencies import RoleChecker
from modules.auth.models import User
from core.config import settings
from modules.settings import schemas
import os

router = APIRouter(prefix="/settings", tags=["settings"])

# Restrict settings to admins only
admin_guard = Depends(RoleChecker(["admin"]))

@router.get("", response_model=schemas.SettingsRead)
async def get_settings(current_user: User = admin_guard):
    return schemas.SettingsRead(
        zoom_account_id=settings.zoom_account_id,
        zoom_client_id=settings.zoom_client_id,
        zoom_client_secret_set=bool(settings.zoom_client_secret),
        zoom_user_id=settings.zoom_user_id,
        google_calendar_id=settings.google_calendar_id,
        google_sheet_id=settings.google_sheet_id,
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password_set=bool(settings.smtp_password),
        smtp_from=settings.smtp_from,
        app_url=settings.app_url,
        timezone_default=settings.timezone_default,
        gemini_api_key_set=bool(settings.gemini_api_key),
    )

@router.post("", status_code=status.HTTP_200_OK)
async def update_settings(payload: schemas.SettingsUpdate, current_user: User = admin_guard):
    updates = {}
    
    # 1. Map schema keys to environment variable keys
    key_mapping = {
        "zoom_account_id": "ZOOM_ACCOUNT_ID",
        "zoom_client_id": "ZOOM_CLIENT_ID",
        "zoom_client_secret": "ZOOM_CLIENT_SECRET",
        "zoom_user_id": "ZOOM_USER_ID",
        "google_calendar_id": "GOOGLE_CALENDAR_ID",
        "google_sheet_id": "GOOGLE_SHEET_ID",
        "smtp_host": "SMTP_HOST",
        "smtp_port": "SMTP_PORT",
        "smtp_username": "SMTP_USERNAME",
        "smtp_password": "SMTP_PASSWORD",
        "smtp_from": "SMTP_FROM",
        "app_url": "APP_URL",
        "timezone_default": "TIMEZONE_DEFAULT",
        "gemini_api_key": "GEMINI_API_KEY",
    }

    # 2. Process payload values
    for schema_key, env_key in key_mapping.items():
        val = getattr(payload, schema_key)
        if val is not None:
            # Check for placeholder masks on secret fields
            if schema_key in ["zoom_client_secret", "smtp_password", "gemini_api_key"] and val == "••••••••":
                continue
            updates[env_key] = str(val)

    if not updates:
        return {"status": "no changes applied"}

    # 3. Locate and update the .env file in the backend directory
    # Try directory containing current file, then parent directory, then fallback to current cwd
    env_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(env_dir, ".env")
    if not os.path.exists(env_path):
        env_path = ".env"

    # Read existing lines
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()

    # Parse and update key-value pairs
    keys_found = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue
            
        key = stripped.split("=")[0].strip()
        if key in updates:
            val = updates[key]
            new_lines.append(f"{key}={val}\n")
            keys_found.add(key)
        else:
            new_lines.append(line)

    # Append any new variables that weren't present in the file
    for key, val in updates.items():
        if key not in keys_found:
            new_lines.append(f"{key}={val}\n")

    # Overwrite .env file
    with open(env_path, "w") as f:
        f.writelines(new_lines)

    # 4. Trigger auto-reload by touching main.py
    main_py_path = os.path.join(env_dir, "main.py")
    if os.path.exists(main_py_path):
        os.utime(main_py_path, None)

    return {"status": "success", "message": "Settings updated. Server is restarting to load new configurations."}
