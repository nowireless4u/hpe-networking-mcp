"""Canonical → Central writers for the structural config kinds.

Covers ``vlan_id`` / ``named_vlan`` / ``role`` / ``net_group`` / ``gateway_cluster``
— every kind whose Central shape is a Library create + config-assignment (or, for
named_vlan + gateway_cluster, the LOCAL-override variants). Each writer consumes
its canonical model and returns ordered call descriptors using ``central_common``.

Placement context arrives as keyword args off ``writer_ctx``: ``scope_id`` (the
resolved Central scope-id) and ``device_functions`` (per-kind default,
operator-overridable). A ``None`` ``scope_id`` is surfaced as ``unresolved`` so
``orchestrator.execute`` blocks before writing.
"""

from __future__ import annotations

from hpe_networking_mcp.translations.canonical.gateway_cluster import CanonicalGatewayCluster
from hpe_networking_mcp.translations.canonical.net_group import CanonicalNetGroup
from hpe_networking_mcp.translations.canonical.role import CanonicalRole
from hpe_networking_mcp.translations.canonical.vlan import CanonicalNamedVlan, CanonicalVlanId
from hpe_networking_mcp.translations.writers.central_common import (
    DEFAULT_DEVICE_FUNCTIONS,
    VLAN_DEVICE_FUNCTIONS,
    config_assignment_call,
    create_call,
    local_call,
)

_ALIAS_VLAN_PLACEHOLDER = ["1"]  # Library default; the real ids land via the LOCAL override


def _expand_vlan_ids(ranges: list[str]) -> list[int]:
    """Expand range-preserving id strings (``["108-110"]``) → discrete ints.

    Mirrors the validated ``expand_vlan_id_csv``: each element is either an id or
    an ``x-y`` range; ids must be within 1..4094 and ranges non-inverted.
    """
    out: list[int] = []
    for chunk in ranges:
        if "-" in chunk:
            low_s, high_s = chunk.split("-", 1)
            low, high = int(low_s), int(high_s)
            if low > high:
                raise ValueError(f"Inverted VLAN range {chunk!r} (low > high)")
            if not (1 <= low <= 4094) or not (1 <= high <= 4094):
                raise ValueError(f"VLAN range {chunk!r} contains IDs outside 1..4094")
            out.extend(range(low, high + 1))
        else:
            vid = int(chunk)
            if not (1 <= vid <= 4094):
                raise ValueError(f"VLAN ID {vid} outside 1..4094")
            out.append(vid)
    return out


def central_write_vlan_id(
    canon: CanonicalVlanId,
    *,
    scope_id: str | None = None,
    device_functions: list[str] | None = None,
) -> list[dict]:
    """Emit the Central calls for a bare L2 VLAN: create + config-assignment."""
    dfs = device_functions or VLAN_DEVICE_FUNCTIONS
    body: dict = {"vlan": canon.vlan_id}
    if canon.description is not None:
        body["description"] = canon.description
    if canon.option_82 is not None:
        body["option-82"] = canon.option_82
    if canon.wired_aaa_profile is not None:
        body["wired-aaa-profile"] = canon.wired_aaa_profile
    return [
        create_call("layer2-vlan", canon.vlan_id, body, purpose=f"Create layer2-vlan '{canon.vlan_id}' (library)"),
        config_assignment_call(
            "layer2-vlan", canon.vlan_id, scope_id, dfs, depends_on=[0], kind="vlan_id", name=canon.vlan_id
        ),
    ]


