"""Loader for translation JSON files.

Reads every ``*.json`` under the package's ``targets/<platform>/`` directories
(plus an optional override path), validates each against the pydantic schemas
below, and returns a dict keyed by ``"<target_platform>:<target_id>"``. Fails
fast at startup with readable error messages on malformed translations.

The schemas are deliberately permissive in places (``dict[str, Any]`` for
free-form body templates, optional fields throughout) because the format
is still evolving as we author additional translations. As patterns crystallize
the validation will tighten. ``ConfigDict(extra="forbid")`` is set on the
top-level Translation so typos in well-known field names fail loudly.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class LoaderError(RuntimeError):
    """Raised when one or more translation files fail to load or validate.

    Carries a human-readable summary the lifespan handler logs at startup.
    """


# --------------------------------------------------------------------------- #
# Translation schema (pydantic v2)
# --------------------------------------------------------------------------- #


class TargetEmit(BaseModel):
    """One ordered API call to the target platform within a translation's emits chain."""

    model_config = ConfigDict(extra="forbid")

    step: int = Field(ge=1, description="1-based step number; used by depends_on")
    name: str = Field(min_length=1, description="Short identifier, e.g. 'create_layer2_vlan_shared'")
    purpose: str = Field(min_length=1, description="Why this emit exists; surfaced to operators")
    endpoint: str = Field(min_length=1, description="Target API path; may contain {placeholder} fields")
    method: Literal["POST", "PUT", "PATCH", "DELETE", "GET"]
    query_params: dict[str, str] = Field(
        default_factory=dict,
        description="Query parameters; values may contain {placeholders}",
    )
    body: dict[str, Any] | None = Field(
        default=None,
        description="Request body; may contain {placeholders}. Mutually exclusive with body_template.",
    )
    body_template: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Free-form description of array-shaped bodies that need iterated rendering "
            "(e.g. config-assignments with multi-device-function arrays). The engine "
            "interprets named patterns. v1 is intentionally permissive here — the "
            "engine grows to handle new shapes as they show up in translations."
        ),
    )
    iteration: str = Field(
        description=(
            "How to fan out this emit at runtime. Recognized values: "
            "'once', 'per_vlan_id_in_binding', 'per_device_function', "
            "'per_vlan_id_per_device_function'. Free text outside that set is reserved "
            "for future patterns; engine raises if it encounters an unknown value."
        )
    )
    iteration_notes: str | None = Field(default=None, description="Explanation of the iteration rule")
    depends_on: list[int] = Field(
        default_factory=list,
        description="Step numbers that must complete before this one fires",
    )
    emit_when: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Optional guard. When set, the engine emits ZERO calls for this step "
            "unless the condition holds against the substitution context — used for "
            "strategy/mode forks where some steps are conditional (e.g. emit the "
            "intent-config only for intent_* cluster strategies). Recognized keys: "
            "'context_truthy': '<ctx_key>' (fire only if ctx[key] is truthy); "
            "'context_equals': {'key': '<ctx_key>', 'value': <v>} (fire only if "
            "ctx[key] == v). The whole record is NOT skipped — only this emit."
        ),
    )


class TargetMeta(BaseModel):
    """Target-platform-specific metadata that drives iteration + filtering.

    Schema is intentionally lenient in v1 — Central uses ``device_functions`` +
    ``device_function_filtering_rule``; future target platforms (Mist, etc.)
    will introduce their own platform-specific keys here. Add a discriminated
    union when the second target platform lands.
    """

    model_config = ConfigDict(extra="forbid")

    device_functions: list[str] | None = Field(
        default=None,
        description="Central-specific: device functions (MOBILITY_GW, CAMPUS_AP, etc.) the emits target",
    )
    device_function_filtering_rule: str | None = Field(
        default=None,
        description="Central-specific: plain-English rule for how each step iterates over device_functions",
    )


class ScopeResolution(BaseModel):
    """Documentation for which runtime value the consumer must supply for the deployment scope."""

    model_config = ConfigDict(extra="forbid")

    rule: str
    input: str
    output: str


