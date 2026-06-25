"""Canonical gateway-cluster model (AOS 8 ``cluster_prof`` → Central dual-object).

Central clustering is two LOCAL objects at the target scope: a ``gateway-clusters``
HA profile (always — owns the explicit member gateways + CoA-VRRP IPs) and, on the
modern path, a ``gw-cluster-intent-config`` declaring the cluster-mode (gated by
the operator's ``cluster_strategy``). AOS 8 → Central only.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CanonicalGatewayCluster(BaseModel):
    """A gateway cluster: HA membership + (optional) intent declaration."""

    model_config = ConfigDict(extra="forbid")
    name: str
    ipv4_gateways: list[dict[str, Any]] = Field(default_factory=list)  # [{ip, coa-vrrp-ip?, priority?}]
    multicast_vlan: int | None = None
    heartbeat_threshold: int | None = None
    emit_intent: bool = False  # CM_SITE / CM_MANUAL strategies emit the intent object
    cluster_mode: str | None = None  # CM_SITE | CM_MANUAL (None for ha_only)
