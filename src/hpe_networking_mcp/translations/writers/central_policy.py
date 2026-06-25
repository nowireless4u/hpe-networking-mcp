"""Canonical → Central security-policy writer.

Emits the policy create, the policy-group-list registration (#420 — a policy is
not effective until it is a member of a policy-group), and the config-assignment.
If the reader flagged any unmapped AOS 8 action (fail-closed to ACTION_DENY), the
policy create is marked ``unresolved`` so execution blocks for operator review
rather than silently pushing a deny where the source intent was unclear.
"""

from __future__ import annotations

from hpe_networking_mcp.translations.canonical.policy import CanonicalPolicy
from hpe_networking_mcp.translations.writers.central_common import (
    DEFAULT_DEVICE_FUNCTIONS,
    config_assignment_call,
    create_call,
)

# Central policy-group registration path (#420). A policy alone broadcasts
# nothing; it must be listed in a policy-group to take effect at a scope.
_POLICY_GROUP_LIST = "policy-groups/policy-group/policy-group-list"


def central_write_policy(
    canon: CanonicalPolicy,
    *,
    scope_id: str | None = None,
    device_functions: list[str] | None = None,
) -> list[dict]:
    """Emit the Central calls for a security policy: create + policy-group + assign."""
    dfs = device_functions or DEFAULT_DEVICE_FUNCTIONS

    create = create_call(
        "policies",
        canon.name,
        {
            "name": canon.name,
            "type": "POLICY_TYPE_SECURITY",
            "association": canon.association,
            "security-policy": {"type": "SECURITY_POLICY_TYPE_DEFAULT", "policy-rule": canon.rules},
        },
        purpose=f"Create policy '{canon.name}' (library)",
    )
    if canon.unmapped_actions:
        # Fail-closed: an unmapped action became ACTION_DENY — block for review.
        create["unresolved"] = {"kind": "policy_action", "name": canon.name}

    # #420: register the policy in the policy-group-list so it can be assigned.
    group_entry = create_call(
        _POLICY_GROUP_LIST,
        canon.name,
        {"name": canon.name, "position": 1},
        depends_on=[0],
        purpose=f"Register policy '{canon.name}' in policy-group-list (#420)",
    )

    assign = config_assignment_call(
        "policies", canon.name, scope_id, dfs, depends_on=[1], kind="policy", name=canon.name
    )
    return [create, group_entry, assign]