def central_write_named_vlan(
    canon: CanonicalNamedVlan,
    *,
    scope_id: str | None = None,
    device_functions: list[str] | None = None,
) -> list[dict]:
    """Emit the 6-step Central named-VLAN chain (layer2-vlan + alias + named-vlan).

    Order: layer2-vlan create per expanded id → alias create → named-vlan create →
    layer2-vlan assignments → named-vlan assignment → alias LOCAL override per
    device-function (the real ids; the Library alias keeps the placeholder).
    """
    dfs = device_functions or VLAN_DEVICE_FUNCTIONS
    expanded = _expand_vlan_ids(canon.vlan_ids)
    alias, name = canon.alias_name, canon.vlan_name
    calls: list[dict] = []

    # 1) layer2-vlan create per discrete VLAN id (ranges expanded)
    l2_idx: list[int] = []
    for vid in expanded:
        calls.append(
            create_call("layer2-vlan", vid, {"vlan": str(vid)}, purpose=f"Create layer2-vlan '{vid}' (library)")
        )
        l2_idx.append(len(calls) - 1)

    # 2) ALIAS_VLAN shell (placeholder id; real ids land via the LOCAL override)
    calls.append(
        create_call(
            "aliases",
            alias,
            {
                "name": alias,
                "type": "ALIAS_VLAN",
                "default-value": {"vlan-value": {"vlan-id-ranges": _ALIAS_VLAN_PLACEHOLDER}},
            },
            purpose=f"Create ALIAS_VLAN '{alias}' (placeholder)",
        )
    )

    # 3) named-vlan referencing the alias
    calls.append(
        create_call(
            "named-vlan",
            name,
            {"name": name, "vlan": {"vlan-alias": alias}},
            purpose=f"Create named-vlan '{name}' (library)",
        )
    )
    nv_idx = len(calls) - 1

    # 4) assign each layer2-vlan to the scope
    for j, vid in enumerate(expanded):
        calls.append(
            config_assignment_call(
                "layer2-vlan", vid, scope_id, dfs, depends_on=[l2_idx[j]], kind="named_vlan", name=name
            )
        )

    # 5) assign the named-vlan (Central auto-pulls the alias to the same scope)
    calls.append(
        config_assignment_call("named-vlan", name, scope_id, dfs, depends_on=[nv_idx], kind="named_vlan", name=name)
    )
    step5_idx = len(calls) - 1

    # 6) LOCAL override of the alias with the real ids, per device-function
    for df in dfs:
        calls.append(
            local_call(
                "aliases",
                alias,
                {
                    "name": alias,
                    "type": "ALIAS_VLAN",
                    "default-value": {"vlan-value": {"vlan-id-ranges": canon.vlan_ids}},
                },
                scope_id,
                df,
                depends_on=[step5_idx],
                kind="named_vlan",
                purpose=f"LOCAL override of ALIAS_VLAN '{alias}' with real VLAN ids",
            )
        )

    return calls


def central_write_net_group(
    canon: CanonicalNetGroup,
    *,
    scope_id: str | None = None,
    device_functions: list[str] | None = None,
) -> list[dict]:
    """Emit the Central calls for a net-group: create (with items[]) + config-assignment."""
    dfs = device_functions or DEFAULT_DEVICE_FUNCTIONS
    body: dict = {"name": canon.name, "netdestination-type": canon.address_family, "items": canon.items}
    if canon.invert:
        body["invert"] = True
    return [
        create_call("net-groups", canon.name, body, purpose=f"Create net-group '{canon.name}' (library)"),
        config_assignment_call(
            "net-groups", canon.name, scope_id, dfs, depends_on=[0], kind="net_group", name=canon.name
        ),
    ]


def _group(pairs: list[tuple[str, object]]) -> dict:
    """Build a nested body group, dropping keys whose value is ``None``."""
    return {k: v for k, v in pairs if v is not None}


