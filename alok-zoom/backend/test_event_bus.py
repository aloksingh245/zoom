import asyncio
import logging
import pytest
from core.events import EventBus

logging.basicConfig(level=logging.INFO)

@pytest.mark.asyncio
async def test_event_bus_background_tasks():
    bus = EventBus()
    execution_count = 0
    
    async def slow_listener(*args, **kwargs):
        nonlocal execution_count
        await asyncio.sleep(0.1)
        execution_count += 1

    bus.subscribe("test_event", slow_listener)
    
    # Emit and don't wait (simulating background task)
    await bus.emit("test_event")
    
    # Check that the task is in the background_tasks set
    assert len(bus._background_tasks) == 1
    
    # Wait for completion
    await asyncio.sleep(0.2)
    assert execution_count == 1
    assert len(bus._background_tasks) == 0

@pytest.mark.asyncio
async def test_event_bus_multiple_listeners():
    bus = EventBus()
    results = []
    
    async def listener_a(): results.append("a")
    async def listener_b(): results.append("b")
    
    bus.subscribe("multi", listener_a)
    bus.subscribe("multi", listener_b)
    
    await bus.emit("multi")
    await asyncio.sleep(0.1)
    
    assert "a" in results
    assert "b" in results
