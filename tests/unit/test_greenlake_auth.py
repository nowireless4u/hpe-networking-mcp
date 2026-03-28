"""Unit tests for hpe_networking_mcp.platforms.greenlake.auth — TokenInfo, TokenManager."""

import time
from unittest.mock import MagicMock, patch

import pytest

from hpe_networking_mcp.platforms.greenlake.auth import (
    OAuth2Provider,
    OAuth2TokenResponse,
    TokenInfo,
    TokenManager,
)


# ---------------------------------------------------------------------------
# TokenInfo
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTokenInfo:
    def test_stores_token_and_expiration(self):
        info = TokenInfo(token="abc123", expires_at=time.time() + 3600)
        assert info.token == "abc123"
        assert info.expires_at is not None

    def test_is_expired_returns_true_for_past_token(self):
        info = TokenInfo(token="old", expires_at=time.time() - 100)
        assert info.is_expired() is True

    def test_is_expired_returns_false_for_future_token(self):
        info = TokenInfo(token="fresh", expires_at=time.time() + 3600)
        assert info.is_expired() is False

    def test_is_expired_respects_buffer(self):
        """Token expiring within buffer_seconds should be considered expired."""
        info = TokenInfo(token="soon", expires_at=time.time() + 100)
        assert info.is_expired(buffer_seconds=200) is True

    def test_is_expired_returns_false_when_no_expiration(self):
        info = TokenInfo(token="forever", expires_at=None)
        assert info.is_expired() is False

    def test_time_until_expiry(self):
        info = TokenInfo(token="t", expires_at=time.time() + 1000)
        remaining = info.time_until_expiry()
        assert remaining is not None
        assert 999 <= remaining <= 1001

    def test_time_until_expiry_returns_none_when_no_expiration(self):
        info = TokenInfo(token="t", expires_at=None)
        assert info.time_until_expiry() is None

    def test_time_until_expiry_returns_zero_for_expired(self):
        info = TokenInfo(token="t", expires_at=time.time() - 100)
        assert info.time_until_expiry() == 0


# ---------------------------------------------------------------------------
# OAuth2TokenResponse
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOAuth2TokenResponse:
    def test_expires_at_computed_from_issued_at_and_expires_in(self):
        resp = OAuth2TokenResponse(
            access_token="tok",
            expires_in=3600,
            issued_at=1000.0,
        )
        assert resp.expires_at == 4600.0

    def test_expires_at_is_none_when_no_expires_in(self):
        resp = OAuth2TokenResponse(access_token="tok", expires_in=None)
        assert resp.expires_at is None


# ---------------------------------------------------------------------------
# OAuth2Provider
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOAuth2Provider:
    def test_validate_token_true_for_non_empty(self):
        provider = OAuth2Provider(
            client_id="c",
            client_secret="s",
            token_url="https://example.com/token",
        )
        assert provider.validate_token("valid-token") is True

    def test_validate_token_false_for_empty(self):
        provider = OAuth2Provider(
            client_id="c",
            client_secret="s",
            token_url="https://example.com/token",
        )
        assert provider.validate_token("") is False

    def test_validate_token_false_for_whitespace(self):
        provider = OAuth2Provider(
            client_id="c",
            client_secret="s",
            token_url="https://example.com/token",
        )
        assert provider.validate_token("   ") is False


# ---------------------------------------------------------------------------
# TokenManager
# ---------------------------------------------------------------------------


def _mock_oauth2_response(token="mock-token", expires_in=3600):
    """Create a mock OAuth2TokenResponse."""
    return OAuth2TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in=expires_in,
    )


@pytest.mark.unit
class TestTokenManager:
    @patch.object(OAuth2Provider, "get_token", return_value=_mock_oauth2_response())
    def test_initializes_with_credentials(self, mock_get_token):
        tm = TokenManager(
            api_base_url="https://api.example.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="wid",
        )
        assert tm.is_token_valid() is True
        assert tm.get_raw_token() == "mock-token"
        mock_get_token.assert_called_once()

    @patch.object(OAuth2Provider, "get_token", return_value=_mock_oauth2_response())
    def test_initializes_with_initial_token(self, mock_get_token):
        tm = TokenManager(
            api_base_url="https://api.example.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="wid",
            initial_token="pre-existing-token",
        )
        assert tm.get_raw_token() == "pre-existing-token"
        # Should NOT have called OAuth2 provider since initial_token was given
        mock_get_token.assert_not_called()

    @patch.object(OAuth2Provider, "get_token", return_value=_mock_oauth2_response())
    def test_is_token_valid_returns_false_for_expired(self, mock_get_token):
        tm = TokenManager(
            api_base_url="https://api.example.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="wid",
        )
        # Force the token to be expired
        tm._token_info = TokenInfo(token="expired", expires_at=time.time() - 100)
        assert tm.is_token_valid() is False

    @patch.object(OAuth2Provider, "get_token", return_value=_mock_oauth2_response())
    def test_get_auth_headers_returns_bearer_header(self, mock_get_token):
        tm = TokenManager(
            api_base_url="https://api.example.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="wid",
        )
        headers = tm.get_auth_headers()
        assert headers["Authorization"] == "Bearer mock-token"
        assert headers["Content-Type"] == "application/json"

    @patch.object(OAuth2Provider, "get_token")
    def test_get_auth_headers_refreshes_expired_token(self, mock_get_token):
        # First call for init, second for refresh
        mock_get_token.side_effect = [
            _mock_oauth2_response("token-1"),
            _mock_oauth2_response("token-2"),
        ]
        tm = TokenManager(
            api_base_url="https://api.example.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="wid",
        )
        # Force expiration
        tm._token_info = TokenInfo(token="token-1", expires_at=time.time() - 100)
        headers = tm.get_auth_headers()
        assert headers["Authorization"] == "Bearer token-2"
        assert mock_get_token.call_count == 2

    @patch.object(OAuth2Provider, "get_token", return_value=_mock_oauth2_response())
    def test_update_token_replaces_current(self, mock_get_token):
        tm = TokenManager(
            api_base_url="https://api.example.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="wid",
        )
        tm.update_token("new-manual-token")
        assert tm.get_raw_token() == "new-manual-token"

    @patch.object(OAuth2Provider, "get_token", return_value=_mock_oauth2_response())
    def test_get_token_info_returns_token_info_object(self, mock_get_token):
        tm = TokenManager(
            api_base_url="https://api.example.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="wid",
        )
        info = tm.get_token_info()
        assert isinstance(info, TokenInfo)
        assert info.token == "mock-token"

    @patch.object(OAuth2Provider, "get_token", return_value=_mock_oauth2_response())
    def test_token_url_constructed_correctly(self, mock_get_token):
        tm = TokenManager(
            api_base_url="https://global.api.greenlake.hpe.com",
            client_id="cid",
            client_secret="csec",
            workspace_id="ws-123",
        )
        expected_url = "https://global.api.greenlake.hpe.com/authorization/v2/oauth2/ws-123/token"
        assert tm._oauth2_provider.token_url == expected_url
