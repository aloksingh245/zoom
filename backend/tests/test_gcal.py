import asyncio
import os
import sys
import logging

# Ensure backend folder is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from integrations.google_calendar.client import calendar_service

logging.basicConfig(level=logging.INFO)

async def test():
    print("\n--- STARTING GCAL TEST ---")
    try:
        event_id = await calendar_service.create_event(
            mentor_email="test_mentor@example.com",
            topic="Debug Event Validation",
            date="2026-03-20",
            start_time="10:00",
            zoom_link="https://zoom.us/j/123456789",
            timezone="Asia/Kolkata",
            duration=90
        )
        print(f"\n✅ SUCCESS! Event ID: {event_id}")
    except Exception as e:
        print(f"\n❌ FAILED! Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
