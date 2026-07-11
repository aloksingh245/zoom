from pydantic import BaseModel
from typing import Optional

class SettingsRead(BaseModel):
    zoom_account_id: str
    zoom_client_id: str
    zoom_client_secret_set: bool
    zoom_user_id: str
    google_calendar_id: str
    google_sheet_id: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password_set: bool
    smtp_from: str
    app_url: str
    timezone_default: str
    gemini_api_key_set: bool

class SettingsUpdate(BaseModel):
    zoom_account_id: Optional[str] = None
    zoom_client_id: Optional[str] = None
    zoom_client_secret: Optional[str] = None  # If "••••••••", ignore change
    zoom_user_id: Optional[str] = None
    google_calendar_id: Optional[str] = None
    google_sheet_id: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None       # If "••••••••", ignore change
    smtp_from: Optional[str] = None
    app_url: Optional[str] = None
    timezone_default: Optional[str] = None
    gemini_api_key: Optional[str] = None       # If "••••••••", ignore change
