"""Unit tests for the Axis Atmos Cloud platform (Phase 1: 12 read tools).

Validates the registry wiring, the read-tool surface, the JWT-exp decoder,
the health probe enrichment, and the disabled-tools list. Phase 2 will
add ``manage_*`` write tools and a corresponding test class.
"""

from __future__ import annotations

import importlib

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def axis_registry_populated():
    """Import every Axis tool module so ``REGISTRIES['axis']`` is full."""
    clear_registry("axis")
    from hpe_networking_mcp.platforms.axis import TOOLS

    for category in TOOLS:
        module = importlib.import_module(f"hpe_networking_mcp.platforms.axis.tools.{category}")
        importlib.reload(module)
    yield REGISTRIES["axis"]
    clear_registry("axis")


@pytest.mark.unit
class TestAxisRegistryPopulation:
    def test_axis_in_registries_dict(self):
        assert "axis" in REGISTRIES

    def test_registry_contains_all_tools(self, axis_registry_populated):
        """Every name in ``TOOLS`` registers cleanly."""
        from hpe_networking_mcp.platforms.axis import TOOLS

        expected = {name for names in TOOLS.values() for name in names}
        actual = set(axis_registry_populated.keys())
        assert actual == expected, f"missing: {expected - actual}, extra: {actual - expected}"

    def test_disabled_tools_not_registered(self, axis_registry_populated):
        """``_DISABLED_TOOLS`` entries (403 in our tenant) must not appear in the registry."""
        from hpe_networking_mcp.platforms.axis import _DISABLED_TOOLS

        disabled_names = {n for names in _DISABLED_TOOLS.values() for n in names}
        actual = set(axis_registry_populated.keys())
        assert not (disabled_names & actual), f"disabled tools leaked into registry: {disabled_names & actual}"

    def test_categories_match_module_names(self, axis_registry_populated):
        """Registry category == source module's short name (powers list_tools(category=...))."""
        for name, spec in axis_registry_populated.items():
            module_short = spec.func.__module__.rsplit(".", 1)[-1]
            assert spec.category == module_short, f"{name} category={spec.category} module={module_short}"

    def test_read_tools_carry_no_write_tag(self, axis_registry_populated):
        """``axis_get_*`` tools must not carry a write tag."""
        for name, spec in axis_registry_populated.items():
            if name.startswith("axis_get_"):
                assert not (spec.tags & {"axis_write", "axis_write_delete"}), (
                    f"{name} unexpectedly carries a write tag: {spec.tags}"
                )

    def test_write_tools_carry_write_delete_tag(self, axis_registry_populated):
        """Every ``axis_manage_*`` tool plus ``axis_commit_changes`` and
        ``axis_regenerate_connector`` must carry ``axis_write_delete`` so the
        Visibility transform + ElicitationMiddleware gate them.
        """
        write_names = {n for n in axis_registry_populated if n.startswith("axis_manage_")}
        write_names |= {"axis_commit_changes", "axis_regenerate_connector"}
        for name in write_names:
            spec = axis_registry_populated[name]
            assert "axis_write_delete" in spec.tags, (
                f"{name} missing axis_write_delete tag — write gating won't fire (tags={spec.tags})"
            )

    def test_every_write_tool_references_commit_changes(self, axis_registry_populated):
        """Axis writes stage; the commit tool applies them. Every ``axis_manage_*``
        description must name ``axis_commit_changes`` so the AI knows the follow-up.
        ``axis_regenerate_connector`` is exempt — regenerate is immediate, not staged.
        """
        for name, spec in axis_registry_populated.items():
            if name.startswith("axis_manage_"):
                assert "axis_commit_changes" in spec.description, (
                    f"{name} description must reference axis_commit_changes — got: {spec.description[:200]}"
                )

    def test_descriptions_are_populated(self, axis_registry_populated):
        for name, spec in axis_registry_populated.items():
            assert spec.description, f"{name} has empty description"

    def test_every_tool_anchored_to_axis_platform(self, axis_registry_populated):
        """Code mode's ``search(tags=["axis"])`` and ``tags()`` discovery
        surfaces depend on each tool's ``ToolSpec.platform`` being ``axis``
        (the ``_registry.tool`` shim adds the platform tag at the FastMCP
        layer using this same anchor).
        """
        for name, spec in axis_registry_populated.items():
            assert spec.platform == "axis", f"{name} platform={spec.platform} — code-mode discovery would mis-bucket it"


