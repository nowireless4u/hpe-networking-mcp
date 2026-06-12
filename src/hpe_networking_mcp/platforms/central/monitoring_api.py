"""Faithful async port of the pycentral monitoring/troubleshooting helper subset.

Ported as part of the pycentral SDK removal. The SDK's static-method classes
(``MonitoringAPs``, ``MonitoringGateways``, ``MonitoringSites``,
``MonitoringDevices``, ``Clients``, ``Troubleshooting``) become module-level
async functions that call ``await conn.command(...)`` against the repo's
:class:`~hpe_networking_mcp.platforms.central.client.CentralClient`.

IMPORTANT: exception MESSAGE FORMATS are load-bearing — call sites string-match
them (e.g. ``tools/clients.py`` matches the missing-client text embedded in the
"Error retrieving data from ..." message raised by :func:`execute_get`). Do not
reword any raised message.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger


class ParameterError(ValueError):
    """Invalid or missing parameter (local stand-in for pycentral's ParameterError)."""


# --- Constants (verbatim from the SDK modules) -----------------------------------

AP_LIMIT = 100
WLAN_LIMIT = 100
GATEWAY_LIMIT = 100
SITE_LIMIT = 100
DEVICE_LIMIT = 1000
CLIENT_LIMIT = 1000

_GATEWAY_API_VERSION = "v1alpha1"

SUPPORTED_DEVICE_TYPES = ["aos-s", "cx", "aps", "gateways"]

TROUBLESHOOTING_METHOD_DEVICE_MAPPING = {
    "retrieve_arp_table_test": ["aos-s", "aps", "gateways"],
    "locate_test": ["cx", "aps", "gateways"],
    "http_test": ["cx", "aps", "gateways"],
    "poe_bounce_test": ["cx", "aos-s", "gateways"],
    "port_bounce_test": ["cx", "aos-s", "gateways"],
    "speedtest_test": ["aps"],
    "aaa_test": ["cx", "aps"],
    "tcp_test": ["aps"],
    "iperf_test": ["gateways"],
    "cable_test": ["cx", "aos-s"],
    "nslookup_test": ["aps"],
    "disconnect_user_mac_addr": ["aps"],
    "disconnect_all_users": ["aps"],
    "disconnect_all_users_ssid": ["aps"],
    "disconnect_all_clients": ["gateways"],
    "disconnect_client_mac_addr": ["gateways"],
}

# --- URL generation (port of pycentral.utils.url_utils.generate_url) -------------

_VERSIONS = ["v1alpha1", "v1"]
_CATEGORIES: dict[str, dict[str, str]] = {
    "monitoring": {"value": "network-monitoring", "latest": "v1"},
    "troubleshooting": {"value": "network-troubleshooting", "latest": "v1alpha1"},
}


def _generate_url(api_endpoint: str, category: str = "monitoring", version: str = "latest") -> str:
    """Generate the full API path for an endpoint, category, and version.

    Mirrors pycentral's ``generate_url`` for the two categories this module
    uses: ``monitoring`` resolves ``latest`` to ``v1`` under
    ``network-monitoring/``; ``troubleshooting`` resolves ``latest`` to
    ``v1alpha1`` under ``network-troubleshooting/``. Explicit versions must be
    one of ``v1alpha1`` / ``v1``.

    Args:
        api_endpoint: Endpoint path to append.
        category: API category name ("monitoring" or "troubleshooting").
        version: API version ("latest", "v1", or "v1alpha1").

    Returns:
        Path in the form ``<category-value>/<version>/<api_endpoint>``.

    Raises:
        ValueError: If category or version is unsupported.
        TypeError: If api_endpoint is not a string.
    """
    if category not in _CATEGORIES:
        raise ValueError(f"Invalid category: {category}, Supported categories: {list(_CATEGORIES.keys())}")
    if api_endpoint is not None and not isinstance(api_endpoint, str):
        raise TypeError(f"Invalid type: {type(api_endpoint)} for api_endpoint, expected str")
    category_value = _CATEGORIES[category]["value"]
    if version == "latest":
        version = _CATEGORIES[category]["latest"]
    elif version not in _VERSIONS:
        raise ValueError(f"Invalid version: {version}. Allowed versions: {_VERSIONS}")
    return f"{category_value}/{version}/{api_endpoint}"


# --- Core GET helper (port of monitoring_utils.execute_get) ----------------------


async def execute_get(
    conn: Any,
    endpoint: str,
    params: dict[str, Any] | None = None,
    version: str = "latest",
) -> Any:
    """Execute a GET request to the monitoring API.

    Args:
        conn: CentralClient connection object.
        endpoint: API endpoint path (without the network-monitoring prefix).
        params: Query parameters for the request.
        version: API version to use (e.g. "v1alpha1", "v1"). Defaults to "latest".

    Returns:
        The ``msg`` portion of the API response.

    Raises:
        ParameterError: If conn is None or endpoint is invalid.
        Exception: If the API call returns a non-200 status code. The message
            format is load-bearing (string-matched by call sites) — do not change.
    """
    if not conn:
        raise ParameterError("central_conn(Central connection) is required")

    if not endpoint or (not isinstance(endpoint, str) and len(endpoint) == 0):
        raise ParameterError("endpoint is required and must be a string")

    if endpoint.startswith("/"):
        # remove leading slash if present
        endpoint = endpoint.lstrip("/")

    path = _generate_url(endpoint, "monitoring", version)
    resp = await conn.command(api_method="GET", api_path=path, api_params=params if params is not None else {})

    if resp["code"] != 200:
        raise Exception(f"Error retrieving data from {path}: {resp['code']} - {resp['msg']}")
    return resp["msg"]


# --- Timestamp helpers (verbatim from monitoring_utils) --------------------------


def build_timestamp_filter(
    start_time: str | int | float | None = None,
    end_time: str | int | float | None = None,
    duration: str | None = None,
    fmt: str = "rfc3339",
) -> tuple[str, str]:
    """Build a formatted timestamp filter for API queries.

    Behavior:
        - If start_time and end_time are given, parses and converts them to the
          requested format.
        - If duration is given, computes timestamps relative to now.
        - Max supported duration is 3 months (90 days).

    Args:
        start_time: RFC3339 or Unix timestamp (ms or s) for start.
        end_time: RFC3339 or Unix timestamp (ms or s) for end.
        duration: Duration string like '3h', '2d', '1w', '1m' (hours, days, weeks, minutes).
        fmt: Output format, either 'rfc3339' or 'unix'.

    Returns:
        Tuple of (start_time, end_time) formatted strings.

    Raises:
        ValueError: If invalid parameter combinations are provided or duration exceeds maximum.
    """
    if (start_time or end_time) and duration:
        raise ValueError("Cannot specify start/end timestamps together with duration.")
    if (start_time and not end_time) or (end_time and not start_time):
        raise ValueError("Both start_time and end_time must be provided together.")
    if not duration and not (start_time and end_time):
        raise ValueError("Provide either both start_time and end_time or a duration.")

    if start_time and end_time:
        return (
            _format_timestamp(_parse_timestamp(start_time), fmt),
            _format_timestamp(_parse_timestamp(end_time), fmt),
        )

    # --- Case 2: Duration (guaranteed non-None by the validation above) ---
    if duration is None:  # pragma: no cover - re-checked only to narrow the type
        raise ValueError("Provide either both start_time and end_time or a duration.")
    unit_map = {"w": "weeks", "d": "days", "h": "hours", "m": "minutes"}
    unit = duration[-1].lower()
    if unit not in unit_map:
        raise ValueError("Duration must end with w, h, d, or m (weeks, hours, days, mins).")

    delta = timedelta(**{unit_map[unit]: int(duration[:-1])})
    if delta > timedelta(days=90):
        raise ValueError("Maximum supported duration is 3 months (90 days).")

    now = datetime.now(UTC)
    return _format_timestamp(now - delta, fmt), _format_timestamp(now, fmt)


def _parse_timestamp(ts: str | int | float) -> datetime:
    """Parse an RFC3339 string or Unix ms/s value into a UTC datetime."""
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            ts = float(ts)
    val = float(ts)
    if val > 1e10:
        val /= 1000
    return datetime.fromtimestamp(val, tz=UTC)


def _format_timestamp(dt: datetime, fmt: str) -> str:
    """Format a UTC datetime as a Unix ms string or RFC3339 string."""
    if fmt == "unix":
        return str(int(dt.timestamp() * 1000))
    return dt.isoformat().replace("+00:00", "Z")


def generate_timestamp_str(
    start_time: str | int | float | None,
    end_time: str | int | float | None,
    duration: str | None,
) -> str:
    """Generate a timestamp filter string for API queries.

    Args:
        start_time: Start timestamp.
        end_time: End timestamp.
        duration: Duration string.

    Returns:
        Formatted filter string "timestamp gt <start> and timestamp lt <end>".
    """
    start_time, end_time = build_timestamp_filter(start_time=start_time, end_time=end_time, duration=duration)
    return f"timestamp gt {start_time} and timestamp lt {end_time}"


# --- Response-shaping helpers (verbatim from monitoring_utils) --------------------


def simplified_site_resp(site: dict[str, Any]) -> dict[str, Any]:
    """Simplify the site response structure for easier consumption.

    Args:
        site: Raw site data from API response.

    Returns:
        Simplified site data with restructured health, devices, clients, and alerts.
    """
    site["health"] = _groups_to_dict(site.get("health", {}).get("groups", []))
    site["devices"] = {
        "count": site.get("devices", {}).get("count", 0),
        "health": _groups_to_dict(site.get("devices", {}).get("health", {}).get("groups", [])),
    }
    site["clients"] = {
        "count": site.get("clients", {}).get("count", 0),
        "health": _groups_to_dict(site.get("clients", {}).get("health", {}).get("groups", [])),
    }
    site["alerts"] = {
        "critical": site.get("alerts", {}).get("groups", [{}])[0].get("count", 0)
        if site.get("alerts", {}).get("groups")
        else 0,
        "total": site.get("alerts", {}).get("totalCount", 0),
    }
    site.pop("type", None)
    return site


def _groups_to_dict(groups_list: list[Any]) -> dict[str, Any]:
    """Convert a list of group objects to a dictionary.

    Args:
        groups_list: List of group dictionaries with 'name' and 'value' keys.

    Returns:
        Dictionary with group names as keys and values as values.
        Defaults to {"Poor": 0, "Fair": 0, "Good": 0}.
    """
    result: dict[str, Any] = {"Poor": 0, "Fair": 0, "Good": 0}
    if isinstance(groups_list, list):
        for group in groups_list:
            if isinstance(group, dict) and "name" in group and "value" in group:
                result[group["name"]] = group["value"]
    return result


def clean_raw_trend_data(raw_results: dict[str, Any], data: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Clean and restructure raw trend data from API response.

    Args:
        raw_results: Raw trend data containing 'graph' with 'keys' and 'samples'.
        data: Existing data dictionary to append to.

    Returns:
        Dictionary with timestamps as keys and metric values as nested dictionaries.
    """
    if data is None:
        data = {}
    graph = raw_results.get("graph", {}) or {}
    keys = graph.get("keys", []) or []
    samples = graph.get("samples", []) or []

    for s in samples:
        ts = s.get("timestamp")
        if not ts:
            continue
        vals = s.get("data")
        if isinstance(vals, list | tuple):
            for k, v in zip(keys, vals, strict=False):
                data.setdefault(ts, {})[k] = v
        else:
            target_key = keys[0] if keys else None
            if target_key:
                data.setdefault(ts, {})[target_key] = vals
            else:
                # fallback to a generic key if none provided
                data.setdefault(ts, {})["value"] = vals
    return data


def merged_dict_to_sorted_list(merged: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a merged dictionary to a sorted list of timestamped entries.

    Args:
        merged: Dictionary with timestamps as keys.

    Returns:
        Sorted list of dictionaries with 'timestamp' key and all associated values.
    """
    # try strict RFC3339 parsing (Z -> +00:00), fallback to lexicographic
    try:
        keys = sorted(merged.keys(), key=lambda t: datetime.fromisoformat(t.replace("Z", "+00:00")))
    except Exception:
        keys = sorted(merged.keys())
    return [{"timestamp": ts, **merged[ts]} for ts in keys]


def _validate_mac_address(mac: str) -> bool:
    """Validate a MAC address string in AA:BB:CC:DD:EE:FF format.

    Args:
        mac: MAC address string to validate.

    Returns:
        True if the MAC address is valid.

    Raises:
        ParameterError: If mac is missing or does not match the expected format.
    """
    _mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
    if not mac:
        raise ParameterError("MAC address is required")
    if not isinstance(mac, str) or not _mac_pattern.match(mac):
        raise ParameterError(f"Invalid MAC address format: '{mac}'. Expected format: AA:BB:CC:DD:EE:FF")
    return True


def _validate_device_serial(serial_number: str) -> None:
    """Validate an AP device serial_number.

    Raises:
        ParameterError: If serial_number is missing or not a string.
    """
    if not isinstance(serial_number, str) or not serial_number:
        raise ParameterError("serial_number is required and must be a string")


def _validate_central_conn_and_serial(central_conn: Any, serial_number: str) -> None:
    """Validate central_conn and serial_number (gateway functions).

    Raises:
        ParameterError: If central_conn is None or serial_number is missing/invalid.
    """
    if central_conn is None:
        raise ParameterError("central_conn is required")
    if not isinstance(serial_number, str) or not serial_number:
        raise ParameterError("serial_number is required and must be a string")


# --- APs (port of new_monitoring.aps.MonitoringAPs) -------------------------------


async def get_all_aps(
    central_conn: Any,
    filter_str: str | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve all access points (APs), handling pagination.

    Args:
        central_conn: CentralClient connection object.
        filter_str: Optional filter expression.
        sort: Optional sort parameter.

    Returns:
        List of AP items.
    """
    aps: list[dict[str, Any]] = []
    total_aps = None
    next_page = 1
    while True:
        resp = await get_aps(central_conn, filter_str=filter_str, sort=sort, limit=AP_LIMIT, next_page=next_page)
        if total_aps is None:
            total_aps = resp.get("total", 0)

        aps.extend(resp["items"])

        if len(aps) == total_aps:
            break

        next_val = resp.get("next")
        if not next_val:
            break

        next_page = int(next_val)
    return aps


async def get_aps(
    central_conn: Any,
    filter_str: str | None = None,
    sort: str | None = None,
    limit: int = AP_LIMIT,
    next_page: int = 1,
) -> dict[str, Any]:
    """Retrieve a single page of APs (``GET network-monitoring/v1/aps``).

    Args:
        central_conn: CentralClient connection object.
        filter_str: Optional filter expression.
        sort: Optional sort parameter.
        limit: Number of entries to return (default is 100).
        next_page: Pagination cursor/index for next page (default is 1).

    Returns:
        API response for the aps endpoint (contains 'items', 'total', etc.).

    Raises:
        ParameterError: If limit or next_page values are invalid.
    """
    path = "aps"
    if limit > AP_LIMIT:
        raise ParameterError(f"limit cannot exceed {AP_LIMIT}")
    if next_page < 1:
        raise ParameterError("next_page must be 1 or greater")
    params = {"filter": filter_str, "sort": sort, "limit": limit, "next": next_page}
    return await execute_get(central_conn, endpoint=path, params=params)


async def get_ap_details(central_conn: Any, serial_number: str) -> dict[str, Any]:
    """Get details for a specific AP (``GET network-monitoring/v1/aps/{serial_number}``).

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the AP.

    Returns:
        API response with AP details.

    Raises:
        ParameterError: If serial_number is missing/invalid.
    """
    _validate_device_serial(serial_number)
    path = f"aps/{serial_number}"
    return await execute_get(central_conn, endpoint=path)


async def get_ap_stats(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
    return_raw_response: bool = False,
) -> list[dict[str, Any]] | list[Any]:
    """Collect CPU, memory, and power-consumption statistics for an AP.

    Default is to return sorted trend statistics for the API's default window.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the AP.
        start_time: Start time (epoch seconds or RFC3339) for range queries.
        end_time: End time (epoch seconds or RFC3339) for range queries.
        duration: Duration string (e.g. '5m') for relative queries.
        return_raw_response: If True, return raw per-metric responses.

    Returns:
        Raw list of responses if return_raw_response is True; otherwise merged,
        sorted trend statistics for the AP.

    Raises:
        ParameterError: If serial_number is missing/invalid.
        RuntimeError: If any of the parallel metric requests fail.
    """
    _validate_device_serial(serial_number)

    # dispatch the three metric calls in parallel; helper functions handle timestamp logic
    funcs = [get_ap_cpu_utilization, get_ap_memory_utilization, get_ap_poe_utilization]

    async def _run(func: Callable[..., Awaitable[Any]]) -> Any:
        try:
            return await func(central_conn, serial_number, start_time, end_time, duration)
        except Exception as e:
            # propagate the error for the caller to handle, but include which call failed
            raise RuntimeError(f"{func.__name__} metrics request failed: {e}") from e

    raw_results = list(await asyncio.gather(*(_run(func) for func in funcs)))

    if return_raw_response:
        return raw_results

    data: dict[str, dict[str, Any]] = {}
    for resp in raw_results:
        if not isinstance(resp, dict):
            continue
        data = clean_raw_trend_data(resp, data=data)
    return merged_dict_to_sorted_list(data)


async def get_ap_cpu_utilization(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
) -> Any:
    """Retrieve CPU utilization trends for an AP.

    Calls ``GET network-monitoring/v1/aps/{serial_number}/cpu-utilization-trends``.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the AP.
        start_time: Start time for range queries.
        end_time: End time for range queries.
        duration: Duration string for relative queries.

    Returns:
        API response for cpu-utilization-trends.

    Raises:
        ParameterError: If serial_number is missing/invalid.
    """
    _validate_device_serial(serial_number)
    path = f"aps/{serial_number}/cpu-utilization-trends"
    if start_time is None and end_time is None and duration is None:
        return await execute_get(central_conn, endpoint=path)

    return await execute_get(
        central_conn,
        endpoint=path,
        params={"filter": generate_timestamp_str(start_time=start_time, end_time=end_time, duration=duration)},
    )


async def get_ap_memory_utilization(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
) -> Any:
    """Retrieve memory utilization trends for an AP.

    Calls ``GET network-monitoring/v1/aps/{serial_number}/memory-utilization-trends``.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the AP.
        start_time: Start time for range queries.
        end_time: End time for range queries.
        duration: Duration string for relative queries.

    Returns:
        API response for memory-utilization-trends.

    Raises:
        ParameterError: If serial_number is missing/invalid.
    """
    _validate_device_serial(serial_number)
    path = f"aps/{serial_number}/memory-utilization-trends"
    if start_time is None and end_time is None and duration is None:
        return await execute_get(central_conn, endpoint=path)

    return await execute_get(
        central_conn,
        endpoint=path,
        params={"filter": generate_timestamp_str(start_time=start_time, end_time=end_time, duration=duration)},
    )


async def get_ap_poe_utilization(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
) -> Any:
    """Retrieve power consumption trends for an AP.

    Calls ``GET network-monitoring/v1/aps/{serial_number}/power-consumption-trends``.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the AP.
        start_time: Start time for range queries.
        end_time: End time for range queries.
        duration: Duration string for relative queries.

    Returns:
        API response for power-consumption-trends.

    Raises:
        ParameterError: If serial_number is missing/invalid.
    """
    _validate_device_serial(serial_number)
    path = f"aps/{serial_number}/power-consumption-trends"
    if start_time is None and end_time is None and duration is None:
        return await execute_get(central_conn, endpoint=path)

    return await execute_get(
        central_conn,
        endpoint=path,
        params={"filter": generate_timestamp_str(start_time=start_time, end_time=end_time, duration=duration)},
    )


async def get_wlans(
    central_conn: Any,
    site_id: str | None = None,
    serial_number: str | None = None,
    filter_str: str | None = None,
    sort: str | None = None,
    limit: int = WLAN_LIMIT,
    next_page: int = 1,
) -> dict[str, Any]:
    """Retrieve a list of WLANs associated to a customer (``GET network-monitoring/v1/wlans``).

    Args:
        central_conn: CentralClient connection object.
        site_id: ID of the Site for which WLAN information is requested. Max length 128.
        serial_number: Serial number of an access point device. Max length 16.
        filter_str: OData v4 filter string (limited; 'and' only). Max length 256.
        sort: Comma separated list of sort expressions. Max length 256.
        limit: Maximum number of WLANs to return (0-100).
        next_page: Pagination cursor for next page (default is 1).

    Returns:
        API response containing 'items', 'count', 'total', and 'next'.

    Raises:
        ParameterError: If limit exceeds 100, next_page is less than 1, or any
            string parameter exceeds its maximum length.
    """
    path = "wlans"

    if limit > WLAN_LIMIT:
        raise ParameterError(f"limit cannot exceed {WLAN_LIMIT}")
    if next_page < 1:
        raise ParameterError("next_page must be 1 or greater")

    if site_id is not None and len(site_id) > 128:
        raise ParameterError("site_id cannot exceed 128 characters")
    if serial_number is not None and len(serial_number) > 16:
        raise ParameterError("serial_number cannot exceed 16 characters")
    if filter_str is not None and len(filter_str) > 256:
        raise ParameterError("filter_str cannot exceed 256 characters")
    if sort is not None and len(sort) > 256:
        raise ParameterError("sort cannot exceed 256 characters")

    params = {
        "site-id": site_id,
        "serial-number": serial_number,
        "filter": filter_str,
        "sort": sort,
        "limit": limit,
        "next": next_page,
    }
    return await execute_get(central_conn, endpoint=path, params=params)


async def get_ap_wlans(central_conn: Any, serial_number: str) -> dict[str, Any]:
    """Retrieve WLANs associated with an AP (``GET network-monitoring/v1/aps/{serial_number}/wlans``).

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the AP.

    Returns:
        API response of associated WLANs.

    Raises:
        ParameterError: If serial_number is missing/invalid.
    """
    _validate_device_serial(serial_number)
    path = f"aps/{serial_number}/wlans"
    return await execute_get(central_conn, endpoint=path)


# --- Gateways (port of new_monitoring.gateways.MonitoringGateways) ----------------


async def get_gateway_details(central_conn: Any, serial_number: str) -> dict[str, Any]:
    """Get details for a specific gateway (``GET network-monitoring/v1alpha1/gateways/{serial_number}``).

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the gateway.

    Returns:
        API response with gateway details.

    Raises:
        ParameterError: If central_conn is None or serial_number is missing/invalid.
    """
    _validate_central_conn_and_serial(central_conn, serial_number)
    path = f"gateways/{serial_number}"
    return await execute_get(central_conn, endpoint=path, version=_GATEWAY_API_VERSION)


async def get_gateway_stats(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
    return_raw_response: bool = False,
) -> list[dict[str, Any]] | list[Any]:
    """Collect CPU, memory, and WAN-availability statistics for a gateway.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the gateway.
        start_time: Start time for range queries.
        end_time: End time for range queries.
        duration: Duration string (e.g. '5m') for relative queries.
        return_raw_response: If True, return raw per-metric API responses.

    Returns:
        Raw list of responses if return_raw_response is True; otherwise merged,
        sorted trend statistics for the gateway.

    Raises:
        ParameterError: If central_conn is None or serial_number is missing/invalid.
        RuntimeError: If any of the parallel metric requests fail.
    """
    _validate_central_conn_and_serial(central_conn, serial_number)

    # dispatch the three metric calls in parallel; helper functions handle timestamp logic
    funcs = [get_gateway_cpu_utilization, get_gateway_memory_utilization, get_gateway_wan_availability]

    async def _run(func: Callable[..., Awaitable[Any]]) -> Any:
        try:
            return await func(central_conn, serial_number, start_time, end_time, duration)
        except Exception as e:
            # propagate the error for the caller to handle, but include which call failed
            raise RuntimeError(f"{func.__name__} metrics request failed: {e}") from e

    raw_results = []
    for resp in await asyncio.gather(*(_run(func) for func in funcs)):
        if isinstance(resp, list) and len(resp) == 1:
            resp = resp[0]
        raw_results.append(resp)

    if return_raw_response:
        return raw_results

    data: dict[str, dict[str, Any]] = {}
    for resp in raw_results:
        if not isinstance(resp, dict):
            continue
        data = clean_raw_trend_data(resp, data=data)
    return merged_dict_to_sorted_list(data)


async def get_gateway_cpu_utilization(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
) -> Any:
    """Retrieve CPU utilization trends for a gateway.

    Calls ``GET network-monitoring/v1alpha1/gateways/{serial_number}/cpu-utilization-trends``.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the gateway.
        start_time: Start time for range queries.
        end_time: End time for range queries.
        duration: Duration string for relative queries.

    Returns:
        API response for cpu-utilization-trends.

    Raises:
        ParameterError: If central_conn is None or serial_number is missing/invalid.
    """
    _validate_central_conn_and_serial(central_conn, serial_number)
    endpoint = f"gateways/{serial_number}/cpu-utilization-trends"
    if start_time is None and end_time is None and duration is None:
        return await execute_get(central_conn, endpoint=endpoint, version=_GATEWAY_API_VERSION)

    return await execute_get(
        central_conn,
        endpoint=endpoint,
        params={"filter": generate_timestamp_str(start_time=start_time, end_time=end_time, duration=duration)},
        version=_GATEWAY_API_VERSION,
    )


async def get_gateway_memory_utilization(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
) -> Any:
    """Retrieve memory utilization trends for a gateway.

    Calls ``GET network-monitoring/v1alpha1/gateways/{serial_number}/memory-utilization-trends``.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the gateway.
        start_time: Start time for range queries.
        end_time: End time for range queries.
        duration: Duration string for relative queries.

    Returns:
        API response for memory-utilization-trends.

    Raises:
        ParameterError: If central_conn is None or serial_number is missing/invalid.
    """
    _validate_central_conn_and_serial(central_conn, serial_number)
    endpoint = f"gateways/{serial_number}/memory-utilization-trends"
    if start_time is None and end_time is None and duration is None:
        return await execute_get(central_conn, endpoint=endpoint, version=_GATEWAY_API_VERSION)

    return await execute_get(
        central_conn,
        endpoint=endpoint,
        params={"filter": generate_timestamp_str(start_time=start_time, end_time=end_time, duration=duration)},
        version=_GATEWAY_API_VERSION,
    )


async def get_gateway_wan_availability(
    central_conn: Any,
    serial_number: str,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
    duration: str | None = None,
) -> Any:
    """Retrieve WAN availability trends for a gateway.

    Calls ``GET network-monitoring/v1alpha1/gateways/{serial_number}/wan-availability-trends``.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the gateway.
        start_time: Start time for range queries.
        end_time: End time for range queries.
        duration: Duration string for relative queries.

    Returns:
        API response for wan-availability-trends.

    Raises:
        ParameterError: If central_conn is None or serial_number is missing/invalid.
    """
    _validate_central_conn_and_serial(central_conn, serial_number)
    endpoint = f"gateways/{serial_number}/wan-availability-trends"
    if start_time is None and end_time is None and duration is None:
        return await execute_get(central_conn, endpoint=endpoint, version=_GATEWAY_API_VERSION)

    return await execute_get(
        central_conn,
        endpoint=endpoint,
        params={"filter": generate_timestamp_str(start_time=start_time, end_time=end_time, duration=duration)},
        version=_GATEWAY_API_VERSION,
    )


async def get_tunnel_health_summary(central_conn: Any, serial_number: str) -> dict[str, Any]:
    """Retrieve LAN tunnels health summary for a gateway.

    Calls ``GET network-monitoring/v1alpha1/gateways/{serial_number}/lan-tunnels-health-summary``.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the gateway.

    Returns:
        API response for lan-tunnels-health-summary.

    Raises:
        ParameterError: If central_conn is None or serial_number is missing/invalid.
    """
    _validate_central_conn_and_serial(central_conn, serial_number)
    path = f"gateways/{serial_number}/lan-tunnels-health-summary"
    return await execute_get(central_conn, endpoint=path, version=_GATEWAY_API_VERSION)


# --- Sites (port of new_monitoring.sites.MonitoringSites) -------------------------


async def get_all_sites(central_conn: Any, return_raw_response: bool = False) -> list[dict[str, Any]]:
    """Retrieve all sites information including health details, handling pagination.

    Args:
        central_conn: CentralClient connection object.
        return_raw_response: If True, return the raw API payloads.

    Returns:
        List of site records. If return_raw_response is False, each site
        response is simplified via simplified_site_resp.
    """
    sites: list[dict[str, Any]] = []
    total_sites = None
    limit = SITE_LIMIT
    offset = 0
    while True:
        response = await get_sites(central_conn, limit=limit, offset=offset)
        if total_sites is None:
            total_sites = response.get("total", 0)
        sites.extend(response["items"])
        if len(sites) == total_sites:
            break
        offset += limit
    if not return_raw_response:
        sites = [simplified_site_resp(site) for site in sites]
    return sites


async def get_sites(central_conn: Any, limit: int = SITE_LIMIT, offset: int = 0) -> dict[str, Any]:
    """Retrieve a single page of site health information.

    Calls ``GET network-monitoring/v1/sites-health``. Returns devices, clients,
    and critical alerts with counts, along with health and health reasons per site.

    Args:
        central_conn: CentralClient connection object.
        limit: Number of entries to return (default is 100).
        offset: Number of entries to skip for pagination (default is 0).

    Returns:
        Raw API response for the requested page (typically contains 'items' and 'total').
    """
    params = {"limit": limit, "offset": offset}
    path = "sites-health"
    return await execute_get(central_conn, endpoint=path, params=params)


# --- Devices (port of new_monitoring.devices.MonitoringDevices) -------------------


async def get_all_device_inventory(
    central_conn: Any,
    filter_str: str | None = None,
    sort: str | None = None,
    site_assigned: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve all devices from the account, including devices not yet onboarded.

    Args:
        central_conn: CentralClient connection object.
        filter_str: Optional filter expression.
        sort: Optional sort parameter.
        site_assigned: Filter by site-assigned status ("ASSIGNED" / "UNASSIGNED").

    Returns:
        Processed list of all devices from inventory.
    """
    devices: list[dict[str, Any]] = []
    total_devices = None
    next_int = 1
    while True:
        response = await get_device_inventory(
            central_conn,
            filter_str=filter_str,
            sort=sort,
            site_assigned=site_assigned,
            limit=DEVICE_LIMIT,
            next=next_int,
        )
        if total_devices is None:
            total_devices = response.get("total", 0)
        devices.extend(response.get("items", []))
        if len(devices) == total_devices:
            break
        next_int += 1

    return devices


async def get_device_inventory(
    central_conn: Any,
    filter_str: str | None = None,
    sort: str | None = None,
    site_assigned: str | None = None,
    limit: int = DEVICE_LIMIT,
    next: int = 1,  # parameter name kept identical to the SDK (shadows the builtin)
) -> dict[str, Any]:
    """Retrieve device data from the device inventory API.

    Calls ``GET network-monitoring/v1/device-inventory``. Includes devices yet
    to be onboarded as well as those already onboarded and monitored.

    Args:
        central_conn: CentralClient connection object.
        filter_str: Optional filter expression.
        sort: Optional sort parameter.
        site_assigned: Filter by site-assigned status ("ASSIGNED" / "UNASSIGNED").
        limit: Number of entries to return.
        next: Pagination cursor for next page of resources (default is 1).

    Returns:
        Raw API response containing device inventory.
    """
    params = {
        "limit": limit,
        "next": next,
        "filter": filter_str,
        "sort": sort,
        "site-assigned": site_assigned,
    }
    path = "device-inventory"
    return await execute_get(central_conn, endpoint=path, params=params)


# --- Clients (port of new_monitoring.clients.Clients) -----------------------------


async def get_all_clients(
    central_conn: Any,
    site_id: str | int | None = None,
    site_name: str | None = None,
    serial_number: str | None = None,
    filter_str: str | None = None,
    sort: str | None = None,
    duration: str | None = None,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
) -> list[dict[str, Any]]:
    """Return all clients based on the provided parameters, handling pagination.

    Args:
        central_conn: CentralClient connection object.
        site_id: Identifier of the site to query.
        site_name: Name of the site to query.
        serial_number: Device serial number to filter clients.
        filter_str: Optional filter expression.
        sort: Optional sort parameter.
        duration: Relative time window (e.g., '3h', '2d', '1w', '30m').
        start_time: Start time (RFC 3339 date-time string).
        end_time: End time (RFC 3339 date-time string).

    Returns:
        All client details for the specified parameters.

    Raises:
        ParameterError: If site_id or site_name is provided but invalid.
    """
    if site_id or site_name:
        _validate_site_id(site_id, site_name)
    clients: list[dict[str, Any]] = []
    total_clients = None
    next_page = 1
    while True:
        resp = await get_clients(
            central_conn=central_conn,
            site_id=site_id,
            site_name=site_name,
            serial_number=serial_number,
            filter_str=filter_str,
            sort=sort,
            next_page=next_page,
            limit=CLIENT_LIMIT,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
        )
        if total_clients is None:
            total_clients = resp.get("total", 0)
        clients.extend(resp.get("items", []))
        if len(clients) == total_clients:
            break
        next_val = resp.get("next")
        if not next_val:
            break
        next_page = int(next_val)
    return clients


async def get_clients(
    central_conn: Any,
    site_id: str | int | None = None,
    site_name: str | None = None,
    serial_number: str | None = None,
    filter_str: str | None = None,
    sort: str | None = None,
    next_page: int = 1,
    limit: int = CLIENT_LIMIT,
    duration: str | None = None,
    start_time: str | int | None = None,
    end_time: str | int | None = None,
) -> dict[str, Any]:
    """Fetch a page of clients based on provided parameters.

    Calls ``GET network-monitoring/v1/clients``.

    Args:
        central_conn: CentralClient connection object.
        site_id: Identifier of the site to query.
        site_name: Name of the site to query.
        serial_number: Device serial number to query.
        filter_str: Optional filter expression.
        sort: Optional sort parameter.
        next_page: Page token/index for pagination.
        limit: Maximum number of items to return.
        duration: Relative time window (e.g., '3h', '2d', '1w', '30m').
        start_time: Start time (RFC 3339 date-time string).
        end_time: End time (RFC 3339 date-time string).

    Returns:
        Raw API response containing keys like 'items', 'total', and 'next'.

    Raises:
        ParameterError: If site_id or site_name is provided but invalid.
    """
    path = "clients"

    if site_id or site_name:
        _validate_site_id(site_id, site_name)
    params: dict[str, Any] = {
        "site-id": site_id,
        "site-name": site_name,
        "serial-number": serial_number,
        "filter": filter_str,
        "sort": sort,
        "next": next_page,
        "limit": limit,
    }
    if start_time is None and end_time is None and duration is None:
        return await execute_get(central_conn, endpoint=path, params=params)

    params = _time_filter(params=params, start_time=start_time, end_time=end_time, duration=duration)

    return await execute_get(central_conn, endpoint=path, params=params)


async def get_client_details(central_conn: Any, client_mac: str) -> dict[str, Any]:
    """Fetch details for a specific client by MAC address.

    Calls ``GET network-monitoring/v1/clients/{client_mac}``. NOTE: the
    missing-client error surfaces via :func:`execute_get`'s exception message,
    which call sites string-match — do not change that format.

    Args:
        central_conn: CentralClient connection object.
        client_mac: MAC address of the client to query.

    Returns:
        Client details as returned by the API.

    Raises:
        ParameterError: If client_mac is missing or malformed.
    """
    _validate_mac_address(client_mac)

    path = f"clients/{client_mac}"
    return await execute_get(central_conn, endpoint=path)


def _time_filter(
    params: dict[str, Any],
    start_time: str | int | None,
    end_time: str | int | None,
    duration: str | None,
) -> dict[str, Any]:
    """Apply a time filter to params using RFC 3339 timestamps.

    Args:
        params: Existing query params to augment.
        start_time: Start time (RFC 3339 date-time string).
        end_time: End time (RFC 3339 date-time string).
        duration: Relative time window (e.g., '3h', '2d', '1w', '30m').

    Returns:
        Params augmented with 'start-at' and 'end-at'.
    """
    start_rfc, end_rfc = build_timestamp_filter(
        start_time=start_time,
        end_time=end_time,
        duration=duration,
        fmt="rfc3339",
    )
    params["start-at"] = start_rfc
    params["end-at"] = end_rfc
    return params


def _validate_site_id(site_id: str | int | None = None, site_name: str | None = None) -> None:
    """Validate that at least one valid site identifier is provided.

    Args:
        site_id: Site identifier to validate.
        site_name: Site name to validate.

    Raises:
        ParameterError: If site_id and site_name are not provided or invalid.
    """
    if site_id is None and site_name is None:
        raise ParameterError("either site_id or site_name must be provided")

    if site_id is not None and (not isinstance(site_id, str | int) or not site_id):
        raise ParameterError("site_id must be a non-empty string or integer")

    if site_name is not None and (not isinstance(site_name, str) or not site_name):
        raise ParameterError("site_name must be a non-empty string")


# --- Troubleshooting (port of troubleshooting.Troubleshooting subset) -------------


def _validate_required_device_params(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    subset: list[str] | None = None,
) -> str:
    """Validate that required troubleshooting parameters are set.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
        serial_number: Serial number of the device.
        subset: Subset of supported device types for the calling test.

    Returns:
        Verified device_type in lower-case format.

    Raises:
        ParameterError: If any required parameter is missing or device type is unsupported.
    """
    if not central_conn or not device_type or not serial_number:
        raise ParameterError(
            "central_conn(Central connection), device_type(aps, cx, aos-s, gateways) and serial_number are required"
        )
    if (subset and device_type.lower() not in subset) or (device_type.lower() not in SUPPORTED_DEVICE_TYPES):
        supported_devices = ", ".join(subset if subset else SUPPORTED_DEVICE_TYPES)
        raise ParameterError(f"Unsupported device type: {device_type}, supported types are {supported_devices}")
    return device_type.lower()


def _get_task_id(api_response: dict[str, Any]) -> str:
    """Extract the task ID from an async-operation API response.

    Args:
        api_response: The API response containing the task information.

    Returns:
        The extracted task ID.
    """
    return api_response.get("location", "").split("/")[-1]


async def _poll_task_completion(
    get_result_func: Callable[..., Awaitable[dict[str, Any]]],
    task_id: str,
    conn: Any,
    max_attempts: int = 5,
    poll_interval: int = 5,
    *args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generic polling for async-operation task completion.

    Args:
        get_result_func: Async function to call for getting the task result.
        task_id: Task ID to poll for.
        conn: CentralClient connection object.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.
        *args: Additional positional arguments for get_result_func.
        **kwargs: Additional keyword arguments for get_result_func.

    Returns:
        Final result from get_result_func.
    """
    result: dict[str, Any] = {}
    for _attempt in range(max_attempts):
        result = await get_result_func(conn, task_id, *args, **kwargs)
        if result["status"] in ["COMPLETED", "FAILED"]:
            return result
        await asyncio.sleep(poll_interval)

    logger.warning(f"Task {task_id} did not complete after {max_attempts} attempts. Current status: {result['status']}")
    return result


async def disconnect_all_clients(central_conn: Any, device_type: str, serial_number: str) -> dict[str, Any]:
    """Disconnect all clients from the specified device (GATEWAY only).

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('gateways').
        serial_number: Serial number of the device.

    Returns:
        Response envelope from the API (``{"code", "msg", "headers"}``).

    Raises:
        Exception: If initiating the disconnect fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("disconnect_all_clients"),
    )

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/disconnectClientAll", "troubleshooting"),
    )
    if resp["code"] != 202:
        raise Exception(f"Failed to initiate disconnect for all clients: {resp['code']} - {resp['msg']}")
    logger.info(f"Disconnect all clients initiated successfully for {device_type} {serial_number}.")
    return resp


async def disconnect_all_users(central_conn: Any, device_type: str, serial_number: str) -> dict[str, Any]:
    """Disconnect all users from the specified device (AP only).

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aps').
        serial_number: Serial number of the device.

    Returns:
        Response envelope from the API (``{"code", "msg", "headers"}``).

    Raises:
        Exception: If initiating the disconnect fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("disconnect_all_users"),
    )

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/disconnectUserAll", "troubleshooting"),
    )
    if resp["code"] != 202:
        raise Exception(f"Failed to initiate disconnect for all users: {resp['code']} - {resp['msg']}")
    logger.info(f"Disconnect all users initiated successfully for {device_type} {serial_number}.")
    return resp


async def disconnect_all_users_ssid(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    network: str,
) -> dict[str, Any]:
    """Disconnect all users from the specified device on a given network/SSID (AP only).

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aps').
        serial_number: Serial number of the device.
        network: SSID of the network to disconnect users from.

    Returns:
        Response envelope from the API (``{"code", "msg", "headers"}``).

    Raises:
        ParameterError: If network parameter is invalid.
        Exception: If initiating the disconnect fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("disconnect_all_users_ssid"),
    )

    api_data = {}
    if not isinstance(network, str):
        raise ParameterError("SSID must be a valid string.")
    api_data["networkName"] = network

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/disconnectUserByNetwork", "troubleshooting"),
        api_data=api_data,
    )
    if resp["code"] != 202:
        raise Exception(
            f"Failed to initiate disconnect for all users on SSID {network}: {resp['code']} - {resp['msg']}"
        )
    logger.info(f"Disconnect all users on SSID {network} initiated successfully for {device_type} {serial_number}.")
    return resp


