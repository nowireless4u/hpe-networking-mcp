"""Per-platform tool registry for dynamic tool mode.

Populated as a side effect of each tool module's import — the ``tool()``
decorator in each platform's ``_registry.py`` wraps ``@mcp.tool(...)`` so
the function is both registered with the FastMCP instance (for static mode)
and recorded here (for dynamic mode's meta-tool dispatch).

Write-gating is honored uniformly via ``is_tool_enabled``: ``list_tools``
filters gated tools out of its results and ``invoke_tool`` refuses them
with a 403-shaped response.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolSpec:
    """Everything the meta-tools need to know about one registered tool.

    The FastMCP instance holds the full JSON schema — we retrieve it at
    invocation time via ``mcp.get_tool(name)`` rather than duplicating the
    schema extraction here.
    """

    name: str
    func: Callable[..., Any]
    platform: str
    category: str
    description: str = ""
    tags: set[str] = field(default_factory=set)


# One dict per platform, keyed by tool name. Populated by each platform's
# ``tool()`` shim when tool modules import.
REGISTRIES: dict[str, dict[str, ToolSpec]] = {
    "apstra": {},
    "central": {},
    "clearpass": {},
    "greenlake": {},
    "mist": {},
}


# Tag indicating "this tool is registered as individual FastMCP tool AND is
# discoverable via the platform's list_tools meta-tool." In dynamic mode a
# Visibility transform uses this tag to hide the individual tools from the
# model's tool list, leaving only the three meta-tools exposed.
DYNAMIC_MANAGED_TAG = "dynamic_managed"


# Maps each platform to its write-tool tags. When a tool carries one of
# these tags and the corresponding ENABLE_X_WRITE_TOOLS flag is false,
# the tool is invisible to ``list_tools`` and refused by ``invoke_tool``.
_WRITE_TAG_BY_PLATFORM: dict[str, set[str]] = {
    "apstra": {"apstra_write", "apstra_write_delete"},
    "central": {"central_write_delete"},
    "clearpass": {"clearpass_write_delete"},
    "greenlake": set(),  # GreenLake is read-only today.
    "mist": {"mist_write", "mist_write_delete"},
}

_GATE_CONFIG_ATTR: dict[str, str | None] = {
    "apstra": "enable_apstra_write_tools",
    "central": "enable_central_write_tools",
    "clearpass": "enable_clearpass_write_tools",
    "greenlake": None,
    "mist": "enable_mist_write_tools",
}


def record_tool(spec: ToolSpec) -> None:
    """Register a tool into the platform-scoped registry (idempotent)."""
    if spec.platform not in REGISTRIES:
        raise ValueError(f"Unknown platform: {spec.platform}")
    REGISTRIES[spec.platform][spec.name] = spec


def clear_registry(platform: str | None = None) -> None:
    """Clear one or all platform registries. Used by tests.

    Without an argument, clears every platform — useful when a test needs
    a clean slate because two prior tests both populated the same registry.
    """
    if platform is None:
        for reg in REGISTRIES.values():
            reg.clear()
        return
    if platform not in REGISTRIES:
        raise ValueError(f"Unknown platform: {platform}")
    REGISTRIES[platform].clear()


def is_tool_enabled(spec: ToolSpec, config: Any) -> bool:
    """Decide whether a tool is currently callable given the server config.

    Args:
        spec: The tool's registry entry.
        config: A ``ServerConfig`` (or any object exposing the
            ``enable_<platform>_write_tools`` attribute).

    Returns:
        ``True`` if the tool is reachable right now. Read-only tools always
        return ``True``. Write tools return ``True`` only when their
        platform's write-enable flag is truthy.
    """
    write_tags = _WRITE_TAG_BY_PLATFORM.get(spec.platform, set())
    if not (spec.tags & write_tags):
        return True
    gate_attr = _GATE_CONFIG_ATTR.get(spec.platform)
    if gate_attr is None:
        return True
    return bool(getattr(config, gate_attr, False))
