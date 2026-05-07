"""Loader tests for translation JSON files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hpe_networking_mcp.translations.loader import (
    LoaderError,
    Translation,
    load_translations,
)

pytestmark = pytest.mark.unit


def test_loads_shipped_named_vlan_translation_cleanly() -> None:
    """The shipped Central named-VLAN translation must validate against the schema."""
    translations = load_translations()
    assert "central:named_vlan" in translations
    nv = translations["central:named_vlan"]
    assert nv.version == 1
    assert nv.target_platform == "central"
    assert nv.target_id == "named_vlan"
    assert len(nv.target_emits) == 6
    assert "aos8" in nv.sources
    assert nv.sources["aos8"].mapping_kind == "composite"
    assert nv.sources["aos8"].merge_rule is not None
    steps = [e.step for e in sorted(nv.target_emits, key=lambda e: e.step)]
    assert steps == [1, 2, 3, 4, 5, 6]
    # required_runtime_values declared
    assert "central_scope_id" in nv.required_runtime_values


def test_loader_key_is_composite_platform_and_id(tmp_path: Path) -> None:
    """Loader key is '<target_platform>:<target_id>'; same target_id under
    different platforms doesn't collide."""
    central = tmp_path / "central"
    mist = tmp_path / "mist"
    central.mkdir()
    mist.mkdir()

    def _minimal(platform: str, target_id: str) -> dict:
        return {
            "version": 1,
            "target_platform": platform,
            "target_id": target_id,
            "target_emits": [
                {
                    "step": 1,
                    "name": "x",
                    "purpose": "x",
                    "endpoint": "/x",
                    "method": "POST",
                    "iteration": "once_per_named_vlan",
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
        }

    (central / "wlan_v1.json").write_text(json.dumps(_minimal("central", "wlan")))
    (mist / "wlan_v1.json").write_text(json.dumps(_minimal("mist", "wlan")))

    translations = load_translations(base_path=tmp_path)
    assert "central:wlan" in translations
    assert "mist:wlan" in translations
    assert translations["central:wlan"].target_platform == "central"
    assert translations["mist:wlan"].target_platform == "mist"


def test_overrides_path_replaces_shipped_translation(tmp_path: Path) -> None:
    """An overrides directory file with the same composite key wins."""
    central = tmp_path / "central"
    central.mkdir()

    override = {
        "version": 1,
        "target_platform": "central",
        "target_id": "named_vlan",
        "target_emits": [
            {
                "step": 1,
                "name": "test_step",
                "purpose": "test",
                "endpoint": "/test",
                "method": "POST",
                "iteration": "once_per_named_vlan",
            }
        ],
        "target_meta": {},
        "target_scope_id_resolution": {"rule": "test", "input": "test", "output": "test"},
        "sources": {"aos8": {"kind": "rest", "mapping_kind": "simple", "objects": [{"object": "test_obj"}]}},
    }
    (central / "named_vlan_v1.json").write_text(json.dumps(override))

    translations = load_translations(overrides_path=tmp_path)
    nv = translations["central:named_vlan"]
    # Override produced 1 emit, not the shipped 6
    assert len(nv.target_emits) == 1
    assert nv.target_emits[0].name == "test_step"


class TestSchemaValidation:
    def _platform_dir(self, tmp_path: Path) -> Path:
        d = tmp_path / "central"
        d.mkdir()
        return d

    def test_unknown_field_at_top_level_rejected(self, tmp_path: Path) -> None:
        platform_dir = self._platform_dir(tmp_path)
        bad = {
            "version": 1,
            "target_platform": "central",
            "target_id": "broken",
            "target_emits": [
                {
                    "step": 1,
                    "name": "x",
                    "purpose": "x",
                    "endpoint": "/x",
                    "method": "POST",
                    "iteration": "once_per_named_vlan",
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
            "made_up_field": "boom",
        }
        (platform_dir / "broken_v1.json").write_text(json.dumps(bad))
        with pytest.raises(LoaderError) as exc_info:
            load_translations(base_path=tmp_path, overrides_path=None)
        assert "made_up_field" in str(exc_info.value)

    def test_composite_source_without_merge_rule_rejected(self, tmp_path: Path) -> None:
        platform_dir = self._platform_dir(tmp_path)
        bad = {
            "version": 1,
            "target_platform": "central",
            "target_id": "broken_composite",
            "target_emits": [
                {
                    "step": 1,
                    "name": "x",
                    "purpose": "x",
                    "endpoint": "/x",
                    "method": "POST",
                    "iteration": "once_per_named_vlan",
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {
                "aos8": {
                    "kind": "rest",
                    "mapping_kind": "composite",
                    "objects": [{"object": "x"}],
                    # merge_rule deliberately missing
                }
            },
        }
        (platform_dir / "broken_composite_v1.json").write_text(json.dumps(bad))
        with pytest.raises(LoaderError) as exc_info:
            load_translations(base_path=tmp_path, overrides_path=None)
        assert "merge_rule" in str(exc_info.value)

    def test_dangling_depends_on_step_rejected(self, tmp_path: Path) -> None:
        platform_dir = self._platform_dir(tmp_path)
        bad = {
            "version": 1,
            "target_platform": "central",
            "target_id": "broken_deps",
            "target_emits": [
                {
                    "step": 1,
                    "name": "x",
                    "purpose": "x",
                    "endpoint": "/x",
                    "method": "POST",
                    "iteration": "once_per_named_vlan",
                    "depends_on": [99],
                }
            ],
            "target_meta": {},
            "target_scope_id_resolution": {"rule": "x", "input": "x", "output": "x"},
            "sources": {"aos8": {"kind": "rest", "objects": [{"object": "x"}]}},
        }
        (platform_dir / "broken_deps_v1.json").write_text(json.dumps(bad))
        with pytest.raises(LoaderError) as exc_info:
            load_translations(base_path=tmp_path, overrides_path=None)
        assert "depends_on=99" in str(exc_info.value)

    def test_invalid_json_reported_with_path(self, tmp_path: Path) -> None:
        platform_dir = self._platform_dir(tmp_path)
        (platform_dir / "broken_v1.json").write_text("{not json}")
        with pytest.raises(LoaderError) as exc_info:
            load_translations(base_path=tmp_path, overrides_path=None)
        msg = str(exc_info.value)
        assert "broken_v1.json" in msg
        assert "invalid JSON" in msg


def test_translation_pydantic_model_round_trip() -> None:
    """A loaded Translation survives model_dump → model_validate cycles intact."""
    translations = load_translations()
    nv = translations["central:named_vlan"]
    dumped = nv.model_dump(by_alias=True, exclude_none=True)
    rebuilt = Translation.model_validate(dumped)
    assert len(rebuilt.target_emits) == len(nv.target_emits)
    assert rebuilt.target_id == nv.target_id
    assert rebuilt.target_platform == nv.target_platform
    assert set(rebuilt.sources.keys()) == set(nv.sources.keys())
