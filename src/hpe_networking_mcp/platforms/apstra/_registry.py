"""Apstra tool registry -- module-level FastMCP holder + shared-registry shim.

Tool modules under ``platforms/apstra/tools/`` decorate their functions with
``@tool(...)`` (imported from here) instead of directly with ``@mcp.tool(...)``.
The shim:

1. Delegates to the underlying FastMCP ``mcp.tool(...)`` so the tool is
   registered with the server the same way it was pre-v2.
2. Merges the ``dynamic_managed`` tag onto every registered tool so the
   ``Visibility(False, tags={"dynamic_managed"})`` transform can hide all
   these tools when ``MCP_TOOL_MODE=dynamic``.
3. Populates ``REGISTRIES["apstra"]`` so the three Apstra meta-tools can
   dispatch by name at runtime.

Both modes work from the same decorator — no per-mode branching in tool files.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastmcp import FastMCP

from hpe_networking_mcp.platforms._common.tool_registry import (
    DYNAMIC_MANAGED_TAG,
    ToolSpec,
    record_tool,
)

# Set by platforms.apstra.register_tools() before tool modules are imported.
mcp: FastMCP = None  # type: ignore[assignment]

_PLATFORM = "apstra"


def _derive_category(func: Callable[..., Any]) -> str:
    """Short module name as the registry category (e.g. ``manage_networks``)."""
    module = getattr(func, "__module__", "")
    return module.rsplit(".", 1)[-1] if "." in module else module


def tool(**tool_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Drop-in replacement for ``@mcp.tool(...)`` that also populates the registry.

    Accepts every keyword ``FastMCP.tool`` accepts — forwards them unchanged
    except for ``tags``, which gets ``dynamic_managed`` merged in so the
    Visibility transform in ``server.py`` can hide these tools when the
    server is running in dynamic mode.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        supplied_tags: set[str] = set(tool_kwargs.get("tags") or set())
        resolved_name: str = tool_kwargs.get("name") or func.__name__
        resolved_description: str = tool_kwargs.get("description") or func.__doc__ or ""

        record_tool(
            ToolSpec(
                name=resolved_name,
                func=func,
                platform=_PLATFORM,
                category=_derive_category(func),
                description=resolved_description,
                tags=supplied_tags,
            )
        )

        if mcp is None:
            # register_tools() not yet called — likely an import during test
            # collection before the platform is wired. Leaving the function
            # undecorated is fine: tests that need FastMCP registration set
            # up a real mcp before import (see tests/conftest.py stubs).
            return func

        effective_kwargs = {**tool_kwargs, "tags": supplied_tags | {DYNAMIC_MANAGED_TAG}}
        return mcp.tool(**effective_kwargs)(func)

    return decorator
