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
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client

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


@tool(capability=Capability.WRITE_DELETE)
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
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
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
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in _CA_ACTIONS:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_CA_ACTIONS)}.",
            }
        )
    if action_type in ("sign", "revoke", "reject", "export", "delete") and not certificate_id:
        raise ToolError({"status_code": 400, "message": f"certificate_id is required for action '{action_type}'."})

    try:
        client = await get_clearpass_client()

        if action_type == "import":
            return await client.request("post", "/certificate/import", json_body=payload)
        if action_type == "new":
            return await client.request("post", "/certificate/new", json_body=payload)
        if action_type == "request":
            return await client.request("post", "/certificate/request", json_body=payload)
        if action_type == "delete":
            return await client.request("delete", f"/certificate/{certificate_id}")
        # sign / revoke / reject / export
        return await client.request("post", f"/certificate/{certificate_id}/{action_type}", json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing CA certificate ({action_type}): {e}"}) from e


_ONBOARD_ACTIONS = ("update", "delete")


@tool(capability=Capability.WRITE_DELETE)
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
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
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
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in _ONBOARD_ACTIONS:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be 'update' or 'delete'."}
        )
    if action_type == "update" and not payload:
        raise ToolError({"status_code": 400, "message": "payload is required for action 'update'."})

    try:
        client = await get_clearpass_client()
        path = f"/onboard/device/{record_id}"
        if action_type == "delete":
            return await client.request("delete", path)
        body: Any = payload if payload is not None else {}
        return await client.request("patch", path, json_body=body)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing onboard device ({action_type}): {e}"}) from e
