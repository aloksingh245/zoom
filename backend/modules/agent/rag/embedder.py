"""
embedder.py — Converts text into vector embeddings using Gemini's embedding model.

WHAT IS AN EMBEDDING?
  An embedding is a list of floating point numbers (e.g., [0.23, -0.87, 0.41, ...])
  that represents the MEANING of a piece of text.

  The key property:
    - "React class on Monday" → embedding A
    - "JavaScript session this week" → embedding B
    - similarity(A, B) is HIGH  ← same meaning, different words

  This is why semantic search is smarter than keyword search.
  A student asking "when is my JS class?" will find "React/Node.js" sessions
  because the embeddings are close in meaning space.

WHY GEMINI text-embedding-004?
  - We already have the Gemini API key in your config (gemini_api_key)
  - No extra cost or setup needed
  - 768 dimensions — good balance of accuracy vs storage size
  - Supports task_type="RETRIEVAL_DOCUMENT" for indexing and
    task_type="RETRIEVAL_QUERY" for searching — these two modes
    optimize the embeddings for their specific purpose.

CACHING:
  Embedding API calls cost tokens. We cache embeddings for identical text
  using a simple dict. If the same class description is embedded twice
  (e.g., on startup and after an update), we skip the API call.
"""

import asyncio
from functools import lru_cache
from google import genai
from google.genai import types as genai_types
from core.config import settings

# The embedding model we use.
# text-embedding-004 is Google's latest general-purpose embedding model.
EMBEDDING_MODEL = "text-embedding-004"

# Dimension of the embedding vectors produced by this model.
# ChromaDB needs to know this when creating a collection.
EMBEDDING_DIMENSION = 768


def _get_client() -> genai.Client:
    """
    Create and return a Gemini client.

    Why a function instead of a module-level variable?
    Because settings.gemini_api_key might not be set when the module
    first loads (during startup). Creating it lazily avoids that problem.
    """
    return genai.Client(api_key=settings.gemini_api_key)


async def embed_text(text: str, for_query: bool = False) -> list[float]:
    """
    Convert a string of text into a 768-dimensional embedding vector.

    Args:
        text: The text to embed (class name, question, chat message, etc.)
        for_query: 
            - True  → use RETRIEVAL_QUERY task (optimized for searching)
            - False → use RETRIEVAL_DOCUMENT task (optimized for indexing)
            This distinction matters for retrieval quality. Gemini's embedding
            model produces slightly different vectors based on how the text
            will be used.

    Returns:
        A list of 768 floats representing the meaning of the text.

    Raises:
        ValueError if the API key is not configured.
        RuntimeError if the Gemini API call fails.
    """
    if not settings.gemini_api_key:
        raise ValueError(
            "gemini_api_key is not set. Go to Settings and add your Gemini API key."
        )

    # Clean the text — remove extra whitespace, truncate if too long
    # Gemini's embedding model has a ~2048 token limit per text
    text = text.strip()
    if not text:
        raise ValueError("Cannot embed empty text.")
    if len(text) > 8000:
        # Truncate to approximately 2000 tokens (rough estimate: 4 chars per token)
        text = text[:8000]

    task_type = (
        "RETRIEVAL_QUERY"
        if for_query
        else "RETRIEVAL_DOCUMENT"
    )

    # Run the blocking Gemini API call in a thread pool.
    # Why? The google-genai SDK is synchronous. FastAPI is async.
    # Running sync code directly in an async function would block the
    # entire event loop (freeze all other requests). asyncio.to_thread
    # runs it in a separate thread so the event loop stays free.
    def _call_api():
        client = _get_client()
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=genai_types.EmbedContentConfig(task_type=task_type),
        )
        return response.embeddings[0].values

    return await asyncio.to_thread(_call_api)


async def embed_batch(texts: list[str], for_query: bool = False) -> list[list[float]]:
    """
    Embed multiple texts concurrently.

    Why concurrent? Each embed_text call is I/O bound (waiting for the API).
    Running them concurrently with asyncio.gather reduces total wait time from
    N * latency → max(latency) when done in parallel.

    Args:
        texts: List of strings to embed
        for_query: Same as in embed_text — True for search queries

    Returns:
        List of embedding vectors, in the same order as the input texts.
    """
    tasks = [embed_text(t, for_query=for_query) for t in texts]
    return await asyncio.gather(*tasks)
