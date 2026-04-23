"""Per-platform meta-tool factory for dynamic tool mode.

Every platform exposes exactly three tools when ``MCP_TOOL_MODE=dynamic``:

* ``<platform>_list_tools(filter, category)`` — names + summaries for every
  tool the platform has registered (minus anything currently write-gated).
* ``<platform>_get_tool_schema(name)`` — full parameter schema, pulled from
  the FastMCP instance so we don't duplicate Pydantic's schema generation.
* ``<platform>_invoke_tool(name, params)`` — validates and dispatches.

Write gating, elicitation, and error shapes match the direct-call path
exactly; only the invocation surface changes.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from loguru import logger
from mcp.types import ToolAnnotations

from hpe_networking_mcp.platforms._common.tool_registry import (
    REGISTRIES,
    ToolSpec,
    is_tool_enabled,
)

_META_ANNOTATIONS_READONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)

# ``<platform>_invoke_tool`` dispatches to any registered tool, including
# destructive ones, so advertise that it can do anything.
_META_ANNOTATIONS_INVOKE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


def _tool_summary(spec: ToolSpec, max_len: int = 200) -> str:
    """Extract a short, model-friendly summary from a tool's description."""
    desc = (spec.description or "").strip()
    if not desc:
        return ""
    # Take the first non-empty paragraph, trim to max_len
    first_para = desc.split("\n\n", 1)[0].strip()
    if len(first_para) > max_len:
        return first_para[: max_len - 1].rstrip() + "…"
    return first_para


