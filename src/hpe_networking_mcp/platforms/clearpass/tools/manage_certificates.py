"""ClearPass certificate management write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import ClearPassClient, get_clearpass_client

_CERT_ACTIONS = (
    "import_trust_list",
    "delete_trust_list",
    "delete_client_cert",
    "enable_server_cert",
    "disable_server_cert",
)


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_certificate(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(
            description="Action: 'import_trust_list', 'delete_trust_list', 'delete_client_cert', "
            "'enable_server_cert', or 'disable_server_cert'."
        ),
    ],
    payload: Annotated[
        dict,
        Field(description="Certificate payload. For import: cert data. For delete/enable/disable: empty dict {}."),
    ],
    cert_id: Annotated[
        str | None,
        Field(description="Certificate ID (required for delete_trust_list, delete_client_cert)."),
    ] = None,
    server_uuid: Annotated[
        str | None,
        Field(description="Server UUID (required for enable/disable_server_cert)."),
    ] = None,
    service_name: Annotated[
        str | None,
        Field(description="Service name (required for enable/disable_server_cert, e.g. 'RADIUS', 'HTTPS')."),
    ] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Manage ClearPass certificates (trust lists, client certs, server certs).

    Actions:
        import_trust_list: Import a CA certificate into the trust list. Payload requires cert_file data.
        delete_trust_list: Remove a CA certificate from the trust list by cert_id.
        delete_client_cert: Remove a client certificate by cert_id.
        enable_server_cert: Enable a server certificate for a service (requires server_uuid and service_name).
        disable_server_cert: Disable a server certificate for a service (requires server_uuid and service_name).

    Args:
        action_type: Certificate operation to perform.
        payload: Certificate data for import. Empty dict for other actions.
        cert_id: Certificate ID. Required for delete_trust_list and delete_client_cert.
        server_uuid: Server UUID. Required for enable/disable_server_cert.
        service_name: Service name (e.g. 'RADIUS', 'HTTPS'). Required for enable/disable_server_cert.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in _CERT_ACTIONS:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_CERT_ACTIONS)}.",
            }
        )

    try:
        client = await get_clearpass_client()
        return await _execute_cert_action(client, action_type, payload, cert_id, server_uuid, service_name)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing certificate: {e}"}) from e


async def _execute_cert_action(
    client: ClearPassClient,
    action_type: str,
    payload: dict,
    cert_id: str | None,
    server_uuid: str | None,
    service_name: str | None,
) -> dict | str:
    """Execute the resolved certificate action.

    Args:
        client: ClearPassClient instance.
        action_type: Certificate operation to perform.
        payload: Certificate data payload.
        cert_id: Certificate ID for delete operations.
        server_uuid: Server UUID for enable/disable operations.
        service_name: Service name for enable/disable operations.

    Returns:
        API response dict or error string.
    """
    if action_type == "import_trust_list":
        return await client.request("post", "/cert-trust-list", json_body=payload)

    if action_type == "delete_trust_list":
        if not cert_id:
            raise ToolError({"status_code": 400, "message": "cert_id is required for delete_trust_list."})
        return await client.request("delete", f"/cert-trust-list/{cert_id}")

    if action_type == "delete_client_cert":
        if not cert_id:
            raise ToolError({"status_code": 400, "message": "cert_id is required for delete_client_cert."})
        return await client.request("delete", f"/client-cert/{cert_id}")

    if action_type in ("enable_server_cert", "disable_server_cert"):
        if not server_uuid or not service_name:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": "server_uuid and service_name are required for enable/disable_server_cert.",
                }
            )
        action = "enable" if action_type == "enable_server_cert" else "disable"
        path = f"/server-cert/name/{server_uuid}/{service_name}/{action}"
        return await client.request("patch", path, json_body={})

    raise ToolError({"status_code": 500, "message": f"Unhandled action_type: {action_type}"})


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_create_csr(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description="CSR subject parameters. Include fields like common_name, organization, "
            "organizational_unit, locality, state, country, san_dns, san_ip."
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
    """Generate a Certificate Signing Request (CSR) on ClearPass.

    Creates a CSR with the specified subject parameters. The CSR can then be
    submitted to a Certificate Authority for signing.

    Args:
        payload: CSR subject fields. Must include common_name at minimum.
            Supported fields: common_name, organization, organizational_unit,
            locality, state, country, san_dns (list), san_ip (list).
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_clearpass_client()
        return await client.request("post", "/certificate/csr", json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error creating CSR: {e}"}) from e
