"""Aruba Central Webhooks tools.

Wraps the ``network-services/v1/webhooks`` endpoint family. Webhooks
are outbound notification subscriptions — Central posts events to your
configured URL when alerts fire, configs change, etc.

PII NOTE: webhook payloads carry an HMAC secret. Existing PII rules
do not yet tokenize this — flag for follow-up tokenization extension
before turning on ``ENABLE_CENTRAL_WRITE_TOOLS=true`` on tenants with
untrusted AI clients.
"""

from typing import Annotated, Literal

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


@tool(capability=Capability.READ)
async def central_get_webhooks(
    ctx: Context,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """List configured webhooks.

    Returns webhook definitions (URL, event types, HMAC settings,
    enabled flag). Use ``central_get_webhook`` for a single webhook's
    full configuration.
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-services/v1/webhooks",
        api_params={"limit": limit, "offset": offset},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(capability=Capability.READ)
async def central_get_webhook(
    ctx: Context,
    webhook_id: Annotated[str, Field(description="Webhook identifier.")],
) -> dict:
    """Get one webhook's full configuration by ID."""
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=f"network-services/v1/webhooks/{path_seg(webhook_id)}",
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_webhook(
    ctx: Context,
    action_type: Annotated[
        Literal["create", "update", "delete"],
        Field(description="``'create'`` (POST), ``'update'`` (PATCH — partial), or ``'delete'``."),
    ],
    webhook_id: Annotated[
        str | None,
        Field(description="Webhook identifier. Required for update/delete; ignored for create."),
    ] = None,
    payload: Annotated[
        dict | None,
        Field(
            description=(
                "Webhook configuration. For ``create``: URL, event types, "
                "HMAC config, etc. For ``update``: only fields to change "
                "(PATCH semantics — omitted fields preserved). For "
                "``delete``: ignored."
            ),
        ),
    ] = None,
    replace_existing: Annotated[
        bool,
        Field(
            description=(
                "On ``update``: when True, use PUT (wholesale replace — "
                "fields missing from payload get dropped). Default False "
                "uses PATCH (partial — fields missing from payload "
                "preserved). Has no effect on create/delete."
            ),
        ),
    ] = False,
) -> dict:
    """Create, update, or delete a webhook.

    Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true``. Update defaults to
    PATCH semantics; pass ``replace_existing=True`` for PUT (wholesale
    replace).
    """
    conn = get_central_conn(ctx)

    if action_type == "create":
        if not payload:
            raise ToolError({"status_code": 400, "message": "``payload`` is required for create."})
        response = await retry_central_command(
            central_conn=conn,
            api_method="POST",
            api_path="network-services/v1/webhooks",
            api_data=payload,
        )
    elif action_type == "update":
        if not webhook_id:
            raise ToolError({"status_code": 400, "message": "``webhook_id`` is required for update."})
        if not payload:
            raise ToolError({"status_code": 400, "message": "``payload`` is required for update."})
        method = "PUT" if replace_existing else "PATCH"
        response = await retry_central_command(
            central_conn=conn,
            api_method=method,
            api_path=f"network-services/v1/webhooks/{path_seg(webhook_id)}",
            api_data=payload,
        )
    elif action_type == "delete":
        if not webhook_id:
            raise ToolError({"status_code": 400, "message": "``webhook_id`` is required for delete."})
        response = await retry_central_command(
            central_conn=conn,
            api_method="DELETE",
            api_path=f"network-services/v1/webhooks/{path_seg(webhook_id)}",
        )
    else:
        raise ToolError({"status_code": 400, "message": f"unknown action_type '{action_type}'."})

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "webhook_id": webhook_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(capability=Capability.WRITE_DELETE)
async def central_rotate_webhook_hmac_key(
    ctx: Context,
    webhook_id: Annotated[str, Field(description="Webhook identifier to rotate.")],
) -> dict:
    """Rotate the HMAC signing key for a webhook.

    After rotation, the old key stops signing future deliveries.
    Receivers must update to the new key from the response immediately.
    Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true``.
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="POST",
        api_path=f"network-services/v1/webhooks/{path_seg(webhook_id)}/rotate-hmac-key",
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "webhook_id": webhook_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}
