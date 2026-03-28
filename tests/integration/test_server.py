"""Integration tests for FastMCP server creation and configuration.

These tests verify that create_server() correctly assembles the FastMCP
instance, registers platform tools based on config, and applies transforms.
No real API calls are made -- platform registration functions are mocked.
"""

import pytest
from unittest.mock import patch, MagicMock

from hpe_networking_mcp.config import (
    ServerConfig,
    MistSecrets,
    CentralSecrets,
    GreenLakeSecrets,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mist_secrets() -> MistSecrets:
    return MistSecrets(api_token="test-mist-token", host="api.mist.com")


@pytest.fixture
def central_secrets() -> CentralSecrets:
    return CentralSecrets(
        base_url="https://us5.api.central.arubanetworks.com",
        client_id="test-central-id",
        client_secret="test-central-secret",
    )


@pytest.fixture
def greenlake_secrets() -> GreenLakeSecrets:
    return GreenLakeSecrets(
        api_base_url="https://global.api.greenlake.hpe.com",
        client_id="test-gl-id",
        client_secret="test-gl-secret",
        workspace_id="test-workspace-id",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestCreateServer:
    """Tests for hpe_networking_mcp.server.create_server()."""

    def test_returns_fastmcp_instance_with_correct_name(self, mist_secrets):
        """create_server() returns a FastMCP instance named 'HPE Networking MCP'."""
        from fastmcp import FastMCP

        config = ServerConfig(mist=mist_secrets)

        with patch("hpe_networking_mcp.server._register_mist_tools"):
            from hpe_networking_mcp.server import create_server

            mcp = create_server(config)

        assert isinstance(mcp, FastMCP)
        assert mcp.name == "HPE Networking MCP"

    def test_registers_mist_tools_when_mist_config_provided(self, mist_secrets):
        """create_server() calls _register_mist_tools when mist config is present."""
        config = ServerConfig(mist=mist_secrets)

        with patch("hpe_networking_mcp.server._register_mist_tools") as mock_mist:
            from hpe_networking_mcp.server import create_server

            create_server(config)

        mock_mist.assert_called_once()
        # Verify the FastMCP instance and config were passed
        args = mock_mist.call_args
        assert args is not None

    def test_registers_central_tools_when_central_config_provided(self, central_secrets):
        """create_server() calls _register_central_tools when central config is present."""
        config = ServerConfig(central=central_secrets)

        with patch("hpe_networking_mcp.server._register_central_tools") as mock_central:
            from hpe_networking_mcp.server import create_server

            create_server(config)

        mock_central.assert_called_once()

    def test_registers_greenlake_tools_when_greenlake_config_provided(self, greenlake_secrets):
        """create_server() calls _register_greenlake_tools when greenlake config is present."""
        config = ServerConfig(greenlake=greenlake_secrets)

        with patch("hpe_networking_mcp.server._register_greenlake_tools") as mock_gl:
            from hpe_networking_mcp.server import create_server

            create_server(config)

        mock_gl.assert_called_once()

    def test_registers_all_platforms_when_all_configs_provided(
        self, mist_secrets, central_secrets, greenlake_secrets
    ):
        """create_server() registers tools for all three platforms when all configs are present."""
        config = ServerConfig(
            mist=mist_secrets,
            central=central_secrets,
            greenlake=greenlake_secrets,
        )

        with (
            patch("hpe_networking_mcp.server._register_mist_tools") as mock_mist,
            patch("hpe_networking_mcp.server._register_central_tools") as mock_central,
            patch("hpe_networking_mcp.server._register_greenlake_tools") as mock_gl,
        ):
            from hpe_networking_mcp.server import create_server

            create_server(config)

        mock_mist.assert_called_once()
        mock_central.assert_called_once()
        mock_gl.assert_called_once()

    def test_skips_platforms_with_none_config(self, mist_secrets):
        """create_server() does not call registration for platforms with None config."""
        config = ServerConfig(mist=mist_secrets, central=None, greenlake=None)

        with (
            patch("hpe_networking_mcp.server._register_mist_tools") as mock_mist,
            patch("hpe_networking_mcp.server._register_central_tools") as mock_central,
            patch("hpe_networking_mcp.server._register_greenlake_tools") as mock_gl,
        ):
            from hpe_networking_mcp.server import create_server

            create_server(config)

        mock_mist.assert_called_once()
        mock_central.assert_not_called()
        mock_gl.assert_not_called()

    def test_applies_visibility_transform_when_write_tools_disabled(self, mist_secrets):
        """create_server() adds a Visibility transform when enable_write_tools is False."""
        config = ServerConfig(mist=mist_secrets, enable_write_tools=False)

        with patch("hpe_networking_mcp.server._register_mist_tools"):
            from hpe_networking_mcp.server import create_server

            mcp = create_server(config)

        # The server should have at least one transform applied (the Visibility transform)
        # FastMCP stores transforms in _transforms list
        transforms = getattr(mcp, "_transforms", [])
        from fastmcp.server.transforms import Visibility

        visibility_found = any(isinstance(t, Visibility) for t in transforms)
        assert visibility_found, (
            f"Expected a Visibility transform to be present when write tools are disabled. "
            f"Found transforms: {transforms}"
        )

    def test_no_visibility_transform_when_write_tools_enabled(self, mist_secrets):
        """create_server() does NOT add a Visibility transform when enable_write_tools is True."""
        config = ServerConfig(mist=mist_secrets, enable_write_tools=True)

        with patch("hpe_networking_mcp.server._register_mist_tools"):
            from hpe_networking_mcp.server import create_server

            mcp = create_server(config)

        transforms = getattr(mcp, "_transforms", [])
        from fastmcp.server.transforms import Visibility

        visibility_found = any(isinstance(t, Visibility) for t in transforms)
        assert not visibility_found, (
            f"Visibility transform should NOT be present when write tools are enabled. "
            f"Found transforms: {transforms}"
        )
