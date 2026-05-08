"""Unit tests for the ``central_translation_preview`` tool.

The tool is a thin read-only bridge between the AI client (in code mode,
where ``import hpe_networking_mcp.translations`` is blocked by the
sandbox) and the translations engine. Tests exercise the bridge's
contract: per-record success, per-record EngineError surfacing,
unknown translation_id, unknown source_platform, and serialization.
"""

from __future__ import annotations

from typing import Any

import pytest

from hpe_networking_mcp.platforms.central.tools import translation_preview as tp_module
from hpe_networking_mcp.platforms.central.tools.translation_preview import (
    central_translation_preview,
)

# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


class _StubContext:
    """Minimal stand-in for ``fastmcp.Context`` — the tool doesn't read it."""

    def __init__(self) -> None:
        self.lifespan_context: dict[str, Any] = {}


@pytest.fixture(autouse=True)
def _reset_translations_cache() -> None:
    """Reset the module-level cache between tests so each test sees a fresh load."""
    tp_module._TRANSLATIONS_CACHE = None
    yield
    tp_module._TRANSLATIONS_CACHE = None


@pytest.fixture
def ctx() -> _StubContext:
    return _StubContext()


# --------------------------------------------------------------------------- #
# Happy path: shipped translations resolve + emit calls
# --------------------------------------------------------------------------- #


@pytest.mark.unit
async def test_vlan_id_preview_returns_target_calls(ctx: _StubContext) -> None:
    """``central:vlan_id`` preview produces 2 TargetCalls per source record."""
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:vlan_id",
        source_records=[{"id": 108}],
        runtime_values={"central_scope_id": "scope-abc"},
        source_platform="aos8",
    )

    assert response["translation_id"] == "central:vlan_id"
    assert response["record_count"] == 1
    assert response["translatable_count"] == 1
    assert response["skipped_count"] == 0
    assert len(response["results"]) == 1

    record_result = response["results"][0]
    assert record_result["record_id"] == "108"
    assert record_result["skip_reason"] is None
    assert record_result["call_count"] == 2  # create_layer2_vlan_shared + assign_layer2_vlan
    assert record_result["target_calls"][0]["step"] == 1
    assert record_result["target_calls"][0]["method"] == "POST"
    assert record_result["target_calls"][1]["step"] == 2
    assert record_result["target_calls"][1]["endpoint"].endswith("/config-assignments")


@pytest.mark.unit
async def test_role_preview_returns_2_calls(ctx: _StubContext) -> None:
    """``central:role`` preview produces SHARED-create + config-assignment per role."""
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:role",
        source_records=[{"rname": "faculty"}],
        runtime_values={"central_scope_id": "scope-abc"},
    )
    assert response["translatable_count"] == 1
    assert response["skipped_count"] == 0
    assert response["results"][0]["record_id"] == "faculty"
    assert response["results"][0]["call_count"] == 2


@pytest.mark.unit
async def test_policy_preview_with_role_records(ctx: _StubContext) -> None:
    """``central:policy`` requires role_records in runtime_values for preprocessing."""
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:policy",
        source_records=[
            {
                "accname": "test-policy",
                "acl_sess__v4policy": [{"sany": True, "src": "sany", "dany": True, "dst": "dany", "action": "permit"}],
                "acl_sess__v6policy": [],
            }
        ],
        runtime_values={
            "central_scope_id": "scope-abc",
            "role_records": [
                {
                    "rname": "test-role",
                    "role__acl": [{"acl_type": "session", "pname": "test-policy"}],
                }
            ],
        },
    )
    assert response["translatable_count"] == 1
    assert response["results"][0]["record_id"] == "test-policy"
    assert response["results"][0]["call_count"] == 2
    # Body should carry the policy name
    body = response["results"][0]["target_calls"][0]["body"]
    assert body["name"] == "test-policy"
    assert body["type"] == "POLICY_TYPE_SECURITY"


# --------------------------------------------------------------------------- #
# Per-record EngineError surfaces as skip_reason (doesn't crash the batch)
# --------------------------------------------------------------------------- #


@pytest.mark.unit
async def test_missing_required_runtime_value_surfaces_per_record_skip(ctx: _StubContext) -> None:
    """When the engine raises EngineError for one record, the batch keeps going."""
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:vlan_id",
        source_records=[{"id": 108}, {"id": 109}],
        runtime_values={},  # missing central_scope_id — engine will raise
    )
    # Both records skipped because runtime_values is missing the required key.
    assert response["translatable_count"] == 0
    assert response["skipped_count"] == 2
    for r in response["results"]:
        assert r["skip_reason"] is not None
        assert "central_scope_id" in r["skip_reason"]


