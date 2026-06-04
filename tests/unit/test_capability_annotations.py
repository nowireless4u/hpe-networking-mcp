"""Unit tests for the shared capability classification + tool-decorator factory.

Covers ``_common.annotations.classify`` (the single source that derives MCP
annotations + governance tags from one capability) and the
``make_tool_decorator`` factory that every platform's ``_registry.py`` uses.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms._common.annotations import (
    REQUIRES_CONFIRMATION,
    Capability,
    classify,
)
from hpe_networking_mcp.platforms._common.tool_registry import (
    REGISTRIES,
    clear_registry,
    make_tool_decorator,
)

pytestmark = pytest.mark.unit


class TestClassify:
    def test_read_has_no_governance_tags(self):
        tc = classify(Capability.READ, platform="axis")
        assert tc.annotations.readOnlyHint is True
        assert tc.annotations.destructiveHint is False
        assert tc.capability is Capability.READ
        assert tc.tags == set()  # no enable tag, not gated

    def test_diagnostic_acts_but_is_not_gated(self):
        tc = classify(Capability.DIAGNOSTIC, platform="central")
        # Not read-only (it triggers a probe) but not destructive and not gated.
        assert tc.annotations.readOnlyHint is False
        assert tc.annotations.destructiveHint is False
        assert REQUIRES_CONFIRMATION not in tc.tags
        assert tc.tags == set()

    def test_write_is_gated_with_write_enable_tag(self):
        tc = classify(Capability.WRITE, platform="axis")
        assert tc.annotations.destructiveHint is False
        assert tc.tags == {"axis_write", REQUIRES_CONFIRMATION}

    def test_write_delete_is_gated_and_destructive(self):
        tc = classify(Capability.WRITE_DELETE, platform="axis")
        assert tc.annotations.destructiveHint is True
        assert tc.tags == {"axis_write_delete", REQUIRES_CONFIRMATION}

    def test_operational_gated_but_not_enable_gated_by_default(self):
        tc = classify(Capability.OPERATIONAL, platform="central")
        assert REQUIRES_CONFIRMATION in tc.tags
        assert not (tc.tags & {"central_write", "central_write_delete"})

    def test_operational_gated_override_off(self):
        # e.g. central_clear_alerts — operational but benign, no prompt.
        tc = classify(Capability.OPERATIONAL, platform="central", gated=False)
        assert REQUIRES_CONFIRMATION not in tc.tags

    def test_operational_enable_gated_keeps_write_flag(self):
        # e.g. axis_regenerate_connector — destructive op kept behind the flag.
        tc = classify(Capability.OPERATIONAL, platform="axis", enable_gated=True)
        assert "axis_write_delete" in tc.tags
        assert REQUIRES_CONFIRMATION in tc.tags

    def test_extra_tags_are_merged(self):
        tc = classify(Capability.READ, platform="axis", extra_tags={"foo", "bar"})
        assert {"foo", "bar"} <= tc.tags


class TestMakeToolDecorator:
    def setup_method(self):
        clear_registry("_template")

    def teardown_method(self):
        clear_registry("_template")

    def test_capability_records_spec_and_derives_tags(self):
        tool = make_tool_decorator("_template", lambda: None)

        @tool(name="t_read", capability=Capability.READ)
        async def _read():
            return 1

        spec = REGISTRIES["_template"]["t_read"]
        assert spec.capability is Capability.READ
        assert REQUIRES_CONFIRMATION not in spec.tags
        assert spec.platform == "_template"

    def test_write_delete_derives_gate_and_enable_tags(self):
        tool = make_tool_decorator("_template", lambda: None)

        @tool(name="t_del", capability=Capability.WRITE_DELETE)
        async def _del():
            return 1

        spec = REGISTRIES["_template"]["t_del"]
        assert spec.capability is Capability.WRITE_DELETE
        assert "_template_write_delete" in spec.tags
        assert REQUIRES_CONFIRMATION in spec.tags

    def test_legacy_path_without_capability(self):
        tool = make_tool_decorator("_template", lambda: None)

        @tool(name="t_legacy", tags={"_template_write_delete"})
        async def _legacy():
            return 1

        spec = REGISTRIES["_template"]["t_legacy"]
        assert spec.capability is None
        assert spec.tags == {"_template_write_delete"}
