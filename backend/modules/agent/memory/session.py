"""
session.py — In-memory session store for agent conversation history.

WHY IN-MEMORY?
  We deliberately chose NOT to use the database for chat history because:
  1. Chat history is ephemeral — it's only meaningful during a session
  2. Database writes for every message would add latency to streaming
  3. We only need the last 20 messages, not a permanent audit trail

HOW IT WORKS:
  _sessions is a plain Python dict: { user_id -> deque of messages }
  Each message is: { "role": "user"|"agent", "content": "..." }
  When the deque exceeds MAX_MESSAGES, the oldest message is auto-dropped.

THREAD SAFETY:
  FastAPI runs async — concurrent requests won't corrupt this dict because
  Python's GIL protects dict operations. For multi-worker deployments,
  switch to Redis. For now (single worker), this is perfectly safe.
"""

from collections import deque
from typing import Literal

# Maximum messages to keep per session in memory.
# 20 is the sweet spot: enough context for the LLM to reason well,
# small enough to stay within Gemini's token budget.
MAX_MESSAGES = 20

MessageRole = Literal["user", "agent"]

# Main store: user_id (str) → deque of message dicts
# deque with maxlen automatically drops the oldest message when full.
# This means we never need manual cleanup — Python handles it.
_sessions: dict[str, deque] = {}


def get_history(user_id: str) -> list[dict]:
    """
    Return the full conversation history for a user as a plain list.

    Why convert to list?
    The deque is great for internal use but the LLM API expects a plain list.
    We convert here so callers don't need to know about the deque internals.

    Returns empty list [] if the user has no session yet.
    """
    if user_id not in _sessions:
        return []
    return list(_sessions[user_id])


def add_message(user_id: str, role: MessageRole, content: str) -> None:
    """
    Append a new message to the session history.

    If the user has no session yet, one is created automatically.
    The deque's maxlen=MAX_MESSAGES ensures we never exceed the limit —
    no manual trimming code needed.

    Args:
        user_id: The user's ID (from JWT token)
        role: "user" for the human's message, "agent" for the AI's response
        content: The actual text of the message
    """
    if user_id not in _sessions:
        _sessions[user_id] = deque(maxlen=MAX_MESSAGES)

    _sessions[user_id].append({
        "role": role,
        "content": content
    })


def clear_session(user_id: str) -> None:
    """
    Wipe all history for a user.
    Called when the user clicks "Clear Chat" or logs out.
    """
    if user_id in _sessions:
        del _sessions[user_id]


def get_message_count(user_id: str) -> int:
    """Return how many messages are stored for this user."""
    return len(_sessions.get(user_id, []))


def session_count() -> int:
    """Total number of active sessions. Useful for monitoring."""
    return len(_sessions)
