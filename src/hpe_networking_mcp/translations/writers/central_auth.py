"""Canonical → Central writer for the AAA-chain profile kinds.

All six AAA kinds (auth_server / server_group / dot1x_auth / mac_auth /
captive_portal / aaa_profile) share one Central shape: a Library
``POST /<profile_type>/{name}`` (body pre-built by the reader) plus a
config-assignment whose ``profile-type`` equals that same ``profile_type``. One
writer serves all of them — the canonical carries the ``profile_type`` + ``kind``.
"""

from __future__ import annotations

from hpe_networking_mcp.translations.canonical.auth import CanonicalCentralProfile
from hpe_networking_mcp.translations.writers.central_common import (
    DEFAULT_DEVICE_FUNCTIONS,
    config_assignment_call,
    create_call,
)


def central_write_profile(
    canon: CanonicalCentralProfile,
    *,
    scope_id: str | None = None,
    device_functions: list[str] | None = None,
) -> list[dict]:
    """Emit the Central create + config-assignment for one AAA-chain profile."""
    dfs = device_functions or DEFAULT_DEVICE_FUNCTIONS
    return [
        create_call(
            canon.profile_type,
            canon.name,
            canon.body,
            purpose=f"Create {canon.profile_type} '{canon.name}' (library)",
        ),
        config_assignment_call(
            canon.profile_type,
            canon.name,
            scope_id,
            dfs,
            depends_on=[0],
            kind=canon.kind,
            name=canon.name,
        ),
    ]
