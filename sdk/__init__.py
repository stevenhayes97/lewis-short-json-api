"""Named wrappers around the Cursor Agent SDK.

Call :func:`invoke_agent` from anywhere in Python; the TypeScript twin is
``invokeAgent`` in ``sdk/invokeAgent.ts``.
"""

from sdk.cursor_agents import (
    AgentSpec,
    InvokeResult,
    UnknownAgentError,
    close_agent,
    close_all_agents,
    get_agent,
    invoke_agent,
    list_registered_agents,
    register_agent,
    registered_agent,
    reset_agents,
)

__all__ = [
    "AgentSpec",
    "InvokeResult",
    "UnknownAgentError",
    "close_agent",
    "close_all_agents",
    "get_agent",
    "invoke_agent",
    "list_registered_agents",
    "register_agent",
    "registered_agent",
    "reset_agents",
]
