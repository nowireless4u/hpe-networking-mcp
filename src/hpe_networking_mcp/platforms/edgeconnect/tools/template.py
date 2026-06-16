"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``template``
Operations in this file: 14
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
    name="edgeconnect_delete_template_template_groups",
    description="DELETE /template/templateGroups\n\ndeleteTemplateGroup\n\nDelete a template group (Deprecated)",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_template_template_groups(
    ctx: Context,
    templateGroup: Annotated[
        str, Field(description="Name of the template group to delete. Must not be empty or 'Default Template Group'.")
    ],
    comment: Annotated[
        str | None,
        Field(default=None, description="Optional comment for audit logging. Recorded in the system action log."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if templateGroup is not None:
        query_params["templateGroup"] = templateGroup
    if comment is not None:
        query_params["comment"] = comment
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/template/templateGroups",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_template_appliance_association",
    description="GET /template/applianceAssociation\n\ngetTemplateApplianceAssociation\n\nGet template group associations for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_template_appliance_association(
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
        "/template/applianceAssociation",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_template_history",
    description="GET /template/history\n\ngetLatestTemplateHistoryByNePk\n\nGet template application history for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_template_history(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    latestOnly: Annotated[
        str,
        Field(
            description="When 'true', returns the latest successful template history per template name. When 'false' or any other value, returns null."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if latestOnly is not None:
        query_params["latestOnly"] = latestOnly
    return await edgeconnect_request(
        ctx,
        "GET",
        "/template/history",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_template_history_group_list",
    description="GET /template/history/groupList\n\ngetTemplateGroupsAppliedHistory\n\nGet distinct template group names applied to an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_template_history_group_list(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/template/history/groupList",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_template_template_groups",
    description="GET /template/templateGroups\n\ngetTemplateGroupsOrTemplatesInGroup\n\nGet template groups or templates within a specific group",
    capability=Capability.READ,
)
async def edgeconnect_get_template_template_groups(
    ctx: Context,
    templateGroup: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of a specific template group to retrieve. If omitted, returns all template groups.",
        ),
    ] = None,
    namesOnly: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns only template group names as strings instead of full objects. Only applies when templateGroup is not specified.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if templateGroup is not None:
        query_params["templateGroup"] = templateGroup
    if namesOnly is not None:
        query_params["namesOnly"] = namesOnly
    return await edgeconnect_request(
        ctx,
        "GET",
        "/template/templateGroups",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_template_template_groups_priorities",
    description="GET /template/templateGroupsPriorities\n\ngetTemplateGroupsPriorities\n\nGet template group priority order",
    capability=Capability.READ,
)
async def edgeconnect_get_template_template_groups_priorities(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/template/templateGroupsPriorities",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_template_template_selection",
    description="GET /template/templateSelection\n\ngetSelectedTemplatesInGroup\n\nGet selected templates in a template group",
    capability=Capability.READ,
)
async def edgeconnect_get_template_template_selection(
    ctx: Context,
    templateGroup: Annotated[str, Field(description="Name of the template group to query. Must not be null or empty.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if templateGroup is not None:
        query_params["templateGroup"] = templateGroup
    return await edgeconnect_request(
        ctx,
        "GET",
        "/template/templateSelection",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_template_appliance_association",
    description="POST /template/applianceAssociation\n\npostTemplateApplianceAssociation\n\nAssociate template groups with an appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_template_appliance_association(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/template/applianceAssociation",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_template_appliance_association2",
    description="POST /template/applianceAssociation2\n\npostAllTemplateApplianceAssociations\n\nBulk update template associations for multiple appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_template_appliance_association2(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/template/applianceAssociation2",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_template_delete_template_group",
    description="POST /template/deleteTemplateGroup\n\ndeleteTemplateGroupByPost\n\nDelete a template group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_template_delete_template_group(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/template/deleteTemplateGroup",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_template_template_create",
    description="POST /template/templateCreate\n\ncreateTemplateGroup\n\nCreate a new template group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_template_template_create(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/template/templateCreate",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_template_template_groups",
    description="POST /template/templateGroups\n\nsaveTemplateData\n\nCreate or update a template group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_template_template_groups(
    ctx: Context,
    templateGroup: Annotated[
        str,
        Field(
            description="Target template group name. Must not be empty. If this matches the 'name' in the request body, the group is updated; otherwise a new group is created."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if templateGroup is not None:
        query_params["templateGroup"] = templateGroup
    return await edgeconnect_request(
        ctx,
        "POST",
        "/template/templateGroups",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_template_template_groups_priorities",
    description="POST /template/templateGroupsPriorities\n\npostTemplateGroupsPriorities\n\nUpdate template group priority order",
    capability=Capability.WRITE,
)
async def edgeconnect_post_template_template_groups_priorities(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/template/templateGroupsPriorities",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_template_template_selection",
    description="POST /template/templateSelection\n\nupdateTemplateSelected\n\nUpdate selected templates in a template group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_template_template_selection(
    ctx: Context,
    templateGroup: Annotated[
        str, Field(description="Name of the template group to update. Must not be null or empty.")
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if templateGroup is not None:
        query_params["templateGroup"] = templateGroup
    return await edgeconnect_request(
        ctx,
        "POST",
        "/template/templateSelection",
        query_params=query_params or None,
        body=body,
    )
