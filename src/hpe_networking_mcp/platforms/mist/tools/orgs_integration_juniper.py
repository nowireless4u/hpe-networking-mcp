"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Integration Juniper``
Operations in this file: 2
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
    name="mist_link_org_to_juniper_juniper_account",
    description="POST /api/v1/orgs/{org_id}/setting/juniper/link_accounts\n\nlinkOrgToJuniperJuniperAccount\n\nLink Juniper Accounts",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_link_org_to_juniper_juniper_account(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/setting/juniper/link_accounts"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/juniper/link_accounts",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unlink_org_from_juniper_customer_id",
    description="DELETE /api/v1/orgs/{org_id}/setting/juniper/unlink_account\n\nunlinkOrgFromJuniperCustomerId\n\nUnlink Juniper Customer ID\n`linked_by` field is only required if there are duplicate account_names.",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_unlink_org_from_juniper_customer_id(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for DELETE /api/v1/orgs/{org_id}/setting/juniper/unlink_account"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/juniper/unlink_account",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
