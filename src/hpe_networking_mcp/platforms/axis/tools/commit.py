"""Axis commit tool — applies all staged changes.

Axis writes (create/update/delete via ``axis_manage_*``) are staged. Until
``axis_commit_changes`` is called, the changes are not visible to the
production data plane. This mirrors the behavior of the Axis admin UI,
where edits live in a draft state until the operator commits.

The ``POST /Commit`` endpoint accepts no body and returns ``204 No Content``
on success. We surface that as ``{"status": "committed"}`` to give the
caller a clear positive response.
"""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client

_COMMIT_TIMEOUT = 60.0


@tool(capability=Capability.OPERATIONAL, enable_gated=True)
async def axis_commit_changes(
    ctx: Context,
    confirmed: bool = False,
) -> dict:
    """Apply all staged Axis changes (POST /Commit).

    Every ``axis_manage_*`` write tool stages its change; this is the tool
    that pushes those staged edits live in the Axis cloud. Affects all
    pending writes for this tenant — there is no per-change selection.

    The endpoint can take a while when there's a lot staged; we use a 60-second
    timeout for this call specifically.

    Args:
        confirmed: Fallback confirmation flag — honored only when the client cannot
            show a confirmation prompt (the universal gate prompts otherwise).
    """
    try:
        client = await get_axis_client()
        response = await client.request("POST", "/Commit", timeout=_COMMIT_TIMEOUT)
        if response.status_code == 204:
            return {"status": "committed", "message": "Axis applied all staged changes."}
        body = response.json() if response.content else {}
        return {"status": "committed", "status_code": response.status_code, "body": body}
    except Exception as e:
        detail = format_http_error(e)
        raise ToolError({"status_code": 502, "message": f"Error committing Axis changes: {detail}"}) from e
