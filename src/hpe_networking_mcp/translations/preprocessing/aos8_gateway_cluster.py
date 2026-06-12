"""AOS 8 ``cluster_prof`` (lc-cluster group-profile) → normalized Central
gateway-cluster source shape.

Central clustering is a dual-object model (see the project memory): a
``gateway-clusters`` HA profile that owns the explicit member gateways + their
CoA-VRRP IPs, plus — on the modern path — a ``gw-cluster-intent-config`` that
declares the intent (CM_SITE / CM_MANUAL). The HA profile is always emitted; the
intent emit is gated by ``cluster_strategy`` via the engine's ``emit_when``
guard.

``cluster_strategy`` (required runtime value, supplied by the migration skill
after the operator's gateway-topology answer):

* ``ha_only``       — emit only the HA ``gateway-clusters`` profile (few gateways
                      / DMZ-only deployments that skip the intent service).
* ``intent_site``   — HA profile + intent ``CM_SITE`` (campus auto-grouping at
                      global / site / site-collection — scope supplied at runtime).
* ``intent_manual`` — HA profile + intent ``CM_MANUAL`` (explicit membership at
                      device-group scope; the DMZ-cluster path).

Member-level note: ``cluster_controller[]`` entries carry ``_flags.inherited`` at
descendant scopes — those are NOT dropped (they reflect group-level inheritance;
see the member-inherited-filter bug). Only genuinely ``system`` members are
skipped.
"""

from __future__ import annotations

from typing import Any

_VALID_STRATEGIES = {"ha_only", "intent_site", "intent_manual"}
_MODE_BY_STRATEGY = {"intent_site": "CM_SITE", "intent_manual": "CM_MANUAL"}


def _leaf(wrapped: Any, subkey: str) -> Any:
    if not isinstance(wrapped, dict):
        return None
    if (wrapped.get("_flags") or {}).get("default"):
        return None
    return wrapped.get(subkey)


def preprocess_gateway_cluster(source_data: dict, runtime_values: dict) -> dict:
    """Flatten a ``cluster_prof`` record into ``_<field>`` keys + strategy flags.

    Raises:
        ValueError: If ``runtime_values['cluster_strategy']`` is missing or not
            one of ``ha_only`` / ``intent_site`` / ``intent_manual`` (the engine
            wraps this as ``EngineError`` with translation context).
    """
    strategy = runtime_values.get("cluster_strategy")
    if strategy not in _VALID_STRATEGIES:
        raise ValueError(
            "preprocess_gateway_cluster requires runtime_values['cluster_strategy'] in "
            f"{sorted(_VALID_STRATEGIES)}; got {strategy!r}. The migration skill supplies "
            "this from the operator's gateway-topology answer."
        )

    sd = source_data
    controllers = sd.get("cluster_controller", []) or []

    # Explicit member list. DO NOT filter _flags.inherited (member-inherited just
    # reflects the parent group's inheritance); skip only genuinely system entries.
    gateways: list[dict[str, Any]] = []
    for c in controllers:
        if not isinstance(c, dict):
            continue
        if (c.get("_flags") or {}).get("system"):
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

    # Multicast VLAN: first non-zero mcast_vlan across members (0 = unset/default).
    mcast_vlan = None
    for c in controllers:
        mv = c.get("mcast_vlan") if isinstance(c, dict) else None
        if isinstance(mv, int) and mv > 0:
            mcast_vlan = mv
            break

    hb = _leaf(sd.get("heartbeat_threshold"), "heartbeat-threshold")

    norm: dict[str, Any] = {
        "_name": sd.get("profile-name"),
        "_ipv4_gateways": gateways or None,
        "_multicast_vlan": mcast_vlan,
        "_heartbeat_threshold": hb if (isinstance(hb, int) and hb > 0) else None,
        "_emit_intent": True if strategy in _MODE_BY_STRATEGY else None,
        "_cluster_mode": _MODE_BY_STRATEGY.get(strategy),
    }
    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
