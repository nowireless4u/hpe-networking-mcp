"""Loader for migration mapping JSON files.

Reads every ``*.json`` under the package's ``central_targets/`` directory
(plus an optional override path), validates each against the pydantic
schemas below, and returns a dict keyed by ``central_target_id``. Fails
fast at startup with readable error messages on malformed mappings.

The schemas are deliberately permissive in places (``dict[str, Any]`` for
free-form body templates, optional fields throughout) because the format
is still evolving as we author additional mappings. As patterns crystallize
the validation will tighten. ``ConfigDict(extra="forbid")`` is set on the
top-level Mapping so typos in well-known field names fail loudly.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class LoaderError(RuntimeError):
    """Raised when one or more mapping files fail to load or validate.

    Carries a human-readable summary the lifespan handler logs at startup.
    """


# --------------------------------------------------------------------------- #
# Mapping schema (pydantic v2)
# --------------------------------------------------------------------------- #


class CentralEmit(BaseModel):
    """One ordered POST/PUT to Central within a mapping's emits chain."""

    model_config = ConfigDict(extra="forbid")

    step: int = Field(ge=1, description="1-based step number; used by depends_on")
    name: str = Field(min_length=1, description="Short identifier, e.g. 'create_layer2_vlan_shared'")
    purpose: str = Field(min_length=1, description="Why this emit exists; surfaced to operators")
    endpoint: str = Field(min_length=1, description="Central API path; may contain {placeholder} fields")
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
            "engine grows to handle new shapes as they show up in mappings."
        ),
    )
    iteration: str = Field(
        description=(
            "How to fan out this emit at runtime. Recognized values: "
            "'once_per_named_vlan', 'per_vlan_id_in_binding', 'per_device_function', "
            "'per_vlan_id_per_device_function'. Free text outside that set is reserved "
            "for future patterns; engine raises if it encounters an unknown value."
        )
    )
    iteration_notes: str | None = Field(default=None, description="Explanation of the iteration rule")
    depends_on: list[int] = Field(
        default_factory=list,
        description="Step numbers that must complete before this one fires",
    )


class CentralTargetMeta(BaseModel):
    """Target-side metadata that drives iteration + filtering."""

    model_config = ConfigDict(extra="forbid")

    device_functions: list[str] = Field(
        min_length=1,
        description="Central device functions (MOBILITY_GW, CAMPUS_AP, etc.) the emits target",
    )
    device_function_filtering_rule: str = Field(
        min_length=1,
        description="Plain-English explanation of how each step iterates over device_functions",
    )


class ScopeResolution(BaseModel):
    """Contract for resolving the source binding scope to a Central scope_id."""

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
    """A reverse dependency: which other mappings consume this target."""

    model_config = ConfigDict(extra="forbid")

    central_target_id: str
    field: str
    relation: str
    notes: str | None = None


class Dependency(BaseModel):
    """Forward + reverse dependency declarations for a mapping."""

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
        description="Role this object plays in a composite mapping (e.g. 'name_registration')",
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

    # Either 'from' (source path) or 'from_derived' (computed) — at least one required.
    from_: str | None = Field(default=None, alias="from", description="Source field path")
    to: str = Field(min_length=1, description="Central destination (path/role description)")
    transform: str = Field(min_length=1, description="Named transform; resolved by transforms.py")
    default: str | None = None
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
    """A source form explicitly out of scope for this mapping."""

    model_config = ConfigDict(extra="forbid")

    form: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class SourceBlock(BaseModel):
    """One source-platform's view: how to extract data + transforms to Central."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["rest", "cli_show_run", "paste_yaml"] = Field(
        description="Source-platform extraction shape; v1 only ships 'rest' (AOS 8)"
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


class Mapping(BaseModel):
    """Top-level mapping: target Central artifact + per-source extraction recipes."""

    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1, description="Schema version; 1 today")
    central_target_id: str = Field(
        min_length=1,
        description="Stable identifier for the mapping; used as the loader's dict key",
    )
    central_emits: list[CentralEmit] = Field(min_length=1)
    central_target_meta: CentralTargetMeta
    central_scope_id_resolution: ScopeResolution
    derived: dict[str, DerivedRule] = Field(default_factory=dict)
    dependencies: list[Dependency] = Field(default_factory=list)
    tokenize_kind_per_field: dict[str, str] = Field(default_factory=dict)
    sources: dict[str, SourceBlock] = Field(min_length=1)
    draft_notes: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Loader entry point
# --------------------------------------------------------------------------- #


def _shipped_mappings_dir() -> Path:
    """Path to the ``central_targets/`` directory inside the installed package."""
    return Path(str(resources.files("hpe_networking_mcp.migrations") / "central_targets"))


def load_mappings(
    base_path: Path | None = None,
    overrides_path: Path | None = None,
) -> dict[str, Mapping]:
    """Load + validate every ``*.json`` under the mapping directories.

    Args:
        base_path: Directory for shipped mappings. Defaults to the
            package's ``central_targets/``.
        overrides_path: Optional operator-supplied directory whose files
            replace any same-named shipped mapping (file-level merge).

    Returns:
        Dict keyed by ``central_target_id``. Order: shipped mappings load
        first, then overrides replace any matching ``central_target_id``.

    Raises:
        LoaderError: If any file fails to parse or validate. The error
            message lists every failure in one shot rather than stopping
            on the first one — easier to fix multiple issues per restart.
    """
    base_path = base_path or _shipped_mappings_dir()
    paths: list[Path] = []
    if base_path.exists():
        paths.extend(sorted(base_path.glob("*.json")))
    if overrides_path is not None and overrides_path.exists():
        paths.extend(sorted(overrides_path.glob("*.json")))

    mappings: dict[str, Mapping] = {}
    errors: list[str] = []

    for path in paths:
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON — {exc}")
            continue

        try:
            mapping = Mapping.model_validate(raw)
        except ValidationError as exc:
            errors.append(f"{path}: pydantic validation failed —\n{exc}")
            continue

        # Composite mappings must have a merge_rule on every source block
        for src_id, src in mapping.sources.items():
            if src.mapping_kind == "composite" and src.merge_rule is None:
                errors.append(f"{path}: sources.{src_id} declares mapping_kind='composite' but is missing 'merge_rule'")

        # depends_on step refs must point at real steps
        valid_steps = {emit.step for emit in mapping.central_emits}
        for emit in mapping.central_emits:
            for dep in emit.depends_on:
                if dep not in valid_steps:
                    errors.append(f"{path}: emit '{emit.name}' depends_on={dep} but no such step exists")

        mappings[mapping.central_target_id] = mapping

    if errors:
        raise LoaderError("Migration mapping load failed with the following errors:\n  - " + "\n  - ".join(errors))

    return mappings
