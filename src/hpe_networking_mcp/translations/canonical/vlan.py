"""Canonical VLAN models — ``vlan_id`` (bare L2 VLAN) and ``named_vlan``.

AOS 8 → Central only (unidirectional): the reader builds these from AOS 8
``vlan_id`` / (``vlan_name`` ⨝ ``vlan_name_id``) records; the Central writer
emits the layer2-vlan create + config-assignment (vlan_id) or the 6-step
alias-chain (named_vlan).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CanonicalVlanId(BaseModel):
    """A bare numeric L2 VLAN (AOS 8 ``vlan_id`` → Central ``layer2-vlan``).

    Optional sub-properties (description / option-82 / wired-aaa-profile) are
    GW-only AOS 8 features that surface inline on richer source records; ``None``
    drops the resulting Central body key.
    """

    model_config = ConfigDict(extra="forbid")
    vlan_id: str  # the VLAN id as a string (Central path-param + profile-instance)
    description: str | None = None
    option_82: bool | None = None
    wired_aaa_profile: str | None = None


class CanonicalNamedVlan(BaseModel):
    """A symbolic VLAN name bound to one or more VLAN ids (AOS 8 composite).

    ``vlan_ids`` preserves the AOS 8 ``vlan-ids`` range syntax verbatim (e.g.
    ``["108-110"]``) for the Central alias LOCAL-override; the writer expands
    ranges to discrete ids for the layer2-vlan creates/assignments.
    """

    model_config = ConfigDict(extra="forbid")
    vlan_name: str  # Central named-vlan name (operator-overridable upstream)
    alias_name: str  # ALIAS_VLAN name (default = lower-case of vlan_name)
    vlan_ids: list[str] = Field(default_factory=list)  # range-preserving id strings
