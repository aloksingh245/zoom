import logging
import httpx
from typing import Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)

class CRMService:
    """Service to handle synchronization with the external Partner CRM."""
    
    def __init__(self):
        self.api_url = settings.crm_api_url
        self.bearer_token = settings.crm_bearer_token

    async def sync_class(self, payload: Dict[str, Any]) -> Optional[str]:
        """Send class data to the CRM API."""
        if not self.bearer_token or self.bearer_token == "YOUR_TOKEN":
            logger.info(f"[STUB] Syncing to CRM: {payload}")
            return "stub_crm_id"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.bearer_token}",
                        "Content-Type": "application/json",
                    },
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                crm_id = data.get("Id")
                logger.info(f"Class synced to CRM successfully. CRM ID: {crm_id}")
                return crm_id
        except Exception as e:
            logger.error(f"Failed to sync class to CRM: {e}")
            return None

crm_service = CRMService()
