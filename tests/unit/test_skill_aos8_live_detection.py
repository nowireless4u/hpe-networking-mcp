"""Phase 10 regression test: the 9 AOS8 tools the aos-migration skill
calls for DETECT-01 + COLLECT-01..04 must be registered in the live
tool catalog. Belt-and-suspenders alongside the regex enforcement in
test_skill_tool_references.py — if either guard catches a typo, CI fails.

(Skill was renamed from aos-migration-readiness → aos-migration in v2.5.0.0
when Act II / config translation stages 7-10 were added; the AOS8 live
detection requirements are unchanged.)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit.test_skill_tool_references import _build_full_catalog

# The 9 AOS8 tools required by Phase 10 (DETECT-01 + COLLECT-01..04).
# Sources verified in 10-RESEARCH.md against @mcp.tool(name=...) decorators:
#   aos8_get_md_hierarchy       differentiators.py:49
#   aos8_get_effective_config   differentiators.py:72
#   aos8_get_cluster_state      differentiators.py:157
#   aos8_get_ap_wired_ports     differentiators.py:201
#   aos8_get_ap_database        health.py:46
#   aos8_get_active_aps         health.py:66
#   aos8_get_bss_table          health.py:117
#   aos8_get_clients            clients.py:31
#   aos8_show_command           troubleshooting.py:82
REQUIRED_AOS8_TOOLS = (
    "aos8_get_md_hierarchy",
    "aos8_get_effective_config",
    "aos8_get_ap_database",
    "aos8_get_cluster_state",
    "aos8_show_command",
    "aos8_get_clients",
    "aos8_get_bss_table",
    "aos8_get_active_aps",
    "aos8_get_ap_wired_ports",
)

SKILL_PATH = Path("src/hpe_networking_mcp/skills/aos-migration.md")


@pytest.fixture(scope="module")
def catalog() -> set[str]:
    return _build_full_catalog()


@pytest.mark.unit
class TestAOS8LiveDetectionTools:
    """Every AOS8 tool referenced by Phase 10 must exist in the live catalog."""

    @pytest.mark.parametrize("tool_name", REQUIRED_AOS8_TOOLS)
    def test_tool_registered_in_catalog(self, tool_name: str, catalog: set[str]) -> None:
        assert tool_name in catalog, (
            f"AOS8 tool {tool_name!r} required by Phase 10 (DETECT-01 / COLLECT-01..04) "
            f"is not registered in the live catalog. Verify the @mcp.tool(name=...) "
            f"decorator in src/hpe_networking_mcp/platforms/aos8/tools/."
        )

    def test_skill_file_exists(self) -> None:
        assert SKILL_PATH.is_file(), f"aos-migration skill file missing at {SKILL_PATH}"
