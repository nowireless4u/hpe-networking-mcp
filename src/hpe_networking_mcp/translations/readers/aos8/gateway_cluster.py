"""AOS 8 → canonical gateway-cluster reader.

Flattens an AOS 8 ``cluster_prof`` (``lc-cluster group-profile``) into a
``CanonicalGatewayCluster``. ``cluster_strategy`` (operator gateway-topology
answer) selects the Central path: ``ha_only`` (HA profile only), ``intent_site``
(+ CM_SITE intent), ``intent_manual`` (+ CM_MANUAL intent). Member entries keep
their ``_flags.inherited`` (group-level inheritance); only ``system`` members are
skipped.
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.translations.canonical.gateway_cluster import CanonicalGatewayCluster
from hpe_networking_mcp.translations.readers.aos8._common import leaf

_VALID_STRATEGIES = {"ha_only", "intent_site", "intent_manual"}
_MODE_BY_STRATEGY = {"intent_site": "CM_SITE", "intent_manual": "CM_MANUAL"}


def aos8_read_gateway_cluster(
    cluster_prof: dict[str, Any],
    *,
    cluster_strategy: str | None = None,
) -> CanonicalGatewayCluster:
    """Build a ``CanonicalGatewayCluster`` from one AOS 8 ``cluster_prof`` record.

    Raises:
        ValueError: when ``cluster_strategy`` is not one of ``ha_only`` /
            ``intent_site`` / ``intent_manual`` (the migration skill supplies it
            from the operator's gateway-topology answer).
    """
    if cluster_strategy not in _VALID_STRATEGIES:
        raise ValueError(
            f"gateway_cluster requires cluster_strategy in {sorted(_VALID_STRATEGIES)}; got {cluster_strategy!r}"
        )

    controllers = cluster_prof.get("cluster_controller") or []
    gateways: list[dict[str, Any]] = []
    for c in controllers:
        if not isinstance(c, dict) or (c.get("_flags") or {}).get("system"):
            continue
        entry: dict[str, Any] = {}
        if c.get("ip") is not None:
            entry["ip"] = c["ip"]
        if c.get("vrrp_ip") is not None:
            entry["coa-vrrp-ip"] = c["vrrp_ip"]
        if c.get("prio") is not None:
            entry["priority"] = c["prio"]
        if entry.get("ip"):
            gateways.append(entry)

    multicast_vlan = None
    for c in controllers:
        mv = c.get("mcast_vlan") if isinstance(c, dict) else None
        if isinstance(mv, int) and mv > 0:
            multicast_vlan = mv
            break

    hb = leaf(cluster_prof.get("heartbeat_threshold"), "heartbeat-threshold")
    heartbeat = int(hb) if (isinstance(hb, int) and hb > 0) else None

    return CanonicalGatewayCluster(
        name=str(cluster_prof.get("profile-name") or ""),
        ipv4_gateways=gateways,
        multicast_vlan=int(multicast_vlan) if multicast_vlan is not None else None,
        heartbeat_threshold=heartbeat,
        emit_intent=cluster_strategy in _MODE_BY_STRATEGY,
        cluster_mode=_MODE_BY_STRATEGY.get(cluster_strategy),
    )
