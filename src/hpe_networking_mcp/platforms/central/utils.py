from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from hpe_networking_mcp.platforms.central.models import (
    Alert,
    Client,
    Device,
    EventCategoryCount,
    EventFilters,
    EventNameCount,
    EventSourceTypeCount,
    SiteData,
    SiteMetrics,
)


def normalize_site_name_filter(value: str | list[str] | None) -> list[str] | None:
    """Accept a single site name, a list, or None; return a canonical list or None.

    Exists so tool parameters named ``site_name`` can accept either shape
    without surprising LLMs that pattern-match against the singular-string
    convention used by peer Central tools. Introduced for issue #146.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    return list(value)


def as_comma_separated(value: str | list[str] | None) -> str | None:
    """Normalize a filter value into the comma-separated string form Central expects.

    Central's OData filter helpers (and ``build_odata_filter``) accept a
    comma-separated string and split on commas to build ``in (...)`` clauses.
    This helper lets tool parameters accept either shape::

        "AP43"                 -> "AP43"              (unchanged)
        "AP43,AP44"            -> "AP43,AP44"         (unchanged)
        ["AP43", "AP44"]       -> "AP43,AP44"         (joined)
        None                   -> None

    Introduced for the Mist/Central filter-parameter consistency sweep (#156).
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return ",".join(str(v) for v in value)


@dataclass
class FilterField:
    api_field: str
    allowed_values: list[str] | None = None  # None = free text, list = enumerated


def build_odata_filter(
    pairs: list[tuple["FilterField", str]],
) -> str | None:
    """
    Build an OData v4.0 filter string from (FilterField, value) pairs.

    - Uses 'in (...)' for comma-separated values, 'eq' for single values.
    - Raises ValueError if a value is not in FilterField.allowed_values (when defined).
    - Returns None if pairs is empty.
    """
    if not pairs:
        return None

    parts = []
    for ff, value in pairs:
        if ff.allowed_values is not None:
            submitted = [v.strip() for v in value.split(",")]
            invalid = [v for v in submitted if v not in ff.allowed_values]
            if invalid:
                raise ValueError(f"Invalid value(s) {invalid} for field '{ff.api_field}'. Allowed: {ff.allowed_values}")

        if "," in value:
            values_list = [v.strip() for v in value.split(",")]
            values_str = ", ".join(f"'{v}'" for v in values_list)
            parts.append(f"{ff.api_field} in ({values_str})")
        else:
            parts.append(f"{ff.api_field} eq '{value}'")

    return " and ".join(parts)


SITE_LIMIT = 100


def fetch_site_data_parallel(
    central_conn: Any,
) -> dict[str, SiteData]:
    """
    Fetch site health, device health, and client health data in parallel.

    Args:
        central_conn: Central API connection object

    Returns:
        dict mapping site names to SiteData objects
    """
    endpoints = [
        "network-monitoring/v1/sites-health",
        "network-monitoring/v1/sites-device-health",
        "network-monitoring/v1/sites-client-health",
    ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(paginated_fetch, central_conn, endpoint, SITE_LIMIT) for endpoint in endpoints]
        results = [future.result() for future in futures]

    return process_site_health_data(*results)


def process_site_health_data(
    site_health: list,
    device_health: list,
    client_health: list,
) -> dict[str, SiteData]:
    """
    Combine site health, device health, and client health data into unified
    site objects.

    Args:
        site_health: List of site health data
        device_health: List of device health data by site
        client_health: List of client health data by site

    Returns:
        dict: Dictionary of site names to SiteData objects
    """
    processed_sites: dict[str, SiteData] = {
        site["name"]: transform_to_site_data(site) for site in site_health if "name" in site
    }

    for site in device_health:
        site_name = site.get("name", "")
        if site_name in processed_sites:
            processed_sites[site_name].metrics.devices["Details"] = groups_to_map(site["deviceTypes"])

    for site in client_health:
        site_name = site.get("name", "")
        if site_name in processed_sites:
            processed_sites[site_name].metrics.clients["Details"] = groups_to_map(site["clientTypes"])

    return processed_sites


def paginated_fetch(
    central_conn: Any,
    api_path: str,
    limit: int,
    total_key: str = "total",
    additional_params: dict | None = None,
    use_cursor: bool = True,
    different_response_key: str | None = None,
    items_key: str = "items",
    offset_start: int = 0,
) -> list:
    """
    Generic paginated fetch helper supporting both offset and cursor-based
    pagination.

    Args:
        central_conn: Central API connection object
        api_path: API endpoint path
        limit: Number of items per request
        total_key: Key name for total count in response
        additional_params: Additional query parameters to include
        use_cursor: If True, use cursor-based pagination (next).
            If False, use offset-based.

    Returns:
        list: All fetched items across all pages
    """
    total = None
    items: list = []
    base_params = additional_params.copy() if additional_params else {}
    if use_cursor:
        # Cursor-based pagination (preferred for API stability)
        next_cursor: int | None = 1
        while total is None or next_cursor is not None:
            params = {
                **base_params,
                "limit": limit,
                "next": next_cursor,
            }
            response = retry_central_command(
                central_conn,
                api_method="GET",
                api_path=api_path,
                api_params=params,
            )
            if different_response_key:
                response["msg"] = response["msg"].get(different_response_key, {})
            if total is None:
                total = response["msg"].get(total_key, 0)

            items.extend(response["msg"].get(items_key, []))
            next_cursor = response["msg"].get("next")
    else:
        # Offset-based pagination (legacy fallback)
        offset = offset_start
        while total is None or len(items) < total:
            params = {
                **base_params,
                "limit": limit,
                "offset": offset,
            }
            response = retry_central_command(
                central_conn,
                api_method="GET",
                api_path=api_path,
                api_params=params,
            )
            if total is None:
                total = response["msg"].get(total_key, 0)
            if different_response_key:
                response["msg"] = response["msg"].get(different_response_key, {})

            items.extend(response["msg"].get(items_key, []))
            offset += limit
    return items


def retry_central_command(
    central_conn: Any,
    api_method: str,
    api_path: str,
    api_params: dict | None = None,
    api_data: dict | None = None,
    max_retries: int = 5,
) -> dict:
    """Call central_conn.command and retry up to max_retries on transient errors.

    Args:
        central_conn: pycentral connection object.
        api_method: HTTP method (GET, POST, PUT, DELETE).
        api_path: API endpoint path.
        api_params: URL query parameters.
        api_data: Request body payload (sent as JSON for POST/PUT).
        max_retries: Max retry attempts for transient errors.

    Client errors (4xx) are raised immediately.
    """
    api_params = api_params or {}
    api_data = api_data or {}
    last_response: dict | None = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = central_conn.command(
                api_method=api_method,
                api_path=api_path,
                api_params=api_params,
                api_data=api_data,
            )
        except Exception as exc:
            central_conn.logger.error(
                "Central transport error attempt %d/%d %s %s: %s",
                attempt,
                max_retries,
                api_method,
                api_path,
                exc,
            )
            last_response = {"code": 0, "msg": str(exc)}
            continue

        code = resp.get("code", 0)
        # success
        if 200 <= code < 300:
            return resp

        # retry on server errors or rate limiting
        if code == 429 or 500 <= code < 600:
            central_conn.logger.warning(
                "Central transient response code=%s for %s %s (attempt %d/%d)",
                code,
                api_method,
                api_path,
                attempt,
                max_retries,
            )
            last_response = resp
            continue

        # client errors -> raise immediately
        if 400 <= code < 500:
            raise Exception(f"Client error from central: {resp}")

        last_response = resp

    raise Exception(f"Failed after {max_retries} attempts: {last_response}")


def transform_to_site_data(site_raw: dict) -> SiteData:
    """Transform raw Central API data to standardized SiteData model."""
    health_obj = groups_to_map(site_raw.get("health", {}))
    if all(k in health_obj for k in ["Poor", "Fair", "Good"]):
        health_obj["Summary"] = round((health_obj["Poor"] * 0) + (health_obj["Fair"] * 0.5) + (health_obj["Good"] * 1))
        health_obj.pop("Total", None)

    devices_obj = groups_to_map(site_raw.get("devices", {}))

    metrics = SiteMetrics(
        health=health_obj,
        devices={"Summary": devices_obj},
        clients={"Summary": groups_to_map(site_raw.get("clients", {}))},
        alerts=groups_to_map(site_raw.get("alerts", {})),
    )

    location = site_raw.get("location", {}) or {}
    lat = _safe_float(location.get("latitude"))
    lng = _safe_float(location.get("longitude"))

    return SiteData(
        site_id=str(site_raw.get("id", "")),
        name=str(site_raw.get("name", "")),
        address=site_raw.get("address", {}),
        location={"lat": lat, "lng": lng},
        metrics=metrics,
    )


def groups_to_map(obj: Any) -> Any:
    """
    Transform an object that either is {"groups":[...], ...}
    or wraps that as a parent (e.g. {"health": {"groups":[...], "count": ...}})
    or is a list of device/client types with nested health groups.
    """
    if not isinstance(obj, dict) and not isinstance(obj, list):
        return obj

    # Handle list of device/client types
    if isinstance(obj, list):
        result: dict = {}
        for item in obj:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            if not name:
                continue

            health_obj = item.get("health", {})
            groups = health_obj.get("groups", [])

            if groups:
                result[name] = _groups_list_to_dict(groups)

        return result

    # Handle single object with groups
    if "groups" not in obj:
        for value in obj.values():
            if isinstance(value, dict) and "groups" in value:
                obj = value
                break

    groups = obj.get("groups")
    if not isinstance(groups, list):
        return obj

    flat = _groups_list_to_dict(groups)

    total = obj.get("count") or obj.get("totalCount") or obj.get("total")
    if total is None:
        try:
            total = sum(int(v) for v in flat.values() if isinstance(v, (int, float, str)))
        except Exception:
            total = None

    if total is not None:
        flat["Total"] = total

    return flat


def _groups_list_to_dict(groups: list) -> dict:
    """Convert list of {name, value/count} to dict."""
    return {g.get("name"): g.get("value", g.get("count")) for g in groups if g.get("name") is not None}


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_device_data(devices: list[dict]) -> list[Device]:
    """
    Remove duplicate fields from device inventory data.

    Removes:
    - 'softwareVersion' (keeping 'firmwareVersion')
    - 'id' (keeping 'serialNumber')

    Args:
        devices: List of device dictionaries from API

    Returns:
        List of cleaned device dictionaries
    """
    cleaned_devices = []
    for device in devices:
        if isinstance(device, dict):
            cleaned_devices.append(
                Device(
                    serial_number=str(device.get("serialNumber", "")),
                    mac_address=str(device.get("macAddress", "")),
                    device_type=str(device.get("deviceType", "")),
                    model=str(device.get("model", "")),
                    part_number=str(device.get("partNumber", "")),
                    name=str(device.get("deviceName", "")),
                    function=device.get("deviceFunction"),
                    status=device.get("status"),
                    is_provisioned=(device.get("isProvisioned", "").lower() == "yes"),
                    role=device.get("role"),
                    deployment=device.get("deployment"),
                    tier=device.get("tier"),
                    firmware_version=device.get("firmwareVersion"),
                    site_id=device.get("siteId"),
                    site_name=device.get("siteName"),
                    device_group_name=device.get("deviceGroupName"),
                    scope_id=device.get("scopeId"),
                    ipv4=device.get("ipv4"),
                    stack_id=device.get("stackId"),
                )
            )
    return cleaned_devices


def clean_client_data(clients: list[dict]) -> list[Client]:
    """
    Transform client API response to match Client model schema.

    Converts camelCase fields to snake_case and removes duplicates.

    Args:
        clients: List of client dictionaries from API

    Returns:
        List of cleaned client dictionaries matching Client model schema
    """
    cleaned_clients = []
    for client in clients:
        if isinstance(client, dict):
            cleaned_client = {
                # Primary identifiers
                "mac": client.get("macAddress"),
                "name": client.get("clientName"),
                "ipv4": client.get("ipv4"),
                "ipv6": client.get("ipv6"),
                "hostname": client.get("hostName"),
                # Client classification
                "connection_type": client.get("clientConnectionType"),
                "os": client.get("clientOperatingSystem"),
                "vendor": client.get("clientVendor"),
                "manufacturer": client.get("clientManufacturer"),
                "category": client.get("clientCategory"),
                "function": client.get("clientFunction"),
                "capabilities": client.get("clientCapabilities"),
                # Status and health
                "status": client.get("status"),
                # Connection information
                "connected_device_type": client.get("connectedDeviceType"),
                "connected_device_serial": client.get("connectedDeviceSerial"),
                "connected_to": client.get("connectedTo"),
                "connected_at": client.get("connectedAt"),
                "last_seen_at": client.get("lastSeenAt"),
                "port": client.get("port"),
                # Network configuration
                "vlan_id": client.get("vlanId"),
                "tunnel_type": client.get("tunnelType"),
                "tunnel_id": client.get("tunnelId", None),
                # Wireless-specific fields
                "wlan_name": client.get("wlanName"),
                "wireless_band": client.get("wirelessBand"),
                "wireless_channel": client.get("wirelessChannel"),
                "wireless_security": client.get("wirelessSecurity"),
                "key_management": client.get("keyManagement"),
                "bssid": client.get("bssid"),
                "radio_mac": client.get("radioMacAddress"),
                # Authentication
                "user_name": client.get("userName"),
                "authentication": client.get("authenticationType"),
                # Site information
                "site_id": client.get("siteId"),
                "site_name": client.get("siteName"),
                # Additional metadata
                "role": client.get("role"),
                "tags": client.get("clientTags"),
            }
            conn_type = cleaned_client.get("connection_type")
            if conn_type == "Wired":
                for f in {
                    "wlan_name",
                    "wireless_band",
                    "wireless_channel",
                    "wireless_security",
                    "key_management",
                    "bssid",
                    "radio_mac",
                }:
                    cleaned_client.pop(f, None)
            elif conn_type == "Wireless":
                cleaned_client.pop("port", None)

            cleaned_clients.append(Client(**cleaned_client))
    return cleaned_clients


def clean_alert_data(alerts: list[dict]) -> list[Alert]:
    cleaned_alerts = []
    for alert in alerts:
        cleaned_alerts.append(
            Alert(
                summary=str(alert.get("summary", "")),
                cleared_reason=alert.get("clearedReason"),
                created_at=str(alert.get("createdAt", "")),
                priority=str(alert.get("priority", "")),
                updated_at=alert.get("updatedAt"),
                device_type=alert.get("deviceType"),
                updated_by=alert.get("updatedBy"),
                name=alert.get("name"),
                status=alert.get("status"),
                category=alert.get("category"),
                severity=alert.get("severity"),
            )
        )
    return cleaned_alerts


def clean_event_filters(msg: dict) -> EventFilters:
    """Transform raw event-filters API response into a structured EventFilters model."""
    categories = [EventCategoryCount(category=c["category"], count=c["count"]) for c in msg.get("categories", [])]
    return EventFilters(
        total=sum(c.count for c in categories),
        event_names=[
            EventNameCount(
                event_id=e["eventId"],
                event_name=e["eventName"],
                count=e["count"],
            )
            for e in msg.get("eventNames", [])
        ],
        source_types=[
            EventSourceTypeCount(source_type=s["sourceType"], count=s["count"]) for s in msg.get("sourceTypes", [])
        ],
        categories=categories,
    )


def compute_time_window(
    time_range: str,
) -> tuple[datetime, datetime]:
    now = datetime.now(UTC)

    if time_range == "last_1h":
        start = now - timedelta(hours=1)

    elif time_range == "last_6h":
        start = now - timedelta(hours=6)

    elif time_range == "last_24h":
        start = now - timedelta(hours=24)

    elif time_range == "last_7d":
        start = now - timedelta(days=7)

    elif time_range == "last_30d":
        start = now - timedelta(days=30)

    elif time_range == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    elif time_range == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        now = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    else:
        raise ValueError("Invalid time_range")

    return start, now


def format_rfc3339(dt: datetime) -> str:
    """Format a datetime as an RFC 3339 string with millisecond precision."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def resolve_time_window(
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
    return format_rfc3339(start_dt), format_rfc3339(end_dt)
