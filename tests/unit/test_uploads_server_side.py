# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Server-side upload handling — the security guarantee that raw uploaded file
content (device serials/MACs, AOS 8 PSKs / RADIUS secrets) never reaches the
model. Covers the shared ``read_uploaded_text`` util, ``aos8_parse_config``'s
server-side ``filename`` path, and serial tokenization in the GreenLake bulk-add
result envelope.
"""

from __future__ import annotations

import pathlib
from unittest.mock import MagicMock

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.utils.uploads import read_uploaded_text

pytestmark = pytest.mark.unit


def _ctx_with_provider(provider: object) -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"file_upload_provider": provider}
    return ctx


class TestReadUploadedText:
    """The shared server-side read used by every upload consumer."""

    def test_reads_content(self) -> None:
        provider = MagicMock()
        provider.on_read.return_value = {"name": "c.txt", "content": "hello world"}
        assert read_uploaded_text(_ctx_with_provider(provider), "c.txt") == "hello world"
        provider.on_read.assert_called_once()

    def test_no_provider_raises_400(self) -> None:
        with pytest.raises(ToolError) as e:
            read_uploaded_text(_ctx_with_provider(None), "c.txt")
        assert e.value.args[0]["status_code"] == 400

    def test_not_found_raises_404(self) -> None:
        provider = MagicMock()
        provider.on_read.side_effect = ValueError("File 'c.txt' not found. Available: []")
        with pytest.raises(ToolError) as e:
            read_uploaded_text(_ctx_with_provider(provider), "c.txt")
        assert e.value.args[0]["status_code"] == 404

    def test_empty_or_binary_raises_400(self) -> None:
        provider = MagicMock()
        provider.on_read.return_value = {"name": "c.bin", "content_base64": "QUJD"}  # no text content
        with pytest.raises(ToolError) as e:
            read_uploaded_text(_ctx_with_provider(provider), "c.bin")
        assert e.value.args[0]["status_code"] == 400


_AOS8_CLI = "netdestination corp\n  host 10.0.0.1\n!\n"


class TestAos8ParseConfigSource:
    """aos8_parse_config: server-side filename read keeps the raw config (PSKs,
    RADIUS secrets) out of context; cli_text still works; exactly-one source."""

    async def test_filename_reads_server_side_and_parses(self) -> None:
        from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_parse_config

        provider = MagicMock()
        provider.on_read.return_value = {"name": "cfg.txt", "content": _AOS8_CLI}
        out = await aos8_parse_config(_ctx_with_provider(provider), filename="cfg.txt")
        assert "netdst" in out
        provider.on_read.assert_called_once()  # read happened server-side

    async def test_cli_text_still_parses(self) -> None:
        from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_parse_config

        out = await aos8_parse_config(MagicMock(), cli_text=_AOS8_CLI)
        assert "netdst" in out

    async def test_no_source_raises_400(self) -> None:
        from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_parse_config

        with pytest.raises(ToolError) as e:
            await aos8_parse_config(MagicMock())
        assert e.value.args[0]["status_code"] == 400

    async def test_both_sources_raises_400(self) -> None:
        from hpe_networking_mcp.platforms.aos8.tools.differentiators import aos8_parse_config

        with pytest.raises(ToolError) as e:
            await aos8_parse_config(MagicMock(), cli_text=_AOS8_CLI, filename="cfg.txt")
        assert e.value.args[0]["status_code"] == 400


class TestEnvelopeSerialTokenization:
    """build_result_envelope must not echo raw serials into the model-visible result."""

    def _cache(self) -> dict:
        return {
            "RAWSERIAL1": {"status": "failed", "reason": "already exists"},
            "RAWSERIAL2": {
                "status": "succeeded",
                "service_status": "failed",
                "service_reason": "no subscription",
            },
        }

    def test_serials_tokenized_in_failures(self, tmp_path: pathlib.Path) -> None:
        from hpe_networking_mcp.platforms.greenlake.tools._bulk_assignment import build_result_envelope

        out = build_result_envelope(
            self._cache(), tmp_path / "x.cache.json", 0, 2, safe_serial=lambda s: f"TOK[{s[-1]}]"
        )
        blob = repr(out)
        assert "RAWSERIAL1" not in blob and "RAWSERIAL2" not in blob, "raw serial leaked into result envelope"
        assert out["failures"][0]["serial"] == "TOK[1]"
        assert out["enrichment_failures"][0]["serial"] == "TOK[2]"

    def test_default_safe_serial_never_leaks(self, tmp_path: pathlib.Path) -> None:
        from hpe_networking_mcp.platforms.greenlake.tools._bulk_assignment import build_result_envelope

        # Caller forgot to pass safe_serial → default placeholder, never the raw serial.
        out = build_result_envelope(self._cache(), tmp_path / "x.cache.json", 0, 2)
        assert out["failures"][0]["serial"] == "[serial]"
        assert "RAWSERIAL1" not in repr(out)
