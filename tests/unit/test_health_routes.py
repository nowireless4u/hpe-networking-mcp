"""Unit tests for the plain HTTP health/probe endpoints (#582).

These drive the REAL Starlette app produced by ``FastMCP.http_app`` — the same
ASGI app the server serves — so the routes, status codes, and payloads are
exercised exactly as Kubernetes probes and the Docker healthcheck will see them.

Readiness is asserted WITHOUT entering the lifespan (which would create platform
clients and run best-effort startup probes): ``/readyz`` starts at ``503`` right
after build and flips to ``200`` when ``mark_ready`` runs — the precise call the
lifespan makes once startup completes — so no network or event loop is needed.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from hpe_networking_mcp.config import MistSecrets, ServerConfig
from hpe_networking_mcp.health_routes import mark_ready
from hpe_networking_mcp.middleware.origin_validation import OriginValidationMiddleware
from hpe_networking_mcp.server import create_server

pytestmark = pytest.mark.unit


def _build(tool_mode: str = "code") -> object:
    """Build a real Mist-only server in the given tool mode."""
    cfg = ServerConfig(tool_mode=tool_mode, mist=MistSecrets(api_token="x", host="y"))
    return create_server(cfg)


def _app(mcp: object):
    return mcp.http_app(transport="streamable-http")  # type: ignore[attr-defined]


def test_livez_always_ok() -> None:
    """/livez returns 200 as soon as the process serves HTTP — no lifespan needed,
    no platform calls. This is the property Kubernetes liveness relies on."""
    client = TestClient(_app(_build()))
    resp = client.get("/livez")
    assert resp.status_code == 200
    assert resp.text.strip() == "ok"


def test_livez_independent_of_platform_reachability() -> None:
    """Liveness must not depend on upstream platforms. The Mist host here ('y') is
    unresolvable, yet /livez is 200 because the handler makes no platform call —
    so a real upstream outage can never mark the container unhealthy."""
    client = TestClient(_app(_build()))
    assert client.get("/livez").status_code == 200


def test_readyz_503_before_startup_then_200_after_mark_ready() -> None:
    """/readyz is 503 until startup completes, then 200. mark_ready() is exactly
    what the lifespan calls once it finishes starting."""
    mcp = _build()
    client = TestClient(_app(mcp))

    before = client.get("/readyz")
    assert before.status_code == 503
    assert before.text.strip() == "starting"

    mark_ready(mcp)

    after = client.get("/readyz")
    assert after.status_code == 200
    assert after.text.strip() == "ok"


def test_healthz_payload_shape_and_no_secrets() -> None:
    """/healthz returns non-sensitive operator JSON: service, version, status,
    enabled platform NAMES, uptime. No secrets, tokens, hosts, or counts."""
    mcp = _build()
    client = TestClient(_app(mcp))

    body = client.get("/healthz").json()
    assert body["service"] == "hpe-networking-mcp"
    assert isinstance(body["version"], str) and body["version"]
    assert body["status"] == "starting"  # not ready until mark_ready
    assert body["platforms"] == ["mist"]  # names only
    assert isinstance(body["uptime_seconds"], (int, float))

    mark_ready(mcp)
    assert client.get("/healthz").json()["status"] == "ok"

    # Defense-in-depth: the serialized payload must expose no secret-bearing keys.
    raw = client.get("/healthz").text.lower()
    for forbidden in ("api_token", "secret", "password", "client_secret", "token"):
        assert forbidden not in raw


def test_healthz_platforms_is_enabled_platforms_passthrough() -> None:
    """/healthz reports config.enabled_platforms verbatim. Asserted with a
    Mist-only build to keep this unit test from registering other platforms'
    tools (building a multi-platform server here perturbs the module-level tool
    registries that reload-based dispatch tests depend on). The verbatim
    pass-through is the contract; enabled_platforms' multi-platform behavior is
    covered in the config tests."""
    cfg = ServerConfig(tool_mode="code", mist=MistSecrets(api_token="x", host="y"))
    client = TestClient(_app(create_server(cfg)))
    assert client.get("/healthz").json()["platforms"] == cfg.enabled_platforms == ["mist"]


def test_probes_pass_origin_validation_without_origin_header() -> None:
    """Kubernetes/Docker probes send no Origin header. The DNS-rebinding
    OriginValidationMiddleware must let them through so the probe path is 200,
    not a 403 the orchestrator would read as unhealthy."""
    app = OriginValidationMiddleware(_app(_build()), allowed_origins=["http://localhost:8000"])
    client = TestClient(app)

    # No Origin header (the probe case) → allowed through → 200.
    assert client.get("/livez").status_code == 200

    # A disallowed browser Origin is still rejected — the guard is active, it
    # simply doesn't apply to header-less probe traffic.
    blocked = client.get("/livez", headers={"Origin": "http://evil.example"})
    assert blocked.status_code == 403


def test_health_routes_registered_in_dynamic_mode() -> None:
    """Health endpoints are deployment plumbing — present in every tool mode,
    not just code mode."""
    client = TestClient(_app(_build("dynamic")))
    assert client.get("/livez").status_code == 200
    assert client.get("/readyz").status_code == 503
    assert client.get("/healthz").json()["service"] == "hpe-networking-mcp"
