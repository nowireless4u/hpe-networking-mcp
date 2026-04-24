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

import inspect
from typing import Any, get_args, get_origin, get_type_hints

from fastmcp import Context, FastMCP
from loguru import logger
from mcp.types import ToolAnnotations
from pydantic import ConfigDict, ValidationError, create_model
from pydantic.fields import FieldInfo

from hpe_networking_mcp.platforms._common.tool_registry import (
    REGISTRIES,
    ToolSpec,
    is_tool_enabled,
)

# Parameter names we strip from the Pydantic validation model because
# ``_invoke_tool`` injects them itself.
_CTX_PARAM_NAMES = frozenset({"ctx", "context"})


def _extract_annotated_default(annotation: Any) -> Any:
    """Return a Pydantic-usable default from ``Annotated[T, Field(default=X)]``.

    Many Mist tool signatures use ``Annotated[UUID, Field(default=None)]``
    where the function signature itself has no default — the default lives
    inside the ``Field(...)`` metadata. When ``inspect.Parameter.default``
    is empty, we look into the ``Annotated`` metadata for a ``FieldInfo``
    that carries a default and surface it. Returns ``Ellipsis`` (Pydantic's
    "required" marker) if no default is found.
    """
    if get_origin(annotation) is not None and hasattr(annotation, "__metadata__"):
        for meta in getattr(annotation, "__metadata__", ()):
            if isinstance(meta, FieldInfo):
                default = meta.default
                # ``FieldInfo.default`` uses ``PydanticUndefined`` for
                # required fields; only surface concrete defaults.
                if default is not None and str(type(default).__name__) == "PydanticUndefinedType":
                    continue
                return default
    # Also handle the raw generic form ``Annotated[T, ...]`` where
    # ``__metadata__`` isn't attached directly.
    args = get_args(annotation)
    for meta in args[1:] if len(args) > 1 else ():
        if isinstance(meta, FieldInfo):
            default = meta.default
            if default is not None and str(type(default).__name__) == "PydanticUndefinedType":
                continue
            return default
    return ...


def _coerce_params(spec: ToolSpec, raw_params: dict[str, Any]) -> dict[str, Any]:
    """Build a Pydantic model from the tool signature and validate/coerce.

    FastMCP's normal dispatch path (``tools/call`` → ``@mcp.tool`` wrapper)
    applies Pydantic validation to incoming arguments, converting strings
    into ``Enum`` instances, ``UUID`` objects, etc. The meta-tool
    dispatch in ``_invoke_tool`` calls ``spec.func`` directly, bypassing
    that wrapper — so we have to replicate the coercion step here. Without
    it, tools doing ``my_enum_param.value`` hit
    ``AttributeError: 'str' object has no attribute 'value'``.

    Returns a new dict of coerced parameter values. Raises
    ``ValidationError`` if the params don't match the signature (missing
    required params, unknown keys, or type-coercion failures).
    """
    sig = inspect.signature(spec.func)
    # ``from __future__ import annotations`` in tool modules leaves
    # ``inspect.signature()`` annotations as strings. Pydantic can't
    # evaluate those strings without a matching namespace. Resolve
    # eagerly with ``get_type_hints`` using the function's own globals
    # + localns so ``Annotated``, ``UUID``, enums defined beside the
    # tool, etc. all resolve correctly.
    try:
        resolved_hints = get_type_hints(spec.func, include_extras=True)
    except Exception:
        resolved_hints = {}

    fields: dict[str, Any] = {}
    for pname, param in sig.parameters.items():
        if pname in _CTX_PARAM_NAMES:
            continue
        # Skip variadic parameters (``*args`` / ``**kwargs``). Pydantic
        # can't build a field from them; real tools almost never use this
        # shape, but ``AsyncMock()`` stubs in tests do — and a runtime
        # crash there is worse than no coercion.
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        annotation = resolved_hints.get(pname, param.annotation)
        if annotation is inspect.Parameter.empty:
            annotation = Any
        if param.default is not inspect.Parameter.empty:
            fields[pname] = (annotation, param.default)
        else:
            # Signature has no default; fall back to any default baked
            # into the ``Annotated`` FieldInfo. Returns ``...`` (required)
            # if none is found.
            fields[pname] = (annotation, _extract_annotated_default(annotation))

    if not fields:
        # Signature has no validatable params — nothing to coerce. Hand
        # the raw dict back so ``spec.func(**raw_params)`` still works.
        return dict(raw_params)

    # AI clients often pass explicit ``null`` for optional params that
    # should just fall through to the default. Mist tool signatures
    # commonly use ``Annotated[UUID, Field(default=None)]`` (default=None
    # without typing the field as Optional), so Pydantic rejects
    # ``{"site_id": None}``. Strip explicit-None entries so Pydantic
    # uses the declared default instead. Required params will still be
    # flagged as missing by the validator below.
    cleaned = {k: v for k, v in raw_params.items() if v is not None}

    model_cls = create_model(
        f"{spec.name}__Params",
        __config__=ConfigDict(arbitrary_types_allowed=True, extra="forbid"),
        **fields,
    )
    validated = model_cls.model_validate(cleaned)
    # Use attribute access so we get the Pydantic-coerced Python objects
    # (``Enum`` instances, ``UUID``, etc.) rather than the serialized form
    # that ``model_dump()`` produces.
    return {pname: getattr(validated, pname) for pname in fields}


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


