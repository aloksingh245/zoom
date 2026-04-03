import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from modules.classes.service import ClassService
from modules.classes.schemas import ClassUpdate

@pytest.mark.asyncio
async def test_sync_with_calendar_deleted_event():
    db = AsyncMock()
    service = ClassService()
    
    mock_class = MagicMock()
    mock_class.calendar_event_id = "test_event_id"
    mock_class.id = "local_id"
    
    with patch.object(service, 'list_classes', return_value=[mock_class]), \
         patch.object(service, 'delete_class', new_callable=AsyncMock) as mock_delete, \
         patch('modules.classes.service.calendar_service.get_event', new_callable=AsyncMock) as mock_get_event:
        
        # Simulate deleted event in GCal
        mock_get_event.return_value = None
        
        result = await service.sync_with_calendar(db)
        
        assert result["removed"] == 1
        mock_delete.assert_called_with(db, "local_id")

@pytest.mark.asyncio
async def test_sync_with_calendar_updated_time():
    db = AsyncMock()
    service = ClassService()
    
    mock_class = MagicMock()
    mock_class.calendar_event_id = "test_event_id"
    mock_class.id = "local_id"
    mock_class.date = "2026-03-20"
    mock_class.start_time = "10:00"
    
    with patch.object(service, 'list_classes', return_value=[mock_class]), \
         patch.object(service, 'update_class', new_callable=AsyncMock) as mock_update, \
         patch('modules.classes.service.calendar_service.get_event', new_callable=AsyncMock) as mock_get_event:
        
        # Simulate time change in GCal
        mock_get_event.return_value = {
            'status': 'confirmed',
            'start': {'dateTime': '2026-03-20T11:00:00Z'}
        }
        
        result = await service.sync_with_calendar(db)
        
        assert result["updated"] == 1
        # Check that update_class was called with new time (UTC 11:00)
        args, kwargs = mock_update.call_args
        payload = args[2]
        assert payload.start_time == "11:00"