@pytest.mark.unit
class TestAxisModuleImports:
    """The scaffold's pieces must import cleanly. Catches typos / missing files."""

    def test_axis_package_importable(self):
        import hpe_networking_mcp.platforms.axis  # noqa: F401

    def test_registry_decorator_exposed(self):
        from hpe_networking_mcp.platforms.axis._registry import tool

        assert callable(tool)

    def test_annotation_constants_exposed(self):
        from hpe_networking_mcp.platforms.axis.tools import READ_ONLY, WRITE, WRITE_DELETE

        assert READ_ONLY.readOnlyHint is True
        assert WRITE.readOnlyHint is False
        assert WRITE_DELETE.destructiveHint is True

    def test_client_module_importable(self):
        # AxisClient + get_axis_client + format_http_error are all needed by
        # future tool modules — make sure the import surface is intact.
        from hpe_networking_mcp.platforms.axis.client import (
            AxisAuthError,
            AxisClient,
            format_http_error,
            get_axis_client,
        )

        assert callable(get_axis_client)
        assert callable(format_http_error)
        assert isinstance(AxisAuthError("x"), RuntimeError)
        # Constructor expects an AxisSecrets — don't call it here, just
        # verify it's a class.
        assert isinstance(AxisClient, type)


@pytest.mark.unit
class TestAxisConfig:
    """The config-side wiring (AxisSecrets, _load_axis, ServerConfig fields)."""

    def test_axis_secrets_dataclass(self):
        from hpe_networking_mcp.config import AxisSecrets

        s = AxisSecrets(api_token="abc")
        assert s.api_token == "abc"

    def test_server_config_has_axis_field(self):
        from hpe_networking_mcp.config import AxisSecrets, ServerConfig

        cfg = ServerConfig(axis=AxisSecrets(api_token="t"))
        assert cfg.axis is not None
        assert "axis" in cfg.enabled_platforms

    def test_server_config_has_write_flag(self):
        from hpe_networking_mcp.config import ServerConfig

        cfg = ServerConfig(enable_axis_write_tools=True)
        assert cfg.enable_axis_write_tools is True

        # Default off — matches every other platform's posture.
        cfg2 = ServerConfig()
        assert cfg2.enable_axis_write_tools is False

    def test_axis_disabled_when_token_missing(self, tmp_path, monkeypatch):
        """``_load_axis`` returns None when the secret file is absent."""
        # Point SECRETS_DIR at an empty tmp dir so no file resolves.
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        from hpe_networking_mcp.config import _load_axis

        assert _load_axis() is None

    def test_axis_loaded_when_token_present(self, tmp_path, monkeypatch):
        """``_load_axis`` returns AxisSecrets with the token contents."""
        (tmp_path / "axis_api_token").write_text("secret-token-here\n")
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        from hpe_networking_mcp.config import _load_axis

        secrets = _load_axis()
        assert secrets is not None
        assert secrets.api_token == "secret-token-here"


@pytest.mark.unit
class TestAxisHealthProbe:
    """The cross-platform health.py wiring."""

    def test_axis_in_all_platforms(self):
        from hpe_networking_mcp.platforms.health import _ALL_PLATFORMS

        assert "axis" in _ALL_PLATFORMS

    def test_axis_in_probes_dict(self):
        from hpe_networking_mcp.platforms.health import _PROBES

        assert "axis" in _PROBES
        assert callable(_PROBES["axis"])

    @pytest.mark.asyncio
    async def test_probe_returns_unavailable_when_client_missing(self):
        """If lifespan didn't initialize axis_client, the probe must report 'unavailable'.

        Mirrors the contract every other platform's probe follows.
        """
        from hpe_networking_mcp.platforms.health import _probe_axis

        class _FakeCtx:
            lifespan_context = {}

        result = await _probe_axis(_FakeCtx())
        assert result["status"] == "unavailable"
        assert "Axis is not configured" in result["message"]


