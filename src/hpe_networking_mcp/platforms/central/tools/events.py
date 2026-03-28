from typing import Literal

from fastmcp import Context

from hpe_networking_mcp.platforms.central.models import (
    Event,
    EventFilters,
    PaginatedEvents,
)
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import (
    clean_event_filters,
    compute_time_window,
    retry_central_command,
)

# API hard cap; limit param must not exceed this
EVENT_LIMIT = 100

CONTEXT_TYPE = Literal[
    "SITE",
    "ACCESS_POINT",
    "SWITCH",
    "GATEWAY",
    "WIRELESS_CLIENT",
    "WIRED_CLIENT",
    "BRIDGE",
]

TIME_RANGE = Literal["last_1h", "last_6h", "last_24h", "last_7d", "last_30d", "today", "yesterday"]


def _resolve_time_window(
    time_range: str,
    start_time: str | None,
    end_time: str | None,
) -> tuple[str, str]:
    """Return (start_at, end_at) as RFC 3339 strings.

    If both start_time and end_time are provided, use them as-is.
    Otherwise compute the window from the time_range preset.
    """
    if start_time and end_time:
        return start_time, end_time
    start_dt, end_dt = compute_time_window(time_range)

    def fmt(dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"

    return fmt(start_dt), fmt(end_dt)


def register(mcp):

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_events(
        ctx: Context,
        context_type: CONTEXT_TYPE,
        context_identifier: str,
        site_id: str,
        time_range: TIME_RANGE = "last_1h",
        start_time: str | None = None,
        end_time: str | None = None,
        search: str | None = None,
        limit: int = 50,
        cursor: int | None = None,
    ) -> PaginatedEvents | str:
        """
        Retrieve events for a given context (site, device, or client) within a specified time range.

        Use central_get_events_count first to understand what event types and volumes exist before
        fetching full event records.

        To page through results, pass the `next_cursor` value from the previous response as `cursor`
        in the next call. When `next_cursor` is None, there are no more pages.

        Parameters:
        - context_type: Type of context entity — what context_identifier refers to. Allowed values:
          SITE, ACCESS_POINT, SWITCH, GATEWAY, WIRELESS_CLIENT, WIRED_CLIENT, BRIDGE.
        - context_identifier: Identifier for the context — site ID if context_type is SITE, device
          serial number if context_type is a device type, or client MAC address if a client type.
        - site_id: Site ID to scope events. Required even when context_type is not SITE.
        - time_range: Predefined time window. Allowed values: last_1h, last_6h, last_24h, last_7d,
          last_30d, today, yesterday. Ignored if both start_time and end_time are provided.
        - start_time: Start of the time window in RFC 3339 format
          (e.g. "2026-03-21T00:00:00.000Z"). Overrides time_range when combined with end_time.
        - end_time: End of the time window in RFC 3339 format
          (e.g. "2026-03-21T23:59:59.999Z"). Overrides time_range when combined with start_time.
        - search: Search events by name, serial number, host name, or MAC address. Restricted to
          metadata fields only; full-text search is not supported.
        - limit: Number of events per page (default 50, max 100).
        - cursor: Pagination cursor from a previous response's `next_cursor` field. Omit or
          pass None to start from the first page.

        WARNING: last_30d can match thousands of events. Use central_get_events_count first to
        assess volume, then page incrementally using cursor.
        """
        start_at, end_at = _resolve_time_window(time_range, start_time, end_time)

        query_params: dict = {
            "context-type": context_type,
            "context-identifier": context_identifier,
            "start-at": start_at,
            "end-at": end_at,
            "site-id": site_id,
        }
        if search:
            query_params["search"] = search

        query_params["limit"] = limit
        if cursor is not None:
            query_params["next"] = cursor

        try:
            response = retry_central_command(
                ctx.lifespan_context["central_conn"],
                api_method="GET",
                api_path="network-troubleshooting/v1/events",
                api_params=query_params,
            )
        except Exception as e:
            return f"Error fetching events: {e}"

        msg = response["msg"]
        raw_events = msg.get("events", [])  # key is "events", not "items"
        return PaginatedEvents(
            items=[Event(**e) for e in raw_events],
            total=msg.get("total", 0),
            next_cursor=msg.get("next"),
        )

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_events_count(
        ctx: Context,
        context_type: CONTEXT_TYPE,
        context_identifier: str,
        site_id: str,
        time_range: TIME_RANGE = "last_1h",
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> EventFilters:
        """
        Return a breakdown of event counts for a context without fetching full event details.

        Use this before central_get_events to understand what types and volumes of events exist,
        avoiding the overhead of retrieving all event records.

        Parameters:
        - context_type: Type of context entity. Allowed values: SITE, ACCESS_POINT, SWITCH,
          GATEWAY, WIRELESS_CLIENT, WIRED_CLIENT, BRIDGE.
        - context_identifier: Identifier for the context — site ID, device serial number, or
          client MAC address.
        - site_id: Site ID to scope events to a specific site.
        - time_range: Predefined time window. Allowed values: last_1h, last_6h, last_24h,
          last_7d, last_30d, today, yesterday. Ignored if both start_time and end_time are
          provided.
        - start_time: Start of the time window in RFC 3339 format
          (e.g. "2026-03-21T00:00:00.000Z"). Overrides time_range when combined with end_time.
        - end_time: End of the time window in RFC 3339 format
          (e.g. "2026-03-21T23:59:59.999Z"). Overrides time_range when combined with start_time.

        Returns an EventFilters object: total event count plus breakdowns by event name, source
        type, and category.
        """
        start_at, end_at = _resolve_time_window(time_range, start_time, end_time)

        response = retry_central_command(
            ctx.lifespan_context["central_conn"],
            api_method="GET",
            api_path="network-troubleshooting/v1/event-filters",
            api_params={
                "context-type": context_type,
                "context-identifier": context_identifier,
                "start-at": start_at,
                "end-at": end_at,
                "site-id": site_id,
            },
        )
        return clean_event_filters(response["msg"])
