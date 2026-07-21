from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from core.base import Base

class TenantSettings(Base):
    __tablename__ = "tenant_settings"

    tenant_id = Column(String, primary_key=True, index=True)
    zoom_account_id = Column(String, nullable=True)
    zoom_client_id = Column(String, nullable=True)
    zoom_client_secret = Column(String, nullable=True)
    zoom_user_id = Column(String, nullable=True)
    google_calendar_id = Column(String, nullable=True)
    google_sheet_id = Column(String, nullable=True)
    smtp_host = Column(String, nullable=True)
    smtp_port = Column(Integer, default=587, nullable=True)
    smtp_username = Column(String, nullable=True)
    smtp_password = Column(String, nullable=True)
    smtp_from = Column(String, nullable=True)
    app_url = Column(String, nullable=True)
    timezone_default = Column(String, default="Asia/Kolkata", nullable=True)
    gemini_api_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
