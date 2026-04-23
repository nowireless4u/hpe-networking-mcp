"""Integration test fixtures using Docker secrets for live API access.

These tests run against real Mist and Central APIs. They require
Docker secrets to be available at SECRETS_DIR (default: ./secrets/).
Tests skip gracefully if credentials are missing.

Run via Docker:
    docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm \\
        hpe-networking-mcp sh -c "uv run pytest tests/integration/ -m integration -v"
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def _install_registry_stubs() -> None:
    """Stub ``_registry.mcp`` for each platform so tool modules can be imported.

    Live integration tests (e.g. ``test_ap_monitoring_live.py``) import tool
    functions directly from ``hpe_networking_mcp.platforms.*.tools.*``. Each
    tool module calls ``@mcp.tool(...)`` at import time against
    ``_registry.mcp`` — which is ``None`` until ``register_tools()`` runs.
    Since integration tests don't spin up a FastMCP server (they exercise the
    tool functions against live vendor APIs), ``register_tools()`` never runs
    and the imports fail at collection with ``AttributeError: 'NoneType'
    object has no attribute 'tool'``.

    This fixture installs a ``MagicMock`` whose ``.tool(...)`` and
    ``.prompt(...)`` return pass-through decorators, so decorated functions
    remain intact as regular callables. Idempotent — skips platforms whose
    registry is already populated (e.g. when running unit + integration in
    the same session and a prior fixture set one up).

    Only runs for the ``tests/integration`` tree; ``tests/unit`` does not need
    the stubbing because unit tests import from utils/models/client modules
    rather than from the tool modules.
    """
    platform_registries = (
        "hpe_networking_mcp.platforms.apstra._registry",
        "hpe_networking_mcp.platforms.central._registry",
        "hpe_networking_mcp.platforms.clearpass._registry",
        "hpe_networking_mcp.platforms.greenlake._registry",
        "hpe_networking_mcp.platforms.mist._registry",
    )

    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock(side_effect=lambda *_a, **_kw: lambda fn: fn)
    mock_mcp.prompt = MagicMock(side_effect=lambda *_a, **_kw: lambda fn: fn)

    for module_path in platform_registries:
        try:
            import importlib

            reg = importlib.import_module(module_path)
        except ImportError:
            # Platform module not yet available (e.g. during scaffolding).
            continue
        if getattr(reg, "mcp", None) is None:
            reg.mcp = mock_mcp


_install_registry_stubs()


def _read_secret(name: str) -> str | None:
    """Read a secret file from SECRETS_DIR, matching config.py behavior."""
    secrets_dir = os.environ.get("SECRETS_DIR", "/run/secrets")
    path = Path(secrets_dir) / name
    if path.is_file():
        return path.read_text().strip()
    return None


@pytest.fixture(scope="session")
def central_conn():
    """Create a live Central connection from Docker secrets.

    Skips all tests if Central credentials are not available.
    """
    base_url = _read_secret("central_base_url")
    client_id = _read_secret("central_client_id")
    client_secret = _read_secret("central_client_secret")

    if not all([base_url, client_id, client_secret]):
        pytest.skip("Central credentials not found — skipping live tests")

    from pycentral import NewCentralBase

    conn = NewCentralBase(
        token_info={
            "new_central": {
                "base_url": base_url,
                "client_id": client_id,
                "client_secret": client_secret,
            }
        }
    )
    return conn


@pytest.fixture(scope="session")
def live_ctx(central_conn):
    """Create a mock Context with a live Central connection.

    Mimics the lifespan context that tools receive at runtime.
    """
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": central_conn}
    return ctx
