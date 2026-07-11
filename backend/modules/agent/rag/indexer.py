"""
indexer.py — Populates ChromaDB with your application data.

WHAT IS CHROMADB?
  ChromaDB is an open-source vector database that runs locally (no cloud needed).
  It stores text + its embedding vector + metadata in collections (like DB tables).

  Think of it as a special database where queries are:
    "Give me the 5 most SIMILAR documents to this question"
  instead of:
    "Give me rows WHERE column = value"

HOW INDEXING WORKS:
  1. Fetch all classes from your SQLite database
  2. Convert each class into a human-readable text chunk
  3. Embed that text using Gemini → get a vector
  4. Store (text + vector + metadata) in ChromaDB

  Later, when the agent gets a question:
  1. Embed the question → get a query vector
  2. ChromaDB finds the 5 most similar stored vectors
  3. Return the original text of those 5 chunks
  4. Inject that text into the LLM prompt as context

WHY TWO COLLECTIONS?
  classes_collection → class sessions (schedule, topic, mentor, zoom link)
  courses_collection → course/batch information (name, status)
  qa_collection      → past Q&A pairs extracted from agent conversations

  Separating them lets us search each independently and apply
  different metadata filters (e.g., role-based access).

AUTO-INDEXING ON EVENTS:
  Your project already has an event bus (core/events.py).
  The indexer listens to "class_created", "class_updated", "class_deleted"
  events and automatically keeps ChromaDB in sync with your SQLite DB.
  No manual intervention needed after initial setup.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
from .embedder import embed_text, embed_batch
import logging

logger = logging.getLogger(__name__)

# Where ChromaDB persists its data on disk.
# We store it inside the backend directory so it's co-located with your DB.
# On Docker deployments, mount this path as a volume.
CHROMA_PATH = Path(__file__).parent.parent.parent.parent / "chroma_store"

# Collection names — think of these as table names in ChromaDB
COLLECTION_CLASSES = "classes"
COLLECTION_COURSES = "courses"
COLLECTION_QA      = "qa_pairs"

# Singleton client — created once, reused across all requests
_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    """
    Return the ChromaDB client (create if not yet initialized).

    Why a singleton?
    ChromaDB's PersistentClient maintains a connection to the on-disk store.
    Creating multiple clients would cause file lock conflicts.
    One client shared across all requests is the correct pattern.
    """
    global _client
    if _client is None:
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB initialized at {CHROMA_PATH}")
    return _client


def get_collection(name: str) -> chromadb.Collection:
    """
    Get or create a ChromaDB collection by name.

    get_or_create_collection is idempotent — safe to call on every startup.
    If the collection already exists (from a previous run), it just returns it.
    If it doesn't exist yet, it creates it.

    We use cosine similarity (the default) because embedding vectors
    are direction-sensitive — cosine similarity captures semantic similarity
    better than Euclidean distance for text embeddings.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for text
    )


def _class_to_text(cls: dict) -> str:
    """
    Convert a class record (dict) into a natural language text chunk.

    WHY CONVERT TO TEXT?
    Embeddings work on text. We need to describe the class in a way that
    captures all searchable attributes. The format mimics how a human
    would describe the class, which makes semantic search more natural.

    Example output:
      "Class session: Advanced React Hooks
       Course: Full-Stack Batch 12
       Date: 2026-07-10, Time: 19:00
       Mentor: john@example.com
       Duration: 90 minutes
       Zoom join link: zoom.us/j/123456"
    """
    parts = [
        f"Class session: {cls.get('topic_name', 'Unknown Topic')}",
        f"Course: {cls.get('course_name', 'Unknown Course')}",
        f"Date: {cls.get('date', 'Unknown')}, Time: {cls.get('start_time', 'Unknown')}",
    ]
    if cls.get("mentor_email"):
        parts.append(f"Mentor: {cls['mentor_email']}")
    if cls.get("duration_minutes"):
        parts.append(f"Duration: {cls['duration_minutes']} minutes")
    if cls.get("zoom_join_url"):
        parts.append(f"Zoom join link: {cls['zoom_join_url']}")
    if cls.get("assignment_name"):
        parts.append(f"Assignment/Agenda: {cls['assignment_name']}")
    return "\n".join(parts)


