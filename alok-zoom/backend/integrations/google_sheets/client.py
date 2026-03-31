import logging
import json
import os
from typing import Optional, List, Dict, Any
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from core.config import settings

logger = logging.getLogger(__name__)

class SheetsService:
    """Service to handle Google Sheets logging using Service Account."""
    
    def __init__(self):
        self._creds = None
        if os.path.exists(settings.google_credentials_file):
            with open(settings.google_credentials_file) as f:
                key_data = json.load(f)
                self._creds = ServiceAccountCreds(
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets"
                    ],
                    **key_data
                )
        else:
            logger.warning(f"Google credentials file not found at {settings.google_credentials_file}. Sheets will run in STUB mode.")

    async def append_row(self, row_data: List[Any]) -> str:
        """Append a new log row to the Google Sheet."""
        if not self._creds or not settings.google_sheet_id:
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
        if not self._creds or not settings.google_sheet_id:
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
