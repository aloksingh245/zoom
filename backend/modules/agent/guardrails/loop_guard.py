"""
loop_guard.py — Prevents the agent from entering infinite reasoning loops.

WHY DO WE NEED A LOOP GUARD?
  When agents use tools, they can sometimes enter loops:
  - Tool returns an error → Agent tries to fix arguments → Calls it again → Fails → Loop.
  - Agent gets confused and calls the same read tool (e.g., get_all_classes) repeatedly.

This guard monitors loop iterations and aborts execution if bounds are exceeded,
returning what has been accomplished so far.
"""

import time
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Hard limits for loop execution
MAX_ITERATIONS = 5
MAX_EXECUTION_TIME_SECONDS = 30.0

class LoopGuardException(Exception):
    """Exception raised when execution loops or timeouts occur."""
    pass

class LoopGuard:
    def __init__(self) -> None:
        self.start_time = time.time()
        self.iterations = 0
        self.called_tools: list[str] = []

    def check_iteration(self, latest_tool_call: str | None = None) -> None:
        """
        Increment and check execution bounds.
        Should be called inside the agent loop at the start of each iteration.
        """
        self.iterations += 1

        # 1. Check max iterations
        if self.iterations > MAX_ITERATIONS:
            logger.error(f"Agent exceeded maximum loop iterations ({MAX_ITERATIONS}). Aborting.")
            raise LoopGuardException(
                f"Agent exceeded execution loop limit of {MAX_ITERATIONS} turns."
            )

        # 2. Check total elapsed time
        elapsed = time.time() - self.start_time
        if elapsed > MAX_EXECUTION_TIME_SECONDS:
            logger.error(f"Agent execution timed out after {elapsed:.2f} seconds.")
            raise LoopGuardException(
                f"Agent request timed out. Maximum time of {MAX_EXECUTION_TIME_SECONDS}s exceeded."
            )

        # 3. Detect repetitive tool calls
        if latest_tool_call:
            self.called_tools.append(latest_tool_call)
            # If the same tool has been called 3 times in a row, block it
            if len(self.called_tools) >= 3 and len(set(self.called_tools[-3:])) == 1:
                logger.error(f"Repetitive tool execution loop detected for '{latest_tool_call}'.")
                raise LoopGuardException(
                    f"Agent entered an infinite loop calling '{latest_tool_call}' repeatedly. Execution aborted."
                )
