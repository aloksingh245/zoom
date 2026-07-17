import logging
import json
import os
import base64
from typing import Optional, List, Dict, Any
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from core.config import settings

logger = logging.getLogger(__name__)

class SheetsService:
    """Service to handle Google Sheets logging using Service Account."""
    
    def __init__(self):
        self._creds = None
        key_data = self._load_credentials()
        if key_data:
            self._creds = ServiceAccountCreds(
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets"
                ],
                **key_data
            )
        else:
            logger.warning("Google credentials not found. Sheets will run in STUB mode.")

    def _load_credentials(self) -> Optional[dict]:
        """Load Google service account credentials from env var (preferred) or file (fallback)."""
        # 1. Prefer base64-encoded env var
        if settings.google_credentials_b64:
            try:
                return json.loads(base64.b64decode(settings.google_credentials_b64))
            except Exception as e:
                logger.error(f"Failed to decode GOOGLE_CREDENTIALS_B64: {e}")

        # 2. Fall back to JSON file
        if settings.google_credentials_file and os.path.exists(settings.google_credentials_file):
            with open(settings.google_credentials_file) as f:
                return json.load(f)

        return None

    def is_stub(self) -> bool:
        """Check if Google Sheets integration should run in STUB mode."""
        if not self._creds or not settings.google_sheet_id:
            return True
        sheet_id = settings.google_sheet_id.lower()
        for placeholder in ["sheet_id_123", "placeholder", "your_sheet_id", "test_sheet"]:
            if placeholder in sheet_id:
                return True
        return False

    async def initialize_headers(self) -> None:
        """Write the header row to Sheet1!A1:M1 if not already present."""
        if self.is_stub():
            logger.info("[STUB] Skipping Sheet headers initialization.")
            return
        
        headers = [
            "Log Timestamp", "Class ID", "Course/Batch", "Topic", 
            "Mentor Email", "Date", "Start Time", "Duration (Mins)", 
            "Timezone", "Zoom Meeting ID", "Zoom Link", "Assignment/Agenda", "Status"
        ]
        
        try:
            async with Aiogoogle(service_account_creds=self._creds) as aiogoogle:
                sheets_v4 = await aiogoogle.discover("sheets", "v4")
                # First check if A1 is empty or has headers
                resp = await aiogoogle.as_service_account(
                    sheets_v4.spreadsheets.values.get(
                        spreadsheetId=settings.google_sheet_id,
                        range='Sheet1!A1:M1'
                    )
                )
                values = resp.get('values', [])
                if not values:
                    # Sheet is empty, write headers
                    await aiogoogle.as_service_account(
                        sheets_v4.spreadsheets.values.update(
                            spreadsheetId=settings.google_sheet_id,
                            range='Sheet1!A1',
                            valueInputOption='RAW',
                            json={'values': [headers]}
                        )
                    )
                    logger.info("Google Sheet headers initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Sheet headers: {e}")

    async def append_row(self, row_data: List[Any]) -> str:
        """Append a new log row to the Google Sheet."""
        if self.is_stub():
            logger.info(f"[STUB] Appending to sheet: {row_data}")
            return f"stub_row_{id(row_data)}"

        async with Aiogoogle(service_account_creds=self._creds) as aiogoogle:
            sheets_v4 = await aiogoogle.discover("sheets", "v4")
            
            # Request body for appending values
            body = {
                'values': [row_data]
            }
            
            # Using 'A1' notation as range, Google will append to the end of the sheet automatically
            resp = await aiogoogle.as_service_account(
                sheets_v4.spreadsheets.values.append(
                    spreadsheetId=settings.google_sheet_id,
                    range='Sheet1!A1',
                    valueInputOption='RAW',
                    json=body
                )
            )
            
            # The API doesn't return a "Row ID" like a DB, so we return the updated range for tracking
            updated_range = resp.get('updates', {}).get('updatedRange', 'unknown')
            logger.info(f"Google Sheet row appended to: {updated_range}")
            return updated_range

    async def update_row(self, row_id: str, row_data: List[Any]) -> None:
        """Update an existing log row (row_id here is the cell range)."""
        if self.is_stub() or not row_id or row_id.startswith("stub_row_"):
            logger.info(f"[STUB] Updating sheet row {row_id}")
            return

        async with Aiogoogle(service_account_creds=self._creds) as aiogoogle:
            sheets_v4 = await aiogoogle.discover("sheets", "v4")
            body = {'values': [row_data]}
            
            await aiogoogle.as_service_account(
                sheets_v4.spreadsheets.values.update(
                    spreadsheetId=settings.google_sheet_id,
                    range=row_id,
                    valueInputOption='RAW',
                    json=body
                )
            )

sheets_service = SheetsService()
