"""ClearPass session control write tools (disconnect, CoA)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client

_VALID_TARGETS = ("session_id", "username", "mac", "ip", "bulk")


@tool(capability=Capability.OPERATIONAL, enable_gated=True)
async def clearpass_disconnect_session(
    ctx: Context,
    target_type: Annotated[str, Field(description="Target type: 'session_id', 'username', 'mac', 'ip', or 'bulk'.")],
    target_value: Annotated[
        str | None,
        Field(description="Target value (session ID, username, MAC, or IP). Not needed for bulk."),
    ] = None,
    filter: Annotated[
        dict | None,
        Field(description="Filter criteria for bulk disconnect (e.g. {'nasipaddress': '10.1.1.1'})."),
    ] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Disconnect an active ClearPass session (send RADIUS Disconnect-Request).

    Target types:
        session_id: Disconnect a single session by its ClearPass session ID.
        username: Disconnect all sessions for a username.
        mac: Disconnect all sessions for a MAC address.
        ip: Disconnect all sessions for a client IP.
        bulk: Disconnect sessions matching a filter criteria.

    Args:
        target_type: How to identify the session(s) to disconnect.
        target_value: The session ID, username, MAC, or IP. Not needed for bulk.
        filter: Filter dict for bulk operations. Used only when target_type is 'bulk'.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if target_type not in _VALID_TARGETS:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid target_type '{target_type}'. Must be one of: {', '.join(_VALID_TARGETS)}.",
            }
        )
    if target_type != "bulk" and not target_value:
        raise ToolError(
            {"status_code": 400, "message": f"target_value is required when target_type is '{target_type}'."}
        )
    if target_type == "bulk" and not filter:
        raise ToolError({"status_code": 400, "message": "filter is required when target_type is 'bulk'."})

    try:
        client = await get_clearpass_client()

        # Live-verified routes (#469): the old bulk/selector POSTs to
        # /session/disconnect return HTTP 405; the API surface is
        # /session-action/disconnect[/<selector>/{value}].
        if target_type == "session_id":
            return await client.request(
                "post",
                f"/session/{target_value}/disconnect",
                json_body={"id": target_value, "confirm_disconnect": True},
            )
        if target_type == "bulk":
            return await client.request("post", "/session-action/disconnect", json_body={"filter": filter})
        selector_map = {"username": "username", "mac": "mac", "ip": "ip"}
        return await client.request(
            "post", f"/session-action/disconnect/{selector_map[target_type]}/{target_value}", json_body={}
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error disconnecting session: {e}"}) from e


@tool(capability=Capability.OPERATIONAL, enable_gated=True)
async def clearpass_perform_coa(
    ctx: Context,
    target_type: Annotated[str, Field(description="Target type: 'session_id', 'username', 'mac', 'ip', or 'bulk'.")],
    target_value: Annotated[
        str | None,
        Field(description="Target value (session ID, username, MAC, or IP). Not needed for bulk."),
    ] = None,
    filter: Annotated[
        dict | None,
        Field(description="Filter criteria for bulk CoA (e.g. {'nasipaddress': '10.1.1.1'})."),
    ] = None,
    enforcement_profile: Annotated[
        list[str] | None,
        Field(
            description=(
                "Enforcement profile name(s) to apply. REQUIRED for username/mac/ip/bulk targets "
                "(the /session-action/coa API mandates it). Not used for session_id."
            ),
        ),
    ] = None,
    reauthorize_profile: Annotated[
        str | None,
        Field(description="Optional reauthorization profile name (session_id target only)."),
    ] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Perform a Change of Authorization (CoA) on active ClearPass sessions.

    Sends a RADIUS CoA to re-evaluate authorization for the targeted session(s),
    causing the NAS to re-authenticate the client with updated policies.

    Target types:
        session_id: CoA a single session by its ClearPass session ID.
        username: CoA all sessions for a username.
        mac: CoA all sessions for a MAC address.
        ip: CoA all sessions for a client IP.
        bulk: CoA sessions matching a filter criteria.

    Args:
        target_type: How to identify the session(s) for CoA.
        target_value: The session ID, username, MAC, or IP. Not needed for bulk.
        filter: Filter dict for bulk operations. Used only when target_type is 'bulk'.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if target_type not in _VALID_TARGETS:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid target_type '{target_type}'. Must be one of: {', '.join(_VALID_TARGETS)}.",
            }
        )
    if target_type != "bulk" and not target_value:
        raise ToolError(
            {"status_code": 400, "message": f"target_value is required when target_type is '{target_type}'."}
        )
    if target_type == "bulk" and not filter:
        raise ToolError({"status_code": 400, "message": "filter is required when target_type is 'bulk'."})

    if target_type != "session_id" and not enforcement_profile:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "enforcement_profile is required for username/mac/ip/bulk CoA — the "
                    "/session-action/coa API mandates the enforcement profile(s) to apply."
                ),
            }
        )

    try:
        client = await get_clearpass_client()

        # Live-verified routes (#469): the old GET /session/{id}/reauthorize
        # returned reauth *templates* without performing anything, and the
        # bulk POST /session/reauthorize returns HTTP 405. Performing a CoA is
        # POST /session/{id}/reauthorize (confirm flag in the body) for a
        # single session, or /session-action/coa[/<selector>/{value}] with
        # the mandatory enforcement_profile otherwise.
        if target_type == "session_id":
            body: dict = {"confirm_reauthorize": True}
            if reauthorize_profile:
                body["reauthorize_profile"] = reauthorize_profile
            return await client.request("post", f"/session/{target_value}/reauthorize", json_body=body)
        if target_type == "bulk":
            return await client.request(
                "post",
                "/session-action/coa",
                json_body={"filter": filter, "enforcement_profile": enforcement_profile},
            )
        selector_map = {"username": "username", "mac": "mac", "ip": "ip"}
        return await client.request(
            "post",
            f"/session-action/coa/{selector_map[target_type]}/{target_value}",
            json_body={"enforcement_profile": enforcement_profile},
        )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error performing CoA: {e}"}) from e
