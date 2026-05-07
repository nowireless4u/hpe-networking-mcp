"""Runtime engine — turns a Translation + source data into ordered API calls.

The engine takes a validated ``Translation`` (from the loader), a source-
side dict produced by extracting/merging the source-platform objects, and
a generic ``runtime_values`` dict carrying target-platform-specific runtime
context (e.g. for Central: ``central_scope_id``, ``device_functions``; for
future Mist: ``mist_org_id``, ``mist_site_id``). Returns an ordered list of
``TargetCall`` descriptors.

The engine **does not** dispatch calls. The consuming skill (aos-migration
Phase 3 / issue #240, future WLAN-sync skill, etc.) iterates the descriptors
and invokes the appropriate platform's write tools with elicitation gating.

Iteration patterns recognized by v1:

* ``once_per_named_vlan`` — single call, no fan-out
* ``per_vlan_id_in_binding`` — one call per discrete VLAN ID (range expansion
  handled by ``expand_vlan_id_csv``)
* ``per_device_function`` — one call per device function in
  ``runtime_values["device_functions"]`` (or ``target_meta.device_functions``
  if not overridden)
* ``per_vlan_id_per_device_function`` — Cartesian product

Body-level array iteration (used by the multi-device-function
``config-assignments`` POSTs in steps 4 + 5 of the named-vlan translation)
is expressed via ``body_template`` — the engine recognizes a small set of
template patterns. As more translations show up, new patterns get added
here in clearly-marked branches.

Future-pattern policy: the engine raises ``EngineError`` on unknown
iteration rules or unknown ``body_template`` shapes rather than silently
producing wrong calls. Failures should be loud at integration-test time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from hpe_networking_mcp.translations.loader import KeyMapping, TargetEmit, Translation
from hpe_networking_mcp.translations.transforms import expand_vlan_id_csv, get_transform


class EngineError(RuntimeError):
    """Raised when the engine cannot produce calls from a translation/source pair."""


@dataclass
class TargetCall:
    """One target-platform API call, ready to dispatch.

    The engine produces these in dependency order; the caller dispatches
    them one at a time and records results. Idempotency strategy lives in
    the caller, not here (per the engine's pure-data contract).
    """

    step: int
    step_name: str
    endpoint: str
    method: str
    query_params: dict[str, str]
    body: dict[str, Any] | None
    depends_on_step: list[int]
    purpose: str
    iteration_context: dict[str, Any] = field(default_factory=dict)


def emit_calls(
    translation: Translation,
    source_data: dict[str, Any],
    source_platform_id: str,
    runtime_values: dict[str, Any] | None = None,
    overrides: dict[str, Any] | None = None,
) -> list[TargetCall]:
    """Walk the translation's emits and produce ordered target API call descriptors.

    Args:
        translation: A validated Translation from ``loader.load_translations``.
        source_data: Merged source-side dict. Shape depends on
            ``translation.sources[source_platform_id]``.
        source_platform_id: Which ``translation.sources[X]`` block to consume.
            Raises if the translation doesn't declare this source.
        runtime_values: Generic dict of target-platform-specific runtime context
            keyed by name (e.g. ``{"central_scope_id": "...", "device_functions": [...]}``).
            The translation's ``required_runtime_values`` declares which keys
            must be present. May also override ``target_meta.device_functions``
            via the ``device_functions`` key.
        overrides: Per-session operator overrides for derived values
            (e.g. ``{"alias_name": "custom-name"}``).

    Returns:
        List of ``TargetCall`` descriptors in dependency order. Caller
        dispatches each one to the target platform.

    Raises:
        EngineError: On unknown source platform, missing required runtime
            values, malformed source data, unknown iteration rules, unknown
            body_template shapes, or transform errors.
    """
    if source_platform_id not in translation.sources:
        raise EngineError(
            f"Translation {translation.target_platform}:{translation.target_id} "
            f"does not declare source {source_platform_id!r}; "
            f"available: {sorted(translation.sources.keys())}"
        )

    runtime_values = runtime_values or {}
    overrides = overrides or {}

    # Validate required runtime keys are present
    missing = [k for k in translation.required_runtime_values if k not in runtime_values]
    if missing:
        raise EngineError(
            f"Translation {translation.target_platform}:{translation.target_id} requires "
            f"runtime_values keys {missing} (got {sorted(runtime_values.keys())})"
        )

    source = translation.sources[source_platform_id]

    # device_functions: either supplied via runtime_values (operator override)
    # or pulled from target_meta. None for non-Central targets that don't use
    # the concept; iteration rules that need it will raise if it's missing.
    device_functions = runtime_values.get("device_functions") or translation.target_meta.device_functions or []

    # Build the substitution context shared by every emit
    base_ctx = _build_base_context(
        translation=translation,
        source_data=source_data,
        source=source,
        runtime_values=runtime_values,
        overrides=overrides,
    )

    # Sort emits by step so depends_on is satisfied naturally
    emits_in_order = sorted(translation.target_emits, key=lambda e: e.step)
    out: list[TargetCall] = []
    for emit in emits_in_order:
        out.extend(_render_emit(emit=emit, base_ctx=base_ctx, device_functions=device_functions))
    return out


# --------------------------------------------------------------------------- #
# Internal: substitution context
# --------------------------------------------------------------------------- #


def _build_base_context(
    *,
    translation: Translation,
    source_data: dict[str, Any],
    source: Any,
    runtime_values: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Build the substitution context shared by every emit.

    Layered build order:
    1. ``runtime_values`` — caller-supplied target-platform-specific context
    2. ``source.key_mappings`` resolved against ``source_data``
    3. ``translation.derived`` — target-only derived values
    4. ``overrides`` — per-session operator overrides

    Per-iteration values like ``{vlan_id}`` and ``{device_function}`` are
    layered on top of this base by ``_render_emit``.
    """
    # Layer 1: runtime values (target-platform-specific)
    ctx: dict[str, Any] = dict(runtime_values)

    # Layer 2: source-side key mappings: source_data["name"] -> ctx["vlan_name"], etc.
    for key, km in source.key_mappings.items():
        if km.from_ is None:
            continue
        try:
            raw = _path_lookup(source_data, km.from_)
        except KeyError:
            # Field absent from source — leave unset; emits that need it
            # will fail at substitution time with a clear error
            continue
        ctx[key] = _apply_transform(km, raw)

    # Layer 3: target-side derived values (e.g. alias_name = lower(vlan_name))
    for key, rule in translation.derived.items():
        if key in overrides:
            ctx[key] = overrides[key]
            continue
        ctx[key] = _resolve_derived(rule_name=rule.rule, key=key, ctx=ctx)

    # Layer 4: any other operator overrides not handled by derived rules
    for key, value in overrides.items():
        if key not in ctx:
            ctx[key] = value

    return ctx


def _apply_transform(km: KeyMapping, raw: Any) -> Any:
    """Apply a key-mapping's named transform to a raw source value."""
    if km.transform == "operator_overridable":
        return raw
    try:
        fn = get_transform(km.transform)
    except KeyError as exc:
        raise EngineError(str(exc)) from exc
    try:
        return fn(raw)
    except Exception as exc:  # noqa: BLE001 — surface any transform error to caller
        raise EngineError(f"Transform {km.transform!r} failed on value {raw!r}: {exc}") from exc


def _resolve_derived(*, rule_name: str, key: str, ctx: dict[str, Any]) -> Any:
    """Resolve a target-side derived value rule.

    Rules are named identifiers (e.g. ``lowercase_of_central_named_vlan_name``)
    that map to small computed transformations. v1 supports the ones we
    need for the named-VLAN translation; new translations add new rules here.
    """
    if rule_name == "lowercase_of_central_named_vlan_name":
        try:
            return str(ctx["vlan_name"]).lower()
        except KeyError as exc:
            raise EngineError(f"Derived rule for {key!r} requires 'vlan_name' in context but it wasn't set") from exc
    raise EngineError(f"Unknown derived rule {rule_name!r} for key {key!r}")


# --------------------------------------------------------------------------- #
# Internal: per-emit rendering
# --------------------------------------------------------------------------- #


def _render_emit(
    *,
    emit: TargetEmit,
    base_ctx: dict[str, Any],
    device_functions: list[str],
) -> list[TargetCall]:
    """Expand one emit's iteration rule into one or more TargetCall objects."""
    iteration = emit.iteration.split()[0]  # ignore parenthesized notes after the keyword

    if iteration == "once_per_named_vlan":
        return [_build_call(emit=emit, ctx=base_ctx, device_functions=device_functions)]

    if iteration == "per_vlan_id_in_binding":
        try:
            csv = base_ctx["vlan_ids"]
        except KeyError as exc:
            raise EngineError(
                f"Emit {emit.name!r} requires 'vlan_ids' in context but no source key_mapping populated it"
            ) from exc
        expanded = expand_vlan_id_csv(",".join(csv) if isinstance(csv, list) else csv)
        return [
            _build_call(
                emit=emit,
                ctx={**base_ctx, "vlan_id": str(vid)},
                device_functions=device_functions,
            )
            for vid in expanded
        ]

    if iteration == "per_device_function":
        if not device_functions:
            raise EngineError(
                f"Emit {emit.name!r} requires 'per_device_function' iteration but no "
                f"device_functions are available (target_meta or runtime_values must supply them)"
            )
        return [
            _build_call(emit=emit, ctx={**base_ctx, "device_function": df}, device_functions=device_functions)
            for df in device_functions
        ]

    if iteration == "per_vlan_id_per_device_function":
        try:
            csv = base_ctx["vlan_ids"]
        except KeyError as exc:
            raise EngineError(
                f"Emit {emit.name!r} requires 'vlan_ids' in context but no source key_mapping populated it"
            ) from exc
        expanded = expand_vlan_id_csv(",".join(csv) if isinstance(csv, list) else csv)
        out = []
        for vid in expanded:
            for df in device_functions:
                out.append(
                    _build_call(
                        emit=emit,
                        ctx={**base_ctx, "vlan_id": str(vid), "device_function": df},
                        device_functions=device_functions,
                    )
                )
        return out

    raise EngineError(f"Unknown iteration rule {emit.iteration!r} on emit {emit.name!r}")


def _build_call(
    *,
    emit: TargetEmit,
    ctx: dict[str, Any],
    device_functions: list[str],
) -> TargetCall:
    """Substitute templates and assemble one TargetCall."""
    endpoint = _substitute_str(emit.endpoint, ctx)
    query_params = {k: _substitute_str(v, ctx) for k, v in emit.query_params.items()}
    body = _render_body(emit=emit, ctx=ctx, device_functions=device_functions)
    return TargetCall(
        step=emit.step,
        step_name=emit.name,
        endpoint=endpoint,
        method=emit.method,
        query_params=query_params,
        body=body,
        depends_on_step=list(emit.depends_on),
        purpose=emit.purpose,
        iteration_context={k: v for k, v in ctx.items() if k in ("vlan_id", "device_function") and k in ctx},
    )


def _render_body(
    *,
    emit: TargetEmit,
    ctx: dict[str, Any],
    device_functions: list[str],
) -> dict[str, Any] | None:
    """Render the emit's body via direct substitution OR body_template patterns."""
    if emit.body is not None:
        return _substitute_in_dict(emit.body, ctx)

    if emit.body_template is None:
        return None

    return _render_body_template(emit=emit, ctx=ctx, device_functions=device_functions)


def _render_body_template(
    *,
    emit: TargetEmit,
    ctx: dict[str, Any],
    device_functions: list[str],
) -> dict[str, Any]:
    """Render a body_template — v1 recognizes the multi-DF config-assignments shape."""
    template = emit.body_template
    if template is None:
        return {}

    # Pattern: { "<key>": [ "<descriptor string>" ] }
    if (
        len(template) == 1
        and isinstance(next(iter(template.values())), list)
        and len(next(iter(template.values()))) == 1
        and isinstance(next(iter(template.values()))[0], str)
    ):
        outer_key = next(iter(template.keys()))
        descriptor = template[outer_key][0]
        if "{one entry per device_function" in descriptor:
            return {
                outer_key: [
                    _config_assignment_item(emit=emit, ctx={**ctx, "device_function": df}) for df in device_functions
                ]
            }

    raise EngineError(
        f"Unrecognized body_template pattern on emit {emit.name!r}; engine needs a new branch in _render_body_template."
    )


def _config_assignment_item(*, emit: TargetEmit, ctx: dict[str, Any]) -> dict[str, str]:
    """Build one config-assignment array item for the multi-DF shape.

    Reads profile-type from the emit's body_template descriptor (the
    ``profile-type='X'`` substring) and profile-instance from the matching
    context key (``vlan_id`` or ``vlan_name``).
    """
    template = emit.body_template
    if template is None:
        raise EngineError(f"Emit {emit.name!r} body_template is unexpectedly None")
    descriptor = next(iter(template.values()))[0]
    m = re.search(r"profile-type='([^']+)'", descriptor)
    if not m:
        raise EngineError(f"Emit {emit.name!r} body_template descriptor missing profile-type clause: {descriptor!r}")
    profile_type = m.group(1)

    inst_match = re.search(r"profile-instance='\{([^}]+)\}'", descriptor)
    if not inst_match:
        raise EngineError(
            f"Emit {emit.name!r} body_template descriptor missing profile-instance placeholder: {descriptor!r}"
        )
    inst_key = inst_match.group(1)
    if inst_key not in ctx:
        raise EngineError(
            f"Emit {emit.name!r} body_template references {{{inst_key}}} "
            f"but it isn't in the context (available: {sorted(ctx.keys())})"
        )

    # scope-id pulled from runtime_values (named central_scope_id by Central convention)
    if "central_scope_id" not in ctx:
        raise EngineError(f"Emit {emit.name!r} config-assignment item requires 'central_scope_id' in context")

    return {
        "scope-id": str(ctx["central_scope_id"]),
        "device-function": str(ctx["device_function"]),
        "profile-type": profile_type,
        "profile-instance": str(ctx[inst_key]),
    }


# --------------------------------------------------------------------------- #
# Internal: utilities
# --------------------------------------------------------------------------- #


_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
_WHOLE_STRING_PLACEHOLDER_RE = re.compile(r"^\{([^{}]+)\}$")


def _substitute_str(value: str, ctx: dict[str, Any]) -> str:
    """Replace ``{key}`` placeholders in a string with values from ``ctx``."""

    def replace(m: re.Match) -> str:
        key = m.group(1)
        if key not in ctx:
            raise EngineError(
                f"Template references {{{key}}} but no value is in the context (available: {sorted(ctx.keys())})"
            )
        return str(ctx[key])

    return _PLACEHOLDER_RE.sub(replace, value)


def _substitute_in_dict(value: Any, ctx: dict[str, Any]) -> Any:
    """Recursively substitute ``{placeholders}`` inside a nested dict/list/str.

    Whole-string placeholders (``"{key}"`` and nothing else) preserve the
    underlying Python type — important when the substituted value is a list
    or dict that needs to land in the body as JSON of that type rather than
    a stringified ``"['107']"``. Mixed-content strings (``"prefix-{key}-suffix"``)
    fall through to plain string substitution.
    """
    if isinstance(value, str):
        m = _WHOLE_STRING_PLACEHOLDER_RE.match(value)
        if m:
            key = m.group(1)
            if key not in ctx:
                raise EngineError(
                    f"Template references {{{key}}} but no value is in the context (available: {sorted(ctx.keys())})"
                )
            return ctx[key]
        return _substitute_str(value, ctx)
    if isinstance(value, dict):
        return {k: _substitute_in_dict(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute_in_dict(item, ctx) for item in value]
    return value


def _path_lookup(data: Any, path: str) -> Any:
    """Walk a dotted path through nested dicts/lists; KeyError on miss."""
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                raise KeyError(f"missing key {part!r} at path {path!r}")
            cur = cur[part]
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError) as exc:
                raise KeyError(f"path {path!r} cannot index list with {part!r}") from exc
        else:
            raise KeyError(f"path {path!r} hit non-dict/non-list at {part!r}")
    return cur
