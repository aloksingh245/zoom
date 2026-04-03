import logging
import os
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def check_event_time(event_id):
    if not os.path.exists("token.json"):
        print("token.json not found")
        return

    creds = Credentials.from_authorized_user_file("token.json")
    service = build('calendar', 'v3', credentials=creds)
    
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    start = event.get('start', {})
    end = event.get('end', {})
    
    print(f"Event: {event.get('summary')}")
    print(f"Start: {start.get('dateTime')} (TZ: {start.get('timeZone')})")
    print(f"End:   {end.get('dateTime')} (TZ: {end.get('timeZone')})")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        check_event_time(sys.argv[1])
    else:
        print("Usage: python check_gcal_time.py <event_id>")
