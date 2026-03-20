import logging
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from core.config import settings
from core.utils import async_retry

from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

class CalendarService:
    """Service to handle Google Calendar operations using OAuth User Credentials or Service Account."""
    
    def _get_credentials(self):
        # 1. Try OAuth User Credentials (token.json)
        if os.path.exists("token.json"):
            try:
                creds = Credentials.from_authorized_user_file("token.json")
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    # Save refreshed token
                    with open("token.json", "w") as token:
                        token.write(creds.to_json())
                return creds
            except Exception as e:
                logger.error(f"Error loading/refreshing token.json: {e}")
        
        return None

    def _execute_sync(self, func, *args, **kwargs):
        """Helper to run Google's synchronous API client in a thread pool."""
        return asyncio.get_event_loop().run_in_executor(None, lambda: func(*args, **kwargs))

    @async_retry(max_retries=3, initial_delay=1.0)
    async def create_event(
        self, 
        *, 
        mentor_email: str, 
        topic: str, 
        date: str, 
        start_time: str, 
        zoom_link: str,
        timezone: str,
        duration: int = 90
    ) -> str:
        creds = self._get_credentials()
        if not creds:
            logger.warning("[STUB] Missing token.json. Skipping Google Calendar event creation.")
            return f"stub_gcal_{int(datetime.utcnow().timestamp())}"

        # Combine date and time, and attach the intended timezone to prevent naive object shifting
        tz = ZoneInfo(timezone)
        start_dt_naive = datetime.fromisoformat(f"{date}T{start_time}:00")
        start_dt_aware = start_dt_naive.replace(tzinfo=tz)
        
        # Convert explicitly to UTC to prevent Google API timezone shifting bugs
        start_dt_utc = start_dt_aware.astimezone(ZoneInfo("UTC"))
        start_dt = start_dt_utc.isoformat().replace("+00:00", "Z")
        
        end_dt_aware = start_dt_aware + timedelta(minutes=duration)
        end_dt_utc = end_dt_aware.astimezone(ZoneInfo("UTC"))
        end_dt = end_dt_utc.isoformat().replace("+00:00", "Z")
        
        # Get organizer email to avoid inviting self
        service = build('calendar', 'v3', credentials=creds)
        def get_calendar():
            return service.calendars().get(calendarId='primary').execute()
        
        cal_meta = await self._execute_sync(get_calendar)
        organizer_email = cal_meta.get('id')
        
        attendees = []
        if mentor_email and mentor_email.lower() != organizer_email.lower():
            attendees.append({'email': mentor_email})

        event = {
            'summary': topic,
            'description': f'Zoom Meeting: {zoom_link}\nScheduled via Zoom Scheduler.',
            'start': {
                'dateTime': start_dt,
            },
            'end': {
                'dateTime': end_dt,
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        try:
            def make_request():
                return service.events().insert(
                    calendarId='primary',
                    sendUpdates='all',
                    body=event
                ).execute()

            resp = await self._execute_sync(make_request)
            logger.info(f"Google Calendar event created successfully! Event ID: {resp.get('id')}")
            return resp.get('id')
            
        except Exception as e:
            logger.error(f"CRITICAL GOOGLE CALENDAR ERROR: {e}")
            raise e

    @async_retry(max_retries=3, initial_delay=1.0)
    async def update_event(
        self, 
        *, 
        event_id: str,
        mentor_email: Optional[str] = None, 
        topic: Optional[str] = None, 
        date: Optional[str] = None, 
        start_time: Optional[str] = None, 
        zoom_link: Optional[str] = None,
        timezone: Optional[str] = None,
        duration: int = 90
    ) -> None:
        creds = self._get_credentials()
        if not creds:
            logger.warning(f"[STUB] Updating GCal event {event_id}")
            return

        try:
            service = build('calendar', 'v3', credentials=creds)
            
            def make_request():
                event = service.events().get(calendarId='primary', eventId=event_id).execute()
                
                if topic: event['summary'] = topic
                if zoom_link: event['description'] = f'Zoom Meeting: {zoom_link}\nUpdated via Zoom Scheduler.'
                if date and start_time:
                    tz = ZoneInfo(timezone or event['start'].get('timeZone', 'UTC'))
                    start_dt_naive = datetime.fromisoformat(f"{date}T{start_time}:00")
                    start_dt_aware = start_dt_naive.replace(tzinfo=tz)
                    
                    start_dt_utc = start_dt_aware.astimezone(ZoneInfo("UTC"))
                    
                    end_dt_aware = start_dt_aware + timedelta(minutes=duration)
                    end_dt_utc = end_dt_aware.astimezone(ZoneInfo("UTC"))
                    
                    event['start'] = {'dateTime': start_dt_utc.isoformat().replace("+00:00", "Z")}
                    event['end'] = {'dateTime': end_dt_utc.isoformat().replace("+00:00", "Z")}
                
                if mentor_email:
                    # Get organizer email to avoid inviting self
                    def get_calendar():
                        return service.calendars().get(calendarId='primary').execute()
                    cal_meta = await self._execute_sync(get_calendar)
                    organizer_email = cal_meta.get('id')

                    if mentor_email.lower() != organizer_email.lower():
                        event['attendees'] = [{'email': mentor_email}]
                    else:
                        event['attendees'] = []

                return service.events().update(
                    calendarId='primary',
                    eventId=event_id,
                    sendUpdates='all',
                    body=event
                ).execute()

            await self._execute_sync(make_request)
            
        except Exception as e:
            logger.error(f"Error updating GCal event: {e}")
            raise e

    @async_retry(max_retries=3, initial_delay=1.0)
    async def get_event(self, *, event_id: str) -> Optional[dict]:
        creds = self._get_credentials()
        if not creds:
            logger.warning(f"[STUB] Getting GCal event {event_id}")
            return None

        try:
            service = build('calendar', 'v3', credentials=creds)
            
            def make_request():
                return service.events().get(calendarId='primary', eventId=event_id).execute()

            return await self._execute_sync(make_request)
            
        except Exception as e:
            # If 404, it might be deleted
            if hasattr(e, 'resp') and e.resp.status == 404:
                return None
            logger.error(f"Error getting GCal event {event_id}: {e}")
            raise e

    @async_retry(max_retries=3, initial_delay=1.0)
    async def delete_event(self, *, event_id: str) -> None:
        creds = self._get_credentials()
        if not creds:
            logger.warning(f"[STUB] Deleting GCal event {event_id}")
            return

        try:
            service = build('calendar', 'v3', credentials=creds)
            
            def make_request():
                return service.events().delete(
                    calendarId='primary', 
                    eventId=event_id,
                    sendUpdates='all'
                ).execute()

            await self._execute_sync(make_request)
            
        except Exception as e:
            logger.error(f"Error deleting GCal event {event_id}: {e}")

calendar_service = CalendarService()