async def disconnect_client_mac_addr(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    mac_address: str,
) -> dict[str, Any]:
    """Disconnect a client from the specified device by MAC address (GATEWAY only).

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('gateways').
        serial_number: Serial number of the device.
        mac_address: MAC address of the client to disconnect.

    Returns:
        Response envelope from the API (``{"code", "msg", "headers"}``).

    Raises:
        ParameterError: If MAC address parameter is invalid.
        Exception: If initiating the disconnect fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("disconnect_client_mac_addr"),
    )

    api_data = {}

    if not isinstance(mac_address, str):
        raise ParameterError("MAC address must be a valid string.")
    api_data["clientMacAddress"] = mac_address

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/disconnectClientByMacAddress", "troubleshooting"),
        api_data=api_data,
    )
    if resp["code"] != 202:
        raise Exception(f"Failed to initiate disconnect for mac {mac_address}: {resp['code']} - {resp['msg']}")
    logger.info(f"Disconnect client {mac_address} initiated successfully for {device_type} {serial_number}.")
    return resp


async def disconnect_user_mac_addr(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    mac_address: str,
) -> dict[str, Any]:
    """Disconnect a user from the specified device by MAC address (AP only).

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aps').
        serial_number: Serial number of the device.
        mac_address: MAC address of the user to disconnect.

    Returns:
        Response envelope from the API (``{"code", "msg", "headers"}``).

    Raises:
        ParameterError: If MAC address parameter is invalid.
        Exception: If initiating the disconnect fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("disconnect_user_mac_addr"),
    )

    api_data = {}

    if not isinstance(mac_address, str):
        raise ParameterError("MAC address must be a valid string.")
    api_data["userMacAddress"] = mac_address

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/disconnectUserByMacAddress", "troubleshooting"),
        api_data=api_data,
    )
    if resp["code"] != 202:
        raise Exception(f"Failed to initiate disconnect for mac {mac_address}: {resp['code']} - {resp['msg']}")
    logger.info(f"Disconnect user {mac_address} initiated successfully for {device_type} {serial_number}.")
    return resp


