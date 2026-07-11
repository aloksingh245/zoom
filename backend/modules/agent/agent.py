"""
agent.py — High-level orchestrator for the Google ADK AI Agent.

This module brings together all parts of the agent's architecture:
1. Retrieval Layer (retrieving RAG context from ChromaDB)
2. Episodic Memory (formatting the last 20 messages for the prompt)
3. Role-Based Prompt Configuration
4. Dynamic ADK Agent Construction (with allowed tools & hooks)
5. Execution Guardrails (Input, Tool, Output, Loop)
6. Response Streaming (SSE formatting)

HOW THE ADK RUNNER IS USED:
  - We use `InMemorySessionService` from `google.adk.sessions` to manage ADK session history.
  - We use `Runner` to run the agent in a session asynchronously using `run_async`.
  - The runner yields `Event` objects. We inspect the parts of these events to yield
    text tokens as they arrive, providing a smooth streaming interface.
"""

import logging
from typing import AsyncGenerator
from google.genai import types

from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService

from core.config import settings
from core.database import async_session_factory

# Import our modular agent layers
from .prompts.prompts import get_system_prompt
from .rag.retriever import retrieve_context
from .rag.indexer import bulk_index_classes, bulk_index_courses
from .tools.registry import get_role_tools
from .memory.session import get_history, add_message
from .guardrails.input_guard import run_input_guardrails
from .guardrails.tool_guard import validate_tool_call, ToolGuardException
from .guardrails.output_guard import run_output_guardrails
from .guardrails.loop_guard import LoopGuard, LoopGuardException

# Re-use existing services to read starting records for RAG index
from modules.classes.service import class_service
from modules.courses.service import course_service

logger = logging.getLogger(__name__)

# Shared in-memory session service for the ADK runner
_session_service = InMemorySessionService()


async def initialize_agent_rag() -> None:
    """
    Scans the SQLite database on server startup and indexes all existing
    classes and courses into ChromaDB.
    
    This ensures that the RAG knowledge base is fully populated and ready
    to answer questions from the very first request.
    """
    logger.info("Initializing Agent RAG Knowledge Base...")
    async with async_session_factory() as db:
        try:
            # 1. Fetch and index all classes
            classes = await class_service.list_classes(db)
            classes_dicts = [c.model_dump() for c in classes]
            await bulk_index_classes(classes_dicts)

            # 2. Fetch and index all courses
            courses = await course_service.list_courses(db)
            courses_dicts = [c.model_dump() for c in courses]
            await bulk_index_courses(courses_dicts)
            logger.info("Agent RAG Knowledge Base initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Agent RAG Knowledge Base: {e}")


def _format_history_for_prompt(user_id: str) -> str:
    """
    Format the last 20 messages of the conversation history into a readable
    text transcript to inject into the system prompt.
    """
    history = get_history(user_id)
    if not history:
        return ""
    
    formatted = []
    for msg in history:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        formatted.append(f"{role_label}: {msg['content']}")
    return "\n".join(formatted)


def make_before_tool_callback(user_role: str):
    """
    Create a callback to execute validation checks BEFORE a tool is invoked.
    
    Why use a closure?
    FastAPI handles role context per-request, but ADK tool callbacks run
    within the agent's runner lifecycle. Wrapping this in a closure binds
    the active user_role to the callback instance for that request.
    """
    async def before_tool_callback(tool, args, tool_context) -> None:
        # Enforce tool execution guardrails
        # Raises ToolGuardException if unauthorized or arguments are invalid
        validate_tool_call(tool.name, args, user_role)
        return None  # Returning None lets the framework proceed to execute the tool
    return before_tool_callback


