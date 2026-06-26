"""Tests for discovery safety metadata (#527) + tags-only search guidance (#526).

``tool_safety`` (registry) computes compact safety facets; the server's
``_safety_marker`` / ``_annotate_search_safety`` surface them on brief search
rows.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import hpe_networking_mcp.server as srv
from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, tool_safety

pytestmark = pytest.mark.unit


class TestToolSafety:
    def test_read_tool(self):
        spec = SimpleNamespace(platform="central", tags=set(), capability=Capability.READ)
        assert tool_safety(spec) == {"capability": "read", "requires_confirmation": False, "write_gate": None}

    def test_write_delete_tool(self):
        spec = SimpleNamespace(
            platform="central",
            tags={"central_write_delete", "requires_confirmation"},
            capability=Capability.WRITE_DELETE,
        )
        s = tool_safety(spec)
        assert s["capability"] == "write_delete"
        assert s["requires_confirmation"] is True
        assert s["write_gate"] == "ENABLE_CENTRAL_WRITE_TOOLS"

    def test_capability_inferred_from_tags_when_unset(self):
        spec = SimpleNamespace(platform="mist", tags={"mist_write"}, capability=None)
        s = tool_safety(spec)
        assert s["capability"] == "write"
        assert s["write_gate"] == "ENABLE_MIST_WRITE_TOOLS"


class TestSearchSafetyAnnotation:
    def setup_method(self):
        self._reg = REGISTRIES.setdefault("central", {})
        self._reg["central_zzz_write_527"] = SimpleNamespace(
            platform="central",
            tags={"central_write_delete", "requires_confirmation"},
            capability=Capability.WRITE_DELETE,
        )
        self._reg["central_zzz_read_527"] = SimpleNamespace(platform="central", tags=set(), capability=Capability.READ)

    def teardown_method(self):
        self._reg.pop("central_zzz_write_527", None)
        self._reg.pop("central_zzz_read_527", None)

    def test_marker_for_write_tool(self):
        marker = srv._safety_marker("central_zzz_write_527")
        assert "write_delete" in marker and "confirm" in marker

    def test_no_marker_for_read_tool(self):
        assert srv._safety_marker("central_zzz_read_527") == ""

    def test_no_marker_for_unknown_tool(self):
        assert srv._safety_marker("not_a_real_tool_anywhere") == ""

    def test_annotate_brief_rows(self):
        text = "- central_zzz_read_527: get stuff\n- central_zzz_write_527: do stuff"
        lines = srv._annotate_search_safety(text).split("\n")
        assert lines[0] == "- central_zzz_read_527: get stuff"  # read row untouched
        assert "write_delete" in lines[1] and lines[1].rstrip().endswith("]")

    def test_annotate_is_idempotent(self):
        text = "- central_zzz_write_527: do stuff"
        once = srv._annotate_search_safety(text)
        twice = srv._annotate_search_safety(once)
        assert once == twice  # already-marked row not double-marked
