"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites SecIntel Profiles``
Operations in this file: 1
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
    name="mist_list_site_sec_intel_profiles_derived",
    description="GET /api/v1/sites/{site_id}/secintelprofiles/derived\n\nlistSiteSecIntelProfilesDerived\n\nGet the list of derived Sky-ATP secintel profiles a Site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_sec_intel_profiles_derived(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    resolve: Annotated[bool | None, Field(description="Whether resolve the site variables")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/secintelprofiles/derived",
        path_params={"site_id": site_id},
        query_params={"resolve": resolve},
        body=None,
    )
