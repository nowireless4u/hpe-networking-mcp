"""Canonical tool capability classification — the single source of truth.

Every platform tool is classified into exactly one :class:`Capability`. That
one classification derives, consistently:

* the MCP ``ToolAnnotations`` hints sent to clients,
* the ``requires_confirmation`` tag the universal confirmation gate reads,
* the ``<platform>_write[_delete]`` visibility/enable tag, and
* the searchable capability facet recorded on the tool's ``ToolSpec``.

Never hand-write ``ToolAnnotations`` or the governance tags per tool — call
:func:`classify` (via a platform ``@tool(capability=...)`` shim) so all four
stay in lock-step and cannot drift. See ``docs/tool-annotation-rubric.md`` for
the classification rubric.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from mcp.types import ToolAnnotations

#: The ONLY tag the universal confirmation gate reads. Presence => the tool
#: prompts the user for confirmation before it runs.
REQUIRES_CONFIRMATION = "requires_confirmation"


class Capability(StrEnum):
    """What a tool does, for governance + discovery. Exactly one per tool."""

    READ = "read"
    DIAGNOSTIC = "diagnostic"
    WRITE = "write"
    WRITE_DELETE = "write_delete"
    OPERATIONAL = "operational"


# (readOnlyHint, destructiveHint, idempotentHint, openWorldHint) per category.
_HINTS: dict[Capability, tuple[bool, bool, bool, bool]] = {
    Capability.READ: (True, False, True, True),
    Capability.DIAGNOSTIC: (False, False, True, True),
    Capability.WRITE: (False, False, False, True),
    Capability.WRITE_DELETE: (False, True, False, True),
    Capability.OPERATIONAL: (False, False, True, True),
}

# Whether the category requires user confirmation by default. Overridable
# per tool via ``classify(gated=...)`` (e.g. a benign OPERATIONAL action).
_GATED_DEFAULT: dict[Capability, bool] = {
    Capability.READ: False,
    Capability.DIAGNOSTIC: False,
    Capability.WRITE: True,
    Capability.WRITE_DELETE: True,
    Capability.OPERATIONAL: True,
}


@dataclass(frozen=True)
class ToolClass:
    """The derived governance metadata for one tool."""

    annotations: ToolAnnotations
    tags: set[str]
    capability: Capability


def classify(
    cap: Capability,
    *,
    platform: str,
    gated: bool | None = None,
    enable_gated: bool = False,
    extra_tags: set[str] | None = None,
) -> ToolClass:
    """Derive annotations + tags + capability facet from one classification.

    Args:
        cap: The tool's capability category.
        platform: e.g. ``"axis"`` — used to build the ``<platform>_write*``
            enable tag.
        gated: Override the confirmation default for this tool. ``None`` uses
            the category default (see :data:`_GATED_DEFAULT`). Pass ``False``
            for a benign OPERATIONAL action (e.g. clearing an alert) that
            should not prompt; ``True`` to force a prompt.
        enable_gated: Only meaningful for ``OPERATIONAL``. When ``True`` the
            tool also carries the ``<platform>_write_delete`` enable tag, so it
            is hidden unless the platform's write flag is set (used for
            destructive operational actions like credential regeneration that
            should not be reachable on a read-only deployment). ``WRITE`` and
            ``WRITE_DELETE`` are always enable-gated; ``READ``/``DIAGNOSTIC``
            never are.
        extra_tags: Functional/discovery tags to merge in (platform, service
            group, etc.). Governance tags are added on top, never replaced.

    Returns:
        A :class:`ToolClass` whose ``annotations``/``tags`` go straight to
        ``@mcp.tool`` and whose ``capability`` is recorded for search.
    """
    read_only, destructive, idempotent, open_world = _HINTS[cap]
    annotations = ToolAnnotations(
        readOnlyHint=read_only,
        destructiveHint=destructive,
        idempotentHint=idempotent,
        openWorldHint=open_world,
    )

    tags: set[str] = set(extra_tags or set())

    # Visibility/enable tag (the ENABLE_<PLATFORM>_WRITE_TOOLS gate).
    if cap is Capability.WRITE:
        tags.add(f"{platform}_write")
    elif cap is Capability.WRITE_DELETE or cap is Capability.OPERATIONAL and enable_gated:
        tags.add(f"{platform}_write_delete")

    # The confirmation-gate signal.
    is_gated = _GATED_DEFAULT[cap] if gated is None else gated
    if is_gated:
        tags.add(REQUIRES_CONFIRMATION)

    return ToolClass(annotations=annotations, tags=tags, capability=cap)
