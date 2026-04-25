"""ClearPass internal Certificate Authority (CA) write tools.

Covers the CA cert lifecycle (``/api/certificate/...``: import, new,
request, sign, revoke, reject, export, delete) and onboarded
device/user record management (``/api/onboard/device/{id}`` and
``/api/onboard/user/{id}``).

These operate against ClearPass's internal CA. Many deployments use an
external CA, in which case this surface is inert. Use the read tools
in ``certificate_authority.py`` to discover what's there before
mutating.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE

_CA_ACTIONS = (
    "import",
    "new",
    "request",
    "sign",
    "revoke",
    "reject",
    "export",
    "delete",
)


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_certificate_authority(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(
            description=(
                "CA action: 'import' (POST /api/certificate/import), "
                "'new' (POST /api/certificate/new — create a new cert), "
                "'request' (POST /api/certificate/request — sign a CSR), "
                "'sign' (POST /api/certificate/{id}/sign), "
                "'revoke' (POST /api/certificate/{id}/revoke), "
                "'reject' (POST /api/certificate/{id}/reject), "
                "'export' (POST /api/certificate/{id}/export), "
                "'delete' (DELETE /api/certificate/{id})."
            ),
        ),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Body for the action. For import: cert PEM and metadata. "
                "For new/request: subject + key options. For sign/revoke/reject/export/delete: typically empty {}."
            ),
        ),
    ],
    certificate_id: Annotated[
        str | None,
        Field(description="Cert ID. Required for sign, revoke, reject, export, delete."),
    ] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Manage ClearPass internal-CA certificates.

    The CA endpoints handle the full cert lifecycle: import existing
    certs, generate new ones, sign CSRs, revoke/reject pending requests,
    export, delete. Most operations target a specific cert by
    ``certificate_id``; ``import``, ``new``, and ``request`` create new
    records and don't take a ``certificate_id``.

    See: https://developer.arubanetworks.com/cppm/reference (Certificate Authority)

    Args:
        action_type: One of ``import``, ``new``, ``request``, ``sign``,
            ``revoke``, ``reject``, ``export``, ``delete``.
        payload: Request body. Varies by action — empty dict ``{}`` is
            fine for delete/sign/revoke/reject/export.
        certificate_id: Cert ID. Required for sign/revoke/reject/export/delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in _CA_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_CA_ACTIONS)}."
    if action_type in ("sign", "revoke", "reject", "export", "delete") and not certificate_id:
        return f"certificate_id is required for action '{action_type}'."

    decline = await confirm_write(ctx, f"ClearPass CA: {action_type} certificate {certificate_id or '(new)'}. Confirm?")
    if decline:
        return decline

    try:
        from pyclearpass.api_certificateauthority import ApiCertificateAuthority

        client = await get_clearpass_session(ApiCertificateAuthority)

        if action_type == "import":
            return client._send_request("/certificate/import", "post", query=payload)
        if action_type == "new":
            return client._send_request("/certificate/new", "post", query=payload)
        if action_type == "request":
            return client._send_request("/certificate/request", "post", query=payload)
        if action_type == "delete":
            return client._send_request(f"/certificate/{certificate_id}", "delete")
        # sign / revoke / reject / export
        return client._send_request(f"/certificate/{certificate_id}/{action_type}", "post", query=payload)
    except Exception as e:
        return f"Error managing CA certificate ({action_type}): {e}"


_ONBOARD_ACTIONS = ("update", "delete")


@tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_onboard_device(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(description="Action: 'update' (PATCH) or 'delete'."),
    ],
    record_id: Annotated[str, Field(description="Numeric ID of the onboard device record.")],
    payload: Annotated[
        dict | None,
        Field(description="PATCH body for update. Empty dict or omit for delete."),
    ] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Update or delete a ClearPass onboard device record.

    Onboard records track devices that received a CA-issued cert via the
    onboarding workflow. Updating typically touches metadata or
    revocation state; deletion removes the record (the underlying cert
    is handled separately via ``clearpass_manage_certificate_authority``
    if it needs revoking).

    See: https://developer.arubanetworks.com/cppm/reference
    (Certificate Authority → /onboard/device)

    Args:
        action_type: 'update' (PATCH) or 'delete'.
        record_id: Numeric ID of the onboard device record.
        payload: PATCH body. Required for update, ignored for delete.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in _ONBOARD_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be 'update' or 'delete'."
    if action_type == "update" and not payload:
        return "payload is required for action 'update'."

    decline = await confirm_write(
        ctx,
        f"ClearPass: {action_type} onboard device record {record_id}. Confirm?",
    )
    if decline:
        return decline

    try:
        from pyclearpass.api_certificateauthority import ApiCertificateAuthority

        client = await get_clearpass_session(ApiCertificateAuthority)
        path = f"/onboard/device/{record_id}"
        if action_type == "delete":
            return client._send_request(path, "delete")
        body: Any = payload if payload is not None else {}
        return client._send_request(path, "patch", query=body)
    except Exception as e:
        return f"Error managing onboard device ({action_type}): {e}"
