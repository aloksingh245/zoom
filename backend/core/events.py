import asyncio
import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._background_tasks = set()

    def subscribe(self, event_name: str, listener: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)
        logger.info(f"Subscribed {listener.__name__} to event: {event_name}")

    async def emit(self, event_name: str, *args, **kwargs):
        if event_name in self._listeners:
            logger.info(f"Emitting event: {event_name}")
            for listener in self._listeners[event_name]:
                task = asyncio.create_task(self._safe_execute(listener, event_name, *args, **kwargs))
                # Add task to the set to prevent garbage collection
                self._background_tasks.add(task)
                # Remove task from the set when it completes
                task.add_done_callback(self._background_tasks.discard)

    async def _safe_execute(self, listener: Callable, event_name: str, *args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(listener):
                await listener(*args, **kwargs)
            else:
                listener(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in listener {listener.__name__} for event {event_name}: {e}")

event_bus = EventBus()