async def port_bounce_test(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    ports: list[str],
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a port bounce test on the specified device and poll for the result.

    Supported device types: AOS-S, CX, and GATEWAY. Port bounce disables and
    re-enables the port(s).

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s', 'cx', or 'gateways').
        serial_number: Serial number of the device.
        ports: List of the ports to test.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If there is an error initiating the port bounce test.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("port_bounce_test"),
    )

    try:
        response = await initiate_port_bounce_test(
            central_conn=central_conn,
            ports=ports,
            device_type=device_type,
            serial_number=serial_number,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_port_bounce_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating port bounce test for {device_type} {serial_number} on {ports}: {str(e)}")
        raise


async def initiate_port_bounce_test(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    ports: list[str],
) -> dict[str, Any]:
    """Initiate a port bounce test on the specified device.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s', 'cx', or 'gateways').
        serial_number: Serial number of the device.
        ports: List of the ports to test.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If the ports parameter is invalid.
        Exception: If initiating the port bounce test fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("port_bounce_test"),
    )

    if not ports or not isinstance(ports, list):
        raise ParameterError("Ports must be a non-empty list.")

    api_data = {"ports": ports}

    api_path = _generate_url(f"{device_type}/{serial_number}/portBounce", "troubleshooting")
    resp = await central_conn.command(api_method="POST", api_path=api_path, api_data=api_data)

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate port test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"Port bounce test initiated successfully for {device_type} {serial_number} on {ports}. Task ID: {task_id}"
    )
    return response


async def get_port_bounce_test_result(
    central_conn: Any,
    task_id: str,
    device_type: str,
    serial_number: str,
) -> dict[str, Any]:
    """Retrieve the results of a port bounce test on the specified device.

    Args:
        central_conn: CentralClient connection object.
        task_id: Task ID to poll for.
        device_type: Type of the device ('aos-s', 'cx', or 'gateways').
        serial_number: Serial number of the device.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If retrieving the port bounce test result fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("port_bounce_test"),
    )

    resp = await central_conn.command(
        api_method="GET",
        api_path=_generate_url(
            f"{device_type}/{serial_number}/portBounce/async-operations/{task_id}",
            "troubleshooting",
        ),
    )
    if resp["code"] != 200:
        raise Exception(f"Failed to get port bounce test result: {resp['code']} - {resp['msg']}")

    if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
        logger.info(
            f"Port bounce test for {device_type} {serial_number} with task ID {task_id} is not yet completed. "
            f"Current status: {resp['msg'].get('status')}"
        )
    else:
        logger.info(
            f"Port bounce test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
        )
    return resp["msg"]


