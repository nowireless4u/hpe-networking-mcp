"""ClearPass policy elements write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE


async def _confirm_write(
    ctx: Context, action_type: str, resource: str, identifier: str | None, confirmed: bool
) -> dict | None:
    """Thin wrapper over :func:`middleware.elicitation.confirm_write`.

    Kept as a local helper so existing call sites don't change; the
    shared elicitation/decline/cancel logic now lives in the middleware
    (#148).
    """
    label = identifier or "unknown"
    return await confirm_write(ctx, f"ClearPass: {action_type} {resource} '{label}'. Confirm?")


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_service(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'delete', 'enable', or 'disable'.")],
    payload: Annotated[dict, Field(description="Service config payload. Empty dict {} for delete/enable/disable.")],
    config_service_id: Annotated[str | None, Field(description="Service ID (required for all except create).")] = None,
    name: Annotated[str | None, Field(description="Service name (alternative to ID for delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, delete, enable, or disable a ClearPass service.

    Args:
        action_type: Operation -- 'create', 'update', 'delete', 'enable', or 'disable'.
        payload: JSON config body. Required for create/update. Empty dict for others.
        config_service_id: Numeric service ID. Required for update/delete/enable/disable.
        name: Service name. Alternative to config_service_id for delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    valid = ("create", "update", "delete", "enable", "disable")
    if action_type not in valid:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."
    decline = await _confirm_write(ctx, action_type, "service", config_service_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if action_type == "create":
            return client._send_request("/config/service", "post", query=payload)
        if not config_service_id and not name:
            return "Either config_service_id or name is required."
        if action_type == "update":
            path = f"/config/service/{config_service_id}" if config_service_id else f"/config/service/name/{name}"
            return client._send_request(path, "patch", query=payload)
        if action_type == "enable":
            if not config_service_id:
                return "config_service_id is required for enable."
            return client.update_config_service_by_config_service_id_enable(config_service_id=config_service_id)
        if action_type == "disable":
            if not config_service_id:
                return "config_service_id is required for disable."
            return client.update_config_service_by_config_service_id_disable(config_service_id=config_service_id)
        # delete
        if config_service_id:
            return client.delete_config_service_by_config_service_id(config_service_id=config_service_id)
        return client.delete_config_service_name_by_name(name=name)
    except Exception as e:
        return f"Error managing service: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_device_group(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Device group config payload. Empty dict {} for delete.")],
    network_device_group_id: Annotated[
        str | None, Field(description="Device group ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Group name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass network device group.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        network_device_group_id: Numeric ID. Required for update/delete (or use name).
        name: Group name. Alternative to network_device_group_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "device group", network_device_group_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if action_type == "create":
            return client._send_request("/network-device-group", "post", query=payload)
        if not network_device_group_id and not name:
            return "Either network_device_group_id or name is required for update/delete."
        if action_type == "update":
            path = (
                f"/network-device-group/{network_device_group_id}"
                if network_device_group_id
                else f"/network-device-group/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if network_device_group_id:
            return client.delete_network_device_group_by_network_device_group_id(
                network_device_group_id=network_device_group_id
            )
        return client.delete_network_device_group_name_by_name(name=name)
    except Exception as e:
        return f"Error managing device group: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_posture_policy(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Posture policy config payload. Empty dict {} for delete.")],
    posture_policy_id: Annotated[
        str | None, Field(description="Posture policy ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Policy name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass posture policy.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        posture_policy_id: Numeric ID. Required for update/delete (or use name).
        name: Policy name. Alternative to posture_policy_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "posture policy", posture_policy_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if action_type == "create":
            return client._send_request("/posture-policy", "post", query=payload)
        if not posture_policy_id and not name:
            return "Either posture_policy_id or name is required for update/delete."
        if action_type == "update":
            path = f"/posture-policy/{posture_policy_id}" if posture_policy_id else f"/posture-policy/name/{name}"
            return client._send_request(path, "patch", query=payload)
        if posture_policy_id:
            return client.delete_posture_policy_by_posture_policy_id(posture_policy_id=posture_policy_id)
        return client.delete_posture_policy_name_by_name(name=name)
    except Exception as e:
        return f"Error managing posture policy: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_proxy_target(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Proxy target config payload. Empty dict {} for delete.")],
    proxy_target_id: Annotated[str | None, Field(description="Proxy target ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Target name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass proxy target.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        proxy_target_id: Numeric ID. Required for update/delete (or use name).
        name: Target name. Alternative to proxy_target_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "proxy target", proxy_target_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if action_type == "create":
            return client._send_request("/proxy-target", "post", query=payload)
        if not proxy_target_id and not name:
            return "Either proxy_target_id or name is required for update/delete."
        if action_type == "update":
            path = f"/proxy-target/{proxy_target_id}" if proxy_target_id else f"/proxy-target/name/{name}"
            return client._send_request(path, "patch", query=payload)
        if proxy_target_id:
            return client.delete_proxy_target_by_proxy_target_id(proxy_target_id=proxy_target_id)
        return client.delete_proxy_target_name_by_name(name=name)
    except Exception as e:
        return f"Error managing proxy target: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_radius_dictionary(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'delete', 'enable', or 'disable'.")],
    payload: Annotated[dict, Field(description="RADIUS dictionary config payload. Empty dict {} for delete.")],
    radius_dictionary_id: Annotated[
        str | None, Field(description="Dictionary ID (required for all except create).")
    ] = None,
    name: Annotated[str | None, Field(description="Dictionary name (alternative to ID for delete).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, delete, enable, or disable a ClearPass RADIUS dictionary.

    Args:
        action_type: Operation -- 'create', 'update', 'delete', 'enable', or 'disable'.
        payload: JSON config body. Required for create/update. Empty dict for others.
        radius_dictionary_id: Numeric ID. Required for update/delete/enable/disable.
        name: Dictionary name. Alternative to radius_dictionary_id for delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    valid = ("create", "update", "delete", "enable", "disable")
    if action_type not in valid:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."
    decline = await _confirm_write(ctx, action_type, "RADIUS dictionary", radius_dictionary_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if action_type == "create":
            return client._send_request("/radius-dictionary", "post", query=payload)
        if not radius_dictionary_id and not name:
            return "Either radius_dictionary_id or name is required."
        if action_type == "update":
            path = (
                f"/radius-dictionary/{radius_dictionary_id}"
                if radius_dictionary_id
                else f"/radius-dictionary/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if action_type == "enable":
            if not radius_dictionary_id:
                return "radius_dictionary_id is required for enable."
            return client.update_radius_dictionary_by_radius_dictionary_id_enable(
                radius_dictionary_id=radius_dictionary_id
            )
        if action_type == "disable":
            if not radius_dictionary_id:
                return "radius_dictionary_id is required for disable."
            return client.update_radius_dictionary_by_radius_dictionary_id_disable(
                radius_dictionary_id=radius_dictionary_id
            )
        # delete
        if radius_dictionary_id:
            return client._send_request(f"/radius-dictionary/{radius_dictionary_id}", "delete")
        return client._send_request(f"/radius-dictionary/name/{name}", "delete")
    except Exception as e:
        return f"Error managing RADIUS dictionary: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_tacacs_dictionary(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="TACACS dictionary config payload. Empty dict {} for delete.")],
    tacacs_dictionary_id: Annotated[
        str | None, Field(description="Dictionary ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Dictionary name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass TACACS dictionary.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        tacacs_dictionary_id: Numeric ID. Required for update/delete (or use name).
        name: Dictionary name. Alternative to tacacs_dictionary_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(ctx, action_type, "TACACS dictionary", tacacs_dictionary_id or name, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if action_type == "create":
            return client._send_request("/tacacs-dictionary", "post", query=payload)
        if not tacacs_dictionary_id and not name:
            return "Either tacacs_dictionary_id or name is required for update/delete."
        if action_type == "update":
            path = (
                f"/tacacs-dictionary/{tacacs_dictionary_id}"
                if tacacs_dictionary_id
                else f"/tacacs-dictionary/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if tacacs_dictionary_id:
            return client._send_request(f"/tacacs-dictionary/{tacacs_dictionary_id}", "delete")
        return client._send_request(f"/tacacs-dictionary/name/{name}", "delete")
    except Exception as e:
        return f"Error managing TACACS dictionary: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_application_dictionary(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Application dictionary config payload. Empty dict {} for delete.")],
    application_dictionary_id: Annotated[
        str | None, Field(description="Dictionary ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Dictionary name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass application dictionary.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        application_dictionary_id: Numeric ID. Required for update/delete (or use name).
        name: Dictionary name. Alternative to application_dictionary_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'."
    decline = await _confirm_write(
        ctx, action_type, "application dictionary", application_dictionary_id or name, confirmed
    )
    if decline:
        return decline
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        if action_type == "create":
            return client._send_request("/application-dictionary", "post", query=payload)
        if not application_dictionary_id and not name:
            return "Either application_dictionary_id or name is required for update/delete."
        if action_type == "update":
            path = (
                f"/application-dictionary/{application_dictionary_id}"
                if application_dictionary_id
                else f"/application-dictionary/name/{name}"
            )
            return client._send_request(path, "patch", query=payload)
        if application_dictionary_id:
            return client._send_request(f"/application-dictionary/{application_dictionary_id}", "delete")
        return client._send_request(f"/application-dictionary/name/{name}", "delete")
    except Exception as e:
        return f"Error managing application dictionary: {e}"