def _resolve_type_name(pdef: dict[str, Any]) -> str:
    """Extract a concise type name from a JSON schema property definition.

    Used by ``_param_summary`` to produce a one-word type hint per
    parameter for the ``list_tools`` output. Output is designed for
    AI-consumption, not strict correctness — e.g. ``UUID | None`` is
    shown as ``UUID`` since the null branch is already communicated
    via the ``?`` suffix in the caller.
    """
    # Enum types and nested models are referenced via $ref.
    if "$ref" in pdef:
        return pdef["$ref"].rsplit("/", 1)[-1]
    # Common format hints get short names.
    fmt = pdef.get("format")
    if fmt == "uuid":
        return "UUID"
    if fmt == "date-time":
        return "datetime"
    if fmt:
        return fmt
    # Union types: pick the first non-null branch.
    for key in ("anyOf", "oneOf"):
        options = pdef.get(key)
        if isinstance(options, list):
            for option in options:
                if isinstance(option, dict) and option.get("type") != "null":
                    return _resolve_type_name(option)
            return "any"
    # Array types: include the item type when it's obvious.
    if pdef.get("type") == "array":
        items = pdef.get("items") or {}
        if isinstance(items, dict) and items:
            return f"list[{_resolve_type_name(items)}]"
        return "list"
    # Fall back to the raw JSON schema type name.
    return pdef.get("type", "any")


def _param_summary(fm_tool: Any) -> dict[str, str]:
    """Return a compact ``{name: "Type[?]"}`` map for a tool's params.

    Extracted from FastMCP's parsed JSON schema. Included in the
    ``<platform>_list_tools`` response so AI clients can skip a
    ``<platform>_get_tool_schema`` round-trip for simple tools where
    knowing the parameter names and their rough types is enough to
    compose a valid invoke call. For anything more detailed (full
    descriptions, enum value lists, nested object shapes), the AI
    should still call ``get_tool_schema``.

    Convention: ``"?"`` suffix means optional (has a default or is
    excluded from the schema's ``required`` list). No suffix means
    required.
    """
    if fm_tool is None:
        return {}
    schema = getattr(fm_tool, "parameters", None) or getattr(fm_tool, "input_schema", None)
    if not isinstance(schema, dict):
        return {}
    props = schema.get("properties") or {}
    if not isinstance(props, dict):
        return {}
    required_set = set(schema.get("required") or [])

    result: dict[str, str] = {}
    for pname, pdef in props.items():
        if not isinstance(pdef, dict):
            continue
        type_name = _resolve_type_name(pdef)
        if pname not in required_set:
            type_name = f"{type_name}?"
        result[pname] = type_name
    return result


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
            f"`{{name, category, summary, params}}` records. The `params` "
            f"field is a compact `{{name: 'Type[?]'}}` map — `?` suffix "
            f"means optional, no suffix means required. For simple tools "
            f"where the parameter names + types are enough to compose an "
            f"invoke, you can skip straight to `{platform}_invoke_tool`. "
            f"For full parameter descriptions, enum value lists, or nested "
            f"object shapes, call `{platform}_get_tool_schema(name=...)`."
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

        matches: list[dict[str, Any]] = []
        for name, spec in registry_ref.items():
            if not is_tool_enabled(spec, config):
                continue
            if category_filter and spec.category != category_filter:
                continue
            if substring:
                haystack = f"{name} {spec.description}".lower()
                if substring not in haystack:
                    continue
            # Use the private ``_get_tool`` to bypass the Visibility
            # filter — hidden tools need their schema inspected here.
            fm_tool = await mcp._get_tool(name)
            matches.append(
                {
                    "name": name,
                    "category": spec.category,
                    "summary": _tool_summary(spec),
                    "params": _param_summary(fm_tool),
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

        # Use ``_get_tool`` (underscore prefix) instead of ``get_tool``:
        # the public ``get_tool`` applies the Visibility filter and returns
        # ``None`` for tools hidden by the dynamic-mode transform, which
        # includes every tool in the registry. ``_get_tool`` bypasses the
        # filter so we can actually fetch the schema.
        try:
            fm_tool = await mcp._get_tool(name)
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

        # Replicate the Pydantic coercion FastMCP would do on a direct
        # tool call: turn string enum values into ``Enum`` instances,
        # strings into ``UUID`` objects, etc. Without this, any tool that
        # does ``enum_param.value`` blows up with ``'str' object has no
        # attribute 'value'`` because the meta-tool bypasses FastMCP's
        # normal dispatch wrapper.
        try:
            coerced = _coerce_params(spec, safe_params)
        except ValidationError as exc:
            return {
                "status": "invalid_params",
                "message": str(exc),
                "hint": f"Call {platform}_get_tool_schema(name={name!r}) for the exact parameter shape.",
            }

        try:
            return await spec.func(ctx, **coerced)
        except TypeError as exc:
            # Residual TypeError after validation — typically a signature
            # issue (missing ctx param on the tool, or a mismatch between
            # the signature and the registered call shape).
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
