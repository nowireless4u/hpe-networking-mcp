"""ClearPass policy elements write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_service(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'delete', 'enable', or 'disable'.")],
    payload: Annotated[dict, Field(description="Service config payload. Empty dict {} for delete/enable/disable.")],
    config_service_id: Annotated[str | None, Field(description="Service ID (required for all except create).")] = None,
    name: Annotated[str | None, Field(description="Service name (alternative to ID for delete).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, delete, enable, or disable a ClearPass service.

    Args:
        action_type: Operation -- 'create', 'update', 'delete', 'enable', or 'disable'.
        payload: JSON config body. Required for create/update. Empty dict for others.
        config_service_id: Numeric service ID. Required for update/delete/enable/disable.
        name: Service name. Alternative to config_service_id for delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    valid = ("create", "update", "delete", "enable", "disable")
    if action_type not in valid:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."}
        )
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/config/service", json_body=payload)
        if not config_service_id and not name:
            raise ToolError({"status_code": 400, "message": "Either config_service_id or name is required."})
        if action_type == "update":
            path = f"/config/service/{config_service_id}" if config_service_id else f"/config/service/name/{name}"
            return await client.request("patch", path, json_body=payload)
        if action_type == "enable":
            if not config_service_id:
                raise ToolError({"status_code": 400, "message": "config_service_id is required for enable."})
            return await client.request("patch", f"/config/service/{config_service_id}/enable")
        if action_type == "disable":
            if not config_service_id:
                raise ToolError({"status_code": 400, "message": "config_service_id is required for disable."})
            return await client.request("patch", f"/config/service/{config_service_id}/disable")
        # delete
        if config_service_id:
            return await client.request("delete", f"/config/service/{config_service_id}")
        return await client.request("delete", f"/config/service/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing service: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_device_group(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Device group config payload. Empty dict {} for delete.")],
    network_device_group_id: Annotated[
        str | None, Field(description="Device group ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Group name (alternative to ID).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass network device group.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        network_device_group_id: Numeric ID. Required for update/delete (or use name).
        name: Group name. Alternative to network_device_group_id.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/network-device-group", json_body=payload)
        if not network_device_group_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either network_device_group_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/network-device-group/{network_device_group_id}"
                if network_device_group_id
                else f"/network-device-group/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if network_device_group_id:
            return await client.request("delete", f"/network-device-group/{network_device_group_id}")
        return await client.request("delete", f"/network-device-group/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing device group: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_posture_policy(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Posture policy config payload. Empty dict {} for delete.")],
    posture_policy_id: Annotated[
        str | None, Field(description="Posture policy ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Policy name (alternative to ID).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass posture policy.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        posture_policy_id: Numeric ID. Required for update/delete (or use name).
        name: Policy name. Alternative to posture_policy_id.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/posture-policy", json_body=payload)
        if not posture_policy_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either posture_policy_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = f"/posture-policy/{posture_policy_id}" if posture_policy_id else f"/posture-policy/name/{name}"
            return await client.request("patch", path, json_body=payload)
        if posture_policy_id:
            return await client.request("delete", f"/posture-policy/{posture_policy_id}")
        return await client.request("delete", f"/posture-policy/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing posture policy: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_proxy_target(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Proxy target config payload. Empty dict {} for delete.")],
    proxy_target_id: Annotated[str | None, Field(description="Proxy target ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Target name (alternative to ID).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass proxy target.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        proxy_target_id: Numeric ID. Required for update/delete (or use name).
        name: Target name. Alternative to proxy_target_id.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/proxy-target", json_body=payload)
        if not proxy_target_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either proxy_target_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = f"/proxy-target/{proxy_target_id}" if proxy_target_id else f"/proxy-target/name/{name}"
            return await client.request("patch", path, json_body=payload)
        if proxy_target_id:
            return await client.request("delete", f"/proxy-target/{proxy_target_id}")
        return await client.request("delete", f"/proxy-target/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing proxy target: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_radius_dictionary(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'delete', 'enable', or 'disable'.")],
    payload: Annotated[dict, Field(description="RADIUS dictionary config payload. Empty dict {} for delete.")],
    radius_dictionary_id: Annotated[
        str | None, Field(description="Dictionary ID (required for all except create).")
    ] = None,
    name: Annotated[str | None, Field(description="Dictionary name (alternative to ID for delete).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, delete, enable, or disable a ClearPass RADIUS dictionary.

    Args:
        action_type: Operation -- 'create', 'update', 'delete', 'enable', or 'disable'.
        payload: JSON config body. Required for create/update. Empty dict for others.
        radius_dictionary_id: Numeric ID. Required for update/delete/enable/disable.
        name: Dictionary name. Alternative to radius_dictionary_id for delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    valid = ("create", "update", "delete", "enable", "disable")
    if action_type not in valid:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."}
        )
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/radius-dictionary", json_body=payload)
        if not radius_dictionary_id and not name:
            raise ToolError({"status_code": 400, "message": "Either radius_dictionary_id or name is required."})
        if action_type == "update":
            path = (
                f"/radius-dictionary/{radius_dictionary_id}"
                if radius_dictionary_id
                else f"/radius-dictionary/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if action_type == "enable":
            if not radius_dictionary_id:
                raise ToolError({"status_code": 400, "message": "radius_dictionary_id is required for enable."})
            return await client.request("patch", f"/radius-dictionary/{radius_dictionary_id}/enable")
        if action_type == "disable":
            if not radius_dictionary_id:
                raise ToolError({"status_code": 400, "message": "radius_dictionary_id is required for disable."})
            return await client.request("patch", f"/radius-dictionary/{radius_dictionary_id}/disable")
        # delete
        if radius_dictionary_id:
            return await client.request("delete", f"/radius-dictionary/{radius_dictionary_id}")
        return await client.request("delete", f"/radius-dictionary/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing RADIUS dictionary: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_tacacs_dictionary(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="TACACS dictionary config payload. Empty dict {} for delete.")],
    tacacs_dictionary_id: Annotated[
        str | None, Field(description="Dictionary ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Dictionary name (alternative to ID).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass TACACS dictionary.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        tacacs_dictionary_id: Numeric ID. Required for update/delete (or use name).
        name: Dictionary name. Alternative to tacacs_dictionary_id.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/tacacs-dictionary", json_body=payload)
        if not tacacs_dictionary_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either tacacs_dictionary_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/tacacs-dictionary/{tacacs_dictionary_id}"
                if tacacs_dictionary_id
                else f"/tacacs-dictionary/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if tacacs_dictionary_id:
            return await client.request("delete", f"/tacacs-dictionary/{tacacs_dictionary_id}")
        return await client.request("delete", f"/tacacs-dictionary/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing TACACS dictionary: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_application_dictionary(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Application dictionary config payload. Empty dict {} for delete.")],
    application_dictionary_id: Annotated[
        str | None, Field(description="Dictionary ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Dictionary name (alternative to ID).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass application dictionary.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        application_dictionary_id: Numeric ID. Required for update/delete (or use name).
        name: Dictionary name. Alternative to application_dictionary_id.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/application-dictionary", json_body=payload)
        if not application_dictionary_id and not name:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": "Either application_dictionary_id or name is required for update/delete.",
                }
            )
        if action_type == "update":
            path = (
                f"/application-dictionary/{application_dictionary_id}"
                if application_dictionary_id
                else f"/application-dictionary/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if application_dictionary_id:
            return await client.request("delete", f"/application-dictionary/{application_dictionary_id}")
        return await client.request("delete", f"/application-dictionary/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing application dictionary: {e}"}) from e
