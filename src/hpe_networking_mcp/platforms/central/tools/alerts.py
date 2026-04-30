from typing import Literal

from fastmcp import Context
from mcp.types import ToolAnnotations

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.models import PaginatedAlerts
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import (
    FilterField,
    build_odata_filter,
    clean_alert_data,
    retry_central_command,
)

# API hard cap; limit param must not exceed this
ALERT_LIMIT = 100

ALERT_FILTER_FIELDS: dict[str, FilterField] = {
    "status": FilterField("status"),
    "device_type": FilterField("deviceType"),
    "category": FilterField("category"),
    "site_id": FilterField("siteId"),
}

# Operational annotation for state-transition actions on alerts (clear,
# defer, reactivate, set_priority). Mirrors the pattern in actions.py:
# not read-only (changes alert state), not destructive (every transition
# is reversible — Cleared/Deferred can be reactivated), idempotent (the
# same action applied twice has the same end state). NOT tagged
# `central_write_delete` — alert state transitions are operational
# actions, not config changes, so they ride alongside reboot/AP-action
# tools rather than gated behind ENABLE_CENTRAL_WRITE_TOOLS.
OPERATIONAL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


@tool(annotations=READ_ONLY)
async def central_get_alerts(
    ctx: Context,
    site_id: str,
    status: Literal["Active", "Cleared", "Deferred"] | None = "Active",
    device_type: Literal["Access Point", "Gateway", "Switch", "Bridge"] | None = None,
    category: Literal["Clients", "System", "LAN", "WLAN", "WAN", "Cluster", "Routing", "Security"] | None = None,
    sort: str = "severity desc",
    limit: int = 50,
    cursor: int | None = None,
) -> PaginatedAlerts | str:
    """
    REQUIRES site_id — call central_get_site_health(site_name="<site name>") and extract
    site_id from the returned SiteData. Do NOT call this tool without a site_id; it will
    fail validation.

    Returns a filtered list of alerts for a specific site. Use this to drill into active
    issues by device type or category after identifying the target site.

    Results are sorted by severity descending by default (Critical first), making the most
    important alerts appear in the first page. To page through results, pass the `next_cursor`
    value from the previous response as `cursor` in the next call. When `next_cursor` is None,
    there are no more pages.

    If no alerts match the criteria, returns a message indicating so.

    Parameters:
        - site_id: Site identifier. Obtain by calling
          central_get_site_health(site_name="<name>") and reading site_id from the result.
        - status: "Active" (default) for unresolved alerts, "Cleared" for resolved ones.
        - device_type: Narrow to a device class — "Access Point", "Gateway", "Switch",
          or "Bridge".
        - category: Narrow to an alert domain — "Clients", "System", "LAN", "WLAN",
          "WAN", "Cluster", "Routing", or "Security".
        - sort: Sort expression (default "severity desc" — most critical first).
          Examples: "createdAt desc", "createdAt asc".
        - limit: Number of alerts per page (default 50, max 100).
        - cursor: Pagination cursor from a previous response's `next_cursor` field.
          Omit or pass None to start from the first page.

    Note: Each alert includes summary, name, category, severity, priority, status,
    deviceType, createdAt, updatedAt, updatedBy, and clearedReason.
    """
    raw_pairs = [
        ("status", status),
        ("device_type", device_type),
        ("category", category),
        ("site_id", site_id),
    ]
    pairs = [(ALERT_FILTER_FIELDS[k], v) for k, v in raw_pairs if v is not None]

    query_params: dict = {"sort": sort}
    try:
        odata = build_odata_filter(pairs)
    except ValueError as e:
        return f"Error: {e}"
    if odata:
        query_params["filter"] = odata

    query_params["limit"] = limit
    if cursor is not None:
        query_params["next"] = cursor

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="GET",
        api_path="network-notifications/v1/alerts",
        api_params=query_params,
    )
    msg = response["msg"]
    raw_items = msg.get("items", [])
    if not raw_items:
        return "No alerts found matching criteria"
    return PaginatedAlerts(
        items=clean_alert_data(raw_items),
        total=msg.get("total", 0),
        next_cursor=msg.get("next"),
    )


