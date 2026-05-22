# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Phase 20 assignment primitives: rate limiter, lookup helpers, PATCH helpers.

Extracted into a sibling module of ``bulk_add.py`` to keep the parent file under
the 500-line project limit.  ``bulk_add.py`` imports these via::

    from ._bulk_assignment import _assign_for_row

NOTE: ``_poll_async_operation`` is imported LAZILY inside the PATCH helpers (not at
module scope) to prevent a circular import: ``bulk_add.py`` imports this module at
its top level, so a module-scope back-import would cause ``ImportError`` during
Python's module-initialization sequence.
"""

from __future__ import annotations

from typing import Any

from aiolimiter import AsyncLimiter

from ....utils.logging import logger
from ..client import GreenLakeHttpClient

# PATCH /devices/v2beta1/devices: 20 req/min (API documented 25/min — conservative
# margin). Shared for BOTH service and subscription PATCH calls because both hit
# the same endpoint and therefore the same server-side rate-limit pool. Independent
# of bulk_add._device_add_limiter (5/min POST device-add) — two separate rate pools.
_subscription_patch_limiter = AsyncLimiter(max_rate=20, time_period=60)


def _sanitize_reason(text: str | None) -> str:
    """Strip control characters and truncate API-derived error strings.

    Args:
        text: Raw API error string or None.

    Returns:
        ASCII printable (0x20-0x7E) only, NUL and control characters replaced
        with space; DEL (0x7F) and non-ASCII replaced with space; capped at
        200 chars.  Returns ``""`` for None.
    """
    if text is None:
        return ""
    return "".join(c if 0x20 <= ord(c) < 0x7F else " " for c in text)[:200]


def _escape_odata_string(value: str) -> str:
    """Escape single quotes in an OData eq string literal (double them).

    OData string literals use '' to represent a literal single quote.
    Without escaping, a crafted value can break out of the literal and
    inject arbitrary filter logic (OData injection).
    """
    return value.replace("'", "''")


async def _resolve_subscription_id(
    client: GreenLakeHttpClient,
    subscription_key: str,
    lookup_cache: dict[str, str | None],
) -> str | None:
    """Resolve subscription key (e.g. 'STIQQ4L04') to its resource UUID.

    Caches result per-key to avoid repeated GETs for the same key.

    Args:
        client: Authenticated GreenLake HTTP client.
        subscription_key: User-facing key string from the CSV column.
        lookup_cache: Per-run dict mapping key → UUID (None for misses).

    Returns:
        UUID string on success, ``None`` if not found or on any error.
    """
    if subscription_key in lookup_cache:
        return lookup_cache[subscription_key]

    params: dict[str, Any] = {"filter": f"key eq '{_escape_odata_string(subscription_key)}'", "limit": 1}
    try:
        result = await client.get("/subscriptions/v1/subscriptions", params=params)
    except Exception:
        lookup_cache[subscription_key] = None
        return None

    if not isinstance(result, dict):
        logger.warning("_resolve_subscription_id: unexpected API response type {}", type(result).__name__)
        lookup_cache[subscription_key] = None
        return None
    items = result.get("items", [])
    sub_id: str | None = items[0].get("id") if items else None
    lookup_cache[subscription_key] = sub_id
    return sub_id


async def _resolve_application_id(
    client: GreenLakeHttpClient,
    service_name: str,
    lookup_cache: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Resolve service name to (application_id, region) via the service catalog.

    Fetches ``GET /service-catalog/v1/service-managers`` once; caches the items
    list under ``lookup_cache["_catalog"]`` for subsequent calls.  Substring match
    is case-insensitive across ``name``, ``displayName``, and ``description`` fields.

    Args:
        client: Authenticated GreenLake HTTP client.
        service_name: Name from the CSV ``service`` column (e.g. 'Aruba Central').
        lookup_cache: Per-run dict; catalog stored under ``"_catalog"`` key.

    Returns:
        ``(application_id, region)`` on match; ``(None, None)`` if not found or
        on any error.  ``region`` may be ``None`` if absent from the catalog item.
    """
    catalog: list[dict] | None = lookup_cache.get("_catalog")
    if catalog is None:
        try:
            result = await client.get("/service-catalog/v1/service-managers")
        except Exception:
            lookup_cache["_catalog"] = []
            return (None, None)
        if not isinstance(result, dict):
            logger.warning("_resolve_application_id: unexpected catalog API response type {}", type(result).__name__)
            lookup_cache["_catalog"] = []
            return (None, None)
        catalog = result.get("items", [])
        lookup_cache["_catalog"] = catalog

    normalized = service_name.strip().lower()
    for item in catalog:
        names = [item.get("name", ""), item.get("displayName", ""), item.get("description", "")]
        if any(normalized in n.lower() for n in names if n):
            return (item.get("id"), item.get("region"))
    return (None, None)


