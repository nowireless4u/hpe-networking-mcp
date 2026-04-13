"""Best-practice validation for Mist write operations.

Pure validation functions that inspect payloads and return warnings
when operations violate Mist configuration best practices. No I/O,
no API calls — takes dicts/strings, returns a GuardrailResult.

Best practices are based on Juniper Mist's recommended configuration
model: template everything at org level, use template variables for
site-specific values, let AI RRM manage RF, use Cloud PSK.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# IP address pattern (IPv4) — matches hardcoded IPs but not template variables like {{auth_srv1}}
_IP_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

# Template variable pattern — matches {{variable_name}}
_TEMPLATE_VAR_PATTERN = re.compile(r"^\{\{.+\}\}$")


@dataclass
class GuardrailResult:
    """Result of a best-practice validation check.

    Attributes:
        warnings: Shown in the elicitation message to the user.
        suggestions: Returned in the tool response for the AI to act on.
    """

    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


def validate_site_write(object_type: str, action_type: str, payload: dict) -> GuardrailResult:
    """Validate a site-level write operation against best practices.

    Args:
        object_type: The object type being written (e.g. "wlans", "psks").
        action_type: The action type ("create", "update", "delete").
        payload: The JSON payload for the operation.

    Returns:
        GuardrailResult with any warnings and suggestions.
    """
    result = GuardrailResult()
    _check_site_wlan_creation(object_type, action_type, result)
    _check_site_level_override(object_type, action_type, result)
    _check_hardcoded_radius(object_type, payload, result)
    _check_static_psk(object_type, payload, result)
    return result


def validate_org_write(object_type: str, action_type: str, payload: dict) -> GuardrailResult:
    """Validate an org-level write operation against best practices.

    Args:
        object_type: The object type being written (e.g. "wlans", "rftemplates").
        action_type: The action type ("create", "update", "delete").
        payload: The JSON payload for the operation.

    Returns:
        GuardrailResult with any warnings and suggestions.
    """
    result = GuardrailResult()
    _check_hardcoded_radius(object_type, payload, result)
    _check_fixed_rf(object_type, payload, result)
    _check_static_psk(object_type, payload, result)
    return result


# ---------------------------------------------------------------------------
# Private validation checks
# ---------------------------------------------------------------------------


def _check_site_wlan_creation(object_type: str, action_type: str, result: GuardrailResult) -> None:
    """Warn when creating a site-level WLAN instead of using an org-level template."""
    if object_type == "wlans" and action_type == "create":
        result.warnings.append(
            "BEST PRACTICE: SSIDs should be defined in org-level WLAN templates, "
            "not as site-level WLANs. Use mist_change_org_configuration_objects "
            "with object_type=wlans and a template_id to create the WLAN in an "
            "org-level template, then assign the template to the site's site group."
        )
        result.suggestions.append(
            "Create this WLAN as an org-level WLAN inside a WLAN template instead. "
            "Site-level WLANs cannot be centrally managed and cause configuration drift."
        )


def _check_site_level_override(object_type: str, action_type: str, result: GuardrailResult) -> None:
    """Warn when creating site-level config that should be at org level."""
    if object_type in ("wxrules", "wxtags") and action_type == "create":
        result.suggestions.append(
            f"Consider defining {object_type} at the org level and applying via "
            "templates rather than creating site-level overrides."
        )


def _check_hardcoded_radius(object_type: str, payload: dict, result: GuardrailResult) -> None:
    """Warn when WLAN payloads contain hardcoded RADIUS server IPs."""
    if object_type != "wlans":
        return
    for server_list_key in ("auth_servers", "acct_servers"):
        servers = payload.get(server_list_key, [])
        if not isinstance(servers, list):
            continue
        for server in servers:
            if not isinstance(server, dict):
                continue
            host = server.get("host", "")
            if _IP_PATTERN.match(str(host)) and not _TEMPLATE_VAR_PATTERN.match(str(host)):
                result.warnings.append(
                    f"BEST PRACTICE: RADIUS server IP '{host}' is hardcoded in "
                    f"{server_list_key}. Use template variables like "
                    "{{auth_srv1}} so the same WLAN template can resolve to "
                    "different RADIUS servers per site."
                )
                return  # One warning is enough


def _check_fixed_rf(object_type: str, payload: dict, result: GuardrailResult) -> None:
    """Warn when RF templates have fixed channels or TX power."""
    if object_type != "rftemplates":
        return
    for band_key in ("band_24", "band_5", "band_6", "band_24_usage"):
        band = payload.get(band_key)
        if not isinstance(band, dict):
            continue
        if isinstance(band.get("channels"), list) and band["channels"]:
            result.warnings.append(
                f"BEST PRACTICE: RF template has fixed channels for {band_key}. "
                "Mist AI RRM should manage channel selection automatically. "
                "Only override with explicit justification."
            )
            return  # One warning is enough
        if isinstance(band.get("power"), (int, float)):
            result.warnings.append(
                f"BEST PRACTICE: RF template has fixed TX power for {band_key}. "
                "Mist AI RRM should manage power levels automatically. "
                "Only override with explicit justification."
            )
            return


def _check_static_psk(object_type: str, payload: dict, result: GuardrailResult) -> None:
    """Warn when using static shared PSK instead of Cloud PSK."""
    if object_type != "psks":
        return
    if payload.get("passphrase") and payload.get("usage") != "multi":
        result.suggestions.append(
            "Consider using Cloud PSK (per-user unique passphrase with VLAN "
            "assignment) instead of a static shared PSK. Cloud PSK allows "
            "individual key rotation and per-device VLAN segmentation."
        )
