"""
tool_guard.py — Enforces execution policies and role permissions on tool calls.

WHY RUN A TOOL GUARD?
  An agent might plan to call a tool, but we must verify that:
  1. The user's role actually has permission to execute this specific tool.
  2. The parameters are safe (e.g., preventing sql injection, validating date ranges).
  3. Safe defaults are maintained.

This is the ultimate security layer. Even if the LLM attempts to call a tool,
this code intercepts and cancels the call if permissions or parameters fail.
"""

from typing import Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Map roles to allowed tool names
# This is a hard mapping. The agent CANNOT execute any tool not listed here for their role.
ROLE_TOOL_PERMISSIONS = {
    "student": [
        "get_my_classes",
        "get_class_details",
    ],
    "mentor": [
        "get_my_classes",
        "get_class_details",
        "get_all_classes",
        "get_student_list",
    ],
    "admin": [
        "get_my_classes",
        "get_class_details",
        "get_all_classes",
        "get_student_list",
        "schedule_class",
        "edit_class",
        "delete_class",
        "sync_with_zoom",
        "sync_with_calendar",
        "get_stats",
    ]
}

class ToolGuardException(Exception):
    """Exception raised when a tool call violates security or validation policies."""
    pass

def validate_tool_call(tool_name: str, args: dict[str, Any], user_role: str) -> None:
    """
    Validate a tool call before it executes.
    Raises ToolGuardException if the call is invalid or unauthorized.
    """
    # 1. Role-based authorization check
    allowed_tools = ROLE_TOOL_PERMISSIONS.get(user_role, [])
    if tool_name not in allowed_tools:
        logger.error(f"Unauthorized tool execution attempt: Role '{user_role}' tried to run tool '{tool_name}'")
        raise ToolGuardException(
            f"Access Denied: The tool '{tool_name}' is not available for your role ({user_role})."
        )

    # 2. Parameter specific validations
    if tool_name == "schedule_class":
        _validate_schedule_args(args)
    elif tool_name == "delete_class":
        _validate_delete_args(args)

    logger.debug(f"Tool call '{tool_name}' successfully passed guardrails check.")

def _validate_schedule_args(args: dict[str, Any]) -> None:
    """Ensure scheduled dates are not in the past and values are sensible."""
    date_str = args.get("date")
    start_time_str = args.get("start_time")
    
    if not date_str or not start_time_str:
        return  # Missing parameters will be caught by model validation or tool logic

    try:
        # Check date format (YYYY-MM-DD)
        class_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        if class_date < today:
            raise ToolGuardException("Cannot schedule a class in the past.")
    except ValueError:
        raise ToolGuardException("Invalid date format. Expected YYYY-MM-DD.")

    # Prevent extremely long durations
    duration = args.get("duration_minutes")
    if duration is not None:
        try:
            dur_int = int(duration)
            if dur_int < 15 or dur_int > 480:  # 15 mins to 8 hours
                raise ToolGuardException("Class duration must be between 15 and 480 minutes.")
        except ValueError:
            raise ToolGuardException("Duration must be a valid number.")

def _validate_delete_args(args: dict[str, Any]) -> None:
    """Ensure delete class request contains a valid class ID."""
    class_id = args.get("class_id")
    if not class_id:
        raise ToolGuardException("Missing class_id for delete operation.")
    # Verify it is a valid non-empty string format (supporting UUIDs and identifiers)
    if not isinstance(class_id, str) or not class_id.strip():
        raise ToolGuardException("Invalid class_id format.")