async def poe_bounce_test(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    ports: list[str],
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a PoE bounce test on the specified device and poll for the result.

    Supported device types: AOS-S, CX, and GATEWAY.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s', 'cx', or 'gateways').
        serial_number: Serial number of the device.
        ports: List of the ports to test.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If there is an error initiating the PoE bounce test.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("poe_bounce_test"),
    )
    try:
        response = await initiate_poe_bounce_test(
            central_conn=central_conn,
            ports=ports,
            device_type=device_type,
            serial_number=serial_number,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_poe_bounce_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating PoE bounce test for {device_type} {serial_number} on {ports}: {str(e)}")
        raise


async def initiate_poe_bounce_test(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    ports: list[str],
) -> dict[str, Any]:
    """Initiate a PoE bounce test on the specified device.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s', 'cx', or 'gateways').
        serial_number: Serial number of the device.
        ports: List of the ports to test.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If the ports parameter is invalid.
        Exception: If there is an error initiating the PoE bounce test.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("poe_bounce_test"),
    )

    if not ports or not isinstance(ports, list):
        raise ParameterError("Ports must be a non-empty list.")

    api_data = {"ports": ports}

    api_path = _generate_url(f"{device_type}/{serial_number}/poeBounce", "troubleshooting")
    resp = await central_conn.command(api_method="POST", api_path=api_path, api_data=api_data)

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate PoE test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"PoE bounce test initiated successfully for {device_type} {serial_number} on {ports}. Task ID: {task_id}"
    )
    return response


async def get_poe_bounce_test_result(
    central_conn: Any,
    task_id: str,
    device_type: str,
    serial_number: str,
) -> dict[str, Any]:
    """Retrieve the results of a PoE bounce test on the specified device.

    Args:
        central_conn: CentralClient connection object.
        task_id: Task ID to poll for.
        device_type: Type of the device ('aos-s', 'cx', or 'gateways').
        serial_number: Serial number of the device.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If retrieving the PoE bounce test result fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("poe_bounce_test"),
    )

    resp = await central_conn.command(
        api_method="GET",
        api_path=_generate_url(
            f"{device_type}/{serial_number}/poeBounce/async-operations/{task_id}",
            "troubleshooting",
        ),
    )
    if resp["code"] != 200:
        raise Exception(f"Failed to get PoE bounce test result: {resp['code']} - {resp['msg']}")

    if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
        logger.info(
            f"PoE bounce test for {device_type} {serial_number} with task ID {task_id} is not yet completed. "
            f"Current status: {resp['msg'].get('status')}"
        )
    else:
        logger.info(
            f"PoE bounce test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
        )
    return resp["msg"]


