from datetime import datetime
from zoneinfo import ZoneInfo

def test_timezone_conversion():
    # Simulate the logic in calendar client
    timezone = "Asia/Kolkata"
    date = "2026-03-20"
    start_time = "10:00"
    
    tz = ZoneInfo(timezone)
    dt_naive = datetime.fromisoformat(f"{date}T{start_time}:00")
    dt_aware = dt_naive.replace(tzinfo=tz)
    
    dt_utc = dt_aware.astimezone(ZoneInfo("UTC"))
    print(f"Local ({timezone}): {dt_aware.isoformat()}")
    print(f"UTC: {dt_utc.isoformat()}")
    
    # Expected: 10:00 IST is 04:30 UTC
    assert dt_utc.hour == 4
    assert dt_utc.minute == 30

if __name__ == "__main__":
    test_timezone_conversion()
    print("Timezone reproduction test passed!")
