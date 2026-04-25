"""Central tool registry -- module-level FastMCP holder + shared-registry shim.

Tool modules under ``platforms/central/tools/`` decorate their functions with
``@tool(...)`` (imported from here) instead of directly with ``@mcp.tool(...)``.
The shim mirrors the Apstra and Mist patterns: delegate to the real FastMCP
decorator, merge the ``dynamic_managed`` tag so dynamic-mode ``Visibility`` can
hide individual tools, and record a ``ToolSpec`` into ``REGISTRIES["central"]``
so the three Central meta-tools can dispatch by name at runtime.
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

# Set by platforms.central.register_tools() before tool modules are imported.
mcp: FastMCP = None  # type: ignore[assignment]

_PLATFORM = "central"


def _derive_category(func: Callable[..., Any]) -> str:
    """Short module name as the registry category (e.g. ``sites``)."""
    module = getattr(func, "__module__", "")
    return module.rsplit(".", 1)[-1] if "." in module else module


def tool(**tool_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Drop-in replacement for ``@mcp.tool(...)`` that also populates the registry."""

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
            return func

        effective_kwargs = {**tool_kwargs, "tags": supplied_tags | {DYNAMIC_MANAGED_TAG, _PLATFORM}}
        return mcp.tool(**effective_kwargs)(func)

    return decorator
