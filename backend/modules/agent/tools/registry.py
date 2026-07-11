"""
registry.py — Role-based tool retrieval for the Google ADK Agent.

WHY DO WE NEED A REGISTRY?
  We must prevent the LLM from even knowing about tools it is not allowed to use.
  If a student chats with the agent:
  - We configure the agent with ONLY get_my_classes and get_class_details.
  - The model's system definition will not contain any administrative tools (like delete_class).
  - This completely eliminates any possibility of tool privilege escalation.

HOW IT WORKS:
  get_role_tools(user_role) returns a list of Python function references
  authorized for that role, which are passed directly to `LocalAgentConfig(tools=...)`.
"""

from typing import Callable, Any
from . import functions

# Hard mapping from role names to allowed Python function references.
# Ensure that these match the allowed names in tool_guard.py!
ROLE_TOOLS_MAPPING: dict[str, list[Callable[..., Any]]] = {
    "student": [
        functions.get_my_classes,
        functions.get_class_details,
    ],
    "mentor": [
        functions.get_my_classes,
        functions.get_class_details,
        functions.get_all_classes,
        functions.get_student_list,
    ],
    "admin": [
        functions.get_my_classes,
        functions.get_class_details,
        functions.get_all_classes,
        functions.get_student_list,
        functions.schedule_class,
        functions.edit_class,
        functions.delete_class,
        functions.sync_with_zoom,
        functions.sync_with_calendar,
        functions.get_stats,
    ]
}


def get_role_tools(role: str) -> list[Callable[..., Any]]:
    """
    Return a list of Python functions (tools) that the user is authorized to use.
    If the role is unknown, default to student access (least privilege).
    """
    return ROLE_TOOLS_MAPPING.get(role, ROLE_TOOLS_MAPPING["student"])


def get_all_tool_functions() -> dict[str, Callable[..., Any]]:
    """
    Return a dictionary mapping tool name (string) to the function object.
    Used for manual execution or guardrail inspection.
    """
    all_funcs = [
        functions.get_my_classes,
        functions.get_class_details,
        functions.get_all_classes,
        functions.get_student_list,
        functions.schedule_class,
        functions.edit_class,
        functions.delete_class,
        functions.sync_with_zoom,
        functions.sync_with_calendar,
        functions.get_stats,
    ]
    return {func.__name__: func for func in all_funcs}
