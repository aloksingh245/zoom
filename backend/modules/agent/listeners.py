"""
listeners.py — Event bus subscribers to keep the RAG database synchronized.

WHY USE EVENT LISTENERS?
  When an admin adds, modifies, or deletes class sessions (either in the UI
  or via the agent), the changes are saved to the SQLite database.
  We must ensure that ChromaDB (the RAG vector database) is immediately updated.
  
  Instead of hardcoding indexer calls inside the ClassService, we use a
  Pub/Sub Event Bus pattern (core/events.py).
  When events occur:
  - "class_created"
  - "class_updated"
  - "class_deleted"
  
  These listener callbacks are triggered asynchronously, ensuring the
  semantic index is updated with zero overhead to the main database transaction.
"""

import logging
from core.events import event_bus
from modules.classes.schemas import ClassSession as ClassSchema
from .rag.indexer import index_class, delete_class_from_index

logger = logging.getLogger(__name__)


async def handle_class_created(created_class: ClassSchema) -> None:
    """Triggered when a new class is scheduled. Adds the session details to ChromaDB."""
    try:
        # Convert schema to dict for the indexer
        class_dict = created_class.model_dump()
        await index_class(class_dict)
        logger.info(f"RAG Indexer: Indexed newly created class {created_class.id}")
    except Exception as e:
        logger.error(f"RAG Indexer: Failed to index created class {created_class.id}: {e}")


async def handle_class_updated(updated_class: ClassSchema) -> None:
    """Triggered when class details change. Updates the vector in ChromaDB (via upsert)."""
    try:
        class_dict = updated_class.model_dump()
        await index_class(class_dict)
        logger.info(f"RAG Indexer: Updated class index for {updated_class.id}")
    except Exception as e:
        logger.error(f"RAG Indexer: Failed to update class index for {updated_class.id}: {e}")


async def handle_class_deleted(deleted_class: ClassSchema) -> None:
    """Triggered when a class is canceled. Removes the vector from ChromaDB."""
    try:
        await delete_class_from_index(deleted_class.id)
        logger.info(f"RAG Indexer: Removed deleted class {deleted_class.id} from index")
    except Exception as e:
        logger.error(f"RAG Indexer: Failed to remove deleted class {deleted_class.id} from index: {e}")


def register_listeners() -> None:
    """Subscribe listener callbacks to the event bus."""
    event_bus.subscribe("class_created", handle_class_created)
    event_bus.subscribe("class_updated", handle_class_updated)
    event_bus.subscribe("class_deleted", handle_class_deleted)
    logger.info("Agent event listeners registered with the Event Bus.")
