"""translate_wlan bridge-tool tests.

Cover the preview shape + PII scrubbing, and the apply gate: target-write-flag
disabled → 403, declined elicitation → no write, confirmed → execute. All use
``source_override`` + ``context_override`` so no live clients are needed.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms import translate_wlan as tw

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


_PSK_WLAN = {"ssid": "CORP", "auth": {"type": "psk", "psk": "supersecret-psk"}}
_EAP_WLAN = {
    "ssid": "EAP",
    "auth": {"type": "eap"},
    "auth_servers": [{"host": "10.1.1.1", "port": 1812, "secret": "radsecret"}],
}


async def _preview(ctx, source_obj, **co):
    return await tw._preview_impl(
        ctx,
        "mist",
        "central",
        source_obj["ssid"],
        target_mode="bridged",
        gateway_clusters=None,
        source_override=source_obj,
        context_override={"writer_ctx": {}, **co},
    )


@pytest.mark.asyncio
async def test_preview_redacts_psk_and_omits_bodies() -> None:
    out = await _preview(_ctx(), _PSK_WLAN)
    assert out["canonical"]["security"]["psk"] == tw._REDACT
    # calls never carry bodies (bodies hold the plaintext passphrase)
    assert all("body" not in c for c in out["calls"])
    assert out["calls"][0]["path"].endswith("/wlan-ssids/CORP")
    assert "supersecret-psk" not in str(out)


@pytest.mark.asyncio
async def test_preview_redacts_radius_secret() -> None:
    out = await _preview(_ctx(), _EAP_WLAN)
    rad = out["canonical"]["security"]["radius"]
    assert rad["auth_servers"][0]["secret"] == tw._REDACT
    assert "radsecret" not in str(out)


@pytest.mark.asyncio
async def test_preview_reports_supported_and_preview_text() -> None:
    out = await _preview(_ctx(), _PSK_WLAN)
    assert "central:wlan" in out["supported"]["writers"]
    assert "mist → central" in out["preview"]


async def _apply(ctx, *, confirmed=False, source=_PSK_WLAN):
    return await tw._apply_impl(
        ctx,
        "mist",
        "central",
        source["ssid"],
        target_mode="bridged",
        gateway_clusters=None,
        source_override=source,
        context_override={"writer_ctx": {}},
        confirmed=confirmed,
    )


@pytest.mark.asyncio
async def test_apply_blocked_when_target_writes_disabled() -> None:
    cfg = SimpleNamespace(enable_central_write_tools=False, disable_elicitation=True)
    ctx = _ctx(config=cfg, central_conn=FakeConn())
    with pytest.raises(ToolError) as e:
        await _apply(ctx)
    assert e.value.args[0]["status_code"] == 403


@pytest.mark.asyncio
async def test_apply_declined_gate_writes_nothing(monkeypatch) -> None:
    async def _decline(ctx, description, params):
        return {"status": "declined"}

    monkeypatch.setattr(tw, "confirm_gated_invoke", _decline)
    cfg = SimpleNamespace(enable_central_write_tools=True, disable_elicitation=False)
    conn = FakeConn()
    out = await _apply(_ctx(config=cfg, central_conn=conn))
    assert out == {"status": "declined"}
    assert conn.posts == []  # nothing written


@pytest.mark.asyncio
async def test_apply_executes_when_confirmed() -> None:
    # disable_elicitation -> confirm_gated_invoke auto-accepts (returns None)
    cfg = SimpleNamespace(enable_central_write_tools=True, disable_elicitation=True)
    conn = FakeConn()
    out = await _apply(_ctx(config=cfg, central_conn=conn), confirmed=True)
    assert [r["action"] for r in out["results"]] == ["created"]
    assert any(p.endswith("/wlan-ssids/CORP") for p in conn.posts)


@pytest.mark.asyncio
async def test_build_plan_rejects_aos8_without_override() -> None:
    with pytest.raises(ToolError) as e:
        await tw._build_plan(
            _ctx(),
            "aos8",
            "central",
            "X",
            target_mode="bridged",
            gateway_clusters=None,
            source_override=None,
            context_override=None,
        )
    assert e.value.args[0]["status_code"] == 400


@pytest.mark.asyncio
async def test_build_plan_rejects_unknown_platforms() -> None:
    for src, tgt in [("nope", "central"), ("mist", "nope")]:
        with pytest.raises(ToolError):
            await tw._build_plan(
                _ctx(),
                src,
                tgt,
                "X",
                target_mode="bridged",
                gateway_clusters=None,
                source_override={"ssid": "X"},
                context_override={"writer_ctx": {}},
            )
