# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake Bulk Device Onboarding tool.

API base path: ``/devices/v1/devices``
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import os
import pathlib
import tempfile
from typing import Annotated, Any

from aiolimiter import AsyncLimiter
from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient
from hpe_networking_mcp.platforms.greenlake.tools._bulk_assignment import _assign_for_row
from hpe_networking_mcp.platforms.greenlake.tools._bulk_enrichment import _enrich_for_row
from hpe_networking_mcp.platforms.greenlake.utils.csv_parser import parse_csv
from hpe_networking_mcp.redaction.rules import TokenKind
from hpe_networking_mcp.redaction.tokenizer import Tokenizer

# POST /devices/v1/devices: 5 req/min write rate limit.
# Module-level singleton — state persists across MCP tool invocations within
# the same process so the rate limit is respected even on back-to-back calls.
_device_add_limiter = AsyncLimiter(max_rate=5, time_period=60)

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

    Tries multiple field name variants because the exact schema is
    ASSUMED (HPE GreenLake portal is auth-gated; not verified from live API).
    Update this function once the actual field name is confirmed.
    """
    # Hypothesis A: direct "id" field
    if item.get("id"):
        return item["id"]
    # Hypothesis B: "resourceUri" path — extract trailing UUID
    uri = item.get("resourceUri", "")
    if uri and "/" in uri:
        return uri.rsplit("/", 1)[-1]
    # Hypothesis C: explicit "deviceId" field
    if item.get("deviceId"):
        return item["deviceId"]
    return None


async def _poll_async_operation(
    client: GreenLakeHttpClient,
    async_op_id: str,
) -> dict | None:
    """Poll GET /devices/v1/async-operations/{id} until terminal state.

    Returns the full response dict on SUCCEEDED/FAILED/TIMEOUT.
    Returns None if still non-terminal after MAX_POLL_ATTEMPTS (caller
    marks all rows in the batch as timed_out).

    Terminal states: SUCCEEDED, FAILED, TIMEOUT, TIMEDOUT (OpenAPI enum is TIMEDOUT;
    TIMEOUT kept for forward compatibility).
    Non-terminal: INITIALIZED, RUNNING.

    Uses asyncio.sleep (not time.sleep) so the event loop is never blocked.
    """
    endpoint = f"/devices/v1/async-operations/{async_op_id}"
    for _ in range(MAX_POLL_ATTEMPTS):
        result = await client.get(endpoint)
        status = result.get("status", "")
        if status in ("SUCCEEDED", "FAILED", "TIMEOUT", "TIMEDOUT"):
            # Normalize per-item results regardless of API shape:
            # Some responses use top-level "items"; others split into
            # "succeeded" and "failed" arrays.
            if result.get("items") is None:
                result["items"] = result.get("succeeded", []) + result.get("failed", [])
            return result
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
    return None  # caller marks batch as timed_out


@tool(
    name="greenlake_bulk_add_devices",
    description=(
        "Bulk-add HPE GreenLake devices from a CSV file or inline CSV text.\n\n"
        "Accepts either a local file path (csv_path) or raw CSV text (csv_text) — "
        "not both. Validates CSV columns and each row before making any API call.\n\n"
        "Mandatory CSV columns: serialNumber (aliases: serial, sn, serial_number) "
        "and macAddress (aliases: mac, mac_address). Column headers are matched "
        "case-insensitively.\n\n"
        "Rate limit: 5 POST/min (device-add), 20 PATCH/min (enrichment); batch size: 5 devices/request. "
        "A 10,000-device run takes ~400 min at ceiling; enrichment adds up to 4 PATCH/device. "
        "Resume-on-failure: a .cache.json file is written beside the input CSV "
        "and deleted after a fully successful run."
    ),
    tags={"greenlake", "greenlake_write"},
    annotations={
        "title": "Bulk add GreenLake devices from CSV",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def greenlake_bulk_add_devices(
    ctx: Context,
    acknowledged: Annotated[
        bool,
        Field(
            default=False,
            description=(
                "Set to True to confirm that serial numbers and MAC addresses "
                "will be transmitted to the AI assistant and that your use complies "
                "with your organization's data-handling policy. "
                "No parsing, no API calls, and no file reads will occur until this "
                "parameter is True."
            ),
        ),
    ] = False,
    csv_path: Annotated[
        str | None,
        Field(
            default=None,
            description="Absolute path to a local CSV file. Mutually exclusive with csv_text.",
        ),
    ] = None,
    csv_text: Annotated[
        str | None,
        Field(
            default=None,
            description="Raw CSV text as a string. Mutually exclusive with csv_path.",
        ),
    ] = None,
) -> dict[str, Any] | str:
    """Bulk-add GreenLake devices from CSV input."""
    # SECTION 1 — PII gate (D-01): must be first, before any I/O
    if not acknowledged:
        return (
            "PII ACKNOWLEDGMENT REQUIRED\n\n"
            "This tool will process and expose the following categories of personally "
            "identifiable / sensitive hardware information to the AI assistant:\n"
            "  - Serial numbers (hardware identifiers tied to purchase records)\n"
            "  - MAC addresses (hardware identifiers observable on-network)\n\n"
            "Before proceeding, confirm that transmitting this data to an AI assistant "
            "complies with your organization's data-handling and privacy policy.\n\n"
            "To proceed, re-invoke this tool with acknowledged=True."
        )

    logger.debug(
        "greenlake_bulk_add_devices called, csv_path={}, csv_text_len={}",
        csv_path,
        len(csv_text) if csv_text else 0,
    )

    # Exactly one source required
    if csv_path is None and csv_text is None:
        return "Error: provide either csv_path or csv_text"
    if csv_path is not None and csv_text is not None:
        return "Error: provide csv_path OR csv_text, not both"

    result = parse_csv(csv_path=csv_path, csv_text=csv_text)
    if result.error:
        return f"Error: {result.error}"

    if not result.valid_rows:
        if result.invalid_rows:
            details = "; ".join(r.get("error", "") for r in result.invalid_rows[:10])
            return f"Error: no valid rows found in CSV. Validation failures: {details}"
        return "Error: no valid rows found in CSV"

    # SECTION 2 — Cache path derivation (RESUME-01)
    if csv_path:
        cache_path = pathlib.Path(csv_path).with_suffix(".cache.json")
    else:
        # Inline CSV text — use stable hash-based temp path.
        # (tempfile.gettempdir() is safe here since this IS the cache path,
        #  not a .tmp file being os.replace()'d across drives)
        assert csv_text is not None  # guarded above
        digest = hashlib.sha256(csv_text[:1000].encode()).hexdigest()[:16]
        cache_path = pathlib.Path(tempfile.gettempdir()) / f"greenlake_bulk_{digest}.cache.json"

    # SECTION 3 — Resume-skip (RESUME-02)
    existing_cache = _load_cache(cache_path)
    pending_rows = [
        {**row, "_row_index": idx}
        for idx, row in enumerate(result.valid_rows)
        if existing_cache.get(row["serialNumber"], {}).get("status") != "succeeded"
    ]
    skipped_count = len(result.valid_rows) - len(pending_rows)
    # Copy existing cache so succeeded rows are preserved throughout the run
    cache: dict[str, dict] = dict(existing_cache)

    # Phase 20 in-process lookup caches (per-invocation; discarded at return).
    # _sub_cache: subscription key -> UUID str | None
    # _app_cache: holds the fetched service-catalog under key "_catalog" plus
    #   any per-name lookups derived from it.  Both caches collapse a 10k-row
    #   CSV to a handful of GETs.
    _sub_cache: dict[str, str | None] = {}
    _app_cache: dict[str, Any] = {}

    # SECTION 4 — PII tokenizer setup (D-02)
    token_store = ctx.lifespan_context.get("token_store")
    tokenizer: Tokenizer | None = None
    if token_store is not None:
        keymap = token_store.get_or_create(ctx.session_id)
        tokenizer = Tokenizer(
            keymap,
            session_id=ctx.session_id,
            max_entries=token_store.max_entries_per_session,
        )

    def _safe_serial(value: str) -> str:
        """Return tokenized serial number or fallback placeholder."""
        if tokenizer is not None:
            return tokenizer.tokenize(TokenKind.SERIAL, value)
        return "[serial]"

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
                async with _device_add_limiter:
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
                    sv_a, sv_g, sb_a, sb_g = await _assign_for_row(client, row, cache, sn, _sub_cache, _app_cache)
                    batch_svc_attempted += sv_a
                    batch_svc_assigned += sv_g
                    batch_sub_attempted += sb_a
                    batch_sub_assigned += sb_g
                # 6f.6 — Phase 21: location & tags enrichment
                batch_loc_attempted = batch_loc_succeeded = batch_tags_attempted = batch_tags_succeeded = 0
                for row in batch_rows:
                    la, ls, ta, ts = await _enrich_for_row(client, row, cache, row["serialNumber"])
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

    # SECTION 7 — Post-loop counts
    succeeded_count = sum(1 for v in cache.values() if v.get("status") == "succeeded")
    failed_count = sum(1 for v in cache.values() if v.get("status") in ("failed", "timed_out"))
    # skipped_count already computed in SECTION 3
    # Phase 20 + Phase 21 aggregate assignment/enrichment counts (defensive .get — older cache rows may lack these keys)
    service_succeeded = sum(1 for v in cache.values() if v.get("service_status") == "succeeded")
    service_failed = sum(1 for v in cache.values() if v.get("service_status") == "failed")
    service_skipped = sum(1 for v in cache.values() if v.get("service_status") == "skipped")
    subscription_succeeded = sum(1 for v in cache.values() if v.get("subscription_status") == "succeeded")
    subscription_failed = sum(1 for v in cache.values() if v.get("subscription_status") == "failed")
    subscription_skipped = sum(1 for v in cache.values() if v.get("subscription_status") == "skipped")
    location_succeeded = sum(1 for v in cache.values() if v.get("location_status") == "succeeded")
    location_failed = sum(1 for v in cache.values() if v.get("location_status") == "failed")
    location_skipped = sum(1 for v in cache.values() if v.get("location_status") == "skipped")
    tags_succeeded = sum(1 for v in cache.values() if v.get("tags_status") == "succeeded")
    tags_failed = sum(1 for v in cache.values() if v.get("tags_status") == "failed")
    tags_skipped = sum(1 for v in cache.values() if v.get("tags_status") == "skipped")
    # SECTION 8 — Cache cleanup (RESUME-03)
    # Compare succeeded_count alone (not + skipped_count) because succeeded_count already
    # includes rows that were succeeded in a prior run and are now reflected in cache.values().
    # Adding skipped_count would double-count them and prevent cleanup on resume runs.
    cache_path_str: str | None
    if succeeded_count == len(result.valid_rows) and failed_count == 0:
        with contextlib.suppress(OSError):
            os.remove(cache_path)
        cache_path_str = None
    else:
        cache_path_str = str(cache_path)

    # SECTION 9 — Build failure list (D-06)
    # Use field name "serial" (not "serialNumber") so the outbound middleware
    # PII walker's TOKENIZED_IDENTIFIER_FIELDS fires automatically.
    failures = [
        {"serial": sn, "reason": v["reason"]} for sn, v in cache.items() if v["status"] in ("failed", "timed_out")
    ]
    # Include enrichment failures so callers know when sub/service/location PATCH failed.
    enrichment_failures = [
        {"serial": sn, "phase": phase, "reason": v[f"{phase}_reason"]}
        for sn, v in cache.items()
        for phase in ("subscription", "service", "location", "tags")
        if v.get(f"{phase}_status") == "failed"
    ]

    # SECTION 10 — Return envelope (RESUME-04)
    return {
        "ok": True,
        "succeeded": succeeded_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "total": len(result.valid_rows),
        "cache_path": cache_path_str,
        "failures": failures[:10],
        "enrichment_failures": enrichment_failures[:10],
        "service_succeeded": service_succeeded,
        "service_failed": service_failed,
        "service_skipped": service_skipped,
        "subscription_succeeded": subscription_succeeded,
        "subscription_failed": subscription_failed,
        "subscription_skipped": subscription_skipped,
        "location_succeeded": location_succeeded,
        "location_failed": location_failed,
        "location_skipped": location_skipped,
        "tags_succeeded": tags_succeeded,
        "tags_failed": tags_failed,
        "tags_skipped": tags_skipped,
    }
