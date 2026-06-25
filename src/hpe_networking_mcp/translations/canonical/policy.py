"""Canonical security-policy model (AOS 8 ``acl_sess`` → Central policy).

AOS 8 → Central only. The reader does the heavy lifting (role-attribution
reverse-index, any-any bidirectional expansion, role injection, per-rule
address/service/protocol/action building) and stores the finished Central
``policy-rule[]`` array; the writer assembles the policy create + the
policy-group-list registration (#420) + config-assignment.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CanonicalPolicy(BaseModel):
    """A Central security policy with its ordered rules + role/interface association."""

    model_config = ConfigDict(extra="forbid")
    name: str
    association: str  # ASSOCIATION_ROLE | ASSOCIATION_INTERFACE
    rules: list[dict[str, Any]] = Field(default_factory=list)  # Central policy-rule[]
    # AOS 8 action strings that had no Central mapping. Non-empty → the writer
    # fail-closes those rules to ACTION_DENY and flags the policy unresolved
    # (never a silent fall-through to ACTION_ALLOW — the security-inverting bug).
    unmapped_actions: list[str] = Field(default_factory=list)
