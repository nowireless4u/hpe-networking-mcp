"""ClearPass certificate management write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE

_CERT_ACTIONS = (
    "import_trust_list",
    "delete_trust_list",
    "delete_client_cert",
    "enable_server_cert",
    "disable_server_cert",
)


async def _confirm_write(ctx: Context, action: str, identifier: str | None) -> dict | None:
    """Request user confirmation for destructive certificate actions.

    Args:
        ctx: FastMCP context.
        action: The operation being performed.
        identifier: Item ID for display.

    Returns:
        Error dict if declined/canceled, None if accepted.
    """
    label = identifier or "unknown"
    elicit = await elicitation_handler(
        message=f"ClearPass: {action} certificate '{label}'. Confirm?",
        ctx=ctx,
    )
    if elicit.action == "decline":
        mode = await ctx.get_state("elicitation_mode")
        if mode == "chat_confirm":
            return {
                "status": "confirmation_required",
                "message": f"Please confirm {action} of certificate '{label}'. "
                "Call this tool again with confirmed=true after the user confirms.",
            }
        return {"message": "Action declined by user."}
    elif elicit.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
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
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
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
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in _CERT_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_CERT_ACTIONS)}."

    if not confirmed:
        identifier = cert_id or server_uuid or "certificate"
        decline = await _confirm_write(ctx, action_type.replace("_", " "), identifier)
        if decline:
            return decline

    try:
        from pyclearpass.api_certificateauthority import ApiCertificateAuthority

        client = await get_clearpass_session(ApiCertificateAuthority)
        return _execute_cert_action(client, action_type, payload, cert_id, server_uuid, service_name)
    except Exception as e:
        return f"Error managing certificate: {e}"


def _execute_cert_action(
    client,
    action_type: str,
    payload: dict,
    cert_id: str | None,
    server_uuid: str | None,
    service_name: str | None,
) -> dict | str:
    """Execute the resolved certificate action.

    Args:
        client: pyclearpass ApiCertificateAuthority instance.
        action_type: Certificate operation to perform.
        payload: Certificate data payload.
        cert_id: Certificate ID for delete operations.
        server_uuid: Server UUID for enable/disable operations.
        service_name: Service name for enable/disable operations.

    Returns:
        API response dict or error string.
    """
    if action_type == "import_trust_list":
        return client._send_request("/cert-trust-list", "post", query=payload)

    if action_type == "delete_trust_list":
        if not cert_id:
            return "cert_id is required for delete_trust_list."
        return client.delete_cert_trust_list_by_cert_trust_list_id(cert_trust_list_id=cert_id)

    if action_type == "delete_client_cert":
        if not cert_id:
            return "cert_id is required for delete_client_cert."
        return client.delete_client_cert_by_client_cert_id(client_cert_id=cert_id)

    if action_type in ("enable_server_cert", "disable_server_cert"):
        if not server_uuid or not service_name:
            return "server_uuid and service_name are required for enable/disable_server_cert."
        action = "enable" if action_type == "enable_server_cert" else "disable"
        path = f"/server-cert/name/{server_uuid}/{service_name}/{action}"
        return client._send_request(path, "patch", query={})

    return f"Unhandled action_type: {action_type}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_create_csr(
    ctx: Context,
    payload: Annotated[
        dict,
        Field(
            description="CSR subject parameters. Include fields like common_name, organization, "
            "organizational_unit, locality, state, country, san_dns, san_ip."
        ),
    ],
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Generate a Certificate Signing Request (CSR) on ClearPass.

    Creates a CSR with the specified subject parameters. The CSR can then be
    submitted to a Certificate Authority for signing.

    Args:
        payload: CSR subject fields. Must include common_name at minimum.
            Supported fields: common_name, organization, organizational_unit,
            locality, state, country, san_dns (list), san_ip (list).
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if not confirmed:
        cn = payload.get("common_name", "unknown")
        decline = await _confirm_write(ctx, "generate CSR", cn)
        if decline:
            return decline

    try:
        from pyclearpass.api_certificateauthority import ApiCertificateAuthority

        client = await get_clearpass_session(ApiCertificateAuthority)
        return client._send_request("/certificate/csr", "post", query=payload)
    except Exception as e:
        return f"Error creating CSR: {e}"