# --- Ping tests (port of troubleshooting.Troubleshooting ping subset) -------------


async def ping_aps_test(
    central_conn: Any,
    serial_number: str,
    destination: str,
    packet_size: int | None = None,
    count: int | None = None,
    source_interface: str | None = None,
    source_vlan: int | None = None,
    source_role: str | None = None,
    include_raw_output: bool | None = None,
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a ping test on the specified AP device and poll for the test result.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the device.
        destination: Destination IP or hostname for the ping test.
        packet_size: Packet size in bytes (10-2000).
        count: Number of ping packets to send.
        source_interface: Port to use as source for ping.
        source_vlan: VLAN ID to use as source for ping.
        source_role: Role to use for ping.
        include_raw_output: Whether to include raw output in the response.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If there is an error initiating the ping test.
    """
    device_type = "aps"

    _validate_required_device_params(central_conn, device_type, serial_number)

    try:
        response = await initiate_ping_aps_test(
            central_conn=central_conn,
            destination=destination,
            serial_number=serial_number,
            packet_size=packet_size,
            count=count,
            source_interface=source_interface,
            source_vlan=source_vlan,
            source_role=source_role,
            include_raw_output=include_raw_output,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_ping_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}")
        raise


async def ping_cx_test(
    central_conn: Any,
    serial_number: str,
    destination: str,
    use_ipv6: bool | None = None,
    packet_size: int | None = None,
    count: int | None = None,
    use_management_interface: bool | None = None,
    vrf_name: str | None = None,
    include_raw_output: bool | None = None,
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a ping test on the specified CX device and poll for the test result.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the device.
        destination: Destination IP or hostname for the ping test.
        use_ipv6: Whether to use IPv6.
        packet_size: Packet size in bytes (10-2000).
        count: Number of ping packets to send.
        use_management_interface: Whether to use the management interface.
        vrf_name: Name of the VRF to use for the ping test.
        include_raw_output: Whether to include raw output in the response.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If there is an error initiating the ping test.
    """
    device_type = "cx"

    _validate_required_device_params(central_conn, device_type, serial_number)

    try:
        response = await initiate_ping_cx_test(
            central_conn=central_conn,
            destination=destination,
            serial_number=serial_number,
            use_ipv6=use_ipv6,
            packet_size=packet_size,
            count=count,
            use_management_interface=use_management_interface,
            vrf_name=vrf_name,
            include_raw_output=include_raw_output,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_ping_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}")
        raise


async def ping_gateways_test(
    central_conn: Any,
    serial_number: str,
    destination: str,
    packet_size: int | None = None,
    count: int | None = None,
    use_ipv6: bool | None = None,
    ttl: int | None = None,
    dscp: int | None = None,
    dont_fragment: bool | None = None,
    source_interface: str | None = None,
    source_vlan: int | None = None,
    include_raw_output: bool | None = None,
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a ping test on the specified Gateway device and poll for the test result.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the device.
        destination: Destination IP or hostname for the ping test.
        packet_size: Packet size in bytes (10-2000).
        count: Number of ping packets to send.
        use_ipv6: Whether to use IPv6.
        ttl: Time To Live for IP datagram (1-255).
        dscp: DSCP packet header value between 0 and 63 (0-63).
        dont_fragment: Whether to fragment or not.
        source_interface: Port to use as source for ping.
        source_vlan: VLAN ID to use as source for ping.
        include_raw_output: Whether to include raw output in the response.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If there is an error initiating the ping test.
    """
    device_type = "gateways"

    _validate_required_device_params(central_conn, device_type, serial_number)

    try:
        response = await initiate_ping_gateways_test(
            central_conn=central_conn,
            destination=destination,
            serial_number=serial_number,
            packet_size=packet_size,
            count=count,
            use_ipv6=use_ipv6,
            ttl=ttl,
            dscp=dscp,
            dont_fragment=dont_fragment,
            source_interface=source_interface,
            source_vlan=source_vlan,
            include_raw_output=include_raw_output,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_ping_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}")
        raise


async def initiate_ping_aps_test(
    central_conn: Any,
    destination: str,
    serial_number: str,
    packet_size: int | None = None,
    count: int | None = None,
    source_interface: str | None = None,
    source_vlan: int | None = None,
    source_role: str | None = None,
    include_raw_output: bool | None = None,
) -> dict[str, Any]:
    """Initiate a ping test on the specified AP device.

    Calls ``POST network-troubleshooting/v1alpha1/aps/{serial_number}/ping``.

    Args:
        central_conn: CentralClient connection object.
        destination: Destination IP or hostname for the ping test.
        serial_number: Serial number of the device.
        packet_size: Size of the ping packets.
        count: Number of ping packets to send.
        source_interface: Port to use as source for ping.
        source_vlan: VLAN ID to use as source for ping.
        source_role: Role to use for ping.
        include_raw_output: Whether to include raw output in the response.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If any parameter is invalid.
        Exception: If there is an error initiating the ping test.
    """
    device_type = "aps"

    _validate_required_device_params(central_conn, device_type, serial_number)

    if destination and isinstance(destination, str):
        api_data: dict[str, Any] = {"destination": destination}
    else:
        raise ParameterError("Destination must be a valid IP address or hostname.")

    if packet_size and isinstance(packet_size, int) and 10 <= packet_size <= 2000:
        api_data["packetSize"] = packet_size
    elif packet_size:
        raise ParameterError("packet_size must be an integer value 10-2000.")

    if count and isinstance(count, int) and 1 <= count <= 100:
        api_data["count"] = count
    elif count:
        raise ParameterError("count must be an integer value between 1-100.")

    if source_interface and isinstance(source_interface, str):
        api_data["interfacePort"] = source_interface
    elif source_interface:
        raise ParameterError("source_interface must be a string value.")

    if source_vlan and isinstance(source_vlan, int) and 1 <= source_vlan <= 4094:
        api_data["vlan"] = source_vlan
    elif source_vlan:
        raise ParameterError("source_vlan must be an integer value 1-4094.")

    if source_role and isinstance(source_role, str):
        api_data["role"] = source_role
    elif source_role:
        raise ParameterError("source_role must be a string value.")

    if include_raw_output and isinstance(include_raw_output, bool):
        api_data["includeRawOutput"] = include_raw_output
    elif include_raw_output:
        raise ParameterError("include_raw_output must be a boolean value.")

    api_path = _generate_url(f"{device_type}/{serial_number}/ping", "troubleshooting")
    resp = await central_conn.command(api_method="POST", api_path=api_path, api_data=api_data)

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate ping test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
    )
    return response


async def initiate_ping_cx_test(
    central_conn: Any,
    destination: str,
    serial_number: str,
    use_ipv6: bool | None = None,
    packet_size: int | None = None,
    count: int | None = None,
    use_management_interface: bool | None = None,
    vrf_name: str | None = None,
    include_raw_output: bool | None = None,
) -> dict[str, Any]:
    """Initiate a ping test on the specified CX device.

    Calls ``POST network-troubleshooting/v1alpha1/cx/{serial_number}/ping``.

    Args:
        central_conn: CentralClient connection object.
        destination: Destination IP or hostname for the ping test.
        serial_number: Serial number of the device.
        use_ipv6: Whether to use IPv6.
        packet_size: Size of the ping packets.
        count: Number of ping packets to send.
        use_management_interface: Whether to use the management interface.
        vrf_name: Name of the VRF to use for the ping test.
        include_raw_output: Whether to include raw output in the response.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If any parameter is invalid.
        Exception: If there is an error initiating the ping test.
    """
    device_type = "cx"

    _validate_required_device_params(central_conn, device_type, serial_number)

    if destination and isinstance(destination, str):
        api_data: dict[str, Any] = {"destination": destination}
    else:
        raise ParameterError("Destination must be a valid IP address or hostname.")

    if use_ipv6 is not None and isinstance(use_ipv6, bool):
        api_data["useIpv6"] = use_ipv6
    elif use_ipv6 is not None:
        raise ParameterError("use_ipv6 must be a boolean value.")

    if packet_size and isinstance(packet_size, int):
        api_data["packetSize"] = packet_size
    elif packet_size:
        raise ParameterError("packet_size must be an integer value.")

    if count and isinstance(count, int) and 1 <= count <= 100:
        api_data["count"] = count
    elif count:
        raise ParameterError("count must be an integer value between 1-100.")

    if use_management_interface is not None and isinstance(use_management_interface, bool):
        api_data["useManagementInterface"] = use_management_interface
    elif use_management_interface is not None:
        raise ParameterError("use_management_interface must be a boolean value.")

    if vrf_name and isinstance(vrf_name, str):
        api_data["vrfName"] = vrf_name
    elif vrf_name:
        raise ParameterError("vrf_name must be a string value.")

    if include_raw_output and isinstance(include_raw_output, bool):
        api_data["includeRawOutput"] = include_raw_output
    elif include_raw_output:
        raise ParameterError("include_raw_output must be a boolean value.")

    api_path = _generate_url(f"{device_type}/{serial_number}/ping", "troubleshooting")
    resp = await central_conn.command(api_method="POST", api_path=api_path, api_data=api_data)

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate ping test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
    )
    return response


async def initiate_ping_gateways_test(
    central_conn: Any,
    destination: str,
    serial_number: str,
    packet_size: int | None = None,
    count: int | None = None,
    use_ipv6: bool | None = None,
    ttl: int | None = None,
    dscp: int | None = None,
    dont_fragment: bool | None = None,
    source_interface: str | None = None,
    source_vlan: int | None = None,
    include_raw_output: bool | None = None,
) -> dict[str, Any]:
    """Initiate a ping test on the specified Gateway device.

    Calls ``POST network-troubleshooting/v1alpha1/gateways/{serial_number}/ping``.

    Args:
        central_conn: CentralClient connection object.
        destination: Destination IP or hostname for the ping test.
        serial_number: Serial number of the device.
        packet_size: Size of the ping packets.
        count: Number of ping packets to send.
        use_ipv6: Whether to use IPv6.
        ttl: Time To Live for IP datagram (1-255).
        dscp: DSCP packet header value between 0 and 63 (0-63).
        dont_fragment: Whether to fragment or not.
        source_interface: Port to use as source for ping.
        source_vlan: VLAN ID to use as source for ping.
        include_raw_output: Whether to include raw output in the response.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If any parameter is invalid.
        Exception: If there is an error initiating the ping test.
    """
    device_type = "gateways"

    _validate_required_device_params(central_conn, device_type, serial_number)

    if destination and isinstance(destination, str):
        api_data: dict[str, Any] = {"destination": destination}
    else:
        raise ParameterError("Destination must be a valid IP address or hostname.")

    if packet_size and isinstance(packet_size, int) and 10 <= packet_size <= 2000:
        api_data["packetSize"] = packet_size
    elif packet_size:
        raise ParameterError("packet_size must be an integer value 10-2000.")

    if count and isinstance(count, int) and 1 <= count <= 100:
        api_data["count"] = count
    elif count:
        raise ParameterError("count must be an integer value between 1-100.")

    if ttl and isinstance(ttl, int) and 1 <= ttl <= 255:
        api_data["ttl"] = ttl
    elif ttl:
        raise ParameterError("ttl must be an integer value between 1-255.")

    if dscp and isinstance(dscp, int) and 0 <= dscp <= 63:
        api_data["dscp"] = dscp
    elif dscp:
        raise ParameterError("dscp must be an integer value between 0-63.")

    if source_interface and isinstance(source_interface, str):
        api_data["sourceInterface"] = source_interface
    elif source_interface:
        raise ParameterError("source_interface must be a string value.")

    if source_vlan and isinstance(source_vlan, int) and 1 <= source_vlan <= 4094:
        api_data["vlan"] = source_vlan
    elif source_vlan:
        raise ParameterError("source_vlan must be an integer value 1-4094.")

    if use_ipv6 is not None and isinstance(use_ipv6, bool):
        api_data["useIpv6"] = use_ipv6
    elif use_ipv6 is not None:
        raise ParameterError("use_ipv6 must be a boolean value.")

    if dont_fragment and isinstance(dont_fragment, bool):
        api_data["dontFragmentFlag"] = dont_fragment
    elif dont_fragment:
        raise ParameterError("dont_fragment must be a boolean value.")

    if include_raw_output and isinstance(include_raw_output, bool):
        api_data["includeRawOutput"] = include_raw_output
    elif include_raw_output:
        raise ParameterError("include_raw_output must be a boolean value.")

    api_path = _generate_url(f"{device_type}/{serial_number}/ping", "troubleshooting")
    resp = await central_conn.command(api_method="POST", api_path=api_path, api_data=api_data)

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate ping test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
    )
    return response


async def get_ping_test_result(
    central_conn: Any,
    task_id: str,
    device_type: str,
    serial_number: str,
) -> dict[str, Any]:
    """Retrieve the results of a ping test on the specified device.

    Supported device types: AOS-S, AP, CX, and GATEWAY.

    Args:
        central_conn: CentralClient connection object.
        task_id: Task ID to poll for.
        device_type: Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
        serial_number: Serial number of the device.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If retrieving the ping test result fails.
    """
    device_type = _validate_required_device_params(central_conn, device_type, serial_number)
    resp = await central_conn.command(
        api_method="GET",
        api_path=_generate_url(
            f"{device_type}/{serial_number}/ping/async-operations/{task_id}",
            "troubleshooting",
        ),
    )
    if resp["code"] != 200:
        raise Exception(f"Failed to get ping test result: {resp['code']} - {resp['msg']}")

    if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
        logger.info(
            f"Ping test for {device_type} {serial_number} with task ID {task_id} is not yet completed. "
            f"Current status: {resp['msg'].get('status')}"
        )
    else:
        logger.info(f"Ping test for {device_type} {serial_number} with task ID {task_id} has successfully completed.")
    return resp["msg"]


# --- Traceroute tests (port of troubleshooting.Troubleshooting traceroute subset) --


async def traceroute_aps_test(
    central_conn: Any,
    serial_number: str,
    destination: str,
    source_interface: str | None = None,
    include_raw_output: bool | None = None,
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a traceroute test on the specified AP device and poll for the test result.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the device.
        destination: Destination IP or hostname for the traceroute test.
        source_interface: Port to use as source for the traceroute test.
        include_raw_output: Whether to include raw output in the response.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        Exception: If there is an error initiating the traceroute test.
    """
    device_type = "aps"

    _validate_required_device_params(central_conn, device_type, serial_number)

    try:
        response = await initiate_traceroute_aps_test(
            central_conn=central_conn,
            destination=destination,
            serial_number=serial_number,
            source_interface=source_interface,
            include_raw_output=include_raw_output,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_traceroute_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating traceroute test for {device_type} {serial_number} to {destination}: {str(e)}")
        raise


async def traceroute_cx_test(
    central_conn: Any,
    serial_number: str,
    destination: str,
    use_ipv6: bool | None = None,
    use_management_interface: bool | None = None,
    vrf_name: str | None = None,
    include_raw_output: bool | None = None,
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a traceroute test on the specified CX device and poll for the test result.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the device.
        destination: Destination IP or hostname for the traceroute test.
        use_ipv6: Whether to use IPv6.
        use_management_interface: Whether to use the management interface.
        vrf_name: Name of the VRF to use for the traceroute test.
        include_raw_output: Whether to include raw output in the response.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        Exception: If there is an error initiating the traceroute test.
    """
    device_type = "cx"

    _validate_required_device_params(central_conn, device_type, serial_number)

    try:
        response = await initiate_traceroute_cx_test(
            central_conn=central_conn,
            destination=destination,
            serial_number=serial_number,
            use_ipv6=use_ipv6,
            use_management_interface=use_management_interface,
            vrf_name=vrf_name,
            include_raw_output=include_raw_output,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_traceroute_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating traceroute test for {device_type} {serial_number} to {destination}: {str(e)}")
        raise


async def traceroute_gateways_test(
    central_conn: Any,
    serial_number: str,
    destination: str,
    source_vlan_ip: str | None = None,
    include_raw_output: bool | None = None,
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a traceroute test on the specified Gateway device and poll for the test result.

    Args:
        central_conn: CentralClient connection object.
        serial_number: Serial number of the device.
        destination: Destination IP or hostname for the traceroute test.
        source_vlan_ip: VLAN IP address to use as source for the traceroute test.
        include_raw_output: Whether to include raw output in the response.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        Exception: If there is an error initiating the traceroute test.
    """
    device_type = "gateways"

    _validate_required_device_params(central_conn, device_type, serial_number)

    try:
        response = await initiate_traceroute_gateways_test(
            central_conn=central_conn,
            destination=destination,
            serial_number=serial_number,
            source_vlan_ip=source_vlan_ip,
            include_raw_output=include_raw_output,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_traceroute_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating traceroute test for {device_type} {serial_number} to {destination}: {str(e)}")
        raise


async def initiate_traceroute_aps_test(
    central_conn: Any,
    destination: str,
    serial_number: str,
    source_interface: str | None = None,
    include_raw_output: bool | None = None,
) -> dict[str, Any]:
    """Initiate a traceroute test on the specified AP device.

    Calls ``POST network-troubleshooting/v1alpha1/aps/{serial_number}/traceroute``.

    Args:
        central_conn: CentralClient connection object.
        destination: Destination IP or hostname for the traceroute test.
        serial_number: Serial number of the device.
        source_interface: Source interface to use for the traceroute test.
        include_raw_output: Whether to include raw output in the response.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If any parameter is invalid.
        Exception: If there is an error initiating the traceroute test.
    """
    device_type = "aps"

    _validate_required_device_params(central_conn, device_type, serial_number)

    if destination and isinstance(destination, str):
        api_data: dict[str, Any] = {"destination": destination}
    else:
        raise ParameterError("Destination must be a valid IP address or hostname.")

    if source_interface and isinstance(source_interface, str):
        api_data["sourceInterface"] = source_interface
    elif source_interface:
        raise ParameterError("source_interface must be a string value.")

    if include_raw_output and isinstance(include_raw_output, bool):
        api_data["includeRawOutput"] = include_raw_output
    elif include_raw_output:
        raise ParameterError("include_raw_output must be a boolean value.")

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/traceroute", "troubleshooting"),
        api_data=api_data,
    )

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"Traceroute test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
    )
    return response


async def initiate_traceroute_cx_test(
    central_conn: Any,
    destination: str,
    serial_number: str,
    use_ipv6: bool | None = None,
    use_management_interface: bool | None = None,
    vrf_name: str | None = None,
    include_raw_output: bool | None = None,
) -> dict[str, Any]:
    """Initiate a traceroute test on the specified CX device.

    Calls ``POST network-troubleshooting/v1alpha1/cx/{serial_number}/traceroute``.

    Args:
        central_conn: CentralClient connection object.
        destination: Destination IP or hostname for the traceroute test.
        serial_number: Serial number of the device.
        use_ipv6: Whether to use IPv6.
        use_management_interface: Whether to use the management interface.
        vrf_name: Name of the VRF to use for the traceroute test.
        include_raw_output: Whether to include raw output in the response.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If any parameter is invalid.
        Exception: If there is an error initiating the traceroute test.
    """
    device_type = "cx"
    _validate_required_device_params(central_conn, device_type, serial_number)

    if destination and isinstance(destination, str):
        api_data: dict[str, Any] = {"destination": destination}
    else:
        raise ParameterError("Destination must be a valid IP address or hostname.")

    if use_ipv6 is not None and isinstance(use_ipv6, bool):
        api_data["useIpv6"] = use_ipv6
    elif use_ipv6 is not None:
        raise ParameterError("use_ipv6 must be a boolean value.")

    if use_management_interface is not None and isinstance(use_management_interface, bool):
        api_data["useManagementInterface"] = use_management_interface
    elif use_management_interface is not None:
        raise ParameterError("use_management_interface must be a boolean value.")

    if vrf_name and isinstance(vrf_name, str):
        api_data["vrfName"] = vrf_name
    elif vrf_name:
        raise ParameterError("vrf_name must be a string value.")

    if include_raw_output and isinstance(include_raw_output, bool):
        api_data["includeRawOutput"] = include_raw_output
    elif include_raw_output:
        raise ParameterError("include_raw_output must be a boolean value.")

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/traceroute", "troubleshooting"),
        api_data=api_data,
    )

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"Traceroute test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
    )
    return response


async def initiate_traceroute_gateways_test(
    central_conn: Any,
    destination: str,
    serial_number: str,
    source_vlan_ip: str | None = None,
    include_raw_output: bool | None = None,
) -> dict[str, Any]:
    """Initiate a traceroute test on the specified Gateway device.

    Calls ``POST network-troubleshooting/v1alpha1/gateways/{serial_number}/traceroute``.

    Args:
        central_conn: CentralClient connection object.
        destination: Destination IP or hostname for the traceroute test.
        serial_number: Serial number of the device.
        source_vlan_ip: VLAN IP address to use as source for the traceroute test.
        include_raw_output: Whether to include raw output in the response.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If any parameter is invalid.
        Exception: If there is an error initiating the traceroute test.
    """
    device_type = "gateways"

    _validate_required_device_params(central_conn, device_type, serial_number)

    if destination and isinstance(destination, str):
        api_data: dict[str, Any] = {"destination": destination}
    else:
        raise ParameterError("Destination must be a valid IP address or hostname.")

    if source_vlan_ip and isinstance(source_vlan_ip, str):
        api_data["vlanIp"] = source_vlan_ip
    elif source_vlan_ip:
        raise ParameterError("source_vlan_ip must be a string value.")

    if include_raw_output and isinstance(include_raw_output, bool):
        api_data["includeRawOutput"] = include_raw_output
    elif include_raw_output:
        raise ParameterError("include_raw_output must be a boolean value.")

    resp = await central_conn.command(
        api_method="POST",
        api_path=_generate_url(f"{device_type}/{serial_number}/traceroute", "troubleshooting"),
        api_data=api_data,
    )

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(
        f"Traceroute test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
    )
    return response


async def get_traceroute_test_result(
    central_conn: Any,
    task_id: str,
    device_type: str,
    serial_number: str,
) -> dict[str, Any]:
    """Retrieve the result of a traceroute test on the specified device.

    Supported device types: AOS-S, AP, CX, and GATEWAY.

    Args:
        central_conn: CentralClient connection object.
        task_id: Task ID to poll for.
        device_type: Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
        serial_number: Serial number of the device.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If there is an error retrieving the traceroute test result.
    """
    device_type = _validate_required_device_params(central_conn, device_type, serial_number)
    resp = await central_conn.command(
        api_method="GET",
        api_path=_generate_url(
            f"{device_type}/{serial_number}/traceroute/async-operations/{task_id}",
            "troubleshooting",
        ),
    )
    if resp["code"] != 200:
        raise Exception(f"Failed to get traceroute test result: {resp['code']} - {resp['msg']}")

    if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
        logger.info(
            f"Traceroute test for {device_type} {serial_number} with task ID {task_id} is not yet completed. "
            f"Current status: {resp['msg'].get('status')}"
        )
    else:
        logger.info(
            f"Traceroute test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
        )
    return resp["msg"]


# --- Cable test (port of troubleshooting.Troubleshooting cable subset) ------------


async def cable_test(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    ports: list[str],
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Initiate a cable test on the specified device and poll for the test result.

    Supported device types: AOS-S and CX.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s' or 'cx').
        serial_number: Serial number of the device.
        ports: List of the ports to test.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If initiating the cable test fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
    )

    try:
        response = await initiate_cable_test(
            central_conn=central_conn,
            ports=ports,
            device_type=device_type,
            serial_number=serial_number,
        )
        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_cable_test_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error initiating cable test for {device_type} {serial_number} on {ports}: {str(e)}")
        raise


async def initiate_cable_test(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    ports: list[str],
) -> dict[str, Any]:
    """Initiate a cable test on the specified device.

    Calls ``POST network-troubleshooting/v1alpha1/{device_type}/{serial_number}/cableTest``.
    Supported device types: AOS-S and CX.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s' or 'cx').
        serial_number: Serial number of the device.
        ports: List of the ports to test.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If the ports parameter is invalid.
        Exception: If initiating the cable test fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
    )

    if not ports or not isinstance(ports, list):
        raise ParameterError("Ports must be a non-empty list.")

    api_data = {"ports": ports}

    api_path = _generate_url(f"{device_type}/{serial_number}/cableTest", "troubleshooting")
    resp = await central_conn.command(api_method="POST", api_path=api_path, api_data=api_data)

    if resp["code"] != 202:
        raise Exception(f"Failed to initiate cable test: {resp['code']} - {resp['msg']}")

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(f"Cable test initiated successfully for {device_type} {serial_number} on {ports}. Task ID: {task_id}")
    return response


async def get_cable_test_result(
    central_conn: Any,
    task_id: str,
    device_type: str,
    serial_number: str,
) -> dict[str, Any]:
    """Retrieve the results of a cable test on the specified device.

    Supported device types: AOS-S and CX.

    Args:
        central_conn: CentralClient connection object.
        task_id: Task ID to poll for.
        device_type: Type of the device ('aos-s' or 'cx').
        serial_number: Serial number of the device.

    Returns:
        Response from the test results API.

    Raises:
        Exception: If retrieving the cable test result fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
    )
    resp = await central_conn.command(
        api_method="GET",
        api_path=_generate_url(
            f"{device_type}/{serial_number}/cableTest/async-operations/{task_id}",
            "troubleshooting",
        ),
    )
    if resp["code"] != 200:
        raise Exception(f"Failed to get cable test result: {resp['code']} - {resp['msg']}")

    if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
        logger.info(
            f"Cable test for {device_type} {serial_number} with task ID {task_id} is not yet completed. "
            f"Current status: {resp['msg'].get('status')}"
        )
    else:
        logger.info(f"Cable test for {device_type} {serial_number} with task ID {task_id} has successfully completed.")
    return resp["msg"]


