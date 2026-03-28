# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""OAuth2 authentication and token management for HPE GreenLake API.

Consolidated from the original per-service auth modules (audit-logs, devices,
subscriptions, users, workspaces) which were identical.
"""

from __future__ import annotations

import time

import httpx
from loguru import logger
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class OAuth2TokenResponse(BaseModel):
    """OAuth2 token response from the GreenLake authorization endpoint."""

    access_token: str = Field(description="The access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int | None = Field(default=None, description="Token lifetime in seconds")
    scope: str | None = Field(default=None, description="Token scope")
    issued_at: float = Field(default_factory=time.time, description="Timestamp when token was issued")

    @property
    def expires_at(self) -> float | None:
        """Calculate expiration timestamp."""
        if self.expires_in is None:
            return None
        return self.issued_at + self.expires_in

    def expires_at_timestamp(self) -> float | None:
        """Get expiration timestamp (alias for expires_at property)."""
        return self.expires_at


class TokenInfo(BaseModel):
    """Tracks a single bearer token and its lifetime."""

    token: str = Field(description="The JWT token")
    expires_at: float | None = Field(default=None, description="Token expiration timestamp")
    created_at: float = Field(default_factory=time.time, description="Token creation timestamp")

    def is_expired(self, buffer_seconds: int = 300) -> bool:
        """Return *True* if the token is expired (or will expire within *buffer_seconds*)."""
        if self.expires_at is None:
            return False
        return time.time() >= (self.expires_at - buffer_seconds)

    def time_until_expiry(self) -> float | None:
        """Seconds remaining until expiry, or *None* if unknown."""
        if self.expires_at is None:
            return None
        return max(0, self.expires_at - time.time())


# ---------------------------------------------------------------------------
# OAuth2 Provider
# ---------------------------------------------------------------------------

class OAuth2Provider:
    """OAuth2 client-credentials provider for the GreenLake API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        workspace_id: str | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.workspace_id = workspace_id

        logger.info(
            "OAuth2 provider initialized",
            client_id=client_id,
            token_url=token_url,
            workspace_id=workspace_id,
        )

    def get_token(self) -> OAuth2TokenResponse:
        """Acquire an access token via the client-credentials grant.

        Raises:
            httpx.HTTPStatusError: On non-200 responses.
        """
        try:
            logger.info("Requesting access token", token_url=self.token_url)

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.token_url,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )

                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(
                        "Token request failed",
                        status_code=response.status_code,
                        error=error_msg,
                    )
                    if response.status_code >= 400:
                        response.raise_for_status()
                    else:
                        raise httpx.HTTPStatusError(
                            f"Unexpected status code {response.status_code}, expected 200",
                            request=response.request,
                            response=response,
                        )

                token_data = response.json()

            # Normalise scope — the API may return a list or a string
            scope = token_data.get("scope")
            if isinstance(scope, list):
                scope = " ".join(scope) if scope else None

            oauth_token = OAuth2TokenResponse(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=token_data.get("expires_in"),
                scope=scope,
            )

            logger.info(
                "Access token acquired successfully",
                token_type=oauth_token.token_type,
                expires_in=oauth_token.expires_in,
            )
            return oauth_token

        except Exception:
            logger.error("Failed to acquire access token", token_url=self.token_url)
            raise

    def validate_token(self, token: str) -> bool:
        """Return *True* if *token* is a non-empty string."""
        try:
            return bool(token and len(token.strip()) > 0)
        except Exception as e:
            logger.error("Token validation failed", error=str(e))
            return False


# ---------------------------------------------------------------------------
# Token Manager
# ---------------------------------------------------------------------------

class TokenManager:
    """Manages OAuth2 tokens for the GreenLake API.

    Unlike the original implementation this class accepts credentials directly
    as constructor parameters rather than pulling them from a global settings
    singleton.
    """

    def __init__(
        self,
        api_base_url: str,
        client_id: str,
        client_secret: str,
        workspace_id: str,
        initial_token: str | None = None,
    ) -> None:
        self._token_info: TokenInfo | None = None

        token_url = f"{api_base_url}/authorization/v2/oauth2/{workspace_id}/token"

        self._oauth2_provider = OAuth2Provider(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            workspace_id=workspace_id,
        )

        if initial_token:
            self._set_token(initial_token)
        else:
            self._generate_new_token()

        logger.info("Token manager initialized")

    # -- internal helpers ---------------------------------------------------

    def _set_token(self, token: str, expires_at: float | None = None) -> None:
        self._token_info = TokenInfo(token=token, expires_at=expires_at)
        logger.info("Token updated", has_expiry=self._token_info.expires_at is not None)

    def _set_token_from_oauth2_response(self, response: OAuth2TokenResponse) -> None:
        self._set_token(response.access_token, response.expires_at_timestamp())

    def _generate_new_token(self) -> None:
        if not self._oauth2_provider:
            raise RuntimeError("OAuth2 provider not configured for token generation")
        try:
            response = self._oauth2_provider.get_token()
            self._set_token_from_oauth2_response(response)
            logger.info("New token generated successfully")
        except Exception as e:
            logger.error("Failed to generate new token", error=str(e))
            raise

    def _ensure_valid_token(self) -> None:
        if not self._token_info or self._token_info.is_expired():
            if self._oauth2_provider:
                logger.info("Token expired or missing, generating new token")
                self._generate_new_token()
            else:
                raise RuntimeError("Token expired and no OAuth2 provider configured for renewal")

    # -- public API ---------------------------------------------------------

    def get_auth_headers(self) -> dict[str, str]:
        """Return authorization headers, refreshing the token if necessary."""
        self._ensure_valid_token()
        if not self._token_info:
            raise RuntimeError("No token available")
        return {
            "Authorization": f"Bearer {self._token_info.token}",
            "Content-Type": "application/json",
        }

    def update_token(self, new_token: str) -> None:
        """Manually replace the current token."""
        logger.info("Manually updating token")
        self._set_token(new_token)

    def refresh_token(self) -> None:
        """Force a token refresh via the OAuth2 provider."""
        if not self._oauth2_provider:
            raise RuntimeError("OAuth2 provider not configured for token refresh")
        logger.info("Manually refreshing token")
        self._generate_new_token()

    def is_token_valid(self) -> bool:
        """Return *True* if a non-expired token is held."""
        return self._token_info is not None and not self._token_info.is_expired()

    def get_token_info(self) -> TokenInfo | None:
        """Return the current :class:`TokenInfo`, or *None*."""
        return self._token_info

    def get_raw_token(self) -> str | None:
        """Return the raw token string, or *None*."""
        if self._token_info:
            return self._token_info.token
        return None
