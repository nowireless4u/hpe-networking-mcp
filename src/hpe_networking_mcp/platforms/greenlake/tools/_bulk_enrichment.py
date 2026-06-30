# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Phase 21 enrichment primitives: location and tags PATCH helpers.

Extracted into a sibling module of ``bulk_add.py`` to keep the parent file under
the 500-line project limit.  ``bulk_add.py`` imports these via::

    from ._bulk_enrichment import _enrich_for_row

NOTE: ``_poll_async_operation`` is imported LAZILY inside the PATCH helpers (not at
module scope) to prevent a circular import: ``bulk_add.py`` imports this module at
its top level, so a module-scope back-import would cause ``ImportError`` during
Python's module-initialization sequence.
"""

from __future__ import annotations

from typing import Any

from aiolimiter import AsyncLimiter

from ..client import GreenLakeHttpClient
from ._bulk_assignment import _sanitize_reason, make_patch_limiter


def _parse_tags_to_dict(tags_csv: str) -> dict[str, str]:
    """Convert comma-separated tag string to GreenLake tags dict.

    GreenLake tags are key-value pairs. When a CSV operator provides comma-separated
    tag names without values (ENRICH-02 intent), each name becomes a key with
    empty-string value.

    Args:
        tags_csv: Comma-separated tag names, e.g. "wlan, floor3, us-west"

    Returns:
        Dict of {tag_name: ""} for each non-empty element after stripping whitespace,
        e.g. {"wlan": "", "floor3": "", "us-west": ""}.  Returns {} for blank input.
    """
    return {tag.strip(): "" for tag in tags_csv.split(",") if tag.strip()}


async def _patch_enrich_location(
    client: GreenLakeHttpClient,
    device_uuid: str,
    location_id: str,
) -> tuple[str, str | None]:
    """PATCH location assignment for a single device.

    Endpoint: ``PATCH /devices/v2beta1/devices?id={device_uuid}``
    Body: ``{"location": {"id": location_id}}``
    Content-Type: ``application/merge-patch+json``

    Args:
        client: Authenticated GreenLake HTTP client.
        device_uuid: Device UUID from Phase 19 async-operation result.
        location_id: GreenLake location UUID from the CSV column (D-01 — passed through
            directly; no lookup or name resolution).

    Returns:
        ``("succeeded", None)`` on success; ``("failed", reason)`` otherwise.
        Never raises.
    """
    # Lazy import prevents circular: bulk_add imports this module at top level.
    from .bulk_add import _poll_async_operation  # noqa: PLC0415

    endpoint = "/devices/v2beta1/devices"
    # CONFIRMED via live API (2026-06-29): PATCH /devices/v2beta1/devices?id=<uuid>
    # with {"location": {"id": uuid}} POST-ADD returns 202 + a Location header, and the
    # async-op reaches status SUCCEEDED with resultType "PatchDeviceResponseV2" and
    # result.succeededDevices=[{"id": <uuid>}]. Location is NOT add-time-only — it can be
    # assigned to an already-added device. (Verified against a live HPE device.)
    body: dict[str, Any] = {"location": {"id": location_id}}
    headers = {"Content-Type": "application/merge-patch+json"}

    try:
        response = await client.patch_raw(endpoint, params={"id": device_uuid}, data=body, additional_headers=headers)
    except Exception as exc:
        return ("failed", _sanitize_reason(f"PATCH location exception: {exc}"))

    if response.status_code != 202:
        return ("failed", _sanitize_reason(f"PATCH location {response.status_code}: {response.text}"))

    location = response.headers.get("location", "")
    async_op_id = location.rsplit("/", 1)[-1] if location else ""
    if not async_op_id:
        return ("failed", "PATCH location 202 but no Location header")

    poll_result = await _poll_async_operation(client, async_op_id)
    if poll_result is None:
        return ("failed", "location PATCH poll timeout after 120s")

    op_status = poll_result.get("status", "")
    if op_status == "SUCCEEDED":
        return ("succeeded", None)
    error_raw = poll_result.get("error")
    if isinstance(error_raw, dict):
        error_msg = error_raw.get("message", "unknown")
    else:
        error_msg = str(error_raw) if error_raw is not None else "unknown"
    return ("failed", _sanitize_reason(f"location PATCH {op_status}: {error_msg}"))


async def _patch_enrich_tags(
    client: GreenLakeHttpClient,
    device_uuid: str,
    tags_dict: dict[str, str],
) -> tuple[str, str | None]:
    """PATCH tags assignment for a single device.

    Endpoint: ``PATCH /devices/v2beta1/devices?id={device_uuid}``
    Body: ``{"tags": tags_dict}``
    Content-Type: ``application/merge-patch+json``

    # NOTE: GreenLake tags are key-value pairs (dict[str, str]), not a JSON array.
    # D-05 decision (CSV comma-split) is implemented in _parse_tags_to_dict(); the dict
    # assembly here is the required deviation from D-05's array-of-strings framing.

    Args:
        client: Authenticated GreenLake HTTP client.
        device_uuid: Device UUID from Phase 19 async-operation result.
        tags_dict: Tags dict assembled by ``_parse_tags_to_dict()`` from the CSV cell.
            Each tag name is a key with an empty-string value (e.g. {"wlan": ""}).

    Returns:
        ``("succeeded", None)`` on success; ``("failed", reason)`` otherwise.
        Never raises.
    """
    # Lazy import — same circular-import reason as _patch_enrich_location.
    from .bulk_add import _poll_async_operation  # noqa: PLC0415

    endpoint = "/devices/v2beta1/devices"
    # CONFIRMED via live API (2026-06-29): PATCH {"tags": {...}} POST-ADD returns 202 +
    # async-op SUCCEEDED (resultType "PatchDeviceResponseV2"). merge-patch semantics apply:
    # a tag key set to null deletes it; other existing tags are preserved.
    body: dict[str, Any] = {"tags": tags_dict}
    headers = {"Content-Type": "application/merge-patch+json"}

    try:
        response = await client.patch_raw(endpoint, params={"id": device_uuid}, data=body, additional_headers=headers)
    except Exception as exc:
        return ("failed", _sanitize_reason(f"PATCH tags exception: {exc}"))

    if response.status_code != 202:
        return ("failed", _sanitize_reason(f"PATCH tags {response.status_code}: {response.text}"))

    location = response.headers.get("location", "")
    async_op_id = location.rsplit("/", 1)[-1] if location else ""
    if not async_op_id:
        return ("failed", "PATCH tags 202 but no Location header")

    poll_result = await _poll_async_operation(client, async_op_id)
    if poll_result is None:
        return ("failed", "tags PATCH poll timeout after 120s")

    op_status = poll_result.get("status", "")
    if op_status == "SUCCEEDED":
        return ("succeeded", None)
    error_raw = poll_result.get("error")
    if isinstance(error_raw, dict):
        error_msg = error_raw.get("message", "unknown")
    else:
        error_msg = str(error_raw) if error_raw is not None else "unknown"
    return ("failed", _sanitize_reason(f"tags PATCH {op_status}: {error_msg}"))


async def _enrich_for_row(
    client: GreenLakeHttpClient,
    row: dict[str, Any],
    cache: dict[str, Any],
    sn: str,
    patch_limiter: AsyncLimiter | None = None,
) -> tuple[int, int, int, int]:
    """Run Phase 21 location + tags enrichment for one row.

    Mutates ``cache[sn]`` in-place with four new Phase 21 fields:
    ``location_status``, ``location_reason``, ``tags_status``, ``tags_reason``.

    Returns (loc_attempted, loc_succeeded, tags_attempted, tags_succeeded).

    Args:
        client: Authenticated GreenLake HTTP client.
        row: CSV row dict containing optional ``location`` and ``tags`` columns.
        cache: Live run cache dict (mutated in place).
        sn: Serial number key for this row in ``cache``.

        patch_limiter: Per-invocation rate limiter. If None, a new one is created.

    Returns:
        Four-int tuple: loc_attempted, loc_succeeded, tags_attempted, tags_succeeded.
    """
    limiter = patch_limiter if patch_limiter is not None else make_patch_limiter()

    if cache[sn]["status"] != "succeeded":
        cache[sn]["location_status"] = "not_applicable"
        cache[sn]["location_reason"] = None
        cache[sn]["tags_status"] = "not_applicable"
        cache[sn]["tags_reason"] = None
        return (0, 0, 0, 0)

    device_uuid: str | None = cache[sn].get("device_id")

    loc_attempted = 0
    loc_succeeded = 0
    location_value = row.get("location")
    if not location_value or not str(location_value).strip():
        cache[sn]["location_status"] = "skipped"
        cache[sn]["location_reason"] = None
    elif not device_uuid:
        loc_attempted = 1
        cache[sn]["location_status"] = "failed"
        cache[sn]["location_reason"] = "no device_uuid from async-operations"
    else:
        loc_attempted = 1
        async with limiter:
            loc_status, loc_reason = await _patch_enrich_location(client, device_uuid, str(location_value).strip())
        cache[sn]["location_status"] = loc_status
        cache[sn]["location_reason"] = loc_reason
        if loc_status == "succeeded":
            loc_succeeded = 1

    tags_attempted = 0
    tags_succeeded = 0
    tags_value = row.get("tags")
    if not tags_value or not str(tags_value).strip():
        cache[sn]["tags_status"] = "skipped"
        cache[sn]["tags_reason"] = None
    elif not device_uuid:
        tags_attempted = 1
        cache[sn]["tags_status"] = "failed"
        cache[sn]["tags_reason"] = "no device_uuid from async-operations"
    else:
        tags_dict = _parse_tags_to_dict(str(tags_value))
        if not tags_dict:
            cache[sn]["tags_status"] = "skipped"
            cache[sn]["tags_reason"] = None
        else:
            tags_attempted = 1
            async with limiter:
                tags_status, tags_reason = await _patch_enrich_tags(client, device_uuid, tags_dict)
            cache[sn]["tags_status"] = tags_status
            cache[sn]["tags_reason"] = tags_reason
            if tags_status == "succeeded":
                tags_succeeded = 1

    return (loc_attempted, loc_succeeded, tags_attempted, tags_succeeded)
