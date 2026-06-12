"""Example write tool — reference pattern only, never registered.

Delete this file when you copy the template into a real platform and
replace it with your real ``<platform>_manage_*`` tools.

Demonstrates two important patterns every write tool should follow:

1. **No inline confirmation.** Confirmation is structural: the universal
   gate at the ``<platform>_invoke_tool`` dispatch chokepoint prompts the
   user (via MCP elicitation) for every tool whose ``capability=``
   classification derives the ``requires_confirmation`` tag — which
   ``WRITE`` / ``WRITE_DELETE`` / gated ``OPERATIONAL`` all do. Tools never
   run their own confirmation prompt (that double-prompts). Keep the
   ``confirmed`` parameter: the gate consumes ``confirmed=true`` from params
   as the popup-less fallback when the client cannot present a prompt.
2. ``action_type`` parameter (``create`` / ``update`` / ``delete``) — one
   write tool per entity, dispatched by ``action_type`` inside the
   function body. Reduces tool surface count without losing clarity.
"""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._template._registry import tool
from hpe_networking_mcp.platforms._template.client import format_http_error, get_template_client


@tool(capability=Capability.WRITE_DELETE)
async def template_manage_example(
    ctx: Context,
    action_type: Literal["create", "update", "delete"],
    thing_id: str | None = None,
    name: str | None = None,
    payload: dict[str, Any] | None = None,
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Create, update, or delete an example thing.

    Args:
        action_type: One of ``create``, ``update``, or ``delete``.
        thing_id: Required for update/delete. The thing's UUID.
        name: Required for create.
        payload: Body for create/update.
        confirmed: Fallback confirmation flag — honored only when the client
            cannot show a confirmation prompt (the universal gate prompts
            otherwise).
    """
    try:
        client = await get_template_client()
        if action_type == "create":
            response = await client.request("POST", "/api/v1.0/Things", json_body=payload or {"name": name})
        elif action_type == "update":
            if not thing_id:
                return "thing_id is required for update."
            response = await client.request("PUT", f"/api/v1.0/Things/{thing_id}", json_body=payload or {})
        else:  # delete
            if not thing_id:
                return "thing_id is required for delete."
            response = await client.request("DELETE", f"/api/v1.0/Things/{thing_id}")

        body: Any = response.json() if response.content else {"status": "accepted"}
        return {"action": action_type, "thing_id": thing_id, "data": body}
    except Exception as e:
        return f"Error during {action_type}: {format_http_error(e) if hasattr(e, 'response') else e}"
