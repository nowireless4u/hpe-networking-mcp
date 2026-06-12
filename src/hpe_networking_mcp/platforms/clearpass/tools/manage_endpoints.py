"""ClearPass endpoint write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_endpoint(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Endpoint config payload. For delete: empty dict {}.")],
    endpoint_id: Annotated[str | None, Field(description="Endpoint ID (required for update/delete).")] = None,
    mac_address: Annotated[
        str | None,
        Field(description="MAC address (alternative to ID for update/delete, e.g. '001122334455')."),
    ] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass endpoint in the endpoint database.

    Endpoints represent known MAC addresses tracked by ClearPass for profiling,
    posture assessment, and access control.

    Args:
        action_type: Operation — 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
            For create, must include mac_address at minimum.
        endpoint_id: Numeric ID. Required for update/delete (or use mac_address).
        mac_address: MAC address. Alternative to endpoint_id for update/delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )

    try:
        client = await get_clearpass_client()

        if action_type == "create":
            return await client.request("post", "/endpoint", json_body=payload)

        if not endpoint_id and not mac_address:
            raise ToolError(
                {"status_code": 400, "message": "Either endpoint_id or mac_address is required for update/delete."}
            )

        if action_type == "update":
            if endpoint_id:
                return await client.request("patch", f"/endpoint/{path_seg(endpoint_id)}", json_body=payload)
            return await client.request("patch", f"/endpoint/mac-address/{path_seg(mac_address)}", json_body=payload)

        # delete
        if endpoint_id:
            return await client.request("delete", f"/endpoint/{path_seg(endpoint_id)}")
        return await client.request("delete", f"/endpoint/mac-address/{path_seg(mac_address)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing endpoint: {e}"}) from e
