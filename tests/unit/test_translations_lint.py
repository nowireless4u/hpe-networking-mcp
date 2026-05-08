"""Tests for the translations lint module.

Two layers of coverage:

1. **Shipped translations pass every rule** — the smoke test that
   guarantees the standard template stays enforced as new translations
   are authored.
2. **Per-rule synthetic violations** — each rule fires on a synthetic
   input that breaks just that rule, so the rule actually catches its
   target anti-pattern (not just a no-op).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from hpe_networking_mcp.translations import lint
from hpe_networking_mcp.translations.loader import Translation, load_translations

# --------------------------------------------------------------------------- #
# Smoke test: shipped translations pass every rule
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_shipped_translations_pass_all_rules() -> None:
    """Every rule returns no violations against the shipped translations.

    This is the lint's primary value: it locks in the template across
    new translations. If a future translation drifts from the standard,
    this test fails until either the translation is fixed or the
    template is intentionally evolved (and the lint rule updated).
    """
    results = lint.run_all_rules()
    failures = {rule: msgs for rule, msgs in results.items() if msgs}
    assert failures == {}, f"Shipped translations failed lint: {failures}"


@pytest.mark.unit
def test_run_all_rules_returns_one_entry_per_rule() -> None:
    """Smoke check: every registered rule appears in run_all_rules output."""
    results = lint.run_all_rules()
    assert set(results.keys()) == set(lint._RULE_REGISTRY.keys())


# --------------------------------------------------------------------------- #
# Per-rule synthetic-violation tests
# --------------------------------------------------------------------------- #


# ---- check_no_fat_transforms ---- #


@pytest.mark.unit
def test_check_no_fat_transforms_passes_for_real_registry() -> None:
    """All current transforms are below the line threshold."""
    violations = lint.check_no_fat_transforms()
    assert violations == [], f"Some shipped transforms exceeded the limit: {violations}"


def _fat_fixture_transform(value: Any) -> Any:
    """Synthetic transform whose body length intentionally exceeds the threshold.

    The lint rule counts physical source lines including blanks + comments,
    so we pad the body with enough trivial lines to clear the limit. Used
    by ``test_check_no_fat_transforms_catches_oversize``.
    """
    # 1
    # 2
    # 3
    # 4
    # 5
    # 6
    # 7
    # 8
    # 9
    # 10
    # 11
    # 12
    # 13
    # 14
    # 15
    # 16
    # 17
    # 18
    # 19
    # 20
    # 21
    # 22
    # 23
    # 24
    # 25
    # 26
    # 27
    # 28
    # 29
    # 30
    # 31
    # 32
    # 33
    # 34
    # 35
    # 36
    # 37
    # 38
    # 39
    # 40
    # 41
    # 42
    # 43
    # 44
    # 45
    # 46
    # 47
    # 48
    # 49
    # 50
    # 51
    # 52
    return value


@pytest.mark.unit
def test_check_no_fat_transforms_catches_oversize(monkeypatch: pytest.MonkeyPatch) -> None:
    """Adding a fat transform to the registry surfaces a clear violation."""
    from hpe_networking_mcp.translations import transforms as transforms_module

    patched = dict(transforms_module._REGISTRY)
    patched["fat_fixture_transform"] = _fat_fixture_transform
    monkeypatch.setattr(transforms_module, "_REGISTRY", patched)

    violations = lint.check_no_fat_transforms()
    assert any("fat_fixture_transform" in msg for msg in violations), violations


# ---- check_body_or_body_template ---- #


def _make_minimal_translation(**emit_overrides: Any) -> Translation:
    """Build a minimal valid Translation, then patch in emit overrides for testing."""
    base: dict[str, Any] = {
        "version": 1,
        "target_platform": "central",
        "target_id": "_lint_fixture",
        "target_emits": [
            {
                "step": 1,
                "name": "create_thing",
                "purpose": "Create the thing.",
                "endpoint": "/v1/things/{name}",
                "method": "POST",
                "query_params": {},
                "body": {"name": "{name}"},
                "iteration": "once",
                "depends_on": [],
            }
        ],
        "target_meta": {"device_functions": ["MOBILITY_GW"]},
        "target_scope_id_resolution": {"rule": "x", "input": "y", "output": "z"},
        "required_runtime_values": [],
        "sources": {
            "aos8": {
                "kind": "rest",
                "mapping_kind": "simple",
                "objects": [{"object": "thing"}],
                "key_mappings": {
                    "name": {"from": "name", "to": "name", "transform": "direct_str"},
                },
            }
        },
    }
    base["target_emits"][0].update(emit_overrides)
    return Translation.model_validate(base)


@pytest.mark.unit
def test_check_body_or_body_template_passes_with_only_body() -> None:
    t = _make_minimal_translation()
    violations = lint.check_body_or_body_template({"central:_lint_fixture": t})
    assert violations == []


@pytest.mark.unit
def test_check_body_or_body_template_catches_both_set() -> None:
    t = _make_minimal_translation(
        body={"name": "{name}"},
        body_template={"config-assignment": ["{stuff}"]},
    )
    violations = lint.check_body_or_body_template({"central:_lint_fixture": t})
    assert any("declares BOTH body and body_template" in msg for msg in violations)


@pytest.mark.unit
def test_check_body_or_body_template_catches_neither_on_post() -> None:
    t = _make_minimal_translation(body=None, body_template=None, method="POST")
    violations = lint.check_body_or_body_template({"central:_lint_fixture": t})
    assert any("has neither body nor body_template" in msg for msg in violations)


@pytest.mark.unit
def test_check_body_or_body_template_allows_get_with_neither() -> None:
    t = _make_minimal_translation(body=None, body_template=None, method="GET")
    violations = lint.check_body_or_body_template({"central:_lint_fixture": t})
    assert violations == []


# ---- check_required_runtime_values_referenced ---- #


@pytest.mark.unit
def test_check_required_runtime_values_referenced_passes_when_referenced() -> None:
    t = _make_minimal_translation()
    raw = json.loads(t.model_dump_json(by_alias=True))
    raw["required_runtime_values"] = ["central_scope_id"]
    raw["target_emits"][0]["body"] = {"scope-id": "{central_scope_id}"}
    rebuilt = Translation.model_validate(raw)
    violations = lint.check_required_runtime_values_referenced({"central:_lint_fixture": rebuilt})
    assert violations == []


@pytest.mark.unit
def test_check_required_runtime_values_referenced_catches_unreferenced() -> None:
    raw: dict[str, Any] = {
        "version": 1,
        "target_platform": "central",
        "target_id": "_lint_fixture_unref",
        "target_emits": [
            {
                "step": 1,
                "name": "create_thing",
                "purpose": "create",
                "endpoint": "/v1/things",
                "method": "POST",
                "query_params": {},
                "body": {"name": "{name}"},
                "iteration": "once",
                "depends_on": [],
            }
        ],
        "target_meta": {"device_functions": ["MOBILITY_GW"]},
        "target_scope_id_resolution": {"rule": "x", "input": "y", "output": "z"},
        "required_runtime_values": ["dangling_key_no_one_uses"],
        "sources": {
            "aos8": {
                "kind": "rest",
                "mapping_kind": "simple",
                "objects": [{"object": "thing"}],
                "key_mappings": {"name": {"from": "name", "to": "name", "transform": "direct_str"}},
            }
        },
    }
    t = Translation.model_validate(raw)
    violations = lint.check_required_runtime_values_referenced({"central:_lint_fixture_unref": t})
    assert any("dangling_key_no_one_uses" in msg for msg in violations)


# ---- check_preprocessing_path_resolves ---- #


@pytest.mark.unit
def test_check_preprocessing_path_resolves_passes_for_shipped() -> None:
    """The shipped central:policy preprocessing path resolves cleanly."""
    translations = load_translations()
    violations = lint.check_preprocessing_path_resolves(translations)
    assert violations == []


@pytest.mark.unit
def test_check_preprocessing_path_resolves_catches_bad_path() -> None:
    raw = json.loads(_make_minimal_translation().model_dump_json(by_alias=True))
    raw["preprocessing"] = "totally.fake.module.does_not_exist"
    t = Translation.model_validate(raw)
    violations = lint.check_preprocessing_path_resolves({"central:_lint_fixture": t})
    assert any("couldn't import module" in msg for msg in violations)


@pytest.mark.unit
def test_check_preprocessing_path_resolves_catches_non_dotted() -> None:
    raw = json.loads(_make_minimal_translation().model_dump_json(by_alias=True))
    raw["preprocessing"] = "no_dots_here"
    t = Translation.model_validate(raw)
    violations = lint.check_preprocessing_path_resolves({"central:_lint_fixture": t})
    assert any("isn't a dotted import path" in msg for msg in violations)


@pytest.mark.unit
def test_check_preprocessing_path_resolves_catches_wrong_signature() -> None:
    """A preprocessing function with the wrong arity surfaces a violation."""
    raw = json.loads(_make_minimal_translation().model_dump_json(by_alias=True))
    raw["preprocessing"] = "json.loads"  # one positional arg only
    t = Translation.model_validate(raw)
    violations = lint.check_preprocessing_path_resolves({"central:_lint_fixture": t})
    assert any("positional parameters" in msg for msg in violations)


# ---- CLI ---- #


@pytest.mark.unit
def test_main_returns_zero_when_clean(capsys: pytest.CaptureFixture[str]) -> None:
    rc = lint._main([])
    assert rc == 0
    captured = capsys.readouterr()
    assert "all rules passed" in captured.err


@pytest.mark.unit
def test_main_returns_nonzero_when_dirty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force a violation and verify the CLI surfaces it with non-zero exit."""

    def _fake_run() -> dict[str, list[str]]:
        return {"check_no_fat_transforms": ["synthetic violation message"]}

    monkeypatch.setattr(lint, "run_all_rules", _fake_run)
    rc = lint._main([])
    assert rc == 1
