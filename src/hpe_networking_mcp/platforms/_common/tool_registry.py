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

from fastmcp import FastMCP

from hpe_networking_mcp.platforms._common.annotations import Capability, classify


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
    #: Capability classification (see ``_common.annotations``). The searchable
    #: governance facet — ``None`` for tools not yet migrated to ``capability=``.
    capability: Capability | None = None


# One dict per platform, keyed by tool name. Populated by each platform's
# ``tool()`` shim when tool modules import.
REGISTRIES: dict[str, dict[str, ToolSpec]] = {
    "aos8": {},
    "apstra": {},
    "axis": {},
    "central": {},
    "clearpass": {},
    "edgeconnect": {},
    "greenlake": {},
    "mist": {},
    "uxi": {},
    # Template platform — never registered at runtime, but the registry
    # entry has to exist so test_platform_template can import without
    # ValueError when the example tools are loaded.
    "_template": {},
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
    "aos8": {"aos8_write", "aos8_write_delete"},
    "apstra": {"apstra_write", "apstra_write_delete"},
    "axis": {"axis_write", "axis_write_delete"},
    "central": {"central_write_delete"},
    "clearpass": {"clearpass_write_delete"},
    "edgeconnect": {"edgeconnect_write", "edgeconnect_write_delete"},
    "greenlake": set(),  # GreenLake is read-only today.
    "mist": {"mist_write", "mist_write_delete"},
    "uxi": {"uxi_write", "uxi_write_delete"},
    "_template": {"_template_write", "_template_write_delete"},
}

_GATE_CONFIG_ATTR: dict[str, str | None] = {
    "aos8": "enable_aos8_write_tools",
    "apstra": "enable_apstra_write_tools",
    "axis": "enable_axis_write_tools",
    "central": "enable_central_write_tools",
    "clearpass": "enable_clearpass_write_tools",
    "greenlake": None,
    "mist": "enable_mist_write_tools",
    "uxi": "enable_uxi_write_tools",
    "_template": None,  # Never instantiated at runtime; gating attr unused.
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


def _derive_category(func: Callable[..., Any]) -> str:
    """Short module name as the registry category (e.g. ``connectors``)."""
    module = getattr(func, "__module__", "")
    return module.rsplit(".", 1)[-1] if "." in module else module


def make_tool_decorator(
    platform: str,
    get_mcp: Callable[[], FastMCP | None],
) -> Callable[..., Callable[[Callable[..., Any]], Callable[..., Any]]]:
    """Build a platform's ``@tool`` decorator — the single shared shim.

    Every platform's ``_registry.py`` is just::

        mcp: FastMCP = None
        tool = make_tool_decorator("<platform>", lambda: mcp)

    The decorator records a :class:`ToolSpec` and (once ``mcp`` is wired)
    delegates to ``mcp.tool(...)``, merging ``dynamic_managed`` + the platform
    tag so the dynamic-mode Visibility transform can hide the individual tools.

    Classification — preferred::

        @tool(name="axis_get_users", capability=Capability.READ)
        @tool(name="axis_manage_user", capability=Capability.WRITE_DELETE)
        @tool(name="central_clear_alerts", capability=Capability.OPERATIONAL, gated=False)

    ``capability=`` derives the MCP annotations, the ``<platform>_write[_delete]``
    enable tag, and the ``requires_confirmation`` gate tag from one source
    (see ``_common.annotations``). ``gated=`` overrides the confirmation
    default; ``enable_gated=True`` keeps a destructive OPERATIONAL tool behind
    the write flag. ``tags=`` is for functional/discovery tags only.

    Legacy path: tools not yet migrated may still pass ``annotations=`` and
    governance ``tags=`` directly; those flow through unchanged with
    ``capability`` recorded as ``None``.

    Args:
        platform: Platform key (e.g. ``"axis"``).
        get_mcp: Zero-arg callable returning the live FastMCP holder (a
            ``lambda: mcp`` over the platform module's global, so it reads the
            value set by ``register_tools()`` at decoration time).
    """

    def tool(**tool_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            capability = tool_kwargs.pop("capability", None)
            gated = tool_kwargs.pop("gated", None)
            enable_gated = tool_kwargs.pop("enable_gated", False)
            functional_tags: set[str] = set(tool_kwargs.get("tags") or set())
            resolved_name: str = tool_kwargs.get("name") or func.__name__
            resolved_description: str = tool_kwargs.get("description") or func.__doc__ or ""

            if capability is not None:
                derived = classify(
                    capability,
                    platform=platform,
                    gated=gated,
                    enable_gated=enable_gated,
                    extra_tags=functional_tags,
                )
                tool_kwargs["annotations"] = derived.annotations
                resolved_tags = derived.tags
                resolved_capability: Capability | None = derived.capability
            else:
                resolved_tags = functional_tags
                resolved_capability = None

            record_tool(
                ToolSpec(
                    name=resolved_name,
                    func=func,
                    platform=platform,
                    category=_derive_category(func),
                    description=resolved_description,
                    tags=resolved_tags,
                    capability=resolved_capability,
                )
            )

            mcp = get_mcp()
            if mcp is None:
                # register_tools() not yet called — import during test
                # collection before the platform is wired. Leaving the
                # function undecorated is fine.
                return func

            effective_kwargs = {**tool_kwargs, "tags": resolved_tags | {DYNAMIC_MANAGED_TAG, platform}}
            return mcp.tool(**effective_kwargs)(func)

        return decorator

    return tool
