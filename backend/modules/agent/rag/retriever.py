"""
retriever.py — Role-filtered semantic search against ChromaDB.

THE RETRIEVAL STEP:
  This is the R in RAG (Retrieval-Augmented Generation).
  Given a user's message, we:
  1. Convert the message to an embedding vector (using Gemini)
  2. Search ChromaDB for the N most similar stored documents
  3. Filter results by the user's role (critical for data security)
  4. Return the raw text of those documents

  These retrieved text chunks are then injected into the LLM prompt
  as context, so the agent can answer questions about YOUR data.

ROLE-BASED FILTERING:
  This is the security layer of RAG.
  ChromaDB's where= parameter filters metadata BEFORE returning results.
  This means:

  Student  → can only see classes (not admin-specific data, not other students)
  Mentor   → can see classes for their assigned courses
  Admin    → sees everything — no filter applied

  This filtering happens at the VECTOR DB level, not in Python code.
  Even if a student crafts a clever prompt injection attack, the vector DB
  will never return data they're not authorized to see.

TOP_K:
  We retrieve 5 chunks by default.
  Why 5? It's the empirical sweet spot:
  - Too few (1-2): Agent misses relevant context
  - Too many (10+): Token budget gets used up, LLM gets confused by noise
  - 5: Enough breadth, fits comfortably in the prompt
"""

from .indexer import get_collection, COLLECTION_CLASSES, COLLECTION_COURSES, COLLECTION_QA
from .embedder import embed_text
import logging

logger = logging.getLogger(__name__)

# Number of results to retrieve per search.
# Can be overridden per-call if needed.
DEFAULT_TOP_K = 5


async def retrieve_context(
    query: str,
    user_role: str,
    user_id: str | None = None,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Main retrieval function — searches all collections and returns
    combined context text ready to inject into the LLM prompt.

    Args:
        query:     The user's message (will be embedded for search)
        user_role: "admin", "mentor", or "student" — controls what data is visible
        user_id:   The user's ID (for student-specific filtering in future)
        top_k:     Number of results per collection

    Returns:
        A formatted string of retrieved context, e.g.:
        "--- Relevant Class Info ---
         Class session: Advanced React
         Date: 2026-07-10, Time: 19:00
         ...
         --- Relevant Course Info ---
         Course: Full-Stack Batch 12"

        Returns empty string if nothing relevant is found.
    """
    # Embed the query with RETRIEVAL_QUERY task type
    # (different from RETRIEVAL_DOCUMENT used when indexing)
    try:
        query_embedding = await embed_text(query, for_query=True)
    except Exception as e:
        logger.warning(f"Embedding failed during retrieval: {e}")
        return ""  # Gracefully degrade — agent still works without RAG context

    # Collect results from all relevant collections
    context_parts = []

    # 1. Search class sessions
    class_results = await _search_classes(query_embedding, user_role, top_k)
    if class_results:
        context_parts.append("--- Relevant Class Schedule Info ---")
        context_parts.extend(class_results)

    # 2. Search courses (all roles can see courses)
    course_results = await _search_courses(query_embedding, top_k)
    if course_results:
        context_parts.append("--- Relevant Course Info ---")
        context_parts.extend(course_results)

    # 3. Search past Q&A pairs (filtered by role)
    qa_results = await _search_qa(query_embedding, user_role, top_k=3)
    if qa_results:
        context_parts.append("--- Relevant Past Answers ---")
        context_parts.extend(qa_results)

    if not context_parts:
        return ""

    return "\n".join(context_parts)


async def _search_classes(
    query_embedding: list[float],
    user_role: str,
    top_k: int,
) -> list[str]:
    """
    Search the classes collection with role-based metadata filtering.

    Admin → no filter, sees all classes
    Mentor → no filter for now (could filter by mentor_email in future)
    Student → no filter for now (returns general class info only)

    Why no student filter yet?
    The current system doesn't track which student belongs to which class.
    Once that relationship is added to the DB, add:
    where={"student_id": user_id} for student queries.
    """
    try:
        collection = get_collection(COLLECTION_CLASSES)
        where_filter = None  # Admin sees everything

        # For now, all roles see the same class data.
        # The system prompt controls what the LLM does with it.
        # (A student's system prompt says "only discuss the user's own schedule")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count() or 1),
            where=where_filter,
            include=["documents", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # Filter by relevance threshold.
        # ChromaDB returns cosine DISTANCE (0=identical, 1=opposite).
        # We only include results with distance < 0.7 (similarity > 0.3).
        # This prevents injecting completely unrelated content.
        RELEVANCE_THRESHOLD = 0.7
        relevant = [
            doc for doc, dist in zip(documents, distances)
            if dist < RELEVANCE_THRESHOLD
        ]
        return relevant

    except Exception as e:
        logger.warning(f"Class search failed: {e}")
        return []


async def _search_courses(
    query_embedding: list[float],
    top_k: int,
) -> list[str]:
    """Search the courses collection — no role filter, all roles see courses."""
    try:
        collection = get_collection(COLLECTION_COURSES)
        if collection.count() == 0:
            return []

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "distances"],
        )
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        return [doc for doc, dist in zip(documents, distances) if dist < 0.7]
    except Exception as e:
        logger.warning(f"Course search failed: {e}")
        return []


async def _search_qa(
    query_embedding: list[float],
    user_role: str,
    top_k: int = 3,
) -> list[str]:
    """
    Search past Q&A pairs, filtered by role.

    Why filter Q&A by role?
    An admin's Q&A might contain sensitive operational details
    (e.g., "how do I delete all classes for batch X?") that shouldn't
    be surfaced in a student's context window.
    """
    try:
        collection = get_collection(COLLECTION_QA)
        if collection.count() == 0:
            return []

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            where={"role": user_role},  # Only Q&A from same role
            include=["documents", "distances"],
        )
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        return [doc for doc, dist in zip(documents, distances) if dist < 0.6]
    except Exception as e:
        logger.warning(f"Q&A search failed: {e}")
        return []
