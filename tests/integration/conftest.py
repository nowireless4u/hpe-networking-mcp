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

# Note: the `_install_registry_stubs` call that allowed integration tests to
# import tool modules at collection time used to live here. It was lifted to
# tests/conftest.py for #155 so unit tests can also exercise tool-module-level
# imports. pytest auto-loads the parent conftest before this one, so the
# stubs are already in place by the time anything here runs.


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
