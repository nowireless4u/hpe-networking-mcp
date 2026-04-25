"""ClearPass local server configuration write tools."""

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
async def clearpass_manage_access_control(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'update' or 'delete'.")],
    server_uuid: Annotated[str, Field(description="Server UUID.")],
    resource_name: Annotated[str, Field(description="Access control resource name.")],
    payload: Annotated[dict, Field(description="Access control config payload. Empty dict {} for delete.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Update or delete a ClearPass server access control entry.

    Args:
        action_type: Operation -- 'update' or 'delete'.
        server_uuid: UUID of the target server.
        resource_name: Name of the access control resource.
        payload: JSON config body. Required for update. Empty dict for delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("update", "delete"):
        return f"Invalid action_type '{action_type}'. Must be 'update' or 'delete'."
    decline = await _confirm_write(ctx, action_type, "access control", f"{server_uuid}/{resource_name}", confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        if action_type == "update":
            return client._send_request(f"/server/access-control/{server_uuid}/{resource_name}", "patch", query=payload)
        return client.delete_server_access_control_by_server_uuid_resource_name(
            server_uuid=server_uuid, resource_name=resource_name
        )
    except Exception as e:
        return f"Error managing access control: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_ad_domain(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'join', 'leave', or 'configure_password_servers'.")],
    server_uuid: Annotated[str, Field(description="Server UUID.")],
    payload: Annotated[dict, Field(description="AD domain config payload. Empty dict {} for join/leave.")],
    netbios_name: Annotated[
        str | None, Field(description="NetBIOS name (required for configure_password_servers).")
    ] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Join, leave, or configure password servers for an Active Directory domain.

    Args:
        action_type: Operation -- 'join', 'leave', or 'configure_password_servers'.
        server_uuid: UUID of the ClearPass server.
        payload: JSON config body. Domain credentials for join, empty for leave.
        netbios_name: NetBIOS domain name (required for configure_password_servers).
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    valid = ("join", "leave", "configure_password_servers")
    if action_type not in valid:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."
    decline = await _confirm_write(ctx, action_type, "AD domain", server_uuid, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        if action_type == "join":
            return client._send_request(f"/ad-domain/{server_uuid}/join", "put", query=payload)
        if action_type == "leave":
            return client._send_request(f"/ad-domain/{server_uuid}/leave", "put", query=payload)
        if not netbios_name:
            return "netbios_name is required for configure_password_servers."
        return client._send_request(
            f"/ad-domain/{server_uuid}/netbios-name/{netbios_name}/password-servers", "patch", query=payload
        )
    except Exception as e:
        return f"Error managing AD domain: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_cluster_server(
    ctx: Context,
    server_uuid: Annotated[str, Field(description="Server UUID to update.")],
    payload: Annotated[dict, Field(description="Cluster server config payload.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Update a ClearPass cluster server configuration.

    Args:
        server_uuid: UUID of the cluster server to update.
        payload: JSON config body with server settings.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    decline = await _confirm_write(ctx, "update", "cluster server", server_uuid, confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        return client._send_request(f"/cluster/server/{server_uuid}", "patch", query=payload)
    except Exception as e:
        return f"Error managing cluster server: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_server_service(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'start' or 'stop'.")],
    server_uuid: Annotated[str, Field(description="Server UUID.")],
    service_name: Annotated[str, Field(description="Name of the service to start or stop.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Start or stop a ClearPass server service.

    Args:
        action_type: Operation -- 'start' or 'stop'.
        server_uuid: UUID of the ClearPass server.
        service_name: Name of the service (e.g. 'ClearPass Policy Server').
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("start", "stop"):
        return f"Invalid action_type '{action_type}'. Must be 'start' or 'stop'."
    decline = await _confirm_write(ctx, action_type, "server service", f"{service_name}@{server_uuid}", confirmed)
    if decline:
        return decline
    try:
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        if action_type == "start":
            return client.update_server_service_by_server_uuid_service_name_start(
                server_uuid=server_uuid, service_name=service_name
            )
        return client.update_server_service_by_server_uuid_service_name_stop(
            server_uuid=server_uuid, service_name=service_name
        )
    except Exception as e:
        return f"Error managing server service: {e}"


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
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
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    decline = await _confirm_write(
        ctx,
        "edit_params",
        "server service",
        f"service_id={service_id}@{server_uuid}",
        confirmed,
    )
    if decline:
        return decline
    try:
        from pyclearpass.api_localserverconfiguration import ApiLocalServerConfiguration

        client = await get_clearpass_session(ApiLocalServerConfiguration)
        path = f"/server/{server_uuid}/service/{service_id}"
        return client._send_request(path, "patch", query=param_values)
    except Exception as e:
        return f"Error editing service params: {e}"