def central_write_role(
    canon: CanonicalRole,
    *,
    scope_id: str | None = None,
    device_functions: list[str] | None = None,
) -> list[dict]:
    """Emit the Central calls for a Gateway role: create + config-assignment.

    Optional fields drop their body key; nested groups (session / miscellaneous /
    classification + the bw-contract wrappers) drop entirely when every member is
    absent — matching the validated engine's drop-None / drop-empty behavior.
    """
    dfs = device_functions or DEFAULT_DEVICE_FUNCTIONS
    body: dict = {"name": canon.name}
    if canon.access_vlan_id is not None:
        body["access-vlan-id"] = canon.access_vlan_id
    if canon.access_vlan_name is not None:
        body["access-vlan-name"] = canon.access_vlan_name
    if canon.vlan_type is not None:
        body["vlan-type"] = canon.vlan_type

    session = _group(
        [
            ("captive-portal", canon.captive_portal),
            ("check-for-accounting", canon.check_for_accounting),
            ("max-sessions", canon.max_sessions),
            ("reauthentication-interval", canon.reauth_interval),
            ("reauthentication-interval-seconds", canon.reauth_interval_seconds),
        ]
    )
    if session:
        body["session-parameters"] = session

    misc = _group(
        [
            ("enforce-dhcp", canon.enforce_dhcp),
            ("robust-age-out", canon.robust_age_out),
            ("registration-role", canon.registration_role),
            ("openflow-enable", canon.openflow_enable),
        ]
    )
    if misc:
        body["miscellaneous-parameters"] = misc

    classification = _group(
        [
            ("ip-classification", canon.ip_classification),
            ("dpi-classification", canon.dpi_classification),
            ("dpi-youtube-education", canon.dpi_youtube_education),
            ("web-cc", canon.web_cc),
        ]
    )
    if classification:
        body["classification-parameters"] = classification

    # bw-contract wrappers — each present list nests under its Central outer/inner key
    for outer, inner, value in (
        ("aaa-bw-contract", "bw-contract", canon.bwc_basic),
        ("app-aaa-contract", "app", canon.bwc_app),
        ("app-category-aaa-contract", "app-category", canon.bwc_appcategory),
        ("web-category-aaa-contract", "web-category", canon.bwc_web_category),
        ("web-reputation-aaa-contract", "web-reputation", canon.bwc_web_reputation),
        ("exclude-app-contract", "exclude-app", canon.bwc_exclude_app),
        ("exclude-app-cat-contract", "exclude-app-category", canon.bwc_exclude_appcategory),
    ):
        if value:
            body[outer] = {inner: value}

    return [
        create_call("roles", canon.name, body, purpose=f"Create role '{canon.name}' (library)"),
        config_assignment_call("roles", canon.name, scope_id, dfs, depends_on=[0], kind="role", name=canon.name),
    ]


def central_write_gateway_cluster(
    canon: CanonicalGatewayCluster,
    *,
    scope_id: str | None = None,
    device_functions: list[str] | None = None,
) -> list[dict]:
    """Emit the Central gateway-cluster calls — HA profile (always) + intent (gated).

    Both are LOCAL creates at the target scope (scope-id + device-function ride in
    the query, not a config-assignment). The intent object is emitted only for the
    intent_site / intent_manual strategies (``canon.emit_intent``).
    """
    df = (device_functions or DEFAULT_DEVICE_FUNCTIONS)[0]

    ha_body: dict = {"name": canon.name}
    if canon.ipv4_gateways:
        ha_body["ipv4-gateways"] = canon.ipv4_gateways
    if canon.multicast_vlan is not None:
        ha_body["multicast-vlan"] = canon.multicast_vlan
    if canon.heartbeat_threshold is not None:
        ha_body["heartbeat-threshold"] = canon.heartbeat_threshold

    calls = [
        local_call(
            "gateway-clusters",
            canon.name,
            ha_body,
            scope_id,
            df,
            kind="gateway_cluster",
            purpose=f"Create gateway-cluster '{canon.name}' (HA, LOCAL)",
        )
    ]

    if canon.emit_intent:
        intent_body: dict = {"name": canon.name, "cluster-mode": canon.cluster_mode, "device-type": "MOBILITY_GW"}
        if canon.multicast_vlan is not None:
            intent_body["multicast-vlan"] = canon.multicast_vlan
        if canon.heartbeat_threshold is not None:
            intent_body["heartbeat-threshold"] = canon.heartbeat_threshold
        calls.append(
            local_call(
                "gw-cluster-intent-config",
                canon.name,
                intent_body,
                scope_id,
                df,
                depends_on=[0],
                kind="gateway_cluster",
                purpose=f"Create gw-cluster-intent-config '{canon.name}' ({canon.cluster_mode}, LOCAL)",
            )
        )

    return calls