async def index_class(cls: dict) -> None:
    """
    Index a single class into ChromaDB.

    Called when:
    - A new class is created (via event bus listener)
    - A class is updated (upsert replaces the old vector)

    Args:
        cls: Dict with class fields (id, topic_name, course_name, date, etc.)

    The upsert operation:
    - If a document with this ID already exists → UPDATE it
    - If it doesn't exist → INSERT it
    This means we can safely call this for both create and update events.
    """
    collection = get_collection(COLLECTION_CLASSES)
    text = _class_to_text(cls)

    try:
        embedding = await embed_text(text, for_query=False)
        collection.upsert(
            ids=[str(cls["id"])],
            embeddings=[embedding],
            documents=[text],
            # Metadata is stored alongside the vector for filtering.
            # Role-based access control uses these fields to restrict results.
            metadatas=[{
                "class_id":    str(cls.get("id", "")),
                "course_id":   str(cls.get("course_id", "")),
                "date":        str(cls.get("date", "")),
                "mentor_email": str(cls.get("mentor_email", "")),
            }],
        )
        logger.debug(f"Indexed class {cls['id']}: {cls.get('topic_name')}")
    except Exception as e:
        logger.error(f"Failed to index class {cls.get('id')}: {e}")


async def delete_class_from_index(class_id: str) -> None:
    """
    Remove a class from ChromaDB when it's deleted from the DB.

    Called by the event bus listener on "class_deleted" event.
    If the class wasn't indexed (shouldn't happen), ChromaDB silently ignores it.
    """
    collection = get_collection(COLLECTION_CLASSES)
    try:
        collection.delete(ids=[str(class_id)])
        logger.debug(f"Removed class {class_id} from index")
    except Exception as e:
        logger.error(f"Failed to delete class {class_id} from index: {e}")


async def index_course(course: dict) -> None:
    """
    Index a single course/batch into ChromaDB.

    Similar to index_class but for course data.
    """
    collection = get_collection(COLLECTION_COURSES)
    text = f"Course: {course.get('name', 'Unknown')}\nStatus: Active"

    try:
        embedding = await embed_text(text, for_query=False)
        collection.upsert(
            ids=[str(course["id"])],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"course_id": str(course.get("id", ""))}],
        )
    except Exception as e:
        logger.error(f"Failed to index course {course.get('id')}: {e}")


async def index_qa_pair(question: str, answer: str, user_role: str) -> None:
    """
    Store a Q&A pair from a completed agent conversation.

    WHY INDEX Q&A PAIRS?
    This is the "learning" mechanism. After every conversation, the key
    exchange gets embedded and stored. In future sessions, when a similar
    question is asked, the retriever finds this past answer and includes it
    as context — making the agent progressively smarter about your domain.

    The user_role metadata lets us filter Q&A pairs by role:
    Admin Q&A won't leak into student queries.
    """
    import uuid
    collection = get_collection(COLLECTION_QA)
    text = f"Q: {question}\nA: {answer}"

    try:
        embedding = await embed_text(text, for_query=False)
        collection.upsert(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"role": user_role}],
        )
    except Exception as e:
        logger.error(f"Failed to index Q&A pair: {e}")


async def bulk_index_classes(classes: list[dict]) -> None:
    """
    Index all classes at once — called on server startup.

    WHY BULK?
    On startup we need to populate ChromaDB from your existing SQLite data.
    Calling index_class() one by one would work but is slow (sequential API calls).
    embed_batch() sends all embedding requests concurrently — much faster.

    Args:
        classes: List of class dicts (all classes from your DB)
    """
    if not classes:
        logger.info("No classes to bulk index.")
        return

    collection = get_collection(COLLECTION_CLASSES)
    texts = [_class_to_text(c) for c in classes]

    logger.info(f"Bulk indexing {len(classes)} classes into ChromaDB...")
    try:
        embeddings = await embed_batch(texts, for_query=False)
        collection.upsert(
            ids=[str(c["id"]) for c in classes],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{
                "class_id":    str(c.get("id", "")),
                "course_id":   str(c.get("course_id", "")),
                "date":        str(c.get("date", "")),
                "mentor_email": str(c.get("mentor_email", "")),
            } for c in classes],
        )
        logger.info(f"Successfully indexed {len(classes)} classes.")
    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}")


async def bulk_index_courses(courses: list[dict]) -> None:
    """Index all courses at once — called on server startup."""
    if not courses:
        return

    collection = get_collection(COLLECTION_COURSES)
    texts = [f"Course: {c.get('name', 'Unknown')}\nStatus: Active" for c in courses]

    try:
        embeddings = await embed_batch(texts, for_query=False)
        collection.upsert(
            ids=[str(c["id"]) for c in courses],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"course_id": str(c.get("id", ""))} for c in courses],
        )
        logger.info(f"Indexed {len(courses)} courses into ChromaDB.")
    except Exception as e:
        logger.error(f"Bulk course indexing failed: {e}")
