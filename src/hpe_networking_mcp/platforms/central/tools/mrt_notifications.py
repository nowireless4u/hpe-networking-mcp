"""Aruba Central notification-rule tools.

Wraps the ``network-notifications/v1/notification-rules`` endpoint
family — the modern alert-routing surface where each rule matches a
class of events (``sourceTypes: [ALERTS]``, filtered by ``source``) and
fans them out to one or more destinations (email / syslog / webhook).
This is distinct from ``mrt_webhooks`` (``network-services/v1/webhooks``,
the raw outbound-subscription objects a rule can target).

``central_manage_notification_rule`` covers **create** and **delete**
(both verified live). **Update is deliberately omitted** — the
``PATCH`` endpoint is unusable through the current client: the OAS's
``application/merge-patch+json`` content-type is gateway-rejected (403),
and ``application/json`` PATCH is treated as a full replace that then
fails validation regardless of body shape. Tracked in issue #606.
Create bodies are wrapped in Central's ``{"notificationRuleInput": ...}``
envelope for you.
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
async def central_get_notification_rules(
    ctx: Context,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List configured notification rules.

    Returns the alert-routing rules — each with its match ``source`` /
    ``sourceTypes`` and its ``destination`` fan-out (email / syslog /
    webhook) and enabled flag. Use ``central_get_notification_rule`` for
    one rule's full detail.

    Parameters:
        limit: Results per page (default 100).
        offset: Pagination offset (default 0).
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-notifications/v1/notification-rules",
        api_params={"limit": limit, "offset": offset},
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(capability=Capability.READ)
async def central_get_notification_rule(
    ctx: Context,
    rule_id: Annotated[
        str, Field(description="Notification-rule identifier (from ``central_get_notification_rules``).")
    ],
) -> dict | str:
    """Get one notification rule's full configuration by ID."""
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=f"network-notifications/v1/notification-rules/{path_seg(rule_id)}",
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(capability=Capability.WRITE_DELETE)
async def central_manage_notification_rule(
    ctx: Context,
    action_type: Annotated[
        Literal["create", "delete"],
        Field(
            description=(
                "``'create'`` (POST) or ``'delete'``. Update is not supported "
                "via this tool — the notification-rules PATCH endpoint is "
                "gateway-blocked through the current client (issue #606); "
                "recreate the rule to change it."
            ),
        ),
    ],
    rule_id: Annotated[
        str | None,
        Field(description="Notification-rule identifier. Required for delete; ignored for create."),
    ] = None,
    payload: Annotated[
        dict | None,
        Field(
            description=(
                "Notification-rule fields (create only). Required: ``name`` and "
                "at least one **enabled source** (``source.alerts`` with "
                "``enabled: true`` + one or more ``alertNames``) and one "
                "**enabled destination** (``destination.email`` / ``syslog`` / "
                "``webhook`` with ``enabled: true``; ``email.emailIds`` accepts "
                "raw addresses). ``sourceTypes`` is e.g. ``['ALERTS']``; rule-level "
                "``enabled`` toggles the whole rule. Ignored for delete. Pass the "
                "rule object itself — it is wrapped in the "
                '``{"notificationRuleInput": ...}`` envelope for you.'
            ),
        ),
    ] = None,
) -> dict:
    """Create or delete a notification rule.

    Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true`` and fires an elicitation
    confirmation before it runs. Update is intentionally unsupported (see
    issue #606) — recreate the rule to change it.
    """
    conn = get_central_conn(ctx)

    if action_type == "create":
        if not payload:
            raise ToolError({"status_code": 400, "message": "``payload`` is required for create."})
        response = await retry_central_command(
            central_conn=conn,
            api_method="POST",
            api_path="network-notifications/v1/notification-rules",
            api_data={"notificationRuleInput": payload},
        )
    elif action_type == "delete":
        if not rule_id:
            raise ToolError({"status_code": 400, "message": "``rule_id`` is required for delete."})
        response = await retry_central_command(
            central_conn=conn,
            api_method="DELETE",
            api_path=f"network-notifications/v1/notification-rules/{path_seg(rule_id)}",
        )
    else:
        raise ToolError({"status_code": 400, "message": f"unknown action_type '{action_type}'."})

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "rule_id": rule_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}