# ---------------------------------------------------------------------------
# Read-only: classification + async-task status
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_alert_classification(
    ctx: Context,
    classify_by: Literal[
        "severity",
        "status",
        "priority",
        "category",
        "device_type",
        "impacted_devices",
    ],
    filter: str | None = None,
    search: str | None = None,
) -> dict | str:
    """
    Group alerts by a classification dimension and return the count per bucket.

    Use this for dashboard-style summaries (e.g. "how many critical alerts
    are open?", "which device type has the most open alerts?", "which sites
    have the most impact?"). Cheaper than paging through `central_get_alerts`
    when you only need counts.

    Parameters:
        - classify_by: How to group the alerts:
          * `severity` — by Critical / Major / Minor / etc.
          * `status` — by Active / Cleared / Deferred.
          * `priority` — by Very High / High / Medium / Low / Very Low.
          * `category` — by Clients / System / LAN / WLAN / WAN / Cluster /
            Routing / Security.
          * `device_type` — by Access Point / Gateway / Switch / Bridge.
          * `impacted_devices` — bucketed by how many alerts each affected
            device has.
        - filter: OData filter to narrow the alerts before grouping (same
          syntax as central_get_alerts: `status eq 'Active'`,
          `siteId eq '<uuid>'`, etc.). Optional.
        - search: Free-text search over alert name and summary. Optional.

    Returns the raw classification payload from Central (a dict mapping
    bucket names to counts or device lists, depending on `classify_by`).
    """
    query_params: dict = {"type": classify_by}
    if filter is not None:
        query_params["filter"] = filter
    if search is not None:
        query_params["search"] = search

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="GET",
        api_path="network-notifications/v1/alerts/classification",
        api_params=query_params,
    )
    msg = response.get("msg", response)
    if not msg:
        return "No classification data returned"
    return msg


@tool(annotations=READ_ONLY)
async def central_get_alert_action_status(
    ctx: Context,
    task_id: str,
) -> dict | str:
    """
    Get the status of an asynchronous alert action (clear / defer / reactivate /
    set_priority).

    The four alert-action tools are async — they queue the change and return
    a `task_id`. Poll this endpoint with the returned `task_id` to confirm
    completion (or surface any per-alert failures).

    Parameters:
        - task_id: The unique task identifier returned from any of the
          alert-action tools (`central_clear_alerts`, `central_defer_alerts`,
          `central_reactivate_alerts`, `central_set_alert_priority`).

    Returns the task status payload from Central.
    """
    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="GET",
        api_path=f"network-notifications/v1/alerts/async-operations/{task_id}",
    )
    msg = response.get("msg", response)
    if not msg:
        return f"No status returned for task_id={task_id}"
    return msg


# ---------------------------------------------------------------------------
# Operational: state transitions (clear / defer / reactivate / priority)
# ---------------------------------------------------------------------------
#
# All four endpoints are POSTs to /network-notifications/v1/alerts/{action}
# with a JSON body containing `keys: [string]` (alert keys returned from
# central_get_alerts). They return a task_id which the caller polls via
# central_get_alert_action_status to confirm completion.


@tool(annotations=OPERATIONAL)
async def central_clear_alerts(
    ctx: Context,
    keys: list[str],
    reason: Literal[
        "Problem was resolved",
        "False Positive",
        "Insufficient information for troubleshooting",
        "Alert is not important",
        "Other",
    ],
    notes: str | None = None,
) -> dict | str:
    """
    Clear (resolve) one or more alerts. Active → Cleared.

    Operational action — fires elicitation prompt for confirmation before
    the API call. Async — returns a `task_id`; poll
    `central_get_alert_action_status(task_id)` to confirm completion.

    Parameters:
        - keys: Alert keys to clear. Get these from
          `central_get_alerts(...)` — each item's `key` field.
        - reason: Why the alert is being cleared. Required by Central.
          Choose the closest match:
          * `Problem was resolved` — most common; the underlying issue is fixed.
          * `False Positive` — the alert fired but no real problem existed.
          * `Insufficient information for troubleshooting` — can't act on it.
          * `Alert is not important` — known, accepted, low-priority.
          * `Other` — none of the above; use `notes` to elaborate.
        - notes: Free-text notes about the clear action. Optional.

    Returns the task descriptor from Central (typically containing the
    `task_id`).
    """
    body: dict = {"keys": keys, "reason": reason}
    if notes is not None:
        body["notes"] = notes

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="POST",
        api_path="network-notifications/v1/alerts/clear",
        api_data=body,
    )
    msg = response.get("msg", response)
    return msg or f"Clear request submitted for {len(keys)} alert(s); response was empty"


