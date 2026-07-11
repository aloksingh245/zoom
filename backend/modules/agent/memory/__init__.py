"""
session.py — In-memory session store for agent conversation history.

WHY IN-MEMORY?
  We deliberately chose NOT to use the database for chat history because:
  1. Chat history is ephemeral — it's only meaningful during a session
  2. Database writes for every message would add latency to streaming
  3. We only need the last 20 messages, not a permanent audit trail

HOW IT WORKS:
  _sessions is a plain Python dict: { user_id -> [list of messages] }
  Each message is: { "role": "user"|"agent", "content": "..." }
  When the list exceeds MAX_MESSAGES, the oldest messages are dropped.

THREAD SAFETY:
  FastAPI runs async — concurrent requests won't corrupt this dict because
  Python's GIL protects dict operations. For multi-worker deployments,
  switch to Redis. For now, this is sufficient.
"""

from collections import deque
from typing import Literal

# Maximum messages to keep per session.
# 20 is the sweet spot: enough context for the LLM to reason well,
# small enough to stay within token limits.
MAX_MESSAGES = 20

MessageRole = Literal["user", "agent"]

# Main store: user_id (str) → deque of message dicts
# deque with maxlen automatically drops oldest when full — no manual trimming needed
_sessions: dict[str, deque] = {}


def get_history(user_id: str) -> list[dict]:
    """
    Return the full conversation history for a user as a plain list.
    Returns empty list if no history exists yet.
    """
    if user_id not in _sessions:
        return []
    return list(_sessions[user_id])


def add_message(user_id: str, role: MessageRole, content: str) -> None:
    """
    Append a new message to the session history.
    If the user has no session yet, create one automatically.
    The deque's maxlen ensures we never exceed MAX_MESSAGES.
    """
    if user_id not in _sessions:
        # maxlen=MAX_MESSAGES means oldest message auto-drops when full
        _sessions[user_id] = deque(maxlen=MAX_MESSAGES)

    _sessions[user_id].append({
        "role": role,
        "content": content
    })


def clear_session(user_id: str) -> None:
    """
    Clear all history for a user.
    Called when user logs out or explicitly resets the chat.
    """
    if user_id in _sessions:
        del _sessions[user_id]


def session_count() -> int:
    """
    Return number of active sessions.
    Useful for monitoring/debugging.
    """
    return len(_sessions)
