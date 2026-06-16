"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``applianceWizard``
Operations in this file: 2
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_gms_appliance_wizard_apply",
    description="GET /gms/applianceWizard/apply\n\ngetApplyApplianceWizard259\n\nCheck wizard apply operation status for an appliance.",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_appliance_wizard_apply(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/applianceWizard/apply",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_appliance_wizard_apply",
    description="POST /gms/applianceWizard/apply\n\napplyApplianceWizard260\n\nApply wizard configuration to an appliance asynchronously.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_appliance_wizard_apply(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/applianceWizard/apply",
        query_params=query_params or None,
        body=body,
    )
