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


@pytest.mark.unit
class TestMistDescriptionDisambiguation:
    """Regression coverage for issue #183 — tool descriptions that
    previously misled the AI now contain explicit scope/shape language.

    These tests assert specific strings appear in each tool's source so
    a future rewrite cannot silently drop the disambiguation.
    """

    def test_get_site_health_warns_about_org_wide_aggregate(self):
        """The cited offender — name reads as per-site list, actually returns
        org-wide aggregate. Description must call this out and point at the
        right tool for the per-site-list case.
        """
        import inspect

        from hpe_networking_mcp.platforms.mist.tools import get_site_health

        src = inspect.getsource(get_site_health)
        # Must explicitly say it's org-wide (not per-site) and point at the
        # alternative tool for per-site queries.
        assert "AGGREGATE" in src, "get_site_health description must explicitly say AGGREGATE"
        assert "NOT a per-site" in src, "get_site_health must explicitly negate the per-site reading"
        assert "mist_get_org_or_site_info" in src, (
            "get_site_health must point at mist_get_org_or_site_info for the per-site-list case"
        )

    def test_get_org_or_site_info_describes_returned_fields(self):
        import inspect

        from hpe_networking_mcp.platforms.mist.tools import get_org_or_site_info

        src = inspect.getsource(get_org_or_site_info)
        # Description should name fields the AI can rely on.
        assert "id" in src and "name" in src, (
            "get_org_or_site_info description should list at least the id/name fields it returns"
        )

    def test_get_org_sle_clarifies_org_vs_per_site_scope(self):
        """The previous description said 'all/worst sites' which read as confusingly
        ambiguous. The new description should explicitly distinguish org-wide vs.
        per-site SLE, and point at `mist_get_org_sites_sle` for the per-site case.
        """
        import inspect

        from hpe_networking_mcp.platforms.mist.tools import get_org_sle

        src = inspect.getsource(get_org_sle)
        assert "mist_get_org_sites_sle" in src, (
            "get_org_sle description must point at mist_get_org_sites_sle for the per-site case"
        )

    def test_get_constants_warns_insight_metrics_is_not_sle(self):
        """The `insight_metrics` constants set is a different vocabulary from
        SLE metrics. Description must call this out so the AI doesn't reuse
        the wrong set when looking for SLE metric names.
        """
        import inspect

        from hpe_networking_mcp.platforms.mist.tools import get_constants

        src = inspect.getsource(get_constants)
        assert "mist_list_site_sle_info" in src, (
            "get_constants description should redirect to mist_list_site_sle_info for SLE metrics"
        )


@pytest.mark.unit
class TestClearPassGuestUsersDualMode:
    """Regression for issue #183 — clearpass_get_guest_users is dual-mode
    (single record by ID/username vs. paginated list). Description must
    lead with this, not bury it.
    """

    def test_dual_mode_in_first_line(self):
        from hpe_networking_mcp.platforms.clearpass.tools.guests import clearpass_get_guest_users

        doc = clearpass_get_guest_users.__doc__ or ""
        first_line = doc.strip().split("\n")[0]
        # Must include both modes in the headline so the AI sees both
        # in summary views (search / list_tools).
        assert "single" in first_line.lower() or "OR" in first_line, (
            f"clearpass_get_guest_users docstring's first line must surface "
            f"the dual-mode behavior — got: {first_line!r}"
        )