@pytest.mark.unit
class TestAxisWriteTagWiring:
    """Visibility transform + is_tool_enabled depend on these dicts."""

    def test_axis_in_write_tag_map(self):
        from hpe_networking_mcp.platforms._common.tool_registry import _WRITE_TAG_BY_PLATFORM

        assert "axis" in _WRITE_TAG_BY_PLATFORM
        # When a tool carries axis_write or axis_write_delete tag, gating fires.
        assert _WRITE_TAG_BY_PLATFORM["axis"] == {"axis_write", "axis_write_delete"}

    def test_axis_in_gate_config_attr(self):
        from hpe_networking_mcp.platforms._common.tool_registry import _GATE_CONFIG_ATTR

        assert _GATE_CONFIG_ATTR.get("axis") == "enable_axis_write_tools"

    def test_elicitation_middleware_recognizes_axis_write(self):
        """``ElicitationMiddleware.on_initialize`` must read
        ``config.enable_axis_write_tools`` and call ``ctx.enable_components`` for
        the ``axis_write_delete`` tag — otherwise writes never get the
        elicitation mode set and ``confirm_write`` returns ``declined`` for
        every call. Caught in Phase 2 live-testing.

        Asserts on the middleware source — full async-init flow is too tightly
        coupled to FastMCP internals to mock cleanly.
        """
        import inspect

        from hpe_networking_mcp.middleware import elicitation

        src = inspect.getsource(elicitation.ElicitationMiddleware.on_initialize)
        assert "enable_axis_write_tools" in src, (
            "ElicitationMiddleware.on_initialize doesn't read enable_axis_write_tools"
        )
        assert "axis_write_delete" in src, (
            "ElicitationMiddleware.on_initialize doesn't enable the axis_write_delete tag"
        )


@pytest.mark.unit
class TestAxisJwtExpDecoder:
    """The JWT-exp decoder powers the startup warning + health-probe countdown."""

    def test_decode_real_shaped_jwt(self):
        """A well-formed JWT with an ``exp`` claim returns the integer timestamp."""
        import base64
        import json

        from hpe_networking_mcp.platforms.axis.client import _decode_jwt_exp

        header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256"}).encode()).rstrip(b"=").decode()
        payload = base64.urlsafe_b64encode(json.dumps({"exp": 1900000000}).encode()).rstrip(b"=").decode()
        token = f"{header}.{payload}.fake-sig"

        assert _decode_jwt_exp(token) == 1900000000

    def test_decode_returns_none_for_opaque_string(self):
        from hpe_networking_mcp.platforms.axis.client import _decode_jwt_exp

        assert _decode_jwt_exp("not-a-jwt-just-an-opaque-string") is None

    def test_decode_returns_none_when_exp_missing(self):
        import base64
        import json

        from hpe_networking_mcp.platforms.axis.client import _decode_jwt_exp

        header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256"}).encode()).rstrip(b"=").decode()
        payload = base64.urlsafe_b64encode(json.dumps({"sub": "x"}).encode()).rstrip(b"=").decode()
        token = f"{header}.{payload}.fake-sig"

        assert _decode_jwt_exp(token) is None


@pytest.mark.unit
class TestAxisHealthProbeEnrichment:
    """Health probe must surface token-expiry countdown + downgrade to degraded near expiry."""

    @pytest.mark.asyncio
    async def test_probe_reports_days_when_outside_warning_window(self):
        from hpe_networking_mcp.platforms.health import _probe_axis

        class _FakeClient:
            base_url = "https://x"
            token_expires_in_days = 100

            async def health_check(self):
                return True

        class _FakeCtx:
            lifespan_context = {"axis_client": _FakeClient()}

        result = await _probe_axis(_FakeCtx())
        assert result["status"] == "ok"
        assert result["token_expires_in_days"] == 100

    @pytest.mark.asyncio
    async def test_probe_degrades_inside_30_day_window(self):
        from hpe_networking_mcp.platforms.health import _probe_axis

        class _FakeClient:
            base_url = "https://x"
            token_expires_in_days = 7

            async def health_check(self):
                return True

        class _FakeCtx:
            lifespan_context = {"axis_client": _FakeClient()}

        result = await _probe_axis(_FakeCtx())
        assert result["status"] == "degraded"
        assert result["token_expires_in_days"] == 7
        assert "regenerate" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_probe_degrades_when_already_expired(self):
        from hpe_networking_mcp.platforms.health import _probe_axis

        class _FakeClient:
            base_url = "https://x"
            token_expires_in_days = -1

            async def health_check(self):
                return True

        class _FakeCtx:
            lifespan_context = {"axis_client": _FakeClient()}

        result = await _probe_axis(_FakeCtx())
        assert result["status"] == "degraded"
        assert "expired" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_probe_omits_days_when_undecodable(self):
        """Opaque-token case: probe still ok, just no countdown field."""
        from hpe_networking_mcp.platforms.health import _probe_axis

        class _FakeClient:
            base_url = "https://x"
            token_expires_in_days = None

            async def health_check(self):
                return True

        class _FakeCtx:
            lifespan_context = {"axis_client": _FakeClient()}

        result = await _probe_axis(_FakeCtx())
        assert result["status"] == "ok"
        assert "token_expires_in_days" not in result
