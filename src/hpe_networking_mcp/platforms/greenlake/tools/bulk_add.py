# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake Bulk Device Onboarding tool.

API base path: ``/devices/v1/devices``
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import pathlib
import tempfile
from typing import Annotated, Any

from aiolimiter import AsyncLimiter
from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient
from hpe_networking_mcp.platforms.greenlake.tools._bulk_assignment import (
    _assign_for_row,
    build_result_envelope,
    make_patch_limiter,
    setup_resume,
)
from hpe_networking_mcp.platforms.greenlake.tools._bulk_enrichment import _enrich_for_row
from hpe_networking_mcp.platforms.greenlake.tools._bulk_source import (
    BULK_ADD_DESCRIPTION,
    apply_uniform_assignment,
    make_safe_serial,
    resolve_csv_source,
)
from hpe_networking_mcp.platforms.greenlake.utils.csv_parser import parse_csv

POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 24  # = 120s total per batch


def _write_cache_atomic(path: pathlib.Path, data: dict) -> None:
    """Write *data* as JSON to *path* atomically using a same-directory temp file.

    Uses tempfile.mkstemp in path.parent (NOT path.with_suffix('.tmp')) so that
    concurrent calls with the same CSV path each get a unique temp filename,
    eliminating the race on the shared sibling .tmp file.  Both files are on the
    same drive, which is required for os.replace() on Windows.
    """
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_name, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


def _load_cache(path: pathlib.Path) -> dict:
    """Load an existing cache JSON file, returning {} on any error."""
    try:
        text = path.read_text(encoding="utf-8").strip()
        return json.loads(text) if text else {}
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return {}


def _build_post_payload(rows: list[dict]) -> dict:
    """Build the POST /devices/v1/devices request body from a batch of rows."""
    network = []
    for row in rows:
        item: dict = {
            "serialNumber": row["serialNumber"],
            "macAddress": row["macAddress"],
        }
        if row.get("partNumber"):
            item["partNumber"] = row["partNumber"]
        network.append(item)
    # compute and storage must be present (even as empty lists) or the API
    # returns 400 "compute: must not be null; storage: must not be null".
    return {"network": network, "compute": [], "storage": []}


def _extract_device_id(item: dict) -> str | None:
    """Extract the newly-created device UUID from an async-operation item.

    CONFIRMED via live API (2026-06-28): POST /devices/v1/devices returns a
    202 whose async-operation result has ``resultType: "postDevicesResponse"``
    and an empty ``items`` list — no per-device UUIDs are embedded.  This
    function is kept as a defensive fallback for any future API shape change
    that starts including per-item results, but in practice ``_assign_for_row``
    always resolves the UUID via the lazy GET fallback instead.

    Field priority order (defensive, per device-GET shape confirmation):
      1. ``id`` — the UUID field on device GET responses (confirmed).
      2. ``resourceUri`` trailing segment — common GreenLake pattern.
      3. ``deviceId`` — explicit field seen in some sub-resources.
    """
    if item.get("id"):
        return item["id"]
    uri = item.get("resourceUri", "")
    if uri and "/" in uri:
        return uri.rsplit("/", 1)[-1]
    if item.get("deviceId"):
        return item["deviceId"]
    return None


async def _poll_async_operation(
    client: GreenLakeHttpClient,
    async_op_id: str,
) -> dict | None:
    """Poll GET /devices/v1/async-operations/{id} until terminal state.

    CONFIRMED via live API (2026-06-28): the response shape for a batch POST is::

        {
          "id": "<async-op-uuid>",
          "type": "/async-resource",
          "status": "SUCCEEDED",           # terminal
          "resultType": "postDevicesResponse",
          "result": "SUCCEEDED",
          "progressPercent": 100,
          "logMessages": [],
          ...                              # no "items", "succeeded", or "failed" keys
        }

    ``items`` is absent (not an empty list, simply absent) — device UUIDs are
    not embedded in the async-operation result; they must be resolved via
    GET /devices/v1/devices?filter=serialNumber eq '...'.

    Returns the full response dict on terminal state; None after MAX_POLL_ATTEMPTS
    (caller marks the batch as timed_out).

    Terminal states: SUCCEEDED, FAILED, TIMEOUT, TIMEDOUT.
    Non-terminal: INITIALIZED, RUNNING.
    """
    endpoint = f"/devices/v1/async-operations/{path_seg(async_op_id)}"
    for _ in range(MAX_POLL_ATTEMPTS):
        result = await client.get(endpoint)
        status = result.get("status", "")
        if status in ("SUCCEEDED", "FAILED", "TIMEOUT", "TIMEDOUT"):
            # Normalise to a consistent items list. For postDevicesResponse the
            # list is always empty; kept for forward compatibility if the API
            # shape ever changes to include per-device results.
            if result.get("items") is None:
                result["items"] = result.get("succeeded", []) + result.get("failed", [])
            return result
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
    return None  # caller marks batch as timed_out


