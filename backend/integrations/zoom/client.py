from __future__ import annotations

import logging
from base64 import b64encode
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class ZoomService:
    """Service to handle communication with Zoom REST API v2."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ZoomService, cls).__new__(cls)
            cls._instance.base_url = "https://api.zoom.us/v2"
            cls._instance._access_token = None
            cls._instance._access_token_expiry = None
        return cls._instance

    def get_credentials(self, tenant_settings: Any = None) -> Dict[str, str]:
        if tenant_settings:
            return {
                "account_id": tenant_settings.zoom_account_id or "",
                "client_id": tenant_settings.zoom_client_id or "",
                "client_secret": tenant_settings.zoom_client_secret or "",
                "user_id": tenant_settings.zoom_user_id or ""
            }
        return {
            "account_id": settings.zoom_account_id or "",
            "client_id": settings.zoom_client_id or "",
            "client_secret": settings.zoom_client_secret or "",
            "user_id": settings.zoom_user_id or ""
        }

    def is_stub(self, tenant_settings: Any = None) -> bool:
        creds = self.get_credentials(tenant_settings)
        account_id = creds["account_id"]
        client_id = creds["client_id"]
        if not account_id or not client_id or not creds["client_secret"]:
            return True
        for placeholder in ["test", "your_", "placeholder", "client_id", "account_id"]:
            if placeholder in account_id.lower() or placeholder in client_id.lower():
                return True
        return False

    def ensure_configured(self, tenant_settings: Any = None) -> None:
        if self.is_stub(tenant_settings):
            return
        creds = self.get_credentials(tenant_settings)
        has_oauth = bool(creds["account_id"] and creds["client_id"] and creds["client_secret"])
        has_token = bool(settings.zoom_bearer_token)
        if not (has_oauth or has_token):
            raise RuntimeError(
                "Zoom credentials missing. Please configure Zoom Account ID, Client ID and Client Secret in Settings."
            )
        if not creds["user_id"]:
            raise RuntimeError("Zoom host user missing. Please configure Zoom Host User Email in Settings.")

    async def get_access_token(self, tenant_settings: Any = None) -> str:
        if self.is_stub(tenant_settings):
            return "stub_zoom_access_token"

        if self._access_token and self._access_token_expiry:
            if datetime.utcnow() < self._access_token_expiry:
                return self._access_token

        if settings.zoom_bearer_token:
            return settings.zoom_bearer_token

        creds = self.get_credentials(tenant_settings)
        account_id = creds["account_id"]
        client_id = creds["client_id"]
        client_secret = creds["client_secret"]
        if not (account_id and client_id and client_secret):
            raise RuntimeError(
                "Zoom OAuth credentials missing."
            )

        basic = b64encode(f"{client_id}:{client_secret}".encode()).decode()
        token_url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(token_url, headers={"Authorization": f"Basic {basic}"})
        resp.raise_for_status()
        data = resp.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 0)
        
        if not access_token:
            raise RuntimeError("Zoom OAuth token response missing access_token.")

        self._access_token = access_token
        self._access_token_expiry = datetime.utcnow() + timedelta(seconds=max(0, int(expires_in) - 60))
        return access_token

    def normalize_timezone(self, timezone: str) -> str:
        if timezone == "Asia/Calcutta":
            timezone = "Asia/Kolkata"
        try:
            ZoneInfo(timezone)
        except ZoneInfoNotFoundError:
            timezone = settings.timezone_default
        return timezone

    def _build_start_time(self, date_str: str, time_str: str) -> str:
        return f"{date_str}T{time_str}:00"

    async def create_meeting(
        self, 
        *, 
        topic: str, 
        agenda: str | None, 
        date: str, 
        start_time: str, 
        timezone: str, 
        duration: int = 90,
        tenant_settings: Any = None
    ) -> Dict[str, Any]:
        self.ensure_configured(tenant_settings)
        timezone = self.normalize_timezone(timezone)
        creds = self.get_credentials(tenant_settings)

        if self.is_stub(tenant_settings):
            import random
            stub_id = str(random.randint(1000000000, 9999999999))
            logger.warning(f"[STUB] Creating stub Zoom meeting {stub_id} for topic '{topic}'")
            return {
                "id": stub_id,
                "join_url": f"https://zoom.us/j/{stub_id}"
            }

        access_token = await self.get_access_token(tenant_settings)
        
        payload = {
            "topic": topic,
            "agenda": agenda or "",
            "type": 2,
            "start_time": self._build_start_time(date, start_time),
            "duration": duration,
            "timezone": timezone,
        }
        
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self.base_url}/users/{creds['user_id']}/meetings",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        resp.raise_for_status()
        return resp.json()

    async def update_meeting(
        self, 
        *, 
        meeting_id: str, 
        topic: str, 
        agenda: str | None, 
        date: str, 
        start_time: str, 
        timezone: str, 
        duration: int = 90,
        tenant_settings: Any = None
    ) -> None:
        self.ensure_configured(tenant_settings)
        timezone = self.normalize_timezone(timezone)

        if self.is_stub(tenant_settings):
            logger.warning(f"[STUB] Updating stub Zoom meeting {meeting_id}")
            return

        access_token = await self.get_access_token(tenant_settings)
        
        payload = {
            "topic": topic,
            "agenda": agenda or "",
            "type": 2,
            "start_time": self._build_start_time(date, start_time),
            "duration": duration,
            "timezone": timezone,
        }
        
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.patch(
                f"{self.base_url}/meetings/{meeting_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        resp.raise_for_status()

    async def delete_meeting(self, *, meeting_id: str, tenant_settings: Any = None) -> None:
        self.ensure_configured(tenant_settings)

        if self.is_stub(tenant_settings):
            logger.warning(f"[STUB] Deleting stub Zoom meeting {meeting_id}")
            return

        access_token = await self.get_access_token(tenant_settings)
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.delete(
                f"{self.base_url}/meetings/{meeting_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        resp.raise_for_status()

    async def list_meetings(self, tenant_settings: Any = None) -> Dict[str, Any]:
        """List all meetings for the configured user."""
        self.ensure_configured(tenant_settings)
        creds = self.get_credentials(tenant_settings)

        if self.is_stub(tenant_settings):
            logger.warning("[STUB] Listing Zoom meetings - returning empty list")
            return {"meetings": []}

        access_token = await self.get_access_token(tenant_settings)
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{self.base_url}/users/{creds['user_id']}/meetings",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"type": "upcoming", "page_size": 300}
            )
        resp.raise_for_status()
        return resp.json()

    async def get_meeting(self, meeting_id: str, tenant_settings: Any = None) -> Dict[str, Any]:
        """Fetch details for a specific meeting."""
        self.ensure_configured(tenant_settings)

        if self.is_stub(tenant_settings):
            logger.warning(f"[STUB] Getting stub Zoom meeting {meeting_id}")
            return {
                "id": meeting_id,
                "join_url": f"https://zoom.us/j/{meeting_id}"
            }

        access_token = await self.get_access_token(tenant_settings)
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{self.base_url}/meetings/{meeting_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        resp.raise_for_status()
        return resp.json()


zoom_service = ZoomService()
