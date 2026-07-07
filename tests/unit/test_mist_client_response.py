"""Unit tests for Mist client response normalization (#561).

Several Mist collection endpoints (``GET /orgs/{id}/inventory``, ``/otherdevices``,
``/networks``) return JSON ``null`` — not ``[]`` — for an empty or filtered-empty
result set. ``mist_request`` must normalize that to an empty list so it surfaces
as ``data: []`` (unambiguously "no rows") instead of ``data: null`` (which a model
can't distinguish from data loss). Confirmed live: ``mist_get_org_inventory`` with
the default ``unassigned=True`` returned ``null`` on an all-assigned org while
``unassigned=False`` returned the device list.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from hpe_networking_mcp.platforms.mist._client import mist_request

pytestmark = pytest.mark.unit


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


async def test_null_body_normalizes_to_empty_list():
    """#561: a JSON ``null`` body must return ``[]``, not ``None`` (→ data:null)."""
    ctx = _ctx(_resp(content=b"null", json_value=None))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory")
    assert result == []


async def test_nonempty_list_body_preserved():
    """Regression: a real bare-array response is returned unchanged (no data loss)."""
    rows = [{"serial": "AAA"}, {"serial": "BBB"}]
    ctx = _ctx(_resp(json_value=rows))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory")
    assert result == rows


async def test_empty_list_body_preserved():
    """An actual ``[]`` response stays ``[]`` (already unambiguous)."""
    ctx = _ctx(_resp(json_value=[]))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory")
    assert result == []


async def test_dict_body_preserved():
    """A dict-shaped response (search/count endpoints) is untouched by the fix."""
    body = {"results": [{"model": "AP41"}], "total": 1}
    ctx = _ctx(_resp(json_value=body))
    result = await mist_request(ctx, "GET", "/api/v1/orgs/x/inventory/search")
    # _decode_pagination adds has_more=False to dicts with no next page.
    assert result["results"] == body["results"]
    assert result["total"] == 1