async def _patch_assign_application(
    client: GreenLakeHttpClient,
    device_uuid: str,
    application_id: str,
    region: str | None,
) -> tuple[str, str | None]:
    """PATCH service/application assignment for a single device.

    Endpoint: ``PATCH /devices/v2beta1/devices?id={device_uuid}`` (per CONFIRMED A3).
    Body: ``{"application": {"id": application_id}}`` + ``"region"`` when not None
    (per CONFIRMED A2).  Content-Type must be ``application/merge-patch+json``.

    Args:
        client: Authenticated GreenLake HTTP client.
        device_uuid: Device UUID from Phase 19 async-operation result.
        application_id: Application UUID from the service catalog.
        region: Catalog region string or ``None``.

    Returns:
        ``("succeeded", None)`` on success; ``("failed", reason)`` otherwise.
        Never raises.
    """
    # Lazy import prevents circular: bulk_add imports this module at top level.
    from .bulk_add import _poll_async_operation  # noqa: PLC0415

    endpoint = f"/devices/v2beta1/devices?id={device_uuid}"
    body: dict[str, Any] = {"application": {"id": application_id}}
    if region is not None:
        body["region"] = region
    headers = {"Content-Type": "application/merge-patch+json"}

    try:
        response = await client.patch_raw(endpoint, data=body, additional_headers=headers)
    except Exception as exc:
        return ("failed", _sanitize_reason(f"PATCH application exception: {exc}"))

    if response.status_code != 202:
        return ("failed", _sanitize_reason(f"PATCH application {response.status_code}: {response.text[:200]}"))

    # ASSUMPTION: PATCH /devices/v2beta1/devices returns a Location header whose
    # final path segment is the async-operation UUID under /devices/v1/async-operations/.
    # If GreenLake ever changes this to /devices/v2beta1/async-operations/, polling
    # will silently 404 until timeout (120s per assignment). Verify from live API if
    # v2beta1 async-operations path changes.
    location = response.headers.get("location", "")
    async_op_id = location.rsplit("/", 1)[-1] if location else ""
    if not async_op_id:
        return ("failed", "PATCH application 202 but no Location header")

    poll_result = await _poll_async_operation(client, async_op_id)
    if poll_result is None:
        return ("failed", "application PATCH poll timeout after 120s")

    op_status = poll_result.get("status", "")
    if op_status == "SUCCEEDED":
        return ("succeeded", None)
    error_raw = poll_result.get("error")
    if isinstance(error_raw, dict):
        error_msg = error_raw.get("message", "unknown")
    else:
        error_msg = str(error_raw) if error_raw is not None else "unknown"
    return ("failed", _sanitize_reason(f"application PATCH {op_status}: {error_msg}"))


async def _patch_assign_subscription(
    client: GreenLakeHttpClient,
    device_uuid: str,
    subscription_id: str,
) -> tuple[str, str | None]:
    """PATCH subscription assignment for a single device.

    Endpoint: ``PATCH /devices/v2beta1/devices?id={device_uuid}`` (per CONFIRMED A3).
    Body: ``{"subscription": [{"id": subscription_id}]}``.  No ``"region"`` key —
    region is application-only.

    Args:
        client: Authenticated GreenLake HTTP client.
        device_uuid: Device UUID from Phase 19 async-operation result.
        subscription_id: Subscription resource UUID (resolved from subscription key).

    Returns:
        ``("succeeded", None)`` on success; ``("failed", reason)`` otherwise.
        Never raises.
    """
    # Lazy import — same circular-import reason as _patch_assign_application.
    from .bulk_add import _poll_async_operation  # noqa: PLC0415

    endpoint = f"/devices/v2beta1/devices?id={device_uuid}"
    body: dict[str, Any] = {"subscription": [{"id": subscription_id}]}
    headers = {"Content-Type": "application/merge-patch+json"}

    try:
        response = await client.patch_raw(endpoint, data=body, additional_headers=headers)
    except Exception as exc:
        return ("failed", _sanitize_reason(f"PATCH subscription exception: {exc}"))

    if response.status_code != 202:
        return ("failed", _sanitize_reason(f"PATCH subscription {response.status_code}: {response.text[:200]}"))

    # ASSUMPTION: PATCH /devices/v2beta1/devices returns a Location header whose
    # final path segment is the async-operation UUID under /devices/v1/async-operations/.
    # If GreenLake ever changes this to /devices/v2beta1/async-operations/, polling
    # will silently 404 until timeout (120s per assignment). Verify from live API if
    # v2beta1 async-operations path changes.
    location = response.headers.get("location", "")
    async_op_id = location.rsplit("/", 1)[-1] if location else ""
    if not async_op_id:
        return ("failed", "PATCH subscription 202 but no Location header")

    poll_result = await _poll_async_operation(client, async_op_id)
    if poll_result is None:
        return ("failed", "subscription PATCH poll timeout after 120s")

    op_status = poll_result.get("status", "")
    if op_status == "SUCCEEDED":
        return ("succeeded", None)
    # Extract error from result.failedDevices[].messages (PatchDeviceResponseV2 shape)
    # or fall back to top-level error field.
    error_msg = "unknown"
    batch_result = poll_result.get("result", {})
    if isinstance(batch_result, dict):
        failed_devices = batch_result.get("failedDevices", [])
        if failed_devices:
            msgs = failed_devices[0].get("messages", [])
            code = failed_devices[0].get("errorCode", "")
            error_msg = f"[{code}] {'; '.join(msgs)}" if msgs else code or "unknown"
    if error_msg == "unknown":
        error_raw = poll_result.get("error")
        error_msg = error_raw.get("message", "unknown") if isinstance(error_raw, dict) else str(error_raw or "unknown")
    return ("failed", _sanitize_reason(f"subscription PATCH {op_status}: {error_msg}"))


