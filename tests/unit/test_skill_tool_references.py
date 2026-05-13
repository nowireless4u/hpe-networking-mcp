"""Regression test: every platform-prefixed tool name referenced in a
bundled skill (or in INSTRUCTIONS.md) must resolve to a real tool or
meta-tool registered on the server.

The original v2.3.0.0 skills were authored without this check and shipped
with 12 references to non-existent tool names — silent failures at runtime
because the AI just got "tool not found" errors and skipped those steps.
This test catches the same class of regression at CI time.

How it works:

1. Reload every platform's tool modules so each ``@mcp.tool(...)`` decorator
   re-registers against the shared ``REGISTRIES`` dict in
   ``platforms._common.tool_registry``. We use ``REGISTRIES`` rather than
   building a real FastMCP via ``create_server`` because the server route
   has test-isolation problems: tool modules are decorated at import time
   against whatever FastMCP is wired through ``_registry.py``, and once
   imported the decorators don't re-run for a fresh server in a later
   test. ``REGISTRIES`` survives across tests by design and is what the
   existing per-platform dynamic-mode tests already build on.
2. Add cross-platform tools (``health``, the aggregators, ``skills_list``,
   ``skills_load``) and the dynamic-mode meta-tool patterns (``<platform>_list_tools``
   etc.) to the catalog manually.
3. Walk skills/*.md and INSTRUCTIONS.md, extract every platform-prefixed
   identifier via regex, assert each appears in the catalog OR in
   ``_GLOBAL_ALLOWLIST`` (historical mentions, regex artifacts).
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

# A platform-prefixed identifier — broad enough to catch every form an
# author might write (`tool_name(`, `` `tool_name` ``, in tables, in code blocks).
_TOOL_REF_PATTERN = re.compile(r"\b(mist|central|greenlake|clearpass|apstra|axis|aos8)_[a-z_][a-z_0-9]+\b")

# Names that LOOK like tool references to the regex but aren't ones we want
# the test to enforce — historical mentions ("X was removed in v2.0"),
# secret names, regex artifacts (incomplete patterns inside prose).
_GLOBAL_ALLOWLIST: frozenset[str] = frozenset(
    {
        # Tools removed in v2.0; mentioned historically in INSTRUCTIONS.md
        # so the AI knows the v1.x name is gone.
        "apstra_health",
        "clearpass_test_connection",
        "greenlake_get_endpoint_schema",
        "greenlake_invoke_endpoint",
        "greenlake_list_endpoints",
        # Secret names (axis_api_token is a secret file, not a tool).
        "axis_api_token",
        "aos8_host",
        "aos8_username",
        "aos8_password",
        "aos8_port",
        # Regex artifacts: incomplete platform-prefix mentions like
        # "use the apstra_get_* family". These end with an underscore
        # but the regex eats the trailing wildcard. Add as encountered.
        "apstra_get_",
        "aos8_manage_",
        "axis_get_",
        "axis_manage_",
        "central_get_",  # `aos-migration.md` Stage 10 — "every central_manage_* has a corresponding central_get_*"
        "central_manage_",
        "clearpass_manage_",
        "mist_change_org",
        "mist_update_org",
        # v3.1.0.0 INSTRUCTIONS.md uses these as documentation prefixes
        # describing the naming convention (e.g. "GET on a collection →
        # `mist_list_<resource>`"). The trailing underscore looks like a
        # complete tool name to the regex but is actually a documented
        # prefix template.
        "mist_count_",
        "mist_create_",
        "mist_delete_",
        "mist_get_",
        "mist_list_",
        "mist_search_",
        "mist_update_",
        # v3.1.0.0 (issue #304): Mist platform migrated to spec-driven tool
        # generation. The hand-curated tool names listed here were deleted
        # in the migration; skills + INSTRUCTIONS.md still reference them
        # pending the v3.1.0.1 follow-up skill rewiring. The tools no longer
        # exist; operators are advised to use `mist_list_tools(filter=...)`
        # for discovery against the new ~1000-tool generated surface.
        "mist_bounce_switch_port",
        "mist_change_org_configuration_objects",
        "mist_change_site_configuration_objects",
        "mist_get_ap_details",
        "mist_get_configuration_object_schema",
        "mist_get_configuration_objects",
        "mist_get_constants",
        "mist_get_gateway_details",
        "mist_get_insight_metrics",
        "mist_get_next_page",
        "mist_get_org_licenses",
        "mist_get_org_or_site_info",
        "mist_get_site_health",
        "mist_get_site_rrm_info",
        "mist_get_site_sle",
        "mist_get_stats",
        "mist_get_switch_details",
        "mist_get_wlans",
        "mist_list_rogue_devices",
        "mist_list_site_sle_info",
        "mist_list_upgrades",
        "mist_search_alarms",
        "mist_search_audit_logs",
        "mist_search_client",
        "mist_search_device",
        "mist_search_device_config_history",
        "mist_search_events",
        "mist_search_guest_authorization",
        "mist_search_nac_user_macs",
        "mist_troubleshoot",
        "mist_update_org_configuration_objects",
        "mist_update_site_configuration_objects",
        # Central API gaps explicitly cited as non-existent in `aos-migration.md`
        # Stage 8.1 — listed by name so operators know which tools they would
        # otherwise expect to find. The skill emits `[Central API gap — manual UI]`
        # placeholders for these. Adding here so the regex enforcer doesn't
        # mistake the deliberate "this tool does not exist" mention for a typo.
        "central_manage_ap_system_profile",
        "central_manage_server",
        "central_manage_server_group",
        # `aos-migration.md` Stage 9b uses these as runtime_value keys / variable
        # names inside the engine-driven preview snippets — NOT tools. The regex
        # picks them up because they look like `central_<word>` but they're
        # parameter names in `runtime_values={"central_scope_id": ...}` and a
        # local variable iterating Stage 7 mappings (`central_scope_name`).
        "central_scope_id",
        "central_scope_name",
    }
)

# Cross-platform tools that aren't in REGISTRIES (which is per-platform-keyed).
# Hardcoded because they're a small, stable set; if more get added, update here.
_CROSS_PLATFORM_TOOLS: frozenset[str] = frozenset(
    {
        "health",
        "site_health_check",
        "site_rf_check",
        "manage_wlan_profile",
        "skills_list",
        "skills_load",
    }
)


def _build_full_catalog() -> set[str]:
    """Construct the canonical set of valid tool names.

    Per-platform tool modules call ``record_tool(...)`` at import time,
    populating the shared ``REGISTRIES`` dict. Once a module has been
    imported, however, Python caches it and the registration code won't
    re-fire — so test orderings that clear ``REGISTRIES`` mid-suite
    (e.g. ``test_clearpass_dynamic_mode.py``'s teardown) leave us with
    empty registries and no way to refill them.

    To work around this, we reload every cached
    ``hpe_networking_mcp.platforms.*.tools.*`` module before reading
    ``REGISTRIES``. ``importlib.reload`` re-runs the module body, which
    re-fires the ``@tool(...)`` decorators and re-records each spec.
    Mirrors the pattern used by every per-platform dynamic-mode test.
    """
    import contextlib

    # First, ensure every platform's tool modules are imported at all.
    import pkgutil
    import sys

    from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES

    for platform in ("mist", "central", "clearpass", "apstra", "axis", "greenlake", "aos8"):
        platform_pkg = importlib.import_module(f"hpe_networking_mcp.platforms.{platform}")
        tools_attr = getattr(platform_pkg, "TOOLS", None)
        if tools_attr:
            for category, tool_names in tools_attr.items():
                # Two file-layout conventions across platforms:
                #   - one file per category (e.g. central/tools/sites.py)
                #   - one file per tool, with platform prefix stripped
                #     (Mist convention before v3.1.0.0: tools/search_device.py for mist_search_device)
                module_paths_to_try = [f"hpe_networking_mcp.platforms.{platform}.tools.{category}"]
                if isinstance(tool_names, list):
                    for tool_name in tool_names:
                        stripped = tool_name.removeprefix(f"{platform}_")
                        module_paths_to_try.append(f"hpe_networking_mcp.platforms.{platform}.tools.{stripped}")
                for path in module_paths_to_try:
                    try:
                        importlib.import_module(path)
                    except ModuleNotFoundError:
                        continue
        else:
            # Platform doesn't expose a TOOLS dict (v3.1.0.0 Mist is spec-driven
            # and auto-discovers via pkgutil). Walk the tools/ subpackage
            # directly so every generated module gets imported and the
            # @_mcp_tool decorators populate REGISTRIES.
            try:
                tools_pkg = importlib.import_module(f"hpe_networking_mcp.platforms.{platform}.tools")
            except ModuleNotFoundError:
                continue
            for _finder, modname, _ispkg in pkgutil.iter_modules(tools_pkg.__path__):
                if modname.startswith("_"):
                    continue
                with contextlib.suppress(ModuleNotFoundError, ImportError):
                    importlib.import_module(f"hpe_networking_mcp.platforms.{platform}.tools.{modname}")

    # Now reload every cached tools module so the decorators re-fire and
    # repopulate REGISTRIES. (The first import on a fresh interpreter
    # would have populated it; this handles the cleared-mid-suite case.)
    tool_module_prefixes = tuple(
        f"hpe_networking_mcp.platforms.{p}.tools."
        for p in ("mist", "central", "clearpass", "apstra", "axis", "greenlake", "aos8")
    )
    for name in list(sys.modules):
        if name.startswith(tool_module_prefixes):
            with contextlib.suppress(Exception):
                importlib.reload(sys.modules[name])

    catalog: set[str] = set()
    for _platform_name, registry in REGISTRIES.items():
        catalog.update(registry.keys())

    # Cross-platform always-visible tools (not in REGISTRIES).
    catalog.update(_CROSS_PLATFORM_TOOLS)

    # Dynamic-mode meta-tools — only registered when tool_mode="dynamic", but
    # legitimate names skills can reference for runtime dispatch.
    for platform in ("mist", "central", "greenlake", "clearpass", "apstra", "axis", "aos8"):
        for suffix in ("_list_tools", "_get_tool_schema", "_invoke_tool"):
            catalog.add(platform + suffix)

    return catalog


def _missing_refs(file_path: Path, catalog: set[str]) -> list[str]:
    """Return names referenced in the file that don't resolve — excluding
    the global allowlist.
    """
    text = file_path.read_text(encoding="utf-8")
    refs = {match.group(0) for match in _TOOL_REF_PATTERN.finditer(text)}
    return sorted(n for n in refs if n not in catalog and n not in _GLOBAL_ALLOWLIST)


@pytest.fixture(scope="module")
def catalog() -> set[str]:
    return _build_full_catalog()


@pytest.mark.unit
class TestSkillToolReferences:
    """Bundled skills must only reference tool names that exist."""

    @pytest.mark.parametrize(
        "skill_path",
        sorted(p for p in Path("src/hpe_networking_mcp/skills").glob("*.md") if p.name != "TEMPLATE.md"),
        ids=lambda p: p.name,
    )
    def test_skill_references_resolve(self, skill_path: Path, catalog: set[str]):
        missing = _missing_refs(skill_path, catalog)
        assert not missing, (
            f"Skill {skill_path.name!r} references non-existent tools: {missing}. "
            "Either fix the names to match real tools, or — if the reference is "
            "intentional (historical mention, etc.) — add it to _GLOBAL_ALLOWLIST "
            "in tests/unit/test_skill_tool_references.py."
        )


@pytest.mark.unit
class TestInstructionsToolReferences:
    """INSTRUCTIONS.md is also runtime guidance for the AI — same hygiene applies."""

    def test_instructions_references_resolve(self, catalog: set[str]):
        path = Path("src/hpe_networking_mcp/INSTRUCTIONS.md")
        missing = _missing_refs(path, catalog)
        assert not missing, (
            f"INSTRUCTIONS.md references non-existent tools: {missing}. Either fix or add to _GLOBAL_ALLOWLIST."
        )
