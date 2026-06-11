"""Aruba Central Reporting tools.

Wraps the ``network-reporting/v1/reports`` endpoint family. Reports are
the scheduled / generated outputs Central produces (PDF/CSV bundles of
device / client / alert / utilization data over a time window). Each
report has zero or more report-runs (one per generation cycle).
"""

from typing import Annotated

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


@tool(annotations=READ_ONLY)
async def central_get_reports(
    ctx: Context,
    filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """List Central reports (definitions).

    Returns the configured report definitions — schedules, time-windows,
    formats, recipients. Use ``central_get_report_runs`` to see actual
    generation history for a specific report.

    Parameters:
        filter: Optional OData 4.0 filter.
        limit: Results per page (default 100).
        offset: Pagination offset (default 0).
    """
    conn = get_central_conn(ctx)
    api_params: dict = {"limit": limit, "offset": offset}
    if filter:
        api_params["filter"] = filter
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-reporting/v1/reports",
        api_params=api_params,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(annotations=READ_ONLY)
async def central_get_report_runs(
    ctx: Context,
    report_id: Annotated[str, Field(description="Report identifier (from ``central_get_reports``).")],
    limit: int = 100,
    offset: int = 0,
) -> dict | str:
    """Get the generation history (runs) for a specific report.

    Each run carries timestamps, status, and a downloadable artifact
    reference. Useful for auditing report delivery + spotting failed
    generations.

    Parameters:
        report_id: Report identifier (from ``central_get_reports``).
        limit: Results per page (default 100).
        offset: Pagination offset (default 0).
    """
    conn = get_central_conn(ctx)
    api_params: dict = {"limit": limit, "offset": offset}
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=f"network-reporting/v1/reports/{report_id}/report-runs",
        api_params=api_params,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_update_report(
    ctx: Context,
    report_id: Annotated[str, Field(description="Report identifier to update.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Report-definition fields to update — schedule, time-window, "
                "format, recipients, etc. Consult Central's Reporting schema "
                "for the field set; use ``central_get_reports`` to see an "
                "existing report for reference. PUT replaces the report "
                "definition wholesale — include every field you want kept."
            ),
        ),
    ],
) -> dict | str:
    """Update a Central report definition.

    PUT is a wholesale replacement — the request body becomes the report
    definition. Fields omitted from the body are dropped from the report.
    Requires ``ENABLE_CENTRAL_WRITE_TOOLS=true`` and fires elicitation.
    """
    conn = get_central_conn(ctx)
    response = await retry_central_command(
        central_conn=conn,
        api_method="PUT",
        api_path=f"network-reporting/v1/reports/{report_id}",
        api_data=payload,
    )
    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "report_id": report_id, "data": response.get("msg", {})}
    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}