async def _assign_for_row(
    client: GreenLakeHttpClient,
    row: dict[str, Any],
    cache: dict[str, Any],
    sn: str,
    sub_cache: dict[str, str | None],
    app_cache: dict[str, Any],
) -> tuple[int, int, int, int]:
    """Run Phase 20 service + subscription assignment for one row.

    Mutates ``cache[sn]`` in-place with the four new Phase 20 fields.
    Returns ``(svc_attempted, svc_assigned, sub_attempted, sub_assigned)``
    per-row counters for the caller's batch aggregation.

    Args:
        client: Authenticated GreenLake HTTP client.
        row: CSV row dict containing optional ``service`` and ``subscriptionKey``.
        cache: Live run cache dict (mutated in place).
        sn: Serial number key for this row in ``cache``.
        sub_cache: Per-invocation subscription-key → UUID cache.
        app_cache: Per-invocation service-catalog cache.

    Returns:
        Four-int tuple: svc_attempted, svc_assigned, sub_attempted, sub_assigned.
    """
    if cache[sn]["status"] != "succeeded":
        cache[sn]["service_status"] = "not_applicable"
        cache[sn]["service_reason"] = None
        cache[sn]["subscription_status"] = "not_applicable"
        cache[sn]["subscription_reason"] = None
        return (0, 0, 0, 0)

    device_uuid: str | None = cache[sn].get("device_id")

    # GreenLake batch-add async responses (Shape B/C) do not include per-device
    # items, so device_id is None after a successful add. Resolve it via GET
    # before attempting any PATCH so service/subscription assignment can proceed.
    if device_uuid is None:
        try:
            params: dict[str, Any] = {
                "filter": f"serialNumber eq '{_escape_odata_string(sn)}'",
                "limit": 1,
            }
            lookup = await client.get("/devices/v1/devices", params=params)
            if isinstance(lookup, dict):
                _items = lookup.get("items", [])
                if _items:
                    device_uuid = _items[0].get("id")
                    cache[sn]["device_id"] = device_uuid
        except Exception:
            pass  # device_uuid stays None; assignment helpers will record the failure

    region: str | None = row.get("region")

    svc_attempted = 0
    svc_assigned = 0

    # CSV parser aliases "service" header → "serviceId" canonical key (ALIASES table)
    service_value = row.get("serviceId") or row.get("service")
    if not service_value:
        cache[sn]["service_status"] = "skipped"
        cache[sn]["service_reason"] = None
    elif not device_uuid:
        cache[sn]["service_status"] = "failed"
        cache[sn]["service_reason"] = "no device_uuid from async-operations"
    else:
        app_id, catalog_region = await _resolve_application_id(client, service_value, app_cache)
        if catalog_region is not None:
            region = catalog_region
        if app_id is None:
            cache[sn]["service_status"] = "failed"
            cache[sn]["service_reason"] = f"service not found in workspace: {service_value}"
        else:
            svc_attempted = 1
            async with _subscription_patch_limiter:
                svc_status, svc_reason = await _patch_assign_application(client, device_uuid, app_id, region)
            cache[sn]["service_status"] = svc_status
            cache[sn]["service_reason"] = svc_reason
            if svc_status == "succeeded":
                svc_assigned = 1

    sub_attempted = 0
    sub_assigned = 0

    sub_key = row.get("subscriptionKey")
    if not sub_key:
        cache[sn]["subscription_status"] = "skipped"
        cache[sn]["subscription_reason"] = None
    elif not device_uuid:
        cache[sn]["subscription_status"] = "failed"
        cache[sn]["subscription_reason"] = "no device_uuid from async-operations"
    else:
        sub_id = await _resolve_subscription_id(client, sub_key, sub_cache)
        if sub_id is None:
            safe_key = _sanitize_reason(sub_key)[:32]
            cache[sn]["subscription_status"] = "failed"
            cache[sn]["subscription_reason"] = f"subscription key not found: {safe_key}"
        else:
            sub_attempted = 1
            async with _subscription_patch_limiter:
                sub_status, sub_reason = await _patch_assign_subscription(client, device_uuid, sub_id)
            cache[sn]["subscription_status"] = sub_status
            cache[sn]["subscription_reason"] = sub_reason
            if sub_status == "succeeded":
                sub_assigned = 1

    return (svc_attempted, svc_assigned, sub_attempted, sub_assigned)
