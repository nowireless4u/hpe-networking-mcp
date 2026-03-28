"""Shared fixtures for HPE Networking MCP Server tests."""

import pytest


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
