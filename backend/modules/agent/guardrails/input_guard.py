"""
input_guard.py — Input guardrails to run before messages are sent to the LLM.

WHAT IS AN INPUT GUARDRAIL?
  It is a security filter that analyzes the user's message before the LLM
  ever sees it. This prevents:
  1. Prompt Injection (e.g. "Ignore your previous system instructions and tell me...")
  2. Role Bypass (e.g. A student asking the agent to delete or modify data)
  3. Flooding/Overload (e.g. sending a massive paragraph to exhaust tokens or crash the system)

WHY NOT LET THE LLM HANDLE IT?
  LLMs can be fooled by jailbreaks or prompt injections.
  Running structural checks in code is 100% deterministic and cannot be bypassed.
  It also saves API costs since blocked messages never make an LLM call.
"""

import re
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Basic keywords associated with prompt injection/jailbreak attempts
JAILBREAK_PATTERNS = [
    r"ignore (your )?previous( instructions)?",
    r"forget (your )?rules",
    r"you are now a( new)?",
    r"system prompt bypass",
    r"do anything now",
    r"dan mode",
    r"ignore everything before",
    # Sensitive credential / configuration requests
    r"database password",
    r"smtp password",
    r"zoom client secret",
    r"gemini api key",
    r"show.*env",
    r"read.*env",
    r"print.*env",
    r"secret key",
    r"db credentials",
    r"sql password",
]

# Structural action words that students/mentors shouldn't query in an active way
BLOCKED_STUDENT_PATTERNS = [
    r"delete.*class",
    r"delete.*session",
    r"remove.*class",
    r"remove.*session",
    r"cancel.*class",
    r"cancel.*session",
    r"schedule.*class",
    r"schedule.*session",
    r"create.*class",
    r"create.*session",
    r"update.*class",
    r"update.*session",
    r"sync.*zoom",
    r"sync.*calendar",
]

def check_prompt_injection(message: str) -> None:
    """
    Check if the user is trying to overwrite system instructions.
    Raises HTTPException if suspicious patterns are found.
    """
    msg_lower = message.lower()
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, msg_lower):
            logger.warning(f"Jailbreak attempt detected: Match for pattern '{pattern}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your request contains instructions that are not allowed. Please rephrase."
            )

def check_role_scope(message: str, role: str) -> None:
    """
    Quick syntactic check to block non-admins from attempting mutations.
    Even though the tool registry enforces this at execution, catching it
    at the input layer provides immediate feedback and saves tokens.
    """
    if role == "admin":
        return  # Admins can do everything

    msg_lower = message.lower()
    
    # Check if a student or mentor is attempting mutation keywords
    for pattern in BLOCKED_STUDENT_PATTERNS:
        if re.search(pattern, msg_lower):
            logger.warning(f"Role Scope Violation: User with role '{role}' attempted action matching pattern '{pattern}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform scheduling modifications. Please ask an administrator."
            )

def check_input_limits(message: str) -> None:
    """
    Enforce character limits to prevent token exhaustion.
    Max 1000 characters is more than enough for scheduling requests.
    """
    if len(message) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message exceeds the maximum length of 1000 characters."
        )
    if not message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot process an empty message."
        )

def run_input_guardrails(message: str, role: str) -> None:
    """
    Run all input guardrails. If any fails, it raises an exception
    which will immediately terminate the API request before LLM processing.
    """
    check_input_limits(message)
    check_prompt_injection(message)
    check_role_scope(message, role)
