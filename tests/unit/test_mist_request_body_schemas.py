"""Unit tests for distilled Mist request-body schemas (#384, Mist counterpart).

Covers the runtime loader (``lookup_payload_schema``) and the integrity of the
committed ``_request_body_schemas.json`` artifact: object bodies (WLAN),
oneOf-rooted bodies (device profile), array-rooted bulk bodies, component-level
dedup, and that non-body tools resolve to ``None``.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.mist.request_body_schemas import (
    _ARTIFACT_PATH,
    _load,
    lookup_payload_schema,
)


@pytest.mark.unit
class TestArtifact:
    def test_artifact_ships_and_loads(self):
        assert _ARTIFACT_PATH.exists(), "distilled Mist artifact must be committed under src/"
        data = _load()
        assert data["schemas"], "artifact should contain schemas"
        assert data["tool_index"], "artifact should contain a tool index"

    def test_wlan_object_body_resolves(self):
        schema = lookup_payload_schema("mist_create_site_wlan")
        assert schema is not None
        assert schema["object"] == "wlan"
        assert schema["fields"], "WLAN body should distill to a non-empty field set"
        # ssid is the canonical WLAN field
        assert "ssid" in schema["fields"]

    def test_create_and_update_share_one_component(self):
        """Dedup: create/update WLAN reference the same component schema."""
        create = lookup_payload_schema("mist_create_site_wlan")
        update = lookup_payload_schema("mist_update_site_wlan")
        assert create is not None and update is not None
        assert create["object"] == update["object"] == "wlan"
        assert create == update

    def test_oneof_rooted_body_resolves(self):
        """Device-profile body is a oneOf (ap/switch/gateway) — captured as root.variants."""
        schema = lookup_payload_schema("mist_create_org_device_profile")
        assert schema is not None
        assert "root" in schema
        assert schema["root"].get("variants"), "device profile should distill to variant list"

    def test_array_rooted_body_resolves(self):
        """Bulk import/claim bodies are top-level arrays — captured as root.array."""
        schema = lookup_payload_schema("mist_import_org_psks")
        assert schema is not None
        assert schema["root"]["type"] == "array"


@pytest.mark.unit
class TestLookup:
    def test_non_body_tool_returns_none(self):
        # GET tools take no request body and must not resolve to a schema.
        assert lookup_payload_schema("mist_get_self") is None
        assert lookup_payload_schema("mist_list_org_sites") is None
        assert lookup_payload_schema("not_a_tool") is None

    def test_tool_index_covers_a_meaningful_share_of_bodies(self):
        """Sanity floor: the artifact indexes the full body-tool surface."""
        data = _load()
        # 352 body-bearing ops at time of writing; lock a floor so a broken
        # regeneration that drops most tools is caught.
        assert len(data["tool_index"]) > 300
        assert len(data["schemas"]) > 150
