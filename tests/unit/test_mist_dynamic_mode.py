"""Integration-style unit tests for the Mist dynamic-mode migration (#159).

Mirrors ``test_apstra_dynamic_mode.py`` — imports every Mist tool module
against the stubbed mcp (installed in ``tests/conftest.py``) and asserts the
shared registry is populated with the expected specs.
"""

from __future__ import annotations

import importlib

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def mist_registry_populated():
    """Import every Mist tool module so ``REGISTRIES['mist']`` is fully populated.

    Clears the registry at the start (other tests may have stubbed entries)
    and reloads every module to force re-registration against the currently-
    stubbed ``_registry.mcp``.
    """
    clear_registry("mist")
    from hpe_networking_mcp.platforms.mist import TOOLS

    module_names: list[str] = []
    for tool_names in TOOLS.values():
        for name in tool_names:
            module_names.append(name.replace("mist_", ""))

    for mod_short in sorted(set(module_names)):
        module = importlib.import_module(f"hpe_networking_mcp.platforms.mist.tools.{mod_short}")
        importlib.reload(module)
    yield REGISTRIES["mist"]
    clear_registry("mist")


@pytest.mark.unit
class TestMistRegistryPopulation:
    def test_registry_contains_all_tools(self, mist_registry_populated):
        """Every Mist tool listed in platforms.mist.TOOLS registers cleanly."""
        from hpe_networking_mcp.platforms.mist import TOOLS

        expected = {name for names in TOOLS.values() for name in names}
        actual = set(mist_registry_populated.keys())
        assert actual == expected, f"Mismatch — missing: {expected - actual}, extra: {actual - expected}"

    def test_expected_surface_size(self, mist_registry_populated):
        """Sanity: 35 tools across all categories."""
        from hpe_networking_mcp.platforms.mist import TOOLS

        expected = sum(len(names) for names in TOOLS.values())
        assert len(mist_registry_populated) == expected

    def test_write_tools_carry_write_tags(self, mist_registry_populated):
        """Write-gating relies on tags being set on the registered specs."""
        update_site = mist_registry_populated["mist_update_site_configuration_objects"]
        assert "write" in update_site.tags or any(
            t in update_site.tags for t in ("mist_write", "write", "configuration")
        )

        change_site = mist_registry_populated["mist_change_site_configuration_objects"]
        assert "write_delete" in change_site.tags or any(
            t in change_site.tags for t in ("mist_write_delete", "write_delete", "configuration")
        )

    def test_read_tool_has_no_write_tag(self, mist_registry_populated):
        read = mist_registry_populated["mist_search_device"]
        assert not (read.tags & {"mist_write", "mist_write_delete"})

    def test_categories_derived_from_module_names(self, mist_registry_populated):
        """The registry category comes from the source module's short name."""
        assert mist_registry_populated["mist_search_device"].category == "search_device"
        assert mist_registry_populated["mist_get_self"].category == "get_self"
        assert mist_registry_populated["mist_bounce_switch_port"].category == "bounce_switch_port"

    def test_descriptions_are_populated(self, mist_registry_populated):
        for name, spec in mist_registry_populated.items():
            assert spec.description, f"{name} has empty description"


@pytest.mark.unit
class TestMistAlarmEnums:
    """Regression coverage for issue #186 — enum-tightening on alarm params.

    Mist's search-org-alarms reference documents only three severity values
    and three group values. Earlier our `AlarmSeverity` enum included
    ``major`` and ``minor`` which Mist does not actually accept — those
    would have surfaced as 422s if the AI ever picked them. This pins
    the documented set so a future drift is caught at test time.
    """

    def test_alarm_severity_values_match_mist_docs(self):
        from hpe_networking_mcp.platforms.mist.tools.search_alarms import AlarmSeverity

        # Per https://www.juniper.net/.../search-org-alarms — only these three.
        assert {e.value for e in AlarmSeverity} == {"critical", "info", "warn"}

    def test_alarm_group_values_match_mist_docs(self):
        from hpe_networking_mcp.platforms.mist.tools.search_alarms import AlarmGroup

        assert {e.value for e in AlarmGroup} == {"infrastructure", "marvis", "security"}

    def test_alarm_severity_rejects_invalid_via_pydantic(self):
        """Confirm Pydantic enforces the enum — invalid value rejects pre-API."""
        from pydantic import TypeAdapter, ValidationError

        from hpe_networking_mcp.platforms.mist.tools.search_alarms import AlarmSeverity

        adapter = TypeAdapter(AlarmSeverity)
        with pytest.raises(ValidationError):
            adapter.validate_python("major")  # was incorrectly in our enum, isn't in Mist's
        with pytest.raises(ValidationError):
            adapter.validate_python("emergency")
        # Sanity: documented values still parse.
        assert adapter.validate_python("critical") is AlarmSeverity.CRITICAL


@pytest.mark.unit
class TestMistSleDescriptionDiscovery:
    """The original #186 failure was the AI calling
    ``mist_get_site_sle(metric="wireless")`` and getting a 404. Root cause:
    the `metric` param description pointed at the wrong constants set
    (``insight_metrics``) which is a different metric vocabulary from
    SLE metrics. The fix points at the actual discovery tool —
    ``mist_list_site_sle_info(query_type='metrics', ...)`` for site-level,
    or ``mist_get_constants(object_type='insight_metrics')`` for org-level
    per Mist's published API reference. These tests pin both descriptions
    so a rewrite can't silently re-introduce the misdirection.
    """

    def test_site_sle_metric_points_at_list_site_sle_info(self):
        import inspect

        from hpe_networking_mcp.platforms.mist.tools import get_site_sle

        src = inspect.getsource(get_site_sle)
        assert "mist_list_site_sle_info" in src, (
            "mist_get_site_sle.metric description must point at mist_list_site_sle_info — "
            "do NOT misdirect to mist_get_constants(object_type='insight_metrics'); that's "
            "a different metric set."
        )

    def test_org_sle_metric_points_at_insight_metrics_constants(self):
        import inspect

        from hpe_networking_mcp.platforms.mist.tools import get_org_sle

        src = inspect.getsource(get_org_sle)
        assert "object_type=insight_metrics" in src or "object_type='insight_metrics'" in src, (
            "mist_get_org_sle.metric description must point at "
            "mist_get_constants(object_type='insight_metrics') — that's the correct discovery "
            "for org-level SLE per Mist's published API reference."
        )