class DerivedRule(BaseModel):
    """A target-only derived value (e.g. alias_name = lower(named_vlan_name))."""

    model_config = ConfigDict(extra="forbid")

    rule: str = Field(min_length=1, description="Identifier of the derivation rule")
    examples: list[dict[str, Any]] = Field(default_factory=list)
    rationale: str | None = None
    operator_overridable: bool = False


class DependencyDependedBy(BaseModel):
    """A reverse dependency: which other translations consume this target."""

    model_config = ConfigDict(extra="forbid")

    target_id: str
    field: str
    relation: str
    notes: str | None = None


class Dependency(BaseModel):
    """Forward + reverse dependency declarations for a translation."""

    model_config = ConfigDict(extra="forbid")

    depends_on: str | list[str] | None = None
    depended_by: list[DependencyDependedBy] = Field(default_factory=list)


class SourceObject(BaseModel):
    """One source-side object descriptor inside a sources.<platform>.objects list."""

    model_config = ConfigDict(extra="forbid")

    object: str = Field(min_length=1, description="Source object name (e.g. 'vlan_name')")
    object_path: str | None = Field(
        default=None,
        description="Source-platform path the object is fetched from; informational",
    )
    role: str | None = Field(
        default=None,
        description="Role this object plays in a composite source (e.g. 'name_registration')",
    )
    docs: dict[str, str] = Field(default_factory=dict, description="Per-operation deep-links to vendor docs")
    live_shape_example: str | None = None
    notes: str | None = None


class MergeRule(BaseModel):
    """How a composite source merges multiple objects into one logical record."""

    model_config = ConfigDict(extra="forbid")

    join_key: str = Field(min_length=1)
    scope_policy: str = Field(min_length=1)
    description: str = Field(min_length=1)
    inheritance_handling: str | None = None


class KeyMapping(BaseModel):
    """One source-field → target-field translation rule."""

    model_config = ConfigDict(extra="forbid")

    from_: str | None = Field(default=None, alias="from", description="Source field path")
    to: str = Field(min_length=1, description="Target destination (path/role description)")
    transform: str = Field(min_length=1, description="Named transform; resolved by transforms.py")
    default: str | None = None
    optional: bool = Field(
        default=False,
        description=(
            "If True, a missing source field does not raise — the resulting body key is "
            "dropped from the rendered call instead. Use for sub-properties that may or "
            "may not be present on the source record (e.g. AOS 8 vlan_id sub-properties "
            "like description, option-82, wired-aaa-profile)."
        ),
    )
    transform_examples: list[dict[str, Any]] = Field(default_factory=list)
    notes: str | None = None


class UnmappedField(BaseModel):
    """A source field that doesn't translate; surfaces as a finding to operators."""

    model_config = ConfigDict(extra="forbid")

    from_: str = Field(alias="from", min_length=1)
    reason: str = Field(min_length=1)
    severity_rule: Literal["always_operator_map", "non_empty_regression", "always_regression"]
    central_alternative: str | None = None
    todo: str | None = None