async def run_agent_stream(
    user_id: str,
    user_email: str,
    user_role: str,
    message: str,
) -> AsyncGenerator[str, None]:
    """
    Executes the ADK Agent loop, executes guardrails, and yields text tokens
    as they are streamed from the Gemini model.

    Args:
        user_id: Unique identifier of the logged-in user.
        user_email: Email of the logged-in user.
        user_role: Role of the user ('admin', 'mentor', 'student').
        message: The message typed by the user.

    Yields:
        Text tokens (chunks of sentences) for the streaming typed effect in UI.
    """
    # 1. Run Input Guardrails (PII sanitization, prompt injection check, token limit)
    try:
        run_input_guardrails(message, user_role)
    except Exception as exc:
        # Stream the error message back to the UI nicely
        yield f"Guardrail Alert: {str(exc)}"
        return

    # Check that the Gemini API key is configured
    if not settings.gemini_api_key:
        yield "System Alert: Gemini API Key is not set. Please go to the Settings tab in the application and add your Gemini API Key first."
        return

    # Set the environment variable so the Google GenAI SDK used by ADK picks it up
    import os
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    # Add the user's message to our session store history
    add_message(user_id, "user", message)

    # 2. Retrieve semantic context (RAG) and format session history
    rag_context = await retrieve_context(message, user_role, user_id=user_id)
    session_history = _format_history_for_prompt(user_id)

    # 3. Build the role-gated system prompt
    system_prompt = get_system_prompt(user_role, rag_context, session_history)

    # 4. Get the subset of tools authorized for this user's role
    allowed_tools = get_role_tools(user_role)

    # 5. Instantiate the ADK LlmAgent pydantic model
    # We configure:
    # - name: required unique Python identifier
    # - instruction: the system prompt containing instructions, history and RAG context
    # - tools: authorized tools for this user's role
    # - before_tool_callback: intercepts execution to run validation checks
    agent = Agent(
        name="ZoomBot",
        instruction=system_prompt,
        tools=allowed_tools,
        before_tool_callback=make_before_tool_callback(user_role),
    )

    # 6. Initialize the ADK Runner
    # We wrap our agent and configure the in-memory session service.
    # The runner manages execution turns and persists events/history internally.
    runner = Runner(
        agent=agent,
        app_name=f"zoom-scheduler-agent-{user_id}",
        session_service=_session_service,
        auto_create_session=True,
    )

    # Use the LoopGuard to monitor execution iterations and timeouts
    loop_guard = LoopGuard()
    full_response_text = ""

    # Construct the user message Content object for the Gemini API
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)]
    )

    try:
        # Execute the agent turn asynchronously
        # user_id is the user's UUID, session_id is user_id to ensure one session per logged in user.
        async for event in runner.run_async(
            user_id=user_id,
            session_id=user_id,
            new_message=user_content
        ):
            # Check loop guardrails on every step/event
            tool_name = None
            if event.get_function_calls():
                tool_name = event.get_function_calls()[0].name
            loop_guard.check_iteration(tool_name)

            # If the event contains content, stream it out
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        # 7. Apply Output Guardrails (Redact host Zoom URLs for students, secret scrubbing)
                        sanitized_token = run_output_guardrails(part.text, user_role)
                        full_response_text += sanitized_token
                        yield sanitized_token

    except ToolGuardException as tge:
        yield f"\n[Action Blocked]: {str(tge)}"
        full_response_text += f"\n[Action Blocked]: {str(tge)}"
    except LoopGuardException as lge:
        yield f"\n[System Limit]: {str(lge)}"
        full_response_text += f"\n[System Limit]: {str(lge)}"
    except Exception as e:
        logger.error(f"Error during agent turn: {e}", exc_info=True)
        yield f"\nAn error occurred while processing your request: {str(e)}"
        full_response_text += f"\nAn error occurred: {str(e)}"
    finally:
        # Save response to history
        if full_response_text:
            add_message(user_id, "agent", full_response_text)
            
            # 8. Async learning layer (Index Q&A pair to ChromaDB for future queries)
            try:
                from .rag.indexer import index_qa_pair
                await index_qa_pair(message, full_response_text, user_role)
            except Exception as le:
                logger.warning(f"Failed to save Q&A pair for learning: {le}")
