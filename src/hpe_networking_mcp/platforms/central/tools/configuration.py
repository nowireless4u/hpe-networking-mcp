"""Aruba Central configuration write tools — sites, site collections, device groups.

Provides CRUD operations for Central network configuration objects.
All write tools are gated behind ENABLE_WRITE_TOOLS and require user
confirmation via elicitation before executing.
"""

from enum import Enum
from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

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


def register(mcp):
    """Register Central configuration write tools."""

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
                    "Site configuration payload. For create: 'address' is required "
                    "(or 'latitude' + 'longitude'). Optional fields: name, city, state, "
                    "country, zipcode, timezone (object with timezoneName, timezoneId, "
                    "rawOffset). For update: include only fields to change. "
                    "For delete: payload is ignored."
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
    ) -> dict | str:
        """Create, update, or delete a site in Aruba Central."""
        return await _execute_config_action(
            ctx=ctx,
            action_type=action_type,
            resource_name="site",
            api_path="network-config/v1/sites",
            resource_id=site_id,
            payload=payload,
        )

    # ------------------------------------------------------------------
    # Site Collections
    # ------------------------------------------------------------------

    @mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
    async def central_manage_site_collection(
        ctx: Context,
        action_type: Annotated[
            ActionType,
            Field(description="Action to perform: create, update, or delete."),
        ],
        payload: Annotated[
            dict,
            Field(
                description=(
                    "Site collection payload. For create: 'scopeName' is required. "
                    "Optional: 'description', 'siteIds' (list of site IDs to include). "
                    "For update: include only fields to change. "
                    "For delete: payload is ignored."
                )
            ),
        ],
        collection_id: Annotated[
            str | None,
            Field(
                description=("Site collection ID. Required for update and delete. Obtain from central_get_scope_tree."),
                default=None,
            ),
        ],
    ) -> dict | str:
        """Create, update, or delete a site collection in Aruba Central."""
        return await _execute_config_action(
            ctx=ctx,
            action_type=action_type,
            resource_name="site collection",
            api_path="network-config/v1/site-collections",
            resource_id=collection_id,
            payload=payload,
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
                    "For update: include only fields to change. "
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
    ) -> dict | str:
        """Create, update, or delete a device group in Aruba Central."""
        return await _execute_config_action(
            ctx=ctx,
            action_type=action_type,
            resource_name="device group",
            api_path="network-config/v1/device-groups",
            resource_id=group_id,
            payload=payload,
        )


# ---------------------------------------------------------------------------
# Shared execution helper
# ---------------------------------------------------------------------------


async def _execute_config_action(
    ctx: Context,
    action_type: ActionType,
    resource_name: str,
    api_path: str,
    resource_id: str | None,
    payload: dict,
) -> dict | str:
    """Execute a configuration CRUD action with elicitation and error handling.

    Args:
        ctx: MCP context with lifespan_context containing central_conn.
        action_type: CREATE, UPDATE, or DELETE.
        resource_name: Human-readable name for elicitation messages.
        api_path: Base API path (e.g. "network-config/v1/sites").
        resource_id: Resource ID for update/delete operations.
        payload: Request payload for create/update.

    Returns:
        API response dict or error string.
    """
    if action_type in (ActionType.UPDATE, ActionType.DELETE) and not resource_id:
        raise ToolError(f"Resource ID is required for {action_type.value} operations.")

    action_wording = {
        ActionType.CREATE: "create a new",
        ActionType.UPDATE: "update an existing",
        ActionType.DELETE: "delete an existing",
    }[action_type]

    try:
        elicitation_response = await elicitation_handler(
            message=(f"The LLM wants to {action_wording} {resource_name}. Do you accept to trigger the API call?"),
            ctx=ctx,
        )
    except Exception as exc:
        raise ToolError(
            "AI client does not support elicitation. Cannot execute configuration changes without user confirmation."
        ) from exc

    if elicitation_response.action == "decline":
        return {"message": "Action declined by user."}
    elif elicitation_response.action == "cancel":
        return {"message": "Action canceled by user."}

    conn = ctx.lifespan_context["central_conn"]

    method_map = {
        ActionType.CREATE: "POST",
        ActionType.UPDATE: "PUT",
        ActionType.DELETE: "DELETE",
    }
    api_method = method_map[action_type]
    full_path = f"{api_path}/{resource_id}" if resource_id else api_path

    api_params: dict = {}
    if action_type != ActionType.DELETE:
        api_params = payload

    logger.info("Central config: {} {} — path: {}", api_method, resource_name, full_path)

    response = retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=full_path,
        api_params=api_params,
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
