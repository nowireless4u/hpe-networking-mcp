"""Aruba Central configuration write tools — sites, site collections, device groups.

Provides CRUD operations for Central network configuration objects.
All write tools are gated behind ENABLE_CENTRAL_WRITE_TOOLS and require
user confirmation for update/delete operations.
"""

from enum import Enum
from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


class ActionType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class CollectionActionType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ADD_SITES = "add_sites"
    REMOVE_SITES = "remove_sites"


# ------------------------------------------------------------------
# Sites
# ------------------------------------------------------------------


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_site(
    ctx: Context,
    action_type: Annotated[
        ActionType,
        Field(description="Action to perform: create, update, or delete."),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Site configuration payload. IMPORTANT: All fields must use full names, "
                "no abbreviations (e.g. 'Indiana' not 'IN', 'United States' not 'US'). "
                "Required fields for create: address, name, city, state, country, zipcode, "
                "and timezone. The timezone object must include timezoneName (e.g. "
                "'Eastern Standard Time'), timezoneId (e.g. 'America/Indiana/Indianapolis'), "
                "and rawOffset in milliseconds (e.g. -18000000 for EST). "
                "Determine the correct timezone based on the site address. "
                "For update: include only fields to change. For delete: payload is ignored."
            )
        ),
    ],
    site_id: Annotated[
        str | None,
        Field(
            description="Site ID. Required for update and delete. Obtain from central_get_sites.",
            default=None,
        ),
    ],
    confirmed: Annotated[
        bool,
        Field(
            description="Set to true when the user has confirmed the operation in chat. Required for update/delete.",
            default=False,
        ),
    ],
    replace_existing: Annotated[
        bool,
        Field(
            description=(
                "Only used on update. When false (default) the update is a PATCH — Central merges the payload "
                "with the existing site, preserving fields you don't specify. Set true to issue a PUT that "
                "replaces the entire site; any field absent from the payload is dropped. Use with care."
            ),
            default=False,
        ),
    ],
) -> dict | str:
    """Create, update, or delete a site in Aruba Central."""
    return await _execute_config_action(
        ctx=ctx,
        action_type=action_type,
        resource_name="site",
        api_path="network-config/v1/sites",
        resource_id=site_id,
        payload=payload,
        confirmed=confirmed,
        replace_existing=replace_existing,
    )


# ------------------------------------------------------------------
# Site Collections
# ------------------------------------------------------------------


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_site_collection(
    ctx: Context,
    action_type: Annotated[
        CollectionActionType,
        Field(
            description=(
                "Action to perform: create, update, delete, add_sites, or remove_sites. "
                "Use add_sites to add sites to an existing collection. "
                "Use remove_sites to remove sites from a collection."
            )
        ),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Site collection payload. For create: 'scopeName' is required. "
                "Optional: 'description', 'siteIds' (list of site IDs to include). "
                "For update: include fields to change plus 'scopeId'. "
                "For add_sites/remove_sites: provide 'scopeId' and 'siteIds' list. "
                "For delete: payload is ignored."
            )
        ),
    ],
    collection_id: Annotated[
        str | None,
        Field(
            description=("Site collection ID. Required for update, delete, add_sites, remove_sites."),
            default=None,
        ),
    ],
    confirmed: Annotated[
        bool,
        Field(
            description="Set to true when the user has confirmed the operation in chat. Required for update/delete.",
            default=False,
        ),
    ],
    replace_existing: Annotated[
        bool,
        Field(
            description=(
                "Only used on update. When false (default) the update is a PATCH — Central merges the payload "
                "with the existing collection, preserving fields you don't specify. Set true to issue a PUT that "
                "replaces the entire collection; any field absent from the payload is dropped. "
                "This flag does not apply to add_sites / remove_sites."
            ),
            default=False,
        ),
    ],
) -> dict | str:
    """Create, update, delete, or manage sites within a site collection."""
    if action_type == CollectionActionType.ADD_SITES:
        return await _execute_collection_site_action(
            ctx=ctx, action="add", collection_id=collection_id, payload=payload
        )
    if action_type == CollectionActionType.REMOVE_SITES:
        return await _execute_collection_site_action(
            ctx=ctx, action="remove", collection_id=collection_id, payload=payload
        )
    return await _execute_config_action(
        ctx=ctx,
        action_type=ActionType(action_type.value),
        resource_name="site collection",
        api_path="network-config/v1/site-collections",
        resource_id=collection_id,
        payload=payload,
        confirmed=confirmed,
        replace_existing=replace_existing,
    )


