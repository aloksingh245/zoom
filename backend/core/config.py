from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    app_env: str = "dev"
    app_name: str = "Class Scheduler API"
    app_version: str = "1.0.0"

    # Zoom Configuration
    zoom_bearer_token: str = ""
    zoom_user_id: str = ""
    zoom_account_id: str = ""
    zoom_client_id: str = ""
    zoom_client_secret: str = ""

    # Google Configuration
    google_calendar_id: str = "primary"
    google_sheet_id: str = ""
    google_credentials_b64: str = ""
    google_credentials_file: str = "credentials.json"

    # CRM Configuration
    crm_api_url: str = "https://capi.partnercrm.org/classes"
    crm_bearer_token: str = ""

    # JWT Authentication Configuration
    jwt_secret: str = "super-secret-key-change-in-production-zoom-scheduler"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # SMTP Configuration for Email Verification
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@zoom-scheduler.com"
    app_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    # Application Defaults
    timezone_default: str = "Asia/Kolkata"
    class_duration_minutes: int = 90
    gemini_api_key: str = ""

    # CORS Configuration
    cors_allow_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def cors_origins(self) -> List[str]:
        origins = [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]
        return origins if origins else ["*"]


settings = Settings()
