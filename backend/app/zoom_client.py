from __future__ import annotations

from __future__ import annotations

from base64 import b64encode
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

from .settings import settings


class ZoomClient:
    def __init__(self) -> None:
        self.base_url = "https://api.zoom.us/v2"
        self._access_token: Optional[str] = None
        self._access_token_expiry: Optional[datetime] = None

    def ensure_configured(self) -> None:
        has_oauth = bool(settings.zoom_account_id and settings.zoom_client_id and settings.zoom_client_secret)
        has_token = bool(settings.zoom_bearer_token)
        if not (has_oauth or has_token):
            raise RuntimeError(
                "Zoom credentials missing. Set ZOOM_ACCOUNT_ID/ZOOM_CLIENT_ID/ZOOM_CLIENT_SECRET "
                "or provide ZOOM_BEARER_TOKEN, plus ZOOM_USER_ID."
            )
        if not settings.zoom_user_id:
            raise RuntimeError("Zoom user missing. Set ZOOM_USER_ID.")

    async def get_access_token(self) -> str:
        if self._access_token and self._access_token_expiry:
            if datetime.utcnow() < self._access_token_expiry:
                return self._access_token

        if settings.zoom_bearer_token:
            return settings.zoom_bearer_token

        account_id = settings.zoom_account_id
        client_id = settings.zoom_client_id
        client_secret = settings.zoom_client_secret
        if not (account_id and client_id and client_secret):
            raise RuntimeError(
                "Zoom OAuth credentials missing. Set ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET."
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

        # Refresh a bit early to avoid edge timing.
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

    def build_start_payload(self, date_str: str, time_str: str, timezone: str) -> tuple[str, str]:
        timezone = self.normalize_timezone(timezone)
        try:
            naive = datetime.fromisoformat(f"{date_str}T{time_str}:00")
        except ValueError as exc:
            raise ValueError(f"Invalid date/time: {exc}") from exc
        _ = naive
        start_time = f"{date_str}T{time_str}:00"
        return start_time, timezone

    async def create_meeting(self, *, topic: str, agenda: str | None, date: str, start_time: str, timezone: str, duration: int = 90) -> dict:
        self.ensure_configured()
        start_time, timezone = self.build_start_payload(date, start_time, timezone)
        access_token = await self.get_access_token()
        payload = {
            "topic": topic,
            "agenda": agenda or "",
            "type": 2,
            "start_time": start_time,
            "duration": duration,
            "timezone": timezone,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self.base_url}/users/{settings.zoom_user_id}/meetings",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        resp.raise_for_status()
        return resp.json()

    async def update_meeting(self, *, meeting_id: str, topic: str, agenda: str | None, date: str, start_time: str, timezone: str, duration: int = 90) -> None:
        self.ensure_configured()
        start_time, timezone = self.build_start_payload(date, start_time, timezone)
        access_token = await self.get_access_token()
        payload = {
            "topic": topic,
            "agenda": agenda or "",
            "type": 2,
            "start_time": start_time,
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

    async def delete_meeting(self, *, meeting_id: str) -> None:
        self.ensure_configured()
        access_token = await self.get_access_token()
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.delete(
                f"{self.base_url}/meetings/{meeting_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        resp.raise_for_status()
