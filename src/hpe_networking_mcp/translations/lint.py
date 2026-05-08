"""Lint rules for translation JSONs and the transforms registry.

Every shipped translation must follow the standard template documented in
``translations/AUTHORING.md``. This module implements the rules and ships a
CLI entry point so they can be enforced in CI:

    python -m hpe_networking_mcp.translations.lint

Returns a non-zero exit code on any rule violation; rule output goes to
stderr. The same rule functions are exercised by
``tests/unit/test_translations_lint.py`` (which runs them on the shipped
translations + per-rule synthetic-violation tests).

Rule design notes:

* Rules operate on validated ``Translation`` objects (post-pydantic) so
  the rule code can ignore JSON-shape edge cases and focus on the
  template invariants.
* Rules return a list of human-readable messages; an empty list means
  the rule passed. Each rule is independently testable.
* ``run_all_rules`` runs every rule and returns the aggregated message
  list keyed by rule name.

The rule set deliberately excludes things the loader already enforces
(``ConfigDict(extra="forbid")``, step references valid steps, composite
sources have a merge_rule, etc.) — adding lint duplicates would be noise.
"""

from __future__ import annotations

import importlib
import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from hpe_networking_mcp.translations.loader import Translation, load_translations

# Maximum number of source lines (post-decorator) for a transform body
# before it counts as "fat". 50 is the threshold the AUTHORING guide
# documents and the user requested. Counts physical lines including
# blanks + comments — a generous proxy for cognitive complexity.
_MAX_TRANSFORM_LINES = 50


# --------------------------------------------------------------------------- #
# Rule: transforms must stay small
# --------------------------------------------------------------------------- #


def check_no_fat_transforms() -> list[str]:
    """Every entry in the transforms registry has a body < 50 lines.

    Composite logic (multi-step, source-wide access, fan-out) belongs in
    a preprocessing module, not in a transform.

    The rule sources the registry directly from ``transforms._REGISTRY``
    so any transform that ships is checked. New transforms added to the
    registry are automatically picked up.
    """
    from hpe_networking_mcp.translations import transforms as transforms_module

    violations: list[str] = []
    for name, fn in transforms_module._REGISTRY.items():
        try:
            source = inspect.getsource(fn)
        except (OSError, TypeError):
            # Builtin / C-extension — skip rather than error out.
            continue
        line_count = len(source.splitlines())
        if line_count > _MAX_TRANSFORM_LINES:
            violations.append(
                f"transform {name!r} has {line_count} source lines "
                f"(> {_MAX_TRANSFORM_LINES}). Move the work into a preprocessing "
                f"module under translations/preprocessing/ and use a thin "
                f"transform here."
            )
    return violations


# --------------------------------------------------------------------------- #
# Rule: each emit declares exactly one of body / body_template
# --------------------------------------------------------------------------- #


def check_body_or_body_template(translations: dict[str, Translation]) -> list[str]:
    """Each emit has exactly one of ``body`` or ``body_template``, never both.

    The two are mutually exclusive — ``body`` is direct substitution,
    ``body_template`` is a free-form descriptor the engine renders via
    pattern recognition. Mixing them is ambiguous and the engine doesn't
    define behavior for it.
    """
    violations: list[str] = []
    for key, t in translations.items():
        for emit in t.target_emits:
            has_body = emit.body is not None
            has_template = emit.body_template is not None
            if has_body and has_template:
                violations.append(
                    f"{key} emit {emit.name!r} declares BOTH body and body_template; "
                    f"pick one (body for direct substitution, body_template for the "
                    f"config-assignments pattern)."
                )
            elif not has_body and not has_template and emit.method in ("POST", "PUT", "PATCH"):
                # GET / DELETE may legitimately have neither, but POST/PUT/PATCH need a body.
                violations.append(
                    f"{key} emit {emit.name!r} method={emit.method} has neither "
                    f"body nor body_template; one is required for write methods."
                )
    return violations


# --------------------------------------------------------------------------- #
# Rule: required_runtime_values must be referenced somewhere
# --------------------------------------------------------------------------- #


def check_required_runtime_values_referenced(translations: dict[str, Translation]) -> list[str]:
    """Every key in ``required_runtime_values`` is referenced somewhere in the JSON.

    A required runtime value that's never used is documentation drift —
    the key won't actually do anything if the consumer supplies it.
    Unreferenced keys are usually leftover after a refactor.

    We look for the key:
    * As a ``{placeholder}`` in any body / body_template / query_params /
      endpoint string.
    * As an explicit ``runtime_values["..."]`` reference in the
      preprocessing module's source.
    * In merge_rule descriptions / draft_notes (loose match — narrative
      references count as proof the key is intentionally documented).
    """
    violations: list[str] = []
    for key, t in translations.items():
        if not t.required_runtime_values:
            continue
        haystack = _translation_to_text(t)
        preprocessing_source = _preprocessing_source_or_empty(t)
        full_haystack = haystack + "\n" + preprocessing_source
        for runtime_key in t.required_runtime_values:
            patterns = (
                f"{{{runtime_key}}}",  # placeholder
                f"'{runtime_key}'",  # python string literal
                f'"{runtime_key}"',  # python / json string literal
                f"[{runtime_key}]",  # bare reference (rare, but safe)
            )
            if not any(p in full_haystack for p in patterns):
                violations.append(
                    f"{key} required_runtime_values={runtime_key!r} is never "
                    f"referenced (not as a placeholder, not in preprocessing module, "
                    f"not in narrative). Either use it or remove it."
                )
    return violations


