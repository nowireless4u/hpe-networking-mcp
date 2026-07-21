"""Unit tests for Mist client empty-collection normalization (#561).

Some Mist collection endpoints (``GET /orgs/{id}/inventory``, ``/otherdevices``,
``/networks``) return JSON ``null`` — not ``[]`` — for an empty/filtered-empty
result set. But normalizing that to a bare ``[]`` is NOT enough: an empty list
has no recoverable content block, so ``ResponseEnvelopeMiddleware`` can't tell it
from ``None`` and it still collapses to ``data: null``. So ``mist_request`` returns
a **dict** (``{"items": [], "has_more": False}``) for an empty collection, which
survives the envelope as a non-null, unambiguous "no rows" result.

Confirmed live: ``mist_get_org_inventory`` with the default ``unassigned=True``
returned ``null`` on an all-assigned org while ``unassigned=False`` returned the
device list; ``count`` confirmed the devices existed all along.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Client, FastMCP

from hpe_networking_mcp.middleware.response_envelope import ResponseEnvelopeMiddleware
from hpe_networking_mcp.platforms.mist._client import mist_request

pytestmark = pytest.mark.unit

_EMPTY = {"items": [], "has_more": False}


def _resp(*, status: int = 200, content: bytes = b"x", json_value=None, headers: dict | None = None):
    r = MagicMock()
    r.status_code = status
    r.content = content
    r.headers = headers or {}
    r.json = MagicMock(return_value=json_value)
    r.text = ""
    return r


def _ctx(resp):
    client = MagicMock()
    client.request = AsyncMock(return_value=resp)
    ctx = MagicMock()
    ctx.lifespan_context = {"mist_client": client}
    return ctx


async def test_null_body_normalizes_to_empty_items_dict():
    """#561: a JSON ``null`` body → a non-null ``{"items": []}`` dict, not ``None``."""
    ctx = _ctx(_resp(content=b"null", json_value=None))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory")
    assert result == _EMPTY


async def test_empty_list_body_normalized_to_dict():
    """An actual ``[]`` response is ALSO normalized — a bare empty list would still
    collapse to ``data: null`` through the envelope (see the end-to-end test)."""
    ctx = _ctx(_resp(json_value=[]))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory")
    assert result == _EMPTY


async def test_nonempty_list_body_preserved():
    """Regression: a real bare-array response is returned unchanged (no data loss)."""
    rows = [{"serial": "AAA"}, {"serial": "BBB"}]
    ctx = _ctx(_resp(json_value=rows))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory")
    assert result == rows


async def test_dict_body_preserved():
    """A dict-shaped response (search/count endpoints) is untouched by the fix."""
    body = {"results": [{"model": "AP41"}], "total": 1}
    ctx = _ctx(_resp(json_value=body))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory/search")
    assert result["results"] == body["results"]
    assert result["total"] == 1


async def test_empty_collection_survives_envelope_end_to_end():
    """The regression the isolated mist_request test missed: drive an empty result
    THROUGH ResponseEnvelopeMiddleware and assert ``data`` is a non-null empty
    collection — a bare ``[]`` return collapses to ``data: null`` here, which is
    exactly why mist_request returns a dict."""
    mcp = FastMCP("t", middleware=[ResponseEnvelopeMiddleware()])

    @mcp.tool
    async def returns_empty_dict() -> Any:
        return _EMPTY

    @mcp.tool
    async def returns_empty_list() -> Any:
        return []

    async with Client(mcp) as client:
        dict_res = await client.call_tool("returns_empty_dict", {})
        list_res = await client.call_tool("returns_empty_list", {})

    # The dict shape (what mist_request now returns) survives with real data.
    assert (dict_res.structured_content or {}).get("data") == _EMPTY
    # A bare empty list collapses to data:null — documents WHY the dict is needed.
    assert (list_res.structured_content or {}).get("data") is None


async def test_no_such_metric_404_enriched_with_sle_metric_guidance():
    """#638: a guessed SLE metric key returns a bare 404 `{"detail": "no such
    metric"}`; the enricher must point at `mist_list_site_sles_metrics` and name
    real keys so the AI stops guessing (e.g. `successful-connect` is NOT a key)."""
    from fastmcp.exceptions import ToolError

    ctx = _ctx(_resp(status=404, json_value={"detail": "no such metric"}))
    with pytest.raises(ToolError) as e:
        await mist_request(
            ctx,
            "GET",
            "/api/v1/sites/s/sle/site/s/metric/successful-connect/impact-summary",
        )
    payload = e.value.args[0]
    assert payload["status_code"] == 404
    msg = payload["message"]
    assert "mist_list_site_sles_metrics" in msg
    assert "time-to-connect" in msg
    assert "successful-connect" in msg  # explicitly called out as NOT a key


async def test_403_hint_points_to_existing_self_tool():
    """The 403 hint must name a real tool: `mist_get_self`, not the
    non-existent `mist_get_self_account_info` (which itself returned unknown_tool)."""
    from fastmcp.exceptions import ToolError

    ctx = _ctx(_resp(status=403, json_value={"detail": "permission denied"}))
    with pytest.raises(ToolError) as e:
        await mist_request(ctx, "GET", "/api/v1/orgs/x/sites")
    payload = e.value.args[0]
    assert payload["status_code"] == 403
    assert "mist_get_self" in payload["message"]
    assert "mist_get_self_account_info" not in payload["message"]
