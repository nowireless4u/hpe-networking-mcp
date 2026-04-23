"""Shared fixtures for HPE Networking MCP Server tests."""

import importlib
from unittest.mock import MagicMock

import pytest


def _install_registry_stubs() -> None:
    """Stub ``_registry.mcp`` for each platform so tool modules import cleanly.

    Every ``@mcp.tool(...)`` at import time reads ``_registry.mcp``. In a test
    run, nothing has called ``register_tools()``, so the attribute is ``None``
    and any test that imports from a tool module fails collection with
    ``AttributeError: 'NoneType' object has no attribute 'tool'``. Installing
    a pass-through ``MagicMock`` at conftest load lets tool modules import
    and leaves the decorated functions intact as regular callables.

    Introduced at ``tests/integration/conftest.py`` for #153 and lifted here
    (for #155) when a new unit test under ``tests/unit/`` needed the same
    stubbing. Scoped to both unit and integration tests; idempotent.
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
            reg = importlib.import_module(module_path)
        except ImportError:
            continue
        if getattr(reg, "mcp", None) is None:
            reg.mcp = mock_mcp


_install_registry_stubs()


@pytest.fixture
def secrets_dir(tmp_path):
    """Create a temporary secrets directory with example secret files.

    Returns the path to the temporary directory. Individual tests can
    add or remove files as needed before calling the code under test.
    """
    secrets = {
        "mist_api_token": "test-mist-token-value-1234",
        "mist_host": "api.mist.com",
        "central_base_url": "https://us5.api.central.arubanetworks.com",
        "central_client_id": "central-client-id-value",
        "central_client_secret": "central-client-secret-value",
        "greenlake_api_base_url": "https://global.api.greenlake.hpe.com",
        "greenlake_client_id": "greenlake-client-id-value",
        "greenlake_client_secret": "greenlake-client-secret-value",
        "greenlake_workspace_id": "greenlake-workspace-id-value",
        "apstra_server": "apstra.test.example.com",
        "apstra_port": "443",
        "apstra_username": "admin",
        "apstra_password": "apstra-test-password",
        "apstra_verify_ssl": "true",
    }
    for name, value in secrets.items():
        (tmp_path / name).write_text(value)
    return tmp_path


@pytest.fixture
def patch_secrets_dir(monkeypatch, secrets_dir):
    """Monkeypatch SECRETS_DIR to point at the temporary secrets directory.

    This patches the module-level SECRETS_DIR variable in hpe_networking_mcp.config
    so that _read_secret() reads from the temp directory.
    """
    monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(secrets_dir))
    return secrets_dir