@tool(annotations=OPERATIONAL)
async def central_defer_alerts(
    ctx: Context,
    keys: list[str],
    defer_until: str,
) -> dict | str:
    """
    Defer one or more alerts until a specific future time. Active → Deferred.

    A deferred alert is silenced (won't show in Active queries) until the
    `defer_until` time, after which it returns to Active state automatically
    if the underlying condition still applies.

    Operational action — fires elicitation prompt for confirmation. Async —
    returns a `task_id`; poll `central_get_alert_action_status(task_id)`.

    Parameters:
        - keys: Alert keys to defer. Get these from `central_get_alerts(...)`.
        - defer_until: ISO 8601 datetime string with timezone, e.g.
          `2026-05-15T10:00:00Z` or `2026-05-15T10:00:00-04:00`. Must be a
          future time. The system clock used for "now" is Central's, not
          the operator's — pass an absolute timestamp, not a relative
          offset.

    Returns the task descriptor from Central (typically containing `task_id`).
    """
    body = {"keys": keys, "deferUntil": defer_until}

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="POST",
        api_path="network-notifications/v1/alerts/defer",
        api_data=body,
    )
    msg = response.get("msg", response)
    return msg or f"Defer request submitted for {len(keys)} alert(s); response was empty"


@tool(annotations=OPERATIONAL)
async def central_reactivate_alerts(
    ctx: Context,
    keys: list[str],
) -> dict | str:
    """
    Reactivate one or more alerts. Cleared / Deferred → Active.

    Use this to undo a previous clear or defer, e.g. when a cleared alert
    needs to be revisited or when a deferred alert needs to come back early.

    Operational action — fires elicitation prompt. Async — returns a
    `task_id`; poll `central_get_alert_action_status(task_id)` to confirm.

    Parameters:
        - keys: Alert keys to reactivate. Get these from
          `central_get_alerts(status="Cleared", ...)` or
          `central_get_alerts(status="Deferred", ...)`.

    Returns the task descriptor from Central.
    """
    body = {"keys": keys}

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="POST",
        api_path="network-notifications/v1/alerts/active",
        api_data=body,
    )
    msg = response.get("msg", response)
    return msg or f"Reactivate request submitted for {len(keys)} alert(s); response was empty"


@tool(annotations=OPERATIONAL)
async def central_set_alert_priority(
    ctx: Context,
    keys: list[str],
    priority: Literal["Very High", "High", "Medium", "Low", "Very Low"],
) -> dict | str:
    """
    Set the operator-assigned priority on one or more alerts.

    Priority is the operator's classification (how important the alert is
    *to me*) and is distinct from `severity`, which Central assigns based
    on the alert type. Two alerts with the same severity can have different
    priorities depending on operational context.

    Operational action — fires elicitation prompt. Async — returns a
    `task_id`; poll `central_get_alert_action_status(task_id)` to confirm.

    Parameters:
        - keys: Alert keys to update. Get these from `central_get_alerts(...)`.
        - priority: New priority level. One of `Very High`, `High`, `Medium`,
          `Low`, `Very Low`.

    Returns the task descriptor from Central.
    """
    body = {"keys": keys, "priority": priority}

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="POST",
        api_path="network-notifications/v1/alerts/priority",
        api_data=body,
    )
    msg = response.get("msg", response)
    return msg or f"Priority update submitted for {len(keys)} alert(s); response was empty"
