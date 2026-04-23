"""ClearPass enforcement policy and profile write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE


async def _confirm_write(ctx: Context, action: str, identifier: str | None) -> dict | None:
    """Thin wrapper over :func:`middleware.elicitation.confirm_write`.

    Kept as a local helper so existing call sites don't change; the
    shared elicitation/decline/cancel logic now lives in the middleware
    (#148).
    """
    label = identifier or "unknown"
    return await confirm_write(ctx, f"ClearPass: {action} '{label}'. Confirm?")


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_enforcement_policy(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Enforcement policy config payload. For delete: empty dict {}.")],
    policy_id: Annotated[str | None, Field(description="Policy ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Policy name (alternative to ID for update/delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass enforcement policy.

    Enforcement policies define the rules that determine which enforcement profile
    to apply based on conditions like role, posture, or authentication method.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        policy_id: Numeric ID. Required for update/delete (or use name).
        name: Policy name. Alternative to policy_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} enforcement policy", policy_id or name)
        if decline:
            return decline

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)

        if action_type == "create":
            return client._send_request("/enforcement-policy", "post", query=payload)
        if not policy_id and not name:
            return "Either policy_id or name is required for update/delete."
        if action_type == "update":
            if policy_id:
                return client._send_request(f"/enforcement-policy/{policy_id}", "patch", query=payload)
            return client._send_request(f"/enforcement-policy/name/{name}", "patch", query=payload)
        # delete
        if policy_id:
            return client.delete_enforcement_policy_by_enforcement_policy_id(enforcement_policy_id=policy_id)
        return client.delete_enforcement_policy_name_by_name(name=name)
    except Exception as e:
        return f"Error managing enforcement policy: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_enforcement_profile(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Enforcement profile config payload. For delete: empty dict {}.")],
    profile_id: Annotated[str | None, Field(description="Profile ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Profile name (alternative to ID for update/delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass enforcement profile.

    Enforcement profiles define the actions taken when a policy rule matches,
    such as assigning a VLAN, applying a downloadable ACL, or sending RADIUS attributes.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        profile_id: Numeric ID. Required for update/delete (or use name).
        name: Profile name. Alternative to profile_id for update/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} enforcement profile", profile_id or name)
        if decline:
            return decline

    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)

        if action_type == "create":
            return client._send_request("/enforcement-profile", "post", query=payload)
        if not profile_id and not name:
            return "Either profile_id or name is required for update/delete."
        if action_type == "update":
            if profile_id:
                return client._send_request(f"/enforcement-profile/{profile_id}", "patch", query=payload)
            return client._send_request(f"/enforcement-profile/name/{name}", "patch", query=payload)
        # delete
        if profile_id:
            return client.delete_enforcement_profile_by_enforcement_profile_id(enforcement_profile_id=profile_id)
        return client.delete_enforcement_profile_name_by_name(name=name)
    except Exception as e:
        return f"Error managing enforcement profile: {e}"
