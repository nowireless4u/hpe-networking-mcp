"""Unit tests for hpe_networking_mcp.utils.logging — mask_secret and setup_logging."""

import pytest

from hpe_networking_mcp.utils.logging import mask_secret, setup_logging


@pytest.mark.unit
class TestMaskSecret:
    def test_masks_long_string(self):
        result = mask_secret("abcdefghijklmnop")
        assert result == "abcd...mnop"

    def test_masks_exactly_8_char_string(self):
        result = mask_secret("12345678")
        assert result == "1234...5678"

    def test_returns_stars_for_short_string(self):
        result = mask_secret("short")
        assert result == "***"

    def test_returns_stars_for_7_char_string(self):
        result = mask_secret("1234567")
        assert result == "***"

    def test_returns_stars_for_empty_string(self):
        result = mask_secret("")
        assert result == "***"

    def test_returns_stars_for_single_char(self):
        result = mask_secret("x")
        assert result == "***"

    def test_preserves_first_and_last_four(self):
        secret = "mytoken12345abcd"
        result = mask_secret(secret)
        assert result.startswith("myto")
        assert result.endswith("abcd")
        assert "..." in result


@pytest.mark.unit
class TestSetupLogging:
    def test_setup_logging_info_level(self):
        """setup_logging should not raise with INFO level."""
        setup_logging(level="INFO")

    def test_setup_logging_debug_level(self):
        """setup_logging should not raise with DEBUG level."""
        setup_logging(level="DEBUG")

    def test_setup_logging_warning_level(self):
        """setup_logging should not raise with WARNING level."""
        setup_logging(level="WARNING")

    def test_setup_logging_error_level(self):
        """setup_logging should not raise with ERROR level."""
        setup_logging(level="ERROR")

    def test_setup_logging_with_log_file(self, tmp_path):
        """setup_logging should not raise when given a log file path."""
        log_file = str(tmp_path / "test.log")
        setup_logging(level="INFO", log_file=log_file)
