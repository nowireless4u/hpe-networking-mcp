"""Cross-cutting AOS8 security tests at the tool layer (TEST-04 follow-up).

Complements TestAOS8ClientLogging.test_uidaruba_never_in_logs (client layer)
by exercising the full request path through a tool function.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from hpe_networking_mcp.config import AOS8Secrets
from hpe_networking_mcp.platforms.aos8.client import AOS8Client

pytestmark = pytest.mark.unit

_LEAK_BAIT_TOKEN = "tok-supersecret-leak-bait-99"
_LOGIN_OK = {"_global_result": {"status": "0", "UIDARUBA": _LEAK_BAIT_TOKEN}}


def _make_secrets(**overrides):
    base = {
        "host": "conductor.test",
        "port": 4343,
        "username": "admin",
        "password": "secret",
        "verify_ssl": True,
    }
    base.update(overrides)
    return AOS8Secrets(**base)


def _install(client: AOS8Client, handler):
    transport = httpx.MockTransport(handler)
    client._http = httpx.AsyncClient(
        base_url=f"https://{client._config.host}:{client._config.port}",
        transport=transport,
        verify=client._config.verify_ssl,
    )


async def test_uidaruba_value_not_logged_during_read_tool(loguru_capture):
    from hpe_networking_mcp.platforms.aos8.tools.health import aos8_get_version

    client = AOS8Client(_make_secrets())

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/api/login"):
            return httpx.Response(200, json=_LOGIN_OK)
        return httpx.Response(
            200,
            json={"_global_result": {"status": "0"}, "Version": "8.10.0.0"},
        )

    _install(client, handler)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}
    await aos8_get_version(ctx)
    await client.aclose()

    joined = "\n".join(loguru_capture)
    assert _LEAK_BAIT_TOKEN not in joined, f"UIDARUBA token value leaked: {joined!r}"
    # Per Pitfall 1: any line referencing UIDARUBA must redact it
    for line in loguru_capture:
        if "UIDARUBA" in line:
            assert "<redacted>" in line, f"UIDARUBA appeared without redaction: {line!r}"


async def test_uidaruba_value_not_logged_during_write_tool(loguru_capture):
    from hpe_networking_mcp.platforms.aos8.tools.writes import aos8_manage_ssid_profile

    client = AOS8Client(_make_secrets())

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/api/login"):
            return httpx.Response(200, json=_LOGIN_OK)
        return httpx.Response(
            200,
            json={"_global_result": {"status": "0", "status_str": "Success"}},
        )

    _install(client, handler)
    ctx = MagicMock()
    ctx.lifespan_context = {"aos8_client": client}
    # Signature confirmed via writes.py inspection (STEP 0):
    # (ctx, config_path, action_type, payload, confirmed)
    await aos8_manage_ssid_profile(
        ctx,
        config_path="/md/branch1",
        action_type="create",
        payload={"profile-name": "test-ssid", "essid": "test"},
        confirmed=True,
    )
    await client.aclose()

    joined = "\n".join(loguru_capture)
    assert _LEAK_BAIT_TOKEN not in joined
    for line in loguru_capture:
        if "UIDARUBA" in line:
            assert "<redacted>" in line
