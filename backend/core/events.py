import asyncio
import logging
import sys
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
        print(f"\n🔔 EVENT BUS EMIT: '{event_name}' | Registered events: {list(self._listeners.keys())} | Listener count for this event: {len(self._listeners.get(event_name, []))}", flush=True)
        sys.stdout.flush()
        if event_name in self._listeners:
            logger.info(f"Emitting event: {event_name}")
            for listener in self._listeners[event_name]:
                print(f"  → Dispatching to listener: {listener.__name__}", flush=True)
                task = asyncio.create_task(self._safe_execute(listener, event_name, *args, **kwargs))
                # Add task to the set to prevent garbage collection
                self._background_tasks.add(task)
                # Remove task from the set when it completes
                task.add_done_callback(self._background_tasks.discard)
        else:
            print(f"  ⚠️ No listeners registered for '{event_name}'!", flush=True)

    async def _safe_execute(self, listener: Callable, event_name: str, *args, **kwargs):
        try:
            print(f"  🔄 _safe_execute START: {listener.__name__} for {event_name}", flush=True)
            if asyncio.iscoroutinefunction(listener):
                await listener(*args, **kwargs)
            else:
                listener(*args, **kwargs)
            print(f"  ✅ _safe_execute DONE: {listener.__name__} for {event_name}", flush=True)
        except Exception as e:
            print(f"  ❌ _safe_execute ERROR: {listener.__name__} for {event_name}: {e}", flush=True)
            logger.error(f"Error in listener {listener.__name__} for event {event_name}: {e}", exc_info=True)

event_bus = EventBus()

