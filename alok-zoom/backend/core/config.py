from pydantic import Field
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
    google_credentials_file: str = "credentials.json"

    # AI Configuration
    gemini_api_key: str = Field("", alias="GEMINI_API_KEY")
    groq_api_key: str = Field("", alias="GROQ_API_KEY")

    # Application Defaults
    timezone_default: str = "Asia/Kolkata"
    class_duration_minutes: int = 90

    # CORS Configuration
    cors_allow_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def cors_origins(self) -> List[str]:
        origins = [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]
        return origins if origins else ["*"]


settings = Settings()
