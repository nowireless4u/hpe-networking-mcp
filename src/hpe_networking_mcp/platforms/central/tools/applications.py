from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


def _to_epoch_ms(label: str, value: str) -> int:
    """Validate and normalize an epoch timestamp to milliseconds.

    The Central applications endpoint expects epoch **milliseconds** and returns an
    opaque ``HTTP 400 BAD_REQUEST`` for anything else (ISO-8601 strings, plain dates,
    etc.). Validate up front so callers get an actionable error instead of the bare
    upstream 400 (issue #458). Epoch **seconds** (10-digit) are accepted as a
    convenience and converted to ms — the seconds-vs-ms mixup is the most common
    mistake and 10- vs 13-digit values don't overlap for present-day timestamps.

    Args:
        label: Parameter name, used in the error message.
        value: The raw timestamp string.

    Returns:
        The timestamp as integer epoch milliseconds.

    Raises:
        ToolError: 400 when ``value`` is not a numeric epoch timestamp.
    """
    s = str(value).strip()
    if not s.isdigit():
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    f"{label} must be an epoch timestamp in milliseconds "
                    f"(e.g. '1780876800000'), got {value!r}. ISO-8601 timestamps and "
                    "plain dates are not accepted — convert to epoch milliseconds first."
                ),
            }
        )
    # 10-digit value = epoch seconds → normalize to ms; 13-digit already ms.
    return int(s) * 1000 if len(s) == 10 else int(s)


@tool(annotations=READ_ONLY)
async def central_get_applications(
    ctx: Context,
    site_id: str,
    start_query_time: str,
    end_query_time: str,
    limit: int = 1000,
    offset: int = 0,
    client_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
) -> dict:
    """
    Get application usage data for a site within a time window.

    Returns a list of applications observed on the network with
    traffic volume, client counts, and categorization. Useful for
    understanding application mix and bandwidth consumption.

    Parameters:
        site_id: Site ID to scope the query (required).
        start_query_time: Start of the time window in epoch milliseconds (required).
            Epoch seconds (10-digit) are accepted and converted. ISO-8601 strings and
            plain dates are NOT accepted — the upstream API rejects them with a 400.
        end_query_time: End of the time window in epoch milliseconds (required), and
            must be after start_query_time. Same format rules as start_query_time.
        limit: Number of records per page (default 1000).
        offset: Starting record offset for pagination (default 0).
        client_id: Filter results to a specific client ID.
        filter: OData filter expression to narrow results.
        sort: Sort order for results.
    """
    # Validate inputs up front so a bad timestamp yields an actionable error instead
    # of the opaque upstream HTTP 400 (issue #458).
    if not str(site_id).strip():
        raise ToolError({"status_code": 400, "message": "site_id is required and must be non-empty."})
    start_ms = _to_epoch_ms("start_query_time", start_query_time)
    end_ms = _to_epoch_ms("end_query_time", end_query_time)
    if start_ms >= end_ms:
        raise ToolError(
            {
                "status_code": 400,
                "message": (f"start_query_time ({start_query_time}) must be before end_query_time ({end_query_time})."),
            }
        )

    conn = ctx.lifespan_context["central_conn"]

    query_params: dict = {
        "site-id": site_id,
        "start-query-time": start_ms,
        "end-query-time": end_ms,
        "limit": limit,
        "offset": offset,
    }
    if client_id:
        query_params["client-id"] = client_id
    if filter:
        query_params["filter"] = filter
    if sort:
        query_params["sort"] = sort

    try:
        resp = retry_central_command(
            conn,
            api_method="GET",
            api_path="network-monitoring/v1alpha1/applications",
            api_params=query_params,
        )
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching applications: {e}"}) from e

    code = resp.get("code", 0)
    if not (200 <= code < 300):
        raise ToolError({"status_code": code, "message": f"Central API error: {resp.get('msg')}"})
    return resp.get("msg", {})
