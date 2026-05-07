"""Loader tests for migration mapping JSON files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hpe_networking_mcp.migrations.loader import (
    LoaderError,
    Mapping,
    load_mappings,
)

pytestmark = pytest.mark.unit


def test_loads_shipped_named_vlan_mapping_cleanly() -> None:
    """The shipped named_vlan_v1.json must validate against the schema.

    Locks in that the canonical worked example we authored stays valid as
    the loader schema evolves. Any breaking schema change must update the
    mapping file in lockstep.
    """
    mappings = load_mappings()
    assert "named_vlan" in mappings
    nv = mappings["named_vlan"]
    assert nv.version == 1
    assert len(nv.central_emits) == 6
    assert "aos8" in nv.sources
    assert nv.sources["aos8"].mapping_kind == "composite"
    # Composite must declare merge_rule
    assert nv.sources["aos8"].merge_rule is not None
    # Steps numbered 1..6 in order
    steps = [e.step for e in sorted(nv.central_emits, key=lambda e: e.step)]
    assert steps == [1, 2, 3, 4, 5, 6]


def test_overrides_path_replaces_shipped_mapping(tmp_path: Path) -> None:
    """An overrides directory file with the same central_target_id wins."""
    # Build a minimal valid mapping with the same central_target_id
    override = {
        "version": 1,
        "central_target_id": "named_vlan",
        "central_emits": [
            {
                "step": 1,
                "name": "test_step",
                "purpose": "test",
                "endpoint": "/test",
                "method": "POST",
                "iteration": "once_per_named_vlan",
            }
        ],
        "central_target_meta": {
            "device_functions": ["MOBILITY_GW"],
            "device_function_filtering_rule": "test",
        },
        "central_scope_id_resolution": {
            "rule": "test",
            "input": "test",
            "output": "test",
        },
        "sources": {
            "aos8": {
                "kind": "rest",
                "mapping_kind": "simple",
                "objects": [{"object": "test_obj"}],
            }
        },
    }
    (tmp_path / "named_vlan_v1.json").write_text(json.dumps(override))

    mappings = load_mappings(overrides_path=tmp_path)
    nv = mappings["named_vlan"]
    # Override produced 1 emit, not the shipped 6
    assert len(nv.central_emits) == 1
    assert nv.central_emits[0].name == "test_step"


class TestSchemaValidation:
    """Pydantic-side errors should be aggregated and reported, not first-fail."""

    def test_unknown_field_at_top_level_rejected(self, tmp_path: Path) -> None:
        bad = {
            "version": 1,
            "central_target_id": "broken",
            "central_emits": [],
            "central_target_meta": {"device_functions": ["X"], "device_function_filtering_rule": "x"},
            "central_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
            "made_up_field": "boom",
        }
        (tmp_path / "broken_v1.json").write_text(json.dumps(bad))
        with pytest.raises(LoaderError) as exc_info:
            load_mappings(base_path=tmp_path, overrides_path=None)
        assert "made_up_field" in str(exc_info.value)

    def test_composite_source_without_merge_rule_rejected(self, tmp_path: Path) -> None:
        bad = {
            "version": 1,
            "central_target_id": "broken_composite",
            "central_emits": [
                {
                    "step": 1,
                    "name": "x",
                    "purpose": "x",
                    "endpoint": "/x",
                    "method": "POST",
                    "iteration": "once_per_named_vlan",
                }
            ],
            "central_target_meta": {"device_functions": ["X"], "device_function_filtering_rule": "x"},
            "central_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {
                "aos8": {
                    "kind": "rest",
                    "mapping_kind": "composite",
                    "objects": [{"object": "x"}],
                    # merge_rule deliberately missing
                }
            },
        }
        (tmp_path / "broken_composite_v1.json").write_text(json.dumps(bad))
        with pytest.raises(LoaderError) as exc_info:
            load_mappings(base_path=tmp_path, overrides_path=None)
        assert "merge_rule" in str(exc_info.value)

    def test_dangling_depends_on_step_rejected(self, tmp_path: Path) -> None:
        bad = {
            "version": 1,
            "central_target_id": "broken_deps",
            "central_emits": [
                {
                    "step": 1,
                    "name": "x",
                    "purpose": "x",
                    "endpoint": "/x",
                    "method": "POST",
                    "iteration": "once_per_named_vlan",
                    "depends_on": [99],  # no step 99 exists
                }
            ],
            "central_target_meta": {"device_functions": ["X"], "device_function_filtering_rule": "x"},
            "central_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
        }
        (tmp_path / "broken_deps_v1.json").write_text(json.dumps(bad))
        with pytest.raises(LoaderError) as exc_info:
            load_mappings(base_path=tmp_path, overrides_path=None)
        assert "depends_on=99" in str(exc_info.value)

    def test_invalid_json_reported_with_path(self, tmp_path: Path) -> None:
        (tmp_path / "broken_v1.json").write_text("{not json}")
        with pytest.raises(LoaderError) as exc_info:
            load_mappings(base_path=tmp_path, overrides_path=None)
        msg = str(exc_info.value)
        assert "broken_v1.json" in msg
        assert "invalid JSON" in msg


def test_mapping_pydantic_model_round_trip() -> None:
    """A loaded Mapping survives model_dump → model_validate cycles intact."""
    mappings = load_mappings()
    nv = mappings["named_vlan"]
    dumped = nv.model_dump(by_alias=True, exclude_none=True)
    rebuilt = Mapping.model_validate(dumped)
    # Same number of emits, same target_id, same sources keys
    assert len(rebuilt.central_emits) == len(nv.central_emits)
    assert rebuilt.central_target_id == nv.central_target_id
    assert set(rebuilt.sources.keys()) == set(nv.sources.keys())