def build_meta_tools(platform: str, mcp: FastMCP) -> None:
    """Register the three meta-tools for a platform on the FastMCP server.

    Called from each platform's ``register_tools`` when ``tool_mode`` is
    ``"dynamic"``. The per-platform ``_registry.tool()`` shim has already
    populated ``REGISTRIES[platform]`` with ``ToolSpec`` entries by the time
    this runs.
    """
    if platform not in REGISTRIES:
        raise ValueError(f"Unknown platform: {platform}")

    registry_ref = REGISTRIES[platform]  # reference, not a copy

    # ---- <platform>_list_tools -----------------------------------------

    @mcp.tool(
        name=f"{platform}_list_tools",
        description=(
            f"List every tool registered for the {platform} platform. "
            f"Pass an optional `filter` substring to narrow by name or "
            f"description, and an optional `category` to restrict to one "
            f"module (use this tool with no arguments first to discover "
            f"available categories). Returns an array of "
            f"{{name, category, summary}} records — call "
            f"`{platform}_get_tool_schema(name=...)` next to fetch the "
            f"full parameter schema for any tool you want to invoke."
        ),
        annotations=_META_ANNOTATIONS_READONLY,
        tags={f"{platform}_meta"},
    )
    async def _list_tools(
        ctx: Context,
        filter: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        config = ctx.lifespan_context.get("config")
        substring = (filter or "").lower().strip()
        category_filter = (category or "").strip() or None

        matches: list[dict[str, str]] = []
        for name, spec in registry_ref.items():
            if not is_tool_enabled(spec, config):
                continue
            if category_filter and spec.category != category_filter:
                continue
            if substring:
                haystack = f"{name} {spec.description}".lower()
                if substring not in haystack:
                    continue
            matches.append(
                {
                    "name": name,
                    "category": spec.category,
                    "summary": _tool_summary(spec),
                }
            )

        matches.sort(key=lambda m: (m["category"], m["name"]))
        categories = sorted({spec.category for spec in registry_ref.values() if is_tool_enabled(spec, config)})
        return {
            "platform": platform,
            "total": len(matches),
            "categories": categories,
            "tools": matches,
        }

    # ---- <platform>_get_tool_schema -------------------------------------

    @mcp.tool(
        name=f"{platform}_get_tool_schema",
        description=(
            f"Fetch the full parameter schema for a single {platform} tool. "
            f"Use `{platform}_list_tools` first to find the tool name you "
            f"want to call, then call this to get the parameter types, "
            f"descriptions, required/optional markers, and enums. The "
            f"returned `input_schema` is the JSON schema that "
            f"`{platform}_invoke_tool` will validate `params` against."
        ),
        annotations=_META_ANNOTATIONS_READONLY,
        tags={f"{platform}_meta"},
    )
    async def _get_tool_schema(
        ctx: Context,
        name: str,
    ) -> dict[str, Any]:
        spec = registry_ref.get(name)
        if spec is None:
            return {
                "status": "not_found",
                "message": f"{platform} has no tool named {name!r}.",
                "hint": f"Call {platform}_list_tools to see available tools.",
            }
        config = ctx.lifespan_context.get("config")
        if not is_tool_enabled(spec, config):
            return {
                "status": "forbidden",
                "message": (
                    f"Tool {name!r} is a write tool and writes are disabled for {platform}. "
                    f"Set ENABLE_{platform.upper()}_WRITE_TOOLS=true to expose it."
                ),
            }

        try:
            fm_tool = await mcp.get_tool(name)
        except Exception as exc:
            logger.warning(
                "{}_get_tool_schema: failed to resolve tool {!r} from FastMCP — {}",
                platform,
                name,
                exc,
            )
            return {
                "status": "error",
                "message": f"Could not resolve tool schema: {exc}",
            }

        input_schema = getattr(fm_tool, "parameters", None) or getattr(fm_tool, "input_schema", None)
        annotations = getattr(fm_tool, "annotations", None)
        return {
            "status": "ok",
            "name": name,
            "category": spec.category,
            "description": spec.description,
            "tags": sorted(spec.tags),
            "annotations": _annotations_to_dict(annotations),
            "input_schema": input_schema,
        }

    # ---- <platform>_invoke_tool -----------------------------------------

    @mcp.tool(
        name=f"{platform}_invoke_tool",
        description=(
            f"Invoke any registered {platform} tool by name with a `params` "
            f"dict matching the schema from `{platform}_get_tool_schema`. "
            f"Destructive tools still prompt for user confirmation via "
            f"elicitation — the confirmation path is identical to calling "
            f"the tool directly in static mode."
        ),
        annotations=_META_ANNOTATIONS_INVOKE,
        tags={f"{platform}_meta"},
    )
    async def _invoke_tool(
        ctx: Context,
        name: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        spec = registry_ref.get(name)
        if spec is None:
            return {
                "status": "not_found",
                "message": f"{platform} has no tool named {name!r}.",
                "hint": f"Call {platform}_list_tools to see available tools.",
            }
        config = ctx.lifespan_context.get("config")
        if not is_tool_enabled(spec, config):
            return {
                "status": "forbidden",
                "message": (
                    f"Tool {name!r} is a write tool and writes are disabled for {platform}. "
                    f"Set ENABLE_{platform.upper()}_WRITE_TOOLS=true to expose it."
                ),
            }

        safe_params = params or {}
        logger.info(
            "{}_invoke_tool: dispatching {} with {} param(s)",
            platform,
            name,
            len(safe_params),
        )
        try:
            return await spec.func(ctx, **safe_params)
        except TypeError as exc:
            # Usually "unexpected keyword argument" — the caller sent a
            # param that the tool doesn't accept. Mirror the shape
            # Pydantic-validation errors use so clients can handle them
            # uniformly.
            return {
                "status": "invalid_params",
                "message": str(exc),
                "hint": f"Call {platform}_get_tool_schema(name={name!r}) for the exact parameter shape.",
            }

    logger.info("{}: registered 3 meta-tools (dynamic mode)", platform)


def _annotations_to_dict(annotations: Any) -> dict[str, Any]:
    """Best-effort serialization of FastMCP tool annotations."""
    if annotations is None:
        return {}
    if hasattr(annotations, "model_dump"):
        try:
            return annotations.model_dump(exclude_none=True)
        except Exception:
            pass
    if hasattr(annotations, "__dict__"):
        return {k: v for k, v in annotations.__dict__.items() if v is not None}
    return {}
