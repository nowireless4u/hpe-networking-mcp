"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Tickets``
Operations in this file: 8
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_add_org_ticket_comment",
    description="POST /api/v1/orgs/{org_id}/tickets/{ticket_id}/comments\n\naddOrgTicketComment\n\nAdd Comment to support ticket",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_add_org_ticket_comment(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ticket_id: Annotated[str, Field(description="path parameter 'ticket_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/tickets/{ticket_id}/comments",
        path_params={"org_id": org_id, "ticket_id": ticket_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_count_org_tickets",
    description="GET /api/v1/orgs/{org_id}/tickets/count\n\ncountOrgTickets\n\nCount by Distinct Attributes of Org Tickets",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_tickets(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/tickets/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_create_org_ticket",
    description="POST /api/v1/orgs/{org_id}/tickets\n\ncreateOrgTicket\n\nCreate a support ticket",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_ticket(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/tickets",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_org_ticket",
    description="GET /api/v1/orgs/{org_id}/tickets/{ticket_id}\n\ngetOrgTicket\n\nGet support ticket details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_ticket(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ticket_id: Annotated[str, Field(description="path parameter 'ticket_id'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/tickets/{ticket_id}",
        path_params={"org_id": org_id, "ticket_id": ticket_id},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_ticket_attachment",
    description="GET /api/v1/orgs/{org_id}/tickets/{ticket_id}/attachments/{attachment_id}\n\nGetOrgTicketAttachment\n\nGet Org ticket Attachment",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_ticket_attachment(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ticket_id: Annotated[str, Field(description="path parameter 'ticket_id'")],
    attachment_id: Annotated[str, Field(description="path parameter 'attachment_id'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/tickets/{ticket_id}/attachments/{attachment_id}",
        path_params={"org_id": org_id, "ticket_id": ticket_id, "attachment_id": attachment_id},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_tickets",
    description="GET /api/v1/orgs/{org_id}/tickets\n\nlistOrgTickets\n\nGet List of Tickets of an Org",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_tickets(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/tickets",
        path_params={"org_id": org_id},
        query_params={"start": start, "end": end, "duration": duration},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_ticket",
    description="PUT /api/v1/orgs/{org_id}/tickets/{ticket_id}\n\nupdateOrgTicket\n\nUpdate support ticket",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_ticket(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ticket_id: Annotated[str, Field(description="path parameter 'ticket_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/tickets/{ticket_id}",
        path_params={"org_id": org_id, "ticket_id": ticket_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_org_ticket_attachment",
    description="POST /api/v1/orgs/{org_id}/tickets/{ticket_id}/attachments\n\nUploadOrgTicketAttachment\n\nGet Org ticket Attachment",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_upload_org_ticket_attachment(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ticket_id: Annotated[str, Field(description="path parameter 'ticket_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/tickets/{ticket_id}/attachments",
        path_params={"org_id": org_id, "ticket_id": ticket_id},
        query_params=None,
        body=body,
    )
