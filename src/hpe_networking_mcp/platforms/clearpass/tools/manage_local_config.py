"""ClearPass local server configuration write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_access_control(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'update' or 'delete'.")],
    server_uuid: Annotated[str, Field(description="Server UUID.")],
    resource_name: Annotated[str, Field(description="Access control resource name.")],
    payload: Annotated[dict, Field(description="Access control config payload. Empty dict {} for delete.")],
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Update or delete a ClearPass server access control entry.

    Args:
        action_type: Operation -- 'update' or 'delete'.
        server_uuid: UUID of the target server.
        resource_name: Name of the access control resource.
        payload: JSON config body. Required for update. Empty dict for delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("update", "delete"):
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be 'update' or 'delete'."}
        )
    try:
        client = await get_clearpass_client()
        if action_type == "update":
            return await client.request(
                "put", f"/server/access-control/{path_seg(server_uuid)}/{path_seg(resource_name)}", json_body=payload
            )
        return await client.request(
            "delete", f"/server/access-control/{path_seg(server_uuid)}/{path_seg(resource_name)}"
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing access control: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_ad_domain(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'join', 'leave', or 'configure_password_servers'.")],
    server_uuid: Annotated[str, Field(description="Server UUID.")],
    payload: Annotated[dict, Field(description="AD domain config payload. Empty dict {} for join/leave.")],
    netbios_name: Annotated[
        str | None, Field(description="NetBIOS name (required for configure_password_servers).")
    ] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Join, leave, or configure password servers for an Active Directory domain.

    Args:
        action_type: Operation -- 'join', 'leave', or 'configure_password_servers'.
        server_uuid: UUID of the ClearPass server.
        payload: JSON config body. Domain credentials for join, empty for leave.
        netbios_name: NetBIOS domain name (required for configure_password_servers).
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    valid = ("join", "leave", "configure_password_servers")
    if action_type not in valid:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."}
        )
    try:
        client = await get_clearpass_client()
        if action_type == "join":
            return await client.request("put", f"/ad-domain/join/{path_seg(server_uuid)}", json_body=payload)
        if action_type == "leave":
            return await client.request("put", f"/ad-domain/leave/{path_seg(server_uuid)}", json_body=payload)
        if not netbios_name:
            raise ToolError({"status_code": 400, "message": "netbios_name is required for configure_password_servers."})
        return await client.request(
            "patch",
            f"/ad-domain/password-servers/{path_seg(server_uuid)}",
            json_body={"netbios_name": netbios_name, **payload},
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing AD domain: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_cluster_server(
    ctx: Context,
    server_uuid: Annotated[str, Field(description="Server UUID to update.")],
    payload: Annotated[dict, Field(description="Cluster server config payload.")],
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Update a ClearPass cluster server configuration.

    Args:
        server_uuid: UUID of the cluster server to update.
        payload: JSON config body with server settings.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_clearpass_client()
        return await client.request("patch", f"/cluster/server/{path_seg(server_uuid)}", json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing cluster server: {e}"}) from e


@tool(capability=Capability.OPERATIONAL, enable_gated=True)
async def clearpass_manage_server_service(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'start' or 'stop'.")],
    server_uuid: Annotated[str, Field(description="Server UUID.")],
    service_name: Annotated[str, Field(description="Name of the service to start or stop.")],
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Start or stop a ClearPass server service.

    Args:
        action_type: Operation -- 'start' or 'stop'.
        server_uuid: UUID of the ClearPass server.
        service_name: Name of the service (e.g. 'ClearPass Policy Server').
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("start", "stop"):
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be 'start' or 'stop'."}
        )
    try:
        client = await get_clearpass_client()
        if action_type == "start":
            return await client.request(
                "patch", f"/server/service/{path_seg(server_uuid)}/{path_seg(service_name)}/start"
            )
        return await client.request("patch", f"/server/service/{path_seg(server_uuid)}/{path_seg(service_name)}/stop")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing server service: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_service_params(
    ctx: Context,
    server_uuid: Annotated[str, Field(description="UUID of the ClearPass server node.")],
    service_id: Annotated[
        str,
        Field(description="Numeric service ID (NOT service name). Get via clearpass_get_server_services."),
    ],
    param_values: Annotated[
        dict,
        Field(
            description=(
                "PATCH body containing the service parameters to update. "
                "Shape mirrors the structure returned by clearpass_get_server_services."
            ),
        ),
    ],
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Edit per-server service parameters (PATCH /api/server/{uuid}/service/{id}).

    Use this to change a service's runtime parameter values on a single
    cluster node. Common audit pattern — answer "are all servers in the
    cluster configured the same?" by:

    1. ``clearpass_get_cluster_servers`` for the list of UUIDs.
    2. ``clearpass_get_server_services(server_uuid=...)`` per node.
    3. Compare param values across nodes (in code mode this is one
       ``execute`` call).
    4. If a node drifts, call this tool to align it.

    See: https://developer.arubanetworks.com/cppm/reference
    (Local Server Configuration → /server/{server_uuid}/service/{service_id})

    Args:
        server_uuid: UUID of the ClearPass server node.
        service_id: Numeric service ID (the integer one, not the name).
        param_values: PATCH body with the param structure to apply.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_clearpass_client()
        return await client.request(
            "patch", f"/service-parameter/{path_seg(server_uuid)}/{path_seg(service_id)}", json_body=param_values
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error editing service params: {e}"}) from e
