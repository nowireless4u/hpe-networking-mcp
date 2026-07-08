"""Plain HTTP health/probe endpoints for Kubernetes and Docker.

The MCP protocol endpoint (``/mcp``) is not a clean ``httpGet`` probe target — a
bare ``GET`` can return ``406 Not Acceptable`` and ``HEAD`` can return ``405``,
neither of which Kubernetes treats as success (only ``200``–``399`` pass). These
routes give orchestrators a normal HTTP surface that never requires MCP stream
negotiation:

* ``GET /livez``  — ``200`` whenever the process is alive and serving HTTP.
  Lightweight; makes **no** external-platform calls. Liveness must stay
  decoupled from upstream reachability so a transient Mist/Central/GreenLake
  outage never triggers a pod restart.
* ``GET /readyz`` — ``200`` once server startup (the FastMCP lifespan) has
  completed; ``503`` before that. Also independent of upstream platform health.
* ``GET /healthz`` — non-sensitive operator JSON (service, version, enabled
  platform *names*, readiness, uptime). No secrets, no hostnames, no counts.

The deep per-platform reachability check remains the MCP ``health`` tool; it is
deliberately **not** wired into liveness for the reason above.

Readiness/uptime is tracked per-server in a ``WeakKeyDictionary`` keyed by the
``FastMCP`` instance, so multiple servers built in one process (e.g. the test
suite) never share state and entries are collected with their server.
"""

from __future__ import annotations

import time
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from starlette.responses import JSONResponse, PlainTextResponse

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from starlette.requests import Request
    from starlette.responses import Response

    from hpe_networking_mcp.config import ServerConfig

# Per-server readiness/uptime state. Weak keys so a server that goes out of
# scope (test suite builds many) is not pinned in memory.
_STATE: WeakKeyDictionary = WeakKeyDictionary()


def _service_version() -> str:
    """Best-effort package version for the operator payload."""
    try:
        return version("hpe-networking-mcp")
    except PackageNotFoundError:  # pragma: no cover — installed in all real runs
        return "unknown"


def init_state(mcp: FastMCP) -> None:
    """Register a server's probe state; call once at build time (not ready yet)."""
    _STATE[mcp] = {"ready": False, "started": time.monotonic()}


def mark_ready(mcp: FastMCP) -> None:
    """Flip a server to ready; call from the lifespan once startup completes."""
    state = _STATE.get(mcp)
    if state is not None:
        state["ready"] = True


def register_health_routes(mcp: FastMCP, config: ServerConfig) -> None:
    """Register ``/livez``, ``/readyz`` and ``/healthz`` on *mcp*.

    Registered in every tool mode and regardless of ``MCP_APP_ENABLE`` — these
    are deployment-plumbing endpoints, not model-facing tools. Custom routes sit
    outside the FastMCP tool-middleware chain, so responses are plain HTTP (never
    wrapped by the response envelope). Probes send no ``Origin`` header, so the
    ASGI ``OriginValidationMiddleware`` passes them through untouched.
    """
    init_state(mcp)

    @mcp.custom_route("/livez", methods=["GET"])
    async def livez(request: Request) -> Response:  # noqa: ARG001 — Starlette signature
        return PlainTextResponse("ok\n")

    @mcp.custom_route("/readyz", methods=["GET"])
    async def readyz(request: Request) -> Response:  # noqa: ARG001 — Starlette signature
        state = _STATE.get(mcp)
        if state is not None and state["ready"]:
            return PlainTextResponse("ok\n")
        return PlainTextResponse("starting\n", status_code=503)

    @mcp.custom_route("/healthz", methods=["GET"])
    async def healthz(request: Request) -> Response:  # noqa: ARG001 — Starlette signature
        state = _STATE.get(mcp) or {}
        ready = bool(state.get("ready"))
        started = state.get("started")
        uptime = round(time.monotonic() - started, 3) if started is not None else None
        return JSONResponse(
            {
                "service": "hpe-networking-mcp",
                "version": _service_version(),
                "status": "ok" if ready else "starting",
                "platforms": config.enabled_platforms,
                "uptime_seconds": uptime,
            }
        )
