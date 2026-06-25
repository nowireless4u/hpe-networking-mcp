"""Canonical AAA-chain model (AOS 8 auth-server / server-group / dot1x / mac /
captive-portal / aaa-profile → Central).

These six kinds are unidirectional passthrough flattens: the AOS 8 record's
wrapped fields map field-for-field onto a Central create body (the per-kind reader
does that mapping + the auth-server CoA correlation). They also share one Central
shape — a Library ``POST /<type>/{name}`` whose config-assignment ``profile-type``
equals the create ``type``. So one thin canonical + one writer serves all six; the
cross-references between them (aaa-profile → dot1x/mac/server-group/role by name)
are plain string values in the bodies, resolved by the migration skill's ordering.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CanonicalCentralProfile(BaseModel):
    """A Central Library profile placed via create + config-assignment.

    ``profile_type`` is both the create ``type`` path segment and the
    config-assignment ``profile-type`` (identical for every AAA kind). ``body`` is
    the fully-built Central create body (the reader applies the AOS 8 → Central
    field mapping). ``kind`` is the canonical kind name, used for unresolved labels.
    """

    model_config = ConfigDict(extra="forbid")
    kind: str
    profile_type: str
    name: str
    body: dict[str, Any] = Field(default_factory=dict)