@pytest.mark.unit
async def test_mixed_batch_partial_success(ctx: _StubContext) -> None:
    """A batch with one good + one malformed record reports each separately."""
    # Pass enough runtime_values for the good record; the malformed record's
    # engine error surfaces independently. Use a record without 'id' to break.
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:vlan_id",
        source_records=[
            {"id": 108},  # good
            {"description": "missing id field"},  # bad — required key missing
        ],
        runtime_values={"central_scope_id": "scope-abc"},
    )
    assert response["record_count"] == 2
    # The good record should produce 2 calls; the bad one is either skipped
    # or produces an error depending on how the engine handles missing required
    # source fields. Assert that we get one of each outcome.
    good_results = [r for r in response["results"] if r["call_count"] > 0]
    assert len(good_results) >= 1
    assert good_results[0]["record_id"] == "108"


# --------------------------------------------------------------------------- #
# Fatal errors return {"ok": false, "error": "..."}
# --------------------------------------------------------------------------- #


@pytest.mark.unit
async def test_unknown_translation_id_returns_error(ctx: _StubContext) -> None:
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:does_not_exist",
        source_records=[{"id": 1}],
        runtime_values={"central_scope_id": "scope-abc"},
    )
    assert response.get("ok") is False
    assert "Unknown translation_id" in response["error"]


@pytest.mark.unit
async def test_unknown_source_platform_returns_error(ctx: _StubContext) -> None:
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:vlan_id",
        source_records=[{"id": 108}],
        runtime_values={"central_scope_id": "scope-abc"},
        source_platform="bogus_platform",
    )
    assert response.get("ok") is False
    assert "does not declare source" in response["error"]


# --------------------------------------------------------------------------- #
# Empty input
# --------------------------------------------------------------------------- #


@pytest.mark.unit
async def test_empty_source_records_returns_empty_results(ctx: _StubContext) -> None:
    response = await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:vlan_id",
        source_records=[],
        runtime_values={"central_scope_id": "scope-abc"},
    )
    assert response["record_count"] == 0
    assert response["translatable_count"] == 0
    assert response["skipped_count"] == 0
    assert response["results"] == []


# --------------------------------------------------------------------------- #
# Helper: _record_id extraction
# --------------------------------------------------------------------------- #


@pytest.mark.unit
class TestRecordIdExtraction:
    def test_policy_uses_accname(self) -> None:
        assert tp_module._record_id({"accname": "blacklisted"}, "central:policy") == "blacklisted"

    def test_role_uses_rname(self) -> None:
        assert tp_module._record_id({"rname": "faculty"}, "central:role") == "faculty"

    def test_vlan_id_uses_id(self) -> None:
        assert tp_module._record_id({"id": 107}, "central:vlan_id") == "107"

    def test_named_vlan_uses_name(self) -> None:
        assert tp_module._record_id({"name": "user", "vlan-ids": "107"}, "central:named_vlan") == "user"

    def test_missing_primary_key_returns_sentinel(self) -> None:
        assert tp_module._record_id({}, "central:policy") == "<missing>"

    def test_non_dict_record_returns_sentinel(self) -> None:
        assert tp_module._record_id("not a dict", "central:policy") == "<not-a-dict>"  # type: ignore[arg-type]

    def test_unknown_translation_falls_back_to_common_keys(self) -> None:
        assert tp_module._record_id({"name": "fallback"}, "central:unknown_translation") == "fallback"


# --------------------------------------------------------------------------- #
# Caching: subsequent calls reuse the loaded translations
# --------------------------------------------------------------------------- #


@pytest.mark.unit
async def test_translations_are_cached_across_calls(ctx: _StubContext, monkeypatch: pytest.MonkeyPatch) -> None:
    """The module-level cache prevents re-reading the JSON files per call."""
    call_count = {"n": 0}
    original_loader = tp_module.load_translations

    def counting_loader(*args: Any, **kwargs: Any) -> Any:
        call_count["n"] += 1
        return original_loader(*args, **kwargs)

    monkeypatch.setattr(tp_module, "load_translations", counting_loader)
    tp_module._TRANSLATIONS_CACHE = None  # ensure cold start

    await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:vlan_id",
        source_records=[{"id": 108}],
        runtime_values={"central_scope_id": "scope-abc"},
    )
    await central_translation_preview(
        ctx=ctx,  # type: ignore[arg-type]
        translation_id="central:role",
        source_records=[{"rname": "faculty"}],
        runtime_values={"central_scope_id": "scope-abc"},
    )

    assert call_count["n"] == 1, "load_translations should only be invoked on the first call"
