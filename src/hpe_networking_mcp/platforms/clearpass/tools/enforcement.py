"""ClearPass enforcement policy and profile read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def clearpass_get_enforcement_policies(
    ctx: Context,
    policy_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass enforcement policies.

    Enforcement policies determine what action to take after authentication,
    mapping conditions to enforcement profiles (e.g. VLAN assignment, role).

    If policy_id or name is provided, returns a single policy.
    Otherwise returns a paginated list of all enforcement policies.

    Args:
        policy_id: Numeric ID for single-item lookup.
        name: Policy name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if policy_id:
            return client.get_enforcement_policy_by_enforcement_policy_id(enforcement_policy_id=policy_id)
        if name:
            return client.get_enforcement_policy_name_by_name(name=name)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
            f"calculate_count={'true' if calculate_count else 'false'}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/enforcement-policy" + query, "get")
    except Exception as e:
        return f"Error fetching enforcement policies: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_enforcement_profiles(
    ctx: Context,
    profile_id: str | None = None,
    name: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass enforcement profiles.

    Enforcement profiles define the specific actions applied to a session
    (e.g. VLAN assignment, RADIUS attributes, bandwidth limits).

    If profile_id or name is provided, returns a single profile.
    Otherwise returns a paginated list of all enforcement profiles.

    Args:
        profile_id: Numeric ID for single-item lookup.
        name: Profile name for lookup by name.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_enforcementprofile import ApiEnforcementProfile

        client = await get_clearpass_session(ApiEnforcementProfile)
        if profile_id:
            return client.get_enforcement_profile_by_enforcement_profile_id(enforcement_profile_id=profile_id)
        if name:
            return client.get_enforcement_profile_name_by_name(name=name)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
            f"calculate_count={'true' if calculate_count else 'false'}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/enforcement-profile" + query, "get")
    except Exception as e:
        return f"Error fetching enforcement profiles: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_profile_templates(
    ctx: Context,
) -> dict | str:
    """Get a reference list of common ClearPass enforcement profile templates.

    Returns a curated set of standard enforcement profile patterns used in
    typical ClearPass deployments. These are reference templates, not live
    configurations from the server.
    """
    return {
        "templates": [
            {
                "name": "Corporate VLAN Assignment",
                "description": "Assigns authenticated corporate users to the corporate VLAN.",
                "type": "VLAN",
                "typical_attributes": ["Tunnel-Type", "Tunnel-Medium-Type", "Tunnel-Private-Group-ID"],
            },
            {
                "name": "Guest VLAN Assignment",
                "description": "Assigns guest users to an isolated guest VLAN with internet-only access.",
                "type": "VLAN",
                "typical_attributes": ["Tunnel-Type", "Tunnel-Medium-Type", "Tunnel-Private-Group-ID"],
            },
            {
                "name": "Deny Access",
                "description": "Rejects the authentication request, denying network access.",
                "type": "Deny",
                "typical_attributes": [],
            },
            {
                "name": "Bounce Host Port",
                "description": "Bounces the switch port to force re-authentication after a policy change.",
                "type": "Session Action",
                "typical_attributes": ["Aruba-Port-Bounce-Host"],
            },
            {
                "name": "Downloadable User Role",
                "description": "Pushes a downloadable user role (DUR) with ACLs to the network device.",
                "type": "DUR",
                "typical_attributes": ["Aruba-User-Role", "Aruba-NAS-Filter-Rule"],
            },
            {
                "name": "Posture Remediation",
                "description": "Redirects non-compliant endpoints to a remediation portal.",
                "type": "Redirect",
                "typical_attributes": ["url-redirect", "url-redirect-acl"],
            },
        ],
        "note": "These are reference templates. "
        "Use clearpass_get_enforcement_profiles to see actual configured profiles.",
    }
