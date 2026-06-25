"""Canonical user-role model (AOS 8 ``role`` → Central Gateway role profile).

AOS 8 → Central only. The bandwidth-contract lists are stored in their Central
``[]`` item shape (the reader applies the validated filter/rename/uppercase
transforms); the writer nests them under the Central body groups and drops any
group whose members are all absent.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class CanonicalRole(BaseModel):
    """Gateway-targeted user role. ``None`` fields drop their Central body key."""

    model_config = ConfigDict(extra="forbid")

    name: str

    # VLAN (root, mutually-exclusive id/name + discriminator)
    access_vlan_id: int | None = None
    access_vlan_name: str | None = None
    vlan_type: str | None = None  # VLAN_ID | VLAN_NAME

    # session-parameters
    captive_portal: str | None = None
    check_for_accounting: bool | None = None
    max_sessions: int | None = None
    reauth_interval: int | None = None  # minutes form
    reauth_interval_seconds: int | None = None  # seconds form (mutually exclusive)

    # miscellaneous-parameters
    enforce_dhcp: bool | None = None
    robust_age_out: bool | None = None
    registration_role: bool | None = None
    openflow_enable: bool | None = None

    # classification-parameters (true == feature disabled, per AOS 8 disable-flag convention)
    ip_classification: bool | None = None
    dpi_classification: bool | None = None
    dpi_youtube_education: bool | None = None
    web_cc: bool | None = None

    # bandwidth contracts — Central item shapes, None when none configured
    bwc_basic: list[dict[str, Any]] | None = None
    bwc_app: list[dict[str, Any]] | None = None
    bwc_appcategory: list[dict[str, Any]] | None = None
    bwc_web_category: list[dict[str, Any]] | None = None
    bwc_web_reputation: list[dict[str, Any]] | None = None
    bwc_exclude_app: list[dict[str, Any]] | None = None
    bwc_exclude_appcategory: list[dict[str, Any]] | None = None