@tool(
    name="greenlake_bulk_add_devices",
    description=BULK_ADD_DESCRIPTION,
    capability=Capability.WRITE,
    tags={"greenlake"},
    annotations={"title": "Bulk add GreenLake devices from CSV"},
)
async def greenlake_bulk_add_devices(
    ctx: Context,
    csv_filename: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Name of a CSV the operator uploaded via the `file_manager` widget. Read "
                "SERVER-SIDE from the session upload store — the content never enters the model "
                "context, so this is the right choice for large lists (up to 10k rows). "
                "Mutually exclusive with csv_text / csv_path."
            ),
        ),
    ] = None,
    csv_path: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Absolute path to a local CSV file (CLI / same-host). Mutually exclusive with csv_filename / csv_text."
            ),
        ),
    ] = None,
    csv_text: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Raw CSV text (copy/paste). The AI sees this content — use only for small lists, "
                "not thousands of rows. Mutually exclusive with csv_filename / csv_path."
            ),
        ),
    ] = None,
    subscription_key: Annotated[
        str | None,
        Field(default=None, description="Subscription key applied to EVERY device lacking a subscriptionKey column."),
    ] = None,
    service_id: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Service to assign to EVERY device lacking a serviceId column — a catalog "
                "service ID (UUID) OR a name (e.g. 'Aruba Central'); both resolve."
            ),
        ),
    ] = None,
    location: Annotated[
        str | None,
        Field(default=None, description="Location ID applied to EVERY device lacking a location column."),
    ] = None,
    tags: Annotated[
        str | None,
        Field(default=None, description="Tags applied to EVERY device lacking a tags column."),
    ] = None,
) -> dict[str, Any] | str:
    """Bulk-add GreenLake devices from CSV; see BULK_ADD_DESCRIPTION for the AI-facing contract."""
    logger.debug(
        "greenlake_bulk_add_devices called, csv_filename={}, csv_path={}, csv_text_len={}",
        csv_filename,
        csv_path,
        len(csv_text) if csv_text else 0,
    )

    # Validate exactly-one-source and resolve an upload to text server-side
    # (see _bulk_source — keeps the 10k-row CSV out of the model context).
    csv_path, csv_text = resolve_csv_source(ctx, csv_filename, csv_path, csv_text)

    result = parse_csv(csv_path=csv_path, csv_text=csv_text)
    if result.error:
        raise ToolError({"status_code": 400, "message": result.error})

    if not result.valid_rows:
        if result.invalid_rows:
            details = "; ".join(r.get("error", "") for r in result.invalid_rows[:10])
            raise ToolError(
                {"status_code": 400, "message": f"no valid rows found in CSV. Validation failures: {details}"}
            )  # noqa: E501
        raise ToolError({"status_code": 400, "message": "no valid rows found in CSV"})

    # Apply batch-uniform subscription/service/location/tags to rows that don't
    # already specify them (per-row CSV column wins) — lets the onboarding runbook
    # enrich an uploaded list the AI can't edit.
    apply_uniform_assignment(
        result.valid_rows,
        subscription_key=subscription_key,
        service_id=service_id,
        location=location,
        tags=tags,
    )

    # SECTION 2-3 — Cache path + resume-skip setup
    # Confirmation is handled structurally by the universal gate in
    # greenlake_invoke_tool (confirm_gated_invoke) before dispatch.
    # Write tools in this codebase do not duplicate the gate per-tool.
    cache_path, pending_rows, skipped_count, cache = setup_resume(csv_path, csv_text, result.valid_rows)

    # Per-invocation rate limiters — instantiated here (not at module level) so they
    # always bind to the running event loop and never leak across test loops.
    device_add_limiter = AsyncLimiter(max_rate=5, time_period=60)
    patch_limiter = make_patch_limiter()

    # Phase 20 in-process lookup caches (per-invocation; discarded at return).
    # _sub_cache: subscription key -> UUID str | None
    # _app_cache: holds the fetched service-catalog under key "_catalog" plus
    #   any per-name lookups derived from it.  Both caches collapse a 10k-row
    #   CSV to a handful of GETs.
    _sub_cache: dict[str, str | None] = {}
    _app_cache: dict[str, Any] = {}

    # SECTION 4 — PII serial redactor (D-02): [[SERIAL:uuid]] token or [serial] fallback.
    _safe_serial = make_safe_serial(ctx)

    # SECTION 5 — Client setup
    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    client = GreenLakeHttpClient(token_manager=token_manager, base_url=base_url)
    try:
        # SECTION 6 — Batch loop
        if pending_rows:
            batches = [pending_rows[i : i + 5] for i in range(0, len(pending_rows), 5)]
            total_batches = len(batches)

            for batch_num, batch_rows in enumerate(batches, 1):
                # 6a. Emit pre-submission progress (D-05)
                await ctx.report_progress(
                    progress=float(batch_num),
                    total=float(total_batches),
                    message=f"Batch {batch_num}/{total_batches}: submitted — polling async-operations...",
                )

                # 6b. Rate gate (ONBOARD-05)
                async with device_add_limiter:
                    response = await client.post_raw(
                        "/devices/v1/devices",
                        data=_build_post_payload(batch_rows),
                    )

                # 6c. Non-202 handling (D-03) — mark failed, continue run
                if response.status_code != 202:
                    reason = f"POST {response.status_code}: {response.text[:300]}"
                    with contextlib.suppress(Exception):
                        _e = response.json()
                        _parts = []
                        for _det in _e.get("errorDetails", []):
                            for _iss in _det.get("issues", []):
                                _parts.append(_iss.get("description", _iss.get("subject", "")))
                            if not _det.get("issues"):
                                _parts.append(_det.get("issue", _det.get("type", "")))
                        _base = f"POST {response.status_code}: [{_e.get('errorCode', '')}] {_e.get('message', '')}"
                        _detail = f" -- {'; '.join(_parts)}" if _parts else ""
                        reason = _base + _detail
                    for row in batch_rows:
                        cache[row["serialNumber"]] = {
                            "status": "failed",
                            "device_id": None,
                            "row_index": row.get("_row_index"),
                            "reason": reason,
                        }
                    _write_cache_atomic(cache_path, cache)
                    batch_failed = len(batch_rows)
                    await ctx.report_progress(
                        progress=float(batch_num),
                        total=float(total_batches),
                        message=f"Batch {batch_num}/{total_batches}: 0 succeeded, {batch_failed} failed",
                    )
                    continue

                # 6d. Location extraction
                location = response.headers.get("location", "")
                async_op_id = location.rsplit("/", 1)[-1] if location else ""

                if not async_op_id:
                    reason = "POST 202 but no Location header"
                    for row in batch_rows:
                        cache[row["serialNumber"]] = {
                            "status": "failed",
                            "device_id": None,
                            "row_index": row.get("_row_index"),
                            "reason": reason,
                        }
                    _write_cache_atomic(cache_path, cache)
                    batch_failed = len(batch_rows)
                    await ctx.report_progress(
                        progress=float(batch_num),
                        total=float(total_batches),
                        message=f"Batch {batch_num}/{total_batches}: 0 succeeded, {batch_failed} failed",
                    )
                    continue

                # 6e. Poll (ONBOARD-02)
                poll_result = await _poll_async_operation(client, async_op_id)

                if poll_result is None:
                    # Timeout (D-04) — mark timed_out and continue
                    for row in batch_rows:
                        cache[row["serialNumber"]] = {
                            "status": "timed_out",
                            "device_id": None,
                            "row_index": row.get("_row_index"),
                            "reason": "poll timeout after 120s",
                        }
                    _write_cache_atomic(cache_path, cache)
                    batch_failed = len(batch_rows)
                    await ctx.report_progress(
                        progress=float(batch_num),
                        total=float(total_batches),
                        message=f"Batch {batch_num}/{total_batches}: 0 succeeded, {batch_failed} failed (timed out)",
                    )
                    continue

                # 6f. Per-item result extraction (ONBOARD-02, A1)
                # GreenLake async responses use one of three shapes:
                #   A) items: [{serialNumber, status, ...}]  (per-device detail)
                #   B) result: "SUCCEEDED" + no items       (batch success, no per-device list)
                #   C) result: {failedDevicesSerial: [...]} (batch FAILED with serial list)
                raw_items = poll_result.get("items")
                items: list[dict] = (
                    raw_items
                    if raw_items is not None
                    else poll_result.get("succeeded", []) + poll_result.get("failed", [])
                )
                if not items:
                    batch_result = poll_result.get("result", {})
                    if isinstance(batch_result, dict):
                        # Shape C: synthesize per-device items from failedDevicesSerial
                        failed_set = set(batch_result.get("failedDevicesSerial", []))
                        items = [
                            {
                                "serialNumber": r["serialNumber"],
                                "status": "FAILED" if r["serialNumber"] in failed_set else "SUCCEEDED",
                                "reason": "device already exists in workspace or invalid serial/MAC combination",
                            }
                            for r in batch_rows
                        ]
                    elif poll_result.get("status") == "SUCCEEDED":
                        # Shape B: batch succeeded with no per-device breakdown
                        items = [{"serialNumber": r["serialNumber"], "status": "SUCCEEDED"} for r in batch_rows]
                item_by_serial: dict[str, dict] = {item.get("serialNumber", ""): item for item in items}

                batch_succeeded = 0
                batch_failed = 0
                failure_details: list[str] = []

                for row in batch_rows:
                    sn = row["serialNumber"]
                    item = item_by_serial.get(sn, {})
                    item_status = item.get("status", "FAILED")

                    if item_status == "SUCCEEDED":
                        cache[sn] = {
                            "status": "succeeded",
                            "device_id": _extract_device_id(item),
                            "row_index": row.get("_row_index"),
                            "reason": None,
                        }
                        batch_succeeded += 1
                    else:
                        fail_reason = item.get("reason", "API reported failure")
                        cache[sn] = {
                            "status": "failed",
                            "device_id": None,
                            "row_index": row.get("_row_index"),
                            "reason": fail_reason,
                        }
                        batch_failed += 1
                        failure_details.append(f"  {_safe_serial(sn)}: {fail_reason}")

                # 6f.5 — Phase 20: subscription & service assignment
                # Run immediately after Phase 19 classification; one write per batch
                # (the _write_cache_atomic call below replaces the original placement).
                batch_svc_attempted = 0
                batch_svc_assigned = 0
                batch_sub_attempted = 0
                batch_sub_assigned = 0

                for row in batch_rows:
                    sn = row["serialNumber"]
                    sv_a, sv_g, sb_a, sb_g = await _assign_for_row(
                        client, row, cache, sn, _sub_cache, _app_cache, patch_limiter
                    )
                    batch_svc_attempted += sv_a
                    batch_svc_assigned += sv_g
                    batch_sub_attempted += sb_a
                    batch_sub_assigned += sb_g
                # 6f.6 — Phase 21: location & tags enrichment
                batch_loc_attempted = batch_loc_succeeded = batch_tags_attempted = batch_tags_succeeded = 0
                for row in batch_rows:
                    la, ls, ta, ts = await _enrich_for_row(client, row, cache, row["serialNumber"], patch_limiter)
                    batch_loc_attempted += la
                    batch_loc_succeeded += ls
                    batch_tags_attempted += ta
                    batch_tags_succeeded += ts
                # Batch-scoped write: all Phase 20 fields for every row in this batch
                # are written together after all assignments complete. Rows that hit
                # a batch-level 422/timeout failure above (which `continue` past this
                # block) will NOT have Phase 20 fields (service_status etc.) written —
                # they remain absent from their cache entry. Section 10 reads these
                # fields defensively with .get("service_status") to handle this case.
                _write_cache_atomic(cache_path, cache)

                # 6g. Emit completion progress (D-05)
                await ctx.report_progress(
                    progress=float(batch_num),
                    total=float(total_batches),
                    message=(
                        f"Batch {batch_num}/{total_batches}: {batch_succeeded} succeeded, {batch_failed} failed,"
                        f" svc {batch_svc_assigned}/{batch_svc_attempted},"
                        f" sub {batch_sub_assigned}/{batch_sub_attempted},"
                        f" loc {batch_loc_succeeded}/{batch_loc_attempted},"
                        f" tags {batch_tags_succeeded}/{batch_tags_attempted}"
                    ),
                )
                if failure_details:
                    await ctx.info(message="Batch failures:\n" + "\n".join(failure_details))

    finally:
        await client.close()

    return build_result_envelope(cache, cache_path, skipped_count, len(result.valid_rows), safe_serial=_safe_serial)
