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


def test_loads_shipped_vlan_id_translation_cleanly() -> None:
    """The shipped Central vlan_id translation handles bare + rich AOS 8 records."""
    translations = load_translations()
    assert "central:vlan_id" in translations
    v = translations["central:vlan_id"]
    assert v.target_platform == "central"
    assert v.target_id == "vlan_id"
    assert len(v.target_emits) == 2
    src = v.sources["aos8"]
    assert src.mapping_kind == "simple"
    # Required mapping for id
    assert src.key_mappings["vlan_id"].optional is False
    # Optional mappings for sub-properties
    assert src.key_mappings["description"].optional is True
    assert src.key_mappings["option_82"].optional is True
    assert src.key_mappings["wired_aaa_profile"].optional is True


def test_loads_shipped_role_translation_cleanly() -> None:
    """The shipped Central role translation targets MOBILITY_GW only.

    Field set is verified against the live AOS 8 source shape (parent role at
    /md/Campus/West with full Tier 1 + reauth-seconds) and the Central role
    schema's x-supportedDeviceType=Gateway annotations.
    """
    translations = load_translations()
    assert "central:role" in translations
    r = translations["central:role"]
    assert r.target_platform == "central"
    assert r.target_id == "role"
    assert len(r.target_emits) == 2
    # Gateway-only target (AP roles use a different schema)
    assert r.target_meta.device_functions == ["MOBILITY_GW"]

    src = r.sources["aos8"]
    assert src.mapping_kind == "simple"
    # Required: name (from rname)
    assert src.key_mappings["name"].optional is False
    # All sub-properties optional
    optional_keys = {
        "access_vlan_id",
        "access_vlan_name",
        "vlan_type",
        "captive_portal",
        "check_for_accounting",
        "max_sessions",
        "reauthentication_interval",
        "reauthentication_interval_seconds",
        "openflow_enable",
        "enforce_dhcp",
        "robust_age_out",
        "registration_role",
        "ip_classification",
        "dpi_classification",
        "dpi_youtube_education",
        "web_cc",
        "bw_contract_basic",
        "bw_contract_app",
        "bw_contract_appcategory",
        "bw_contract_web_category",
        "bw_contract_web_reputation",
        "bw_contract_exclude_app",
        "bw_contract_exclude_appcategory",
    }
    for key in optional_keys:
        assert src.key_mappings[key].optional is True, f"{key} should be optional"

    # Verify the single-underscore source field names that surprised me on review
    assert src.key_mappings["ip_classification"].from_ == "role_disable_ipclassify"
    assert src.key_mappings["dpi_youtube_education"].from_ == "role_enable_youtubeedu"
    # Verify the corrected naming: reg_role not registration_role on the source side
    assert src.key_mappings["registration_role"].from_ == "role__reg_role"
    assert src.key_mappings["dpi_classification"].from_ == "role__dpi_disable"
    assert src.key_mappings["web_cc"].from_ == "role__disable_webcc"

    # Verify bw-contract source paths route to all 7 Central body fields
    assert src.key_mappings["bw_contract_basic"].from_ == "role__bwc"
    assert src.key_mappings["bw_contract_app"].from_ == "role__bwc_app"
    assert src.key_mappings["bw_contract_appcategory"].from_ == "role__bwc_app"
    assert src.key_mappings["bw_contract_web_category"].from_ == "role__bwc_web"
    assert src.key_mappings["bw_contract_web_reputation"].from_ == "role__bwc_web"
    assert src.key_mappings["bw_contract_exclude_app"].from_ == "role__bwc_ex"
    assert src.key_mappings["bw_contract_exclude_appcategory"].from_ == "role__bwc_ex"

    # Confirm policies dropped: there is no key_mapping that produces a 'policies' body field
    body = next(e.body for e in r.target_emits if e.step == 1)
    assert body is not None
    assert "policies" not in body

    # role__acl still captured as the explicit deferred entry (handled by future central:policy)
    deferred_topics = " ".join(u.from_ for u in src.unmapped_fields)
    assert "role__acl" in deferred_topics


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
                    "iteration": "once",
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
                "iteration": "once",
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
                    "iteration": "once",
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
                    "iteration": "once",
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
                    "iteration": "once",
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


def test_loads_shipped_policy_translation_cleanly() -> None:
    """The shipped Central policy translation handles AOS 8 acl_sess records.

    Schema-validates: target_platform=central, target_id=policy, 2 emits,
    composite source with both acl_sess + role objects, required runtime
    values include both central_scope_id and role_attribution.
    """
    translations = load_translations()
    assert "central:policy" in translations
    p = translations["central:policy"]
    assert p.target_platform == "central"
    assert p.target_id == "policy"
    assert len(p.target_emits) == 2
    assert p.target_meta.device_functions == ["MOBILITY_GW"]
    assert "central_scope_id" in p.required_runtime_values
    assert "role_records" in p.required_runtime_values

    # Standardized template compliance: declares preprocessing, uses thin
    # per-field key_mappings, body is structurally complete (security-policy.
    # policy-rule[] supplied as a pre-computed array via {policy_rules}).
    assert p.preprocessing == ("hpe_networking_mcp.translations.preprocessing.aos8_policy.preprocess_acl_for_policy")

    src = p.sources["aos8"]
    assert src.mapping_kind == "composite"
    assert src.merge_rule is not None
    # Two source objects: acl_sess (the ACL definition) + role (for attribution lookup)
    object_names = {obj.object for obj in src.objects}
    assert object_names == {"acl_sess", "role"}

    # Required mapping for the policy name; thin transforms for rules
    assert src.key_mappings["name"].optional is False
    assert src.key_mappings["policy_rules"].transform == "direct"
    assert src.key_mappings["policy_rules"].optional is True
    assert src.key_mappings["policy_rules"].from_ == "_central_rules"

    # Body shape sanity-checks
    body = next(e.body for e in p.target_emits if e.step == 1)
    assert body is not None
    assert body["type"] == "POLICY_TYPE_SECURITY"
    # association is now a placeholder fed by the preprocessing function's
    # _association (ASSOCIATION_ROLE default; ASSOCIATION_INTERFACE for validuser).
    assert body["association"] == "{association}"
    assert body["security-policy"]["type"] == "SECURITY_POLICY_TYPE_DEFAULT"


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
