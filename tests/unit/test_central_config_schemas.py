"""Unit tests for distilled Central config-model payload schemas (#384).

Covers the runtime loader (``lookup_payload_schema``) and the integrity of the
committed ``_config_payload_schemas.json`` artifact — specifically that the two
objects whose schema-guessing motivated this feature (named-condition and
policy) resolve to the correct field names and enum values.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.central.config_schemas import (
    _ARTIFACT_PATH,
    _load,
    lookup_payload_schema,
)


@pytest.mark.unit
class TestArtifact:
    def test_artifact_ships_and_loads(self):
        assert _ARTIFACT_PATH.exists(), "distilled schema artifact must be committed under src/"
        data = _load()
        assert data["schemas"], "artifact should contain schemas"
        assert data["tool_index"], "artifact should contain a tool index"

    def test_named_condition_schema_is_correct(self):
        """The exact values the failed session guessed wrong must be present."""
        schema = lookup_payload_schema("central_manage_named_condition")
        assert schema is not None
        assert schema["object"] == "named-condition"
        fields = schema["fields"]
        # rules-type real enum (model guessed ipv4/ip/acl — all wrong)
        assert "NAMED_CONDITION_IP" in fields["rules-type"]["enum"]
        assert fields["rules-type"].get("mandatory") is True
        # entry list is `condition-rule` (model guessed condition-entry-list/condition-list)
        assert fields["condition-rule"]["type"] == "array"
        item = fields["condition-rule"]["items"]
        assert "position" in item
        assert "ip-header" in item
        assert "dscp" in item["ip-header"]["properties"]

    def test_get_and_manage_share_the_same_schema(self):
        get_schema = lookup_payload_schema("central_get_named_condition")
        manage_schema = lookup_payload_schema("central_manage_named_condition")
        assert get_schema == manage_schema

    def test_subnet_mask_field_carries_format_hint(self):
        """Pattern-typed string fields expose x-patternSources as `format` (#390).

        network-subnet-address is dotted-mask (ipv4-subnet-mask), NOT CIDR — the
        bare `type: string` can't convey that; the format hint must.
        """
        schema = lookup_payload_schema("central_manage_named_condition")
        assert schema is not None
        item = schema["fields"]["condition-rule"]["items"]
        nsa = item["destination"]["properties"]["subnet-address"]["properties"]["network-subnet-address"]
        assert "ipv4-subnet-mask" in (nsa.get("format") or ""), nsa

    def test_policy_exposes_qos_type(self):
        """central_manage_policy is unified — its type enum includes POLICY_QOS."""
        schema = lookup_payload_schema("central_manage_policy")
        assert schema is not None
        assert schema["object"] == "policy"
        # `type` lives on the policy object (possibly nested via allOf merge)
        type_field = schema["fields"].get("type")
        assert type_field is not None
        assert "POLICY_QOS" in type_field["enum"]

    def test_long_enums_are_capped_with_count(self):
        """Catalog-sized enums are truncated but record their true length."""
        schema = lookup_payload_schema("central_manage_policy")
        assert schema is not None

        def _find_capped(node):
            if isinstance(node, dict):
                if "enum_count" in node:
                    return node
                for v in node.values():
                    found = _find_capped(v)
                    if found:
                        return found
            elif isinstance(node, list):
                for v in node:
                    found = _find_capped(v)
                    if found:
                        return found
            return None

        capped = _find_capped(schema["fields"])
        assert capped is not None, "policy slice should contain at least one truncated enum"
        assert capped["enum_count"] > len(capped["enum"])


@pytest.mark.unit
class TestLookup:
    def test_unknown_tool_returns_none(self):
        assert lookup_payload_schema("central_get_clients") is None
        assert lookup_payload_schema("not_a_tool") is None

    def test_hand_curated_tool_is_indexed(self):
        # policy is a hand-curated (skip-list) object; it must still resolve.
        assert lookup_payload_schema("central_manage_policy") is not None
        assert lookup_payload_schema("central_get_policies") is not None

    @pytest.mark.parametrize(
        "tool_name",
        [
            # The hand-curated gap closed in #386 — these diverge from the
            # importer naming formula and must be explicitly mapped.
            "central_manage_role",
            "central_manage_wlan_profile",
            "central_manage_config_assignment",
            "central_manage_gateway_cluster",
            "central_manage_gateway_cluster_intent_profile",
            # read-only hand-curated objects (GET tool maps to the schema)
            "central_get_named_vlans",
            "central_get_aliases",
            "central_get_server_groups",
        ],
    )
    def test_hand_curated_gap_objects_resolve(self, tool_name):
        """Regression lock: every hand-curated config tool surfaces its schema."""
        schema = lookup_payload_schema(tool_name)
        assert schema is not None, f"{tool_name} should resolve to a payload schema"
        assert schema["fields"], f"{tool_name} schema should have fields"