# ------------------------------------------------------------------
# Device Groups
# ------------------------------------------------------------------


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_group(
    ctx: Context,
    action_type: Annotated[
        ActionType,
        Field(description="Action to perform: create, update, or delete."),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Device group payload. For create: 'scopeName' is required. "
                "Optional: 'description'. "
                "For update: include fields to change plus 'scopeId'. "
                "For delete: payload is ignored."
            )
        ),
    ],
    group_id: Annotated[
        str | None,
        Field(
            description=("Device group ID. Required for update and delete. Obtain from central_get_scope_tree."),
            default=None,
        ),
    ],
    confirmed: Annotated[
        bool,
        Field(
            description="Set to true when the user has confirmed the operation in chat. Required for update/delete.",
            default=False,
        ),
    ],
    replace_existing: Annotated[
        bool,
        Field(
            description=(
                "Only used on update. When false (default) the update is a PATCH — Central merges the payload "
                "with the existing device group, preserving fields you don't specify. Set true to issue a PUT "
                "that replaces the entire device group; any field absent from the payload is dropped. Use with care."
            ),
            default=False,
        ),
    ],
) -> dict | str:
    """Create, update, or delete a device group in Aruba Central."""
    return await _execute_config_action(
        ctx=ctx,
        action_type=action_type,
        resource_name="device group",
        api_path="network-config/v1/device-groups",
        resource_id=group_id,
        payload=payload,
        confirmed=confirmed,
        replace_existing=replace_existing,
    )


# ---------------------------------------------------------------------------
# Shared execution helpers
# ---------------------------------------------------------------------------


async def _execute_config_action(
    ctx: Context,
    action_type: ActionType,
    resource_name: str,
    api_path: str,
    resource_id: str | None,
    payload: dict,
    confirmed: bool = False,
    replace_existing: bool = False,
) -> dict | str:
    """Execute a configuration CRUD action with confirmation and error handling.

    Central API patterns:
    - CREATE: POST to base path, payload as JSON body
    - UPDATE (default): PATCH — Central merges the payload with the existing
      resource server-side. Callers pass only the fields they want to change;
      untouched fields are preserved.
    - UPDATE (replace_existing=True): PUT — full-resource replacement. Every
      field missing from the payload is dropped. Use only when the caller
      has fetched the current resource and is deliberately sending a
      complete replacement. This path reproduces the pre-v0.9.2.2 behavior
      that silently clobbered fields in partial updates (#141, #155).
    - DELETE: DELETE to {path}/bulk, body is {"items": [{"id": "..."}]}
    """
    if action_type in (ActionType.UPDATE, ActionType.DELETE) and not resource_id:
        raise ToolError(f"Resource ID is required for {action_type.value} operations.")

    action_wording = {
        ActionType.CREATE: "create a new",
        ActionType.UPDATE: "update an existing",
        ActionType.DELETE: "delete an existing",
    }[action_type]

    # Confirm with user for update and delete only (skip if already confirmed)
    if action_type != ActionType.CREATE and not confirmed:
        if action_type == ActionType.UPDATE and replace_existing:
            warning = (
                " NOTE: replace_existing=True — this is a full-resource PUT. Any "
                "field not in the payload will be dropped from the stored resource."
            )
        else:
            warning = ""
        elicitation_response = await elicitation_handler(
            message=(
                f"The LLM wants to {action_wording} {resource_name}.{warning} Do you accept to trigger the API call?"
            ),
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} {resource_name}. "
                        "Please confirm with the user before proceeding. "
                        "Call this tool again with the same parameters and confirmed=true after the user confirms."
                    ),
                }
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    conn = ctx.lifespan_context["central_conn"]

    if action_type == ActionType.CREATE:
        api_method = "POST"
        full_path = api_path
        api_data = payload
    elif action_type == ActionType.UPDATE:
        api_method = "PUT" if replace_existing else "PATCH"
        full_path = api_path
        api_data = {**payload, "scopeId": resource_id}
    else:
        api_method = "DELETE"
        full_path = f"{api_path}/bulk"
        api_data = {"items": [{"id": resource_id}]}

    logger.info("Central config: {} {} — path: {}", api_method, resource_name, full_path)

    response = retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=full_path,
        api_data=api_data,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {
            "status": "success",
            "action": action_type.value,
            "resource": resource_name,
            "data": response.get("msg", {}),
        }

    return {
        "status": "error",
        "code": code,
        "message": response.get("msg", "Unknown error"),
    }


async def _execute_collection_site_action(
    ctx: Context,
    action: str,
    collection_id: str | None,
    payload: dict,
) -> dict | str:
    """Add or remove sites from a site collection.

    Args:
        action: "add" or "remove".
        collection_id: The site collection ID.
        payload: Must contain 'siteIds' list.
    """
    if not collection_id:
        raise ToolError("collection_id is required for add_sites/remove_sites.")

    site_ids = payload.get("siteIds", [])
    if not site_ids:
        raise ToolError("payload must contain 'siteIds' list.")

    conn = ctx.lifespan_context["central_conn"]

    if action == "add":
        api_method = "POST"
        api_path = "network-config/v1/site-collection-add-sites"
    else:
        api_method = "DELETE"
        api_path = "network-config/v1/site-collection-remove-sites"

    api_data = {"scopeId": collection_id, "siteIds": site_ids}
    logger.info("Central config: {} sites {} collection {}", action, len(site_ids), collection_id)

    response = retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=api_path,
        api_data=api_data,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {
            "status": "success",
            "action": f"{action}_sites",
            "resource": "site collection",
            "data": response.get("msg", {}),
        }

    return {
        "status": "error",
        "code": code,
        "message": response.get("msg", "Unknown error"),
    }
