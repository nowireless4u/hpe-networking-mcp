# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Real captured GreenLake async-operation responses (sanitized) + shape tests.

These are ACTUAL responses captured from a live HPE GreenLake workspace, not
hand-approximated, per the repo's real-captured-fixtures rule:

* device add  — POST /devices/v1/devices            (captured 2026-06-29/30)
* device PATCH — PATCH /devices/v2beta1/devices?id=  (captured 2026-06-29)

Identifiers (serials, UUIDs) are replaced with placeholders; no personal data is
present in async-operation payloads. The tests run the production poll / enrich
helpers against these exact shapes so the contract is pinned to reality.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from hpe_networking_mcp.platforms.greenlake.tools._bulk_enrichment import _patch_enrich_location
from hpe_networking_mcp.platforms.greenlake.tools.bulk_add import _poll_async_operation

pytestmark = pytest.mark.unit

# --- Real captured async-operation responses (sanitized) ---------------------

# POST /devices/v1/devices for a serial already in the workspace -> terminal FAILED.
# Confirms: resultType "postDevicesResponse"; failures carry result.failedDevicesSerial.
POST_ASYNC_OP_FAILED = {
    "id": "00000000-0000-0000-0000-0000000000aa",
    "type": "/async-resource",
    "sourceResourceUri": "AsyncOperationResource",
    "status": "FAILED",
    "progressPercent": 0,
    "suggestedPollingIntervalSeconds": 2,
    "timeoutMinutes": 2,
    "result": {"failedDevicesSerial": ["SN-EXAMPLE-01"]},
    "logMessages": [],
    "resultType": "postDevicesResponse",
}

# PATCH /devices/v2beta1/devices?id=<uuid> with {"location":{"id":...}} post-add -> SUCCEEDED.
# Confirms: location IS patchable post-add; resultType "PatchDeviceResponseV2";
# result.succeededDevices carries the device id. (Tags PATCH returns the same shape.)
PATCH_ASYNC_OP_SUCCEEDED = {
    "id": "00000000-0000-0000-0000-0000000000bb",
    "status": "SUCCEEDED",
    "resultType": "PatchDeviceResponseV2",
    "result": {"succeededDevices": [{"id": "00000000-0000-0000-0000-0000000000cc"}]},
    "progressPercent": 100,
    "logMessages": [],
}


def _client_returning(poll_response, patch_status=202):
    """Fake GreenLakeHttpClient: get() -> poll_response; patch_raw() -> 202+Location."""
    client = MagicMock()
    client.get = AsyncMock(return_value=poll_response)
    resp = MagicMock()
    resp.status_code = patch_status
    resp.headers = {"location": "/devices/v1/async-operations/00000000-0000-0000-0000-0000000000bb"}
    resp.text = ""
    client.patch_raw = AsyncMock(return_value=resp)
    return client


class TestCapturedAsyncOpShapes:
    async def test_poll_recognizes_post_failed_terminal(self) -> None:
        client = _client_returning(POST_ASYNC_OP_FAILED)
        out = await _poll_async_operation(client, "00000000-0000-0000-0000-0000000000aa")
        assert out is not None and out["status"] == "FAILED"
        assert out["resultType"] == "postDevicesResponse"

    async def test_location_patch_post_add_succeeds_on_real_shape(self) -> None:
        client = _client_returning(PATCH_ASYNC_OP_SUCCEEDED)
        status, reason = await _patch_enrich_location(
            client, "00000000-0000-0000-0000-0000000000cc", "11111111-1111-1111-1111-111111111111"
        )
        assert status == "succeeded" and reason is None
        # PATCH issued with merge-patch content type + ?id= param (the confirmed contract).
        _, kwargs = client.patch_raw.call_args
        assert kwargs["additional_headers"]["Content-Type"] == "application/merge-patch+json"
        assert kwargs["params"] == {"id": "00000000-0000-0000-0000-0000000000cc"}
