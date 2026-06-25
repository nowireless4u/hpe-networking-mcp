"""translate_config bridge-tool tests.

Cover the preview shape + PII scrubbing, the apply gate (target-write-flag
disabled → 403, auth_server PII → 403, declined elicitation → no write, confirmed
→ execute), and input validation (unknown kind, missing reader context).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms import translate_config as tc

pytestmark = pytest.mark.unit


class FakeConn:
    """Central conn stub: GET → missing (200+{}), POST → created."""

    def __init__(self) -> None:
        self.posts: list[str] = []

    async def command(self, method, path, api_params=None, api_data=None):
        if method == "POST":
            self.posts.append(path)
            return {"code": 200, "msg": {"id": "x"}}
        return {"code": 200, "msg": {}}


def _ctx(**lifespan):
    return SimpleNamespace(lifespan_context=lifespan)


_ROLE = {"rname": "employee", "role__vlan": {"vlanstr": "104"}}
_AUTH = {"rad_server_name": "RAD1", "rad_host": {"host": "10.1.1.1"}, "rad_key": {"key": "supersecret"}}
_NETG = {"dstname": "cppm", "netdst__entry": [{"address": "10.0.0.5", "_objname": "netdst__host"}]}


async def _preview(ctx, kind, record, *, scope_id="S1", extra_ctx=None):
    return await tc._preview_impl(
        ctx, "aos8", "central", kind, record, scope_id=scope_id, device_functions=None, extra_ctx=extra_ctx
    )


@pytest.mark.asyncio
async def test_preview_shape_and_bodies_omitted() -> None:
    out = await _preview(_ctx(), "role", _ROLE)
    assert "aos8:role" in out["supported"]["readers"]
    assert all("body" not in c for c in out["calls"])
    assert out["calls"][0]["path"].endswith("/roles/employee")
    assert out["calls"][-1]["path"].endswith("/config-assignments")


@pytest.mark.asyncio
async def test_preview_redacts_auth_server_secret() -> None:
    out = await _preview(_ctx(), "auth_server", _AUTH)
    assert "supersecret" not in str(out)
    body = out["canonical"]["body"]
    assert body["shared-secret-config"]["plaintext-value"] == tc._REDACT


@pytest.mark.asyncio
async def test_preview_unresolved_scope_blocks() -> None:
    out = await _preview(_ctx(), "role", _ROLE, scope_id=None)
    assert out["unresolved"]  # config-assignment scope unresolved


@pytest.mark.asyncio
async def test_preview_unknown_kind_raises() -> None:
    with pytest.raises(ToolError) as e:
        await _preview(_ctx(), "nonsense", _ROLE)
    assert e.value.args[0]["status_code"] == 400


@pytest.mark.asyncio
async def test_preview_policy_without_role_records_raises() -> None:
    with pytest.raises(ToolError) as e:
        await _preview(_ctx(), "policy", {"accname": "x", "acl_sess__v4policy": []})
    assert e.value.args[0]["status_code"] == 400


@pytest.mark.asyncio
async def test_preview_policy_with_role_records_ok() -> None:
    out = await _preview(_ctx(), "policy", {"accname": "x", "acl_sess__v4policy": []}, extra_ctx={"role_records": []})
    assert any("/policy-groups/" in c["path"] for c in out["calls"])  # #420 fix present


async def _apply(ctx, kind, record, *, confirmed=False, extra_ctx=None):
    return await tc._apply_impl(
        ctx,
        "aos8",
        "central",
        kind,
        record,
        scope_id="S1",
        device_functions=None,
        extra_ctx=extra_ctx,
        confirmed=confirmed,
    )


@pytest.mark.asyncio
async def test_apply_blocked_when_writes_disabled() -> None:
    cfg = SimpleNamespace(enable_central_write_tools=False, disable_elicitation=True)
    with pytest.raises(ToolError) as e:
        await _apply(_ctx(config=cfg, central_conn=FakeConn()), "role", _ROLE)
    assert e.value.args[0]["status_code"] == 403


@pytest.mark.asyncio
async def test_apply_auth_server_pii_blocked() -> None:
    cfg = SimpleNamespace(enable_central_write_tools=True, disable_elicitation=True)
    conn = FakeConn()
    with pytest.raises(ToolError) as e:
        await _apply(_ctx(config=cfg, central_conn=conn), "auth_server", _AUTH, confirmed=True)
    assert e.value.args[0]["status_code"] == 403
    assert conn.posts == []  # nothing written


@pytest.mark.asyncio
async def test_apply_declined_gate_writes_nothing(monkeypatch) -> None:
    async def _decline(ctx, description, params):
        return {"status": "declined"}

    monkeypatch.setattr(tc, "confirm_gated_invoke", _decline)
    cfg = SimpleNamespace(enable_central_write_tools=True, disable_elicitation=False)
    conn = FakeConn()
    out = await _apply(_ctx(config=cfg, central_conn=conn), "role", _ROLE)
    assert out == {"status": "declined"}
    assert conn.posts == []


@pytest.mark.asyncio
async def test_apply_executes_when_confirmed() -> None:
    cfg = SimpleNamespace(enable_central_write_tools=True, disable_elicitation=True)
    conn = FakeConn()
    out = await _apply(_ctx(config=cfg, central_conn=conn), "net_group", _NETG, confirmed=True)
    assert [r["action"] for r in out["results"]] == ["created", "assigned"]
    assert any(p.endswith("/net-groups/cppm") for p in conn.posts)