def _translation_to_text(translation: Translation) -> str:
    """Serialize a translation to a flat string for keyword search.

    Excludes ``required_runtime_values`` itself from the haystack — otherwise
    every required value is "found" in its own declaration list, which
    defeats the rule's purpose of catching unreferenced keys.
    """
    import json as _json

    data = translation.model_dump(by_alias=True, exclude={"required_runtime_values"})
    return _json.dumps(data)


def _preprocessing_source_or_empty(translation: Translation) -> str:
    """Return the source of the translation's preprocessing function, or ''."""
    if not translation.preprocessing:
        return ""
    module_path, _, _ = translation.preprocessing.rpartition(".")
    if not module_path:
        return ""
    try:
        module = importlib.import_module(module_path)
        return inspect.getsource(module)
    except (ImportError, OSError, TypeError):
        return ""


# --------------------------------------------------------------------------- #
# Rule: preprocessing path resolves to a callable with the right signature
# --------------------------------------------------------------------------- #


def check_preprocessing_path_resolves(translations: dict[str, Translation]) -> list[str]:
    """When ``preprocessing`` is set, the dotted import path resolves to a callable
    with signature ``(source_data, runtime_values) -> dict``.

    The engine validates this at call time, but enforcing it here means a
    typo / rename failure surfaces at lint time (or test time) rather
    than only when a downstream skill actually invokes ``emit_calls``.
    """
    violations: list[str] = []
    for key, t in translations.items():
        if not t.preprocessing:
            continue
        path = t.preprocessing
        if "." not in path:
            violations.append(
                f"{key} preprocessing={path!r} isn't a dotted import path (expected 'module.path.func_name')."
            )
            continue
        module_path, func_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            violations.append(f"{key} preprocessing={path!r} couldn't import module {module_path!r}: {exc}")
            continue
        fn = getattr(module, func_name, None)
        if fn is None or not callable(fn):
            violations.append(f"{key} preprocessing={path!r} resolved to {fn!r} (not a callable).")
            continue
        try:
            sig = inspect.signature(fn)
        except (ValueError, TypeError):
            continue
        positional = [
            p
            for p in sig.parameters.values()
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        if len(positional) != 2:
            violations.append(
                f"{key} preprocessing {path!r} signature has {len(positional)} "
                f"positional parameters (expected 2 — source_data, runtime_values)."
            )
    return violations


# --------------------------------------------------------------------------- #
# Rule aggregator + CLI
# --------------------------------------------------------------------------- #


_RULE_REGISTRY: dict[str, Callable[..., list[str]]] = {
    "check_no_fat_transforms": check_no_fat_transforms,
    "check_body_or_body_template": check_body_or_body_template,
    "check_required_runtime_values_referenced": check_required_runtime_values_referenced,
    "check_preprocessing_path_resolves": check_preprocessing_path_resolves,
}


def run_all_rules(translations: dict[str, Translation] | None = None) -> dict[str, list[str]]:
    """Run every lint rule and return ``{rule_name: violations}``.

    Args:
        translations: Pre-loaded translations. Defaults to the shipped set.

    Returns:
        Dict mapping rule name to list of violation messages. A rule with
        an empty list means it passed.
    """
    if translations is None:
        translations = load_translations()
    results: dict[str, list[str]] = {}
    for rule_name, fn in _RULE_REGISTRY.items():
        if _rule_takes_translations(fn):
            results[rule_name] = fn(translations)
        else:
            results[rule_name] = fn()
    return results


def _rule_takes_translations(fn: Callable[..., Any]) -> bool:
    """True when the rule accepts a ``translations`` argument."""
    try:
        sig = inspect.signature(fn)
    except (ValueError, TypeError):
        return False
    return len(sig.parameters) >= 1


def _main(argv: list[str] | None = None) -> int:
    """CLI entry point — exits non-zero on any violation."""
    _ = argv  # reserved for future flags (e.g. --rules, --json)
    results = run_all_rules()
    total = sum(len(v) for v in results.values())
    if total == 0:
        print("translations lint: all rules passed", file=sys.stderr)
        return 0
    rule_count = sum(1 for v in results.values() if v)
    print(f"translations lint: {total} violations across {rule_count} rules", file=sys.stderr)
    for rule_name, violations in results.items():
        if not violations:
            continue
        print(f"\n[{rule_name}]", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))


# --------------------------------------------------------------------------- #
# Test helpers
# --------------------------------------------------------------------------- #


def _load_from_path(path: Path) -> dict[str, Translation]:
    """Helper for tests — load translations from a specific path."""
    return load_translations(base_path=path)