# --- Show commands (port of troubleshooting.Troubleshooting show-command subset) ---


async def run_show_commands(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    commands: str | list[str],
    max_attempts: int = 5,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Run 'show' command(s) on a device and poll for the test result.

    Supported device types: AOS-S, AP, CX, and GATEWAY. All commands must
    start with 'show '.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
        serial_number: Serial number of the device.
        commands: Single show command as a string (e.g., "show version") or a
            list of show commands (e.g., ["show version", "show ip route"]).
            Max 20 commands. All commands must start with 'show '.
        max_attempts: Maximum number of polling attempts.
        poll_interval: Time to wait between polls in seconds.

    Returns:
        Response from the test results API containing command output and status.

    Raises:
        Exception: If initiating the show command fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=["aps", "gateways", "cx", "aos-s"],
    )

    try:
        response = await initiate_show_commands(
            central_conn=central_conn,
            device_type=device_type,
            serial_number=serial_number,
            commands=commands,
        )

        task_id = _get_task_id(response)

        return await _poll_task_completion(
            get_show_commands_result,
            task_id,
            central_conn,
            max_attempts=max_attempts,
            poll_interval=poll_interval,
            device_type=device_type,
            serial_number=serial_number,
        )
    except Exception as e:
        logger.error(f"Error running show command on {device_type} {serial_number}: {str(e)}")
        raise


