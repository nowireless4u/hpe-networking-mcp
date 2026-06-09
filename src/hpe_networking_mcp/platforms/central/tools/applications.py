from datetime import UTC, datetime

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


def _parse_iso_to_epoch_ms(value: str) -> int | None:
    """Parse an ISO-8601 datetime to epoch milliseconds, or return None if it isn't
    a parseable ISO-8601 string. A naive datetime (no offset) is assumed UTC."""
    iso = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return int(dt.timestamp() * 1000)


def _to_epoch_ms(label: str, value: str) -> int:
    """Validate and normalize a timestamp to epoch milliseconds.

    The Central applications endpoint expects epoch **milliseconds** and returns an
    opaque ``HTTP 400 BAD_REQUEST`` for anything else, so normalize up front and give
    an actionable error for genuinely bad input (issue #458). Accepted forms:

    * **13-digit** epoch milliseconds — used as-is.
    * **10-digit** epoch seconds — converted to ms (the seconds-vs-ms mixup is the
      most common mistake; 10- vs 13-digit values don't overlap for present-day times).
    * **ISO-8601** datetimes (e.g. ``2026-06-08T23:00:00Z``) — converted to ms. This
      is the natural form for an LLM that can't read the clock inside the code-mode
      sandbox (``datetime.now()`` / ``time.time()`` are blocked there), so accept it
      and do the conversion server-side where a clock is available.

    Anything else (a plain date, a word, an 11/12/14-digit typo) is rejected.

    Args:
        label: Parameter name, used in the error message.
        value: The raw timestamp string.

    Returns:
        The timestamp as integer epoch milliseconds.

    Raises:
        ToolError: 400 when ``value`` is not a recognized timestamp form.
    """
    s = str(value).strip()
    if s.isdigit() and len(s) in (10, 13):
        # 10-digit = epoch seconds → ms; 13-digit already ms.
        return int(s) * 1000 if len(s) == 10 else int(s)
    iso_ms = _parse_iso_to_epoch_ms(s)
    if iso_ms is not None:
        return iso_ms
    raise ToolError(
        {
            "status_code": 400,
            "message": (
                f"{label} must be epoch milliseconds (13-digit, e.g. '1780876800000'), "
                f"epoch seconds (10-digit), or an ISO-8601 datetime (e.g. "
                f"'2026-06-08T23:00:00Z'); got {value!r}."
            ),
        }
    )


def _normalize_sort(value: str) -> str:
    """Normalize a sort expression to the OData ``<field> asc|desc`` form Central wants.

    The endpoint rejects the common ``-field`` / ``+field`` shorthand (e.g. ``-usage``)
    with an opaque 400 — it only accepts ``<field> desc`` / ``<field> asc``. Convert the
    single-field leading-sign shorthand; pass anything already OData-shaped (or a
    multi-field / comma list) through unchanged for Central to validate.

    ``-usage`` -> ``usage desc`` · ``+usage`` -> ``usage asc`` · ``usage desc`` -> unchanged
    """
    s = value.strip()
    if s and s[0] in "+-" and " " not in s and "," not in s:
        return f"{s[1:].strip()} {'desc' if s[0] == '-' else 'asc'}"
    return s


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
        start_query_time: Start of the time window (required). Accepts epoch
            milliseconds (13-digit), epoch seconds (10-digit), or an ISO-8601
            datetime (e.g. "2026-06-08T23:00:00Z"); all are normalized to epoch ms.
        end_query_time: End of the time window (required), must be after
            start_query_time. Same accepted formats as start_query_time.
        limit: Number of records per page (default 1000).
        offset: Starting record offset for pagination (default 0).
        client_id: Filter results to a specific client ID.
        filter: OData filter expression to narrow results.
        sort: OData sort order, "<field> asc|desc" (e.g. "usage desc" for the top
            apps by traffic). The "-field" / "+field" shorthand is also accepted and
            normalized (e.g. "-usage" -> "usage desc").
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
        query_params["sort"] = _normalize_sort(sort)

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
