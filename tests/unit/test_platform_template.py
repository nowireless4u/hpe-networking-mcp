"""Tests for the platform-template module.

The template is a real Python package that ships in source but is never
wired into ``server.py:create_server`` — so it never registers any tool
at runtime. These tests guard the template's structural conventions so
copies of the template stay in sync with the rest of the codebase. If
you change a convention in a real platform, update the template + this
test in the same PR.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestTemplateImportable:
    """The template's modules must import cleanly. Catches typos / dangling refs."""

    def test_package_importable(self):
        import hpe_networking_mcp.platforms._template  # noqa: F401

    def test_register_tools_callable(self):
        from hpe_networking_mcp.platforms._template import register_tools

        assert callable(register_tools)

    def test_tool_decorator_exposed(self):
        from hpe_networking_mcp.platforms._template._registry import tool

        assert callable(tool)

    def test_annotation_constants_exposed(self):
        from hpe_networking_mcp.platforms._template.tools import READ_ONLY, WRITE, WRITE_DELETE

        # READ_ONLY is read-only, idempotent, non-destructive.
        assert READ_ONLY.readOnlyHint is True
        assert READ_ONLY.idempotentHint is True
        assert READ_ONLY.destructiveHint is False

        # WRITE is mutating but non-destructive.
        assert WRITE.readOnlyHint is False
        assert WRITE.destructiveHint is False

        # WRITE_DELETE is mutating AND destructive.
        assert WRITE_DELETE.readOnlyHint is False
        assert WRITE_DELETE.destructiveHint is True

    def test_example_tool_modules_importable(self):
        # The example tools are reference patterns — they must at least
        # parse and import without raising. Anyone copying the template
        # will encounter their first errors here if these break.
        from hpe_networking_mcp.platforms._template.tools import example_read, example_write  # noqa: F401

    def test_client_module_importable(self):
        from hpe_networking_mcp.platforms._template.client import (
            TemplateAuthError,
            TemplateClient,
            format_http_error,
            get_template_client,
        )

        assert callable(get_template_client)
        assert callable(format_http_error)
        assert isinstance(TemplateAuthError("x"), RuntimeError)
        assert isinstance(TemplateClient, type)


@pytest.mark.unit
class TestTemplateConventions:
    """The patterns the template captures must match what every real platform follows."""

    def test_tools_dict_shape(self):
        """``TOOLS`` is a dict[str, list[str]] — same shape as every platform."""
        from hpe_networking_mcp.platforms._template import TOOLS

        assert isinstance(TOOLS, dict)
        for category, names in TOOLS.items():
            assert isinstance(category, str)
            assert isinstance(names, list)
            for name in names:
                assert isinstance(name, str)

    def test_registered_template_platform_in_registries(self):
        """Tool registry has a ``_template`` entry so example tools register cleanly."""
        from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES

        assert "_template" in REGISTRIES

    def test_template_write_tag_dict(self):
        """``_WRITE_TAG_BY_PLATFORM`` carries a ``_template`` entry.

        Without it, decorating an example write tool with ``tags={"_template_write"}``
        would silently fail to gate at runtime — same trap any new platform copy
        would hit if the gating wiring is missed.
        """
        from hpe_networking_mcp.platforms._common.tool_registry import _WRITE_TAG_BY_PLATFORM

        assert "_template" in _WRITE_TAG_BY_PLATFORM


@pytest.mark.unit
class TestTemplateNotAutoRegistered:
    """The template must NEVER appear in the live server's registration path."""

    def test_template_not_in_server_create_server(self):
        """server.py:create_server has no reference to ``_template``."""
        import inspect

        from hpe_networking_mcp import server

        source = inspect.getsource(server)
        # Excludes occurrences inside docstrings/comments — so check for
        # the import or function-call patterns specifically.
        assert "platforms._template" not in source
        assert "_register__template_tools" not in source

    def test_template_not_in_config_load_config(self):
        """config.py:load_config doesn't try to load template secrets."""
        import inspect

        from hpe_networking_mcp import config

        source = inspect.getsource(config)
        assert "_load__template" not in source
        assert "TemplateSecrets" not in source

    def test_template_not_in_health_probes(self):
        """health.py has no probe entry for the template platform."""
        from hpe_networking_mcp.platforms.health import _ALL_PLATFORMS, _PROBES

        assert "_template" not in _ALL_PLATFORMS
        assert "_template" not in _PROBES