async def initiate_show_commands(
    central_conn: Any,
    device_type: str,
    serial_number: str,
    commands: str | list[str],
) -> dict[str, Any]:
    """Initiate an asynchronous execution of 'show' command(s) on a device.

    Calls ``POST network-troubleshooting/v1alpha1/{device_type}/{serial_number}/showCommands``.
    Supported device types: AOS-S, AP, CX, and GATEWAY. All commands must
    start with 'show '.

    Args:
        central_conn: CentralClient connection object.
        device_type: Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
        serial_number: Serial number of the device.
        commands: Single show command as a string or list of show commands.
            Max 20 commands. All commands must start with 'show '.

    Returns:
        Response from the API containing task ID and other details.

    Raises:
        ParameterError: If commands is not a valid string or list, the list is
            empty or exceeds 20 items, or any command doesn't start with 'show '.
        Exception: If initiating the show command fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=["aps", "gateways", "cx", "aos-s"],
    )

    # Normalize commands to a list
    if isinstance(commands, str):
        # Single command provided as string
        if not commands or not commands.strip():
            raise ParameterError("commands must be a non-empty string")

        if not commands.strip().lower().startswith("show "):
            raise ParameterError("Command must start with 'show '. Example: 'show ap debug system-status'")

        commands_list = [commands]

    elif isinstance(commands, list):
        # List of commands provided
        if len(commands) == 0:
            raise ParameterError("commands list cannot be empty")

        if len(commands) > 20:
            raise ParameterError(f"commands list cannot exceed 20 items. Provided: {len(commands)}")

        # Validate each command in the list
        for idx, cmd in enumerate(commands):
            if not cmd or not isinstance(cmd, str) or not cmd.strip():
                raise ParameterError(f"Command at index {idx} must be a valid non-empty string")

            if not cmd.strip().lower().startswith("show "):
                raise ParameterError(f"Command at index {idx} must start with 'show '. Got: '{cmd}'")

        commands_list = commands

    else:
        raise ParameterError(
            "commands must be either a string (single command) or a list of strings (multiple commands)"
        )

    api_data = {"commands": commands_list}

    api_path = _generate_url(f"{device_type}/{serial_number}/showCommands", "troubleshooting")
    resp = await central_conn.command(api_method="POST", api_path=api_path, api_data=api_data)

    if resp["code"] != 202:
        raise Exception(
            f"Failed to initiate show command for {device_type} {serial_number}: {resp['code']} - {resp['msg']}"
        )

    response = resp["msg"]
    task_id = _get_task_id(response)
    logger.info(f"Show command initiated successfully for {device_type} {serial_number}. Task ID: {task_id}")
    return response


async def get_show_commands_result(
    central_conn: Any,
    task_id: str,
    device_type: str,
    serial_number: str,
) -> dict[str, Any]:
    """Retrieve the results of a show command execution on a device.

    Supported device types: AOS-S, AP, CX, and GATEWAY.

    Args:
        central_conn: CentralClient connection object.
        task_id: Task ID to poll for.
        device_type: Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
        serial_number: Serial number of the device.

    Returns:
        Response from the test results API containing command output and status.

    Raises:
        Exception: If retrieving the command result fails.
    """
    device_type = _validate_required_device_params(
        central_conn,
        device_type,
        serial_number,
        subset=["aps", "gateways", "cx", "aos-s"],
    )
    resp = await central_conn.command(
        api_method="GET",
        api_path=_generate_url(
            f"{device_type}/{serial_number}/showCommands/async-operations/{task_id}",
            "troubleshooting",
        ),
    )

    if resp["code"] != 200:
        raise Exception(f"Failed to get show command result: {resp['code']} - {resp['msg']}")

    if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
        logger.info(
            f"Show command for {device_type} {serial_number} with task ID {task_id} "
            f"is not yet completed. Current status: {resp['msg'].get('status')}"
        )
    else:
        logger.info(
            f"Show command for {device_type} {serial_number} with task ID {task_id} has successfully completed."
        )

    return resp["msg"]