class IgnoredVariant(BaseModel):
    """A source form explicitly out of scope for this translation."""

    model_config = ConfigDict(extra="forbid")

    form: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class SourceBlock(BaseModel):
    """One source-platform's view: how to extract data + transforms to the target."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["rest", "cli_show_run", "paste_yaml"] = Field(
        description="Source-platform extraction shape; v1 only ships 'rest' (AOS 8 / Central / Mist REST)"
    )
    mapping_kind: Literal["simple", "composite"] = "simple"
    objects: list[SourceObject] = Field(min_length=1)
    merge_rule: MergeRule | None = Field(
        default=None,
        description="Required when mapping_kind == 'composite'; ignored otherwise",
    )
    key_mappings: dict[str, KeyMapping] = Field(default_factory=dict)
    unmapped_fields: list[UnmappedField] = Field(default_factory=list)
    ignored_variants: list[IgnoredVariant] = Field(default_factory=list)


class Translation(BaseModel):
    """Top-level translation: target platform + emits + per-source extraction recipes."""

    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1, description="Schema version; 1 today")
    target_platform: str = Field(
        min_length=1,
        description="Which platform the emits target (e.g. 'central', 'mist', 'clearpass')",
    )
    target_id: str = Field(
        min_length=1,
        description="Stable identifier within the target platform; loader composite key is '<platform>:<id>'",
    )
    target_emits: list[TargetEmit] = Field(min_length=1)
    target_meta: TargetMeta
    target_scope_id_resolution: ScopeResolution
    required_runtime_values: list[str] = Field(
        default_factory=list,
        description=(
            "Runtime-context keys this translation needs supplied by the consumer "
            "(e.g. ['central_scope_id'] for Central targets). Engine validates these "
            "are present in runtime_values before emitting calls."
        ),
    )
    derived: dict[str, DerivedRule] = Field(default_factory=dict)
    dependencies: list[Dependency] = Field(default_factory=list)
    tokenize_kind_per_field: dict[str, str] = Field(default_factory=dict)
    sources: dict[str, SourceBlock] = Field(min_length=1)
    preprocessing: str | None = Field(
        default=None,
        description=(
            "Optional dotted import path to a preprocessing function. The function "
            "must accept ``(source_data: dict, runtime_values: dict) -> dict`` and "
            "return an augmented source_data dict (don't mutate the input). The "
            "engine invokes it before key_mappings, after the source platform check "
            "and required_runtime_values validation. Used by translations whose "
            "source shape doesn't fit per-field key_mapping (parallel arrays, "
            "cross-record lookups, fan-out expansion). Empty / null means no "
            "preprocessing — the simple pattern that fits most translations."
        ),
    )
    draft_notes: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Loader entry point
# --------------------------------------------------------------------------- #


def _shipped_targets_root() -> Path:
    """Path to the ``targets/`` directory inside the installed package."""
    return Path(str(resources.files("hpe_networking_mcp.translations") / "targets"))


def _composite_key(translation: Translation) -> str:
    """Build the loader's dict key: '<target_platform>:<target_id>'."""
    return f"{translation.target_platform}:{translation.target_id}"


def load_translations(
    base_path: Path | None = None,
    overrides_path: Path | None = None,
) -> dict[str, Translation]:
    """Load + validate every ``*.json`` under the targets directories.

    Args:
        base_path: Root directory containing ``<platform>/`` subdirectories
            with translation JSONs. Defaults to the package's ``targets/``.
        overrides_path: Optional operator-supplied directory whose files
            replace any same-keyed shipped translation (file-level merge).

    Returns:
        Dict keyed by ``"<target_platform>:<target_id>"``. Order: shipped
        translations load first, then overrides replace any matching key.

    Raises:
        LoaderError: If any file fails to parse or validate. The error
            message lists every failure in one shot rather than stopping
            on the first one — easier to fix multiple issues per restart.
    """
    base_path = base_path or _shipped_targets_root()
    paths: list[Path] = []
    if base_path.exists():
        # Walk every <platform>/*.json under the targets root
        for platform_dir in sorted(base_path.iterdir()):
            if platform_dir.is_dir():
                paths.extend(sorted(platform_dir.glob("*.json")))
    if overrides_path is not None and overrides_path.exists():
        # Same shape under overrides root
        for platform_dir in sorted(overrides_path.iterdir()):
            if platform_dir.is_dir():
                paths.extend(sorted(platform_dir.glob("*.json")))

    translations: dict[str, Translation] = {}
    errors: list[str] = []

    for path in paths:
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON — {exc}")
            continue

        try:
            translation = Translation.model_validate(raw)
        except ValidationError as exc:
            errors.append(f"{path}: pydantic validation failed —\n{exc}")
            continue

        # Composite sources must have a merge_rule on every block
        for src_id, src in translation.sources.items():
            if src.mapping_kind == "composite" and src.merge_rule is None:
                errors.append(f"{path}: sources.{src_id} declares mapping_kind='composite' but is missing 'merge_rule'")

        # depends_on step refs must point at real steps
        valid_steps = {emit.step for emit in translation.target_emits}
        for emit in translation.target_emits:
            for dep in emit.depends_on:
                if dep not in valid_steps:
                    errors.append(f"{path}: emit '{emit.name}' depends_on={dep} but no such step exists")

        translations[_composite_key(translation)] = translation

    if errors:
        raise LoaderError("Translation load failed with the following errors:\n  - " + "\n  - ".join(errors))

    return translations
