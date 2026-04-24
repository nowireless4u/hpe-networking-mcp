"""Regression tests for ``<platform>_invoke_tool`` dispatch shape.

The v2.0.0.0 release shipped with a latent bug in Mist: the dynamic-mode
meta-tool ``mist_invoke_tool`` passes ``ctx: Context`` positionally to the
underlying tool function, but Mist tools (ported from upstream mistmcp
using FastMCP's ``get_context()`` helper internally) didn't accept ``ctx``
as a parameter. Every Mist invocation in dynamic mode failed with
``TypeError: got multiple values for argument 'action_type'`` (or the
equivalent for whichever parameter occupied the first positional slot).

This class of bug is undetectable by the existing registry-population tests
because they never exercise the dispatch path. These tests assert the
invariant that makes ``_invoke_tool`` dispatch work: **every tool function
in every platform registry must accept ``ctx: Context`` as its first
parameter**. Fixed in v2.0.0.1.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


def _populate_all_registries() -> None:
    """Import every per-platform tool module so every registry is filled.

    Two module-naming conventions in use:
    - Apstra, Central, ClearPass, GreenLake: ``TOOLS`` keys are the module
      names (one module per category, e.g. ``tools/sites.py``).
    - Mist: ``TOOLS`` keys are category labels like ``"devices"``; the actual
      module files are named after the tools (e.g. ``tools/search_device.py``),
      derived by stripping the ``mist_`` prefix.
    """
    for platform in ("apstra", "central", "clearpass", "greenlake", "mist"):
        clear_registry(platform)

    for pkg in ("apstra", "central", "clearpass", "greenlake", "mist"):
        try:
            pkg_mod = importlib.import_module(f"hpe_networking_mcp.platforms.{pkg}")
        except ImportError:
            continue
        tools_dict = getattr(pkg_mod, "TOOLS", None)
        if not tools_dict:
            continue

        if pkg == "mist":
            # Mist: derive module names from tool names (strip ``mist_``).
            module_names = {name.removeprefix("mist_") for tool_names in tools_dict.values() for name in tool_names}
        else:
            # Other platforms: category key == module name.
            module_names = set(tools_dict.keys())

        for mod_short in sorted(module_names):
            try:
                mod = importlib.import_module(f"hpe_networking_mcp.platforms.{pkg}.tools.{mod_short}")
            except ImportError:
                continue
            importlib.reload(mod)


@pytest.fixture
def every_platform_registry_populated():
    _populate_all_registries()
    try:
        yield {p: dict(reg) for p, reg in REGISTRIES.items()}
    finally:
        for platform in REGISTRIES:
            clear_registry(platform)


@pytest.mark.unit
class TestInvokeToolDispatchShape:
    """Every registered tool must be callable via ``func(ctx, **params)``.

    This is the exact call shape emitted by ``_common/meta_tools.py::_invoke_tool``.
    If a tool's first positional parameter isn't reserved for ``ctx``, the
    meta-tool dispatch will collide — which is what caused Seth's bug.
    """

    @pytest.mark.parametrize("platform", ["apstra", "central", "clearpass", "greenlake", "mist"])
    def test_every_tool_accepts_ctx_as_first_parameter(self, every_platform_registry_populated, platform):
        from fastmcp import Context

        registry = every_platform_registry_populated.get(platform, {})
        if not registry:
            pytest.skip(f"{platform} registry empty — tool modules failed to import")

        failures: list[str] = []
        for name, spec in registry.items():
            sig = inspect.signature(spec.func)
            params = list(sig.parameters.values())
            if not params:
                failures.append(f"{name}: function has no parameters")
                continue

            first = params[0]
            if first.name not in ("ctx", "context"):
                failures.append(
                    f"{name}: first parameter is {first.name!r} (expected 'ctx' so "
                    f"{platform}_invoke_tool can pass the Context positionally)"
                )
                continue

            annotation = first.annotation
            # Accept either the exact Context class or a string annotation
            # named Context (files using ``from __future__ import annotations``
            # produce string annotations).
            if annotation is inspect.Parameter.empty:
                failures.append(f"{name}: first param 'ctx' is untyped (expected Context)")
                continue
            annotation_name = getattr(annotation, "__name__", None) or str(annotation)
            if annotation is not Context and "Context" not in annotation_name:
                failures.append(f"{name}: first param 'ctx' is typed {annotation!r} (expected Context)")

        assert not failures, (
            f"\n{len(failures)} {platform} tool(s) have the wrong dispatch shape — "
            f"this breaks {platform}_invoke_tool in dynamic mode:\n  " + "\n  ".join(failures)
        )
