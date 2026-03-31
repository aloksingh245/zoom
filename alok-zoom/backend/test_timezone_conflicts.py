import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from modules.classes.service import ClassService

@pytest.mark.asyncio
async def test_check_conflicts_overlap():
    service = ClassService()
    db = AsyncMock()
    
    # Existing class: 10:00 - 11:30 IST
    existing = MagicMock()
    existing.id = "existing_id"
    existing.date = "2026-03-20"
    existing.start_time = "10:00"
    existing.duration_minutes = 90
    existing.timezone = "Asia/Kolkata"
    
    with patch.object(service, 'list_classes', return_value=[existing]):
        # New class: 11:00 - 12:30 IST (Overlaps)
        with pytest.raises(HTTPException) as exc:
            await service._check_conflicts(db, "2026-03-20", "11:00", "Asia/Kolkata", 90)
        assert exc.value.status_code == 400
        assert "Time conflict" in exc.value.detail

@pytest.mark.asyncio
async def test_check_conflicts_different_timezones():
    service = ClassService()
    db = AsyncMock()
    
    # Existing class: 10:00 - 11:30 IST (04:30 - 06:00 UTC)
    existing = MagicMock()
    existing.id = "existing_id"
    existing.date = "2026-03-20"
    existing.start_time = "10:00"
    existing.duration_minutes = 90
    existing.timezone = "Asia/Kolkata"
    
    with patch.object(service, 'list_classes', return_value=[existing]):
        # New class: 05:00 - 06:30 UTC (Overlaps in absolute time)
        with pytest.raises(HTTPException) as exc:
            await service._check_conflicts(db, "2026-03-20", "05:00", "UTC", 90)
        assert exc.value.status_code == 400
        assert "Time conflict" in exc.value.detail

@pytest.mark.asyncio
async def test_check_conflicts_no_overlap():
    service = ClassService()
    db = AsyncMock()
    
    existing = MagicMock()
    existing.id = "existing_id"
    existing.date = "2026-03-20"
    existing.start_time = "10:00"
    existing.duration_minutes = 90
    existing.timezone = "Asia/Kolkata"
    
    with patch.object(service, 'list_classes', return_value=[existing]):
        # New class: 12:00 - 13:30 IST (No overlap)
        await service._check_conflicts(db, "2026-03-20", "12:00", "Asia/Kolkata", 90)
        # Should not raise any exception
