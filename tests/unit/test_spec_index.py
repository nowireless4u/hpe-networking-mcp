"""Tests for the spec-lookup index (builder + query layer).

Builds the real index from the vendored OpenAPI corpus once per session, then
asserts the canonical lookups that motivated it (Mike's ``system-info.hostname``
case; Mist/ClearPass schema-level enums resolved via ``$ref``) plus graceful
degradation when the index is absent.
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from hpe_networking_mcp.spec_index import SpecIndex
from hpe_networking_mcp.spec_index import tool_schema as ts

_REPO = Path(__file__).resolve().parents[2]
_BUILDER = _REPO / "scripts" / "build_spec_index.py"


@pytest.fixture(scope="session")
def index_db(tmp_path_factory) -> Path:
    """Build the real index from vendor/** once for the test session."""
    db = tmp_path_factory.mktemp("spec_index") / "spec_index.db"
    subprocess.run([sys.executable, str(_BUILDER), str(db)], check=True)
    return db


@pytest.fixture(scope="session")
def idx(index_db) -> SpecIndex:
    return SpecIndex(index_db)


@pytest.mark.unit
class TestBuild:
    def test_index_available_and_populated(self, idx: SpecIndex):
        assert idx.available
        con = sqlite3.connect(idx._path)
        (endpoints,) = con.execute("SELECT COUNT(*) FROM endpoints").fetchone()
        (fields,) = con.execute("SELECT COUNT(*) FROM fields").fetchone()
        assert endpoints > 4000
        assert fields > 20000

    def test_aoscx_excluded(self, index_db: Path):
        """aoscx is an orphan spec (no platform/tools) — never indexed."""
        con = sqlite3.connect(index_db)
        (n,) = con.execute("SELECT COUNT(*) FROM endpoints WHERE platform='aoscx'").fetchone()
        assert n == 0
        (n,) = con.execute("SELECT COUNT(*) FROM schemas WHERE platform='aoscx'").fetchone()
        assert n == 0

    def test_manifests_skipped_not_indexed(self, index_db: Path):
        """Non-spec JSON (_manifest.json / sources.json) contributes no rows."""
        con = sqlite3.connect(index_db)
        (n,) = con.execute("SELECT COUNT(*) FROM endpoints WHERE spec_file LIKE '%_manifest.json'").fetchone()
        assert n == 0


@pytest.mark.unit
class TestFieldAndEnumLookups:
    def test_system_info_hostname_field(self, idx: SpecIndex):
        """Mike's AP-rename case: the system-info profile exposes a `hostname` field."""
        fields = idx.schema_fields("central", "ArubaSystemInfo_SystemInfoprofileSchema")
        names = {f["name"] for f in fields}
        assert "hostname" in names

    def test_mist_wlan_auth_enum_via_ref(self, idx: SpecIndex):
        """Mist models the WLAN auth mode as a `$ref` to a schema-level enum;
        the resolver must follow the ref to surface the legal values."""
        values = idx.field_enum("mist", "wlan_auth", "type")
        assert values is not None
        assert "psk" in values and "open" in values

    def test_clearpass_schema_level_enum_indexed(self, index_db: Path):
        """ClearPass encodes enums as standalone named schemas (e.g. GrantType)."""
        con = sqlite3.connect(index_db)
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT enum_json FROM schemas WHERE platform='clearpass' AND schema_name='GrantType'"
        ).fetchone()
        assert row is not None and row["enum_json"] is not None
        assert "client_credentials" in row["enum_json"]

    def test_field_enum_unknown_returns_none(self, idx: SpecIndex):
        assert idx.field_enum("central", "ArubaSystemInfo_SystemInfoprofileSchema", "hostname") is None
        assert idx.field_enum("mist", "no_such_schema", "no_field") is None

    def test_schema_fields_unknown_returns_empty(self, idx: SpecIndex):
        assert idx.schema_fields("central", "NoSuchSchema") == []


@pytest.mark.unit
class TestEndpointLookups:
    def test_system_info_patch_params_include_scope(self, idx: SpecIndex):
        """The scope query params Mike was missing must be discoverable."""
        ep = idx.endpoint("central", path="/network-config/v1alpha1/system-info/{name}", method="PATCH")
        assert ep is not None
        pnames = {p["name"] for p in ep["parameters"]}
        assert {"name", "scope-id", "object-type", "device-function"} <= pnames

    def test_device_notes_endpoint_resolves(self, idx: SpecIndex):
        ep = idx.endpoint("central", operation_id="updateDeviceNotesV1")
        assert ep is not None
        assert ep["method"] == "PATCH"

    def test_unknown_endpoint_returns_none(self, idx: SpecIndex):
        assert idx.endpoint("central", operation_id="nope_does_not_exist") is None


@pytest.mark.unit
class TestSearch:
    def test_field_search_cross_platform(self, idx: SpecIndex):
        rows = idx.search("hostname", kind="field")
        assert any(r["name"] == "hostname" for r in rows)

    def test_endpoint_search_platform_filter(self, idx: SpecIndex):
        rows = idx.search("notes", kind="endpoint", platform="central")
        assert any(r["name"] == "updateDeviceNotesV1" for r in rows)

    def test_search_special_chars_no_crash(self, idx: SpecIndex):
        # Arbitrary punctuation must not break FTS5 MATCH syntax.
        assert isinstance(idx.search('a"b(c) OR', kind="field"), list)

    def test_search_invalid_kind_raises(self, idx: SpecIndex):
        with pytest.raises(ValueError, match="kind must be one of"):
            idx.search("x", kind="bogus")

    def test_response_search(self, idx: SpecIndex):
        assert isinstance(idx.search("token", kind="response", platform="mist"), list)


@pytest.mark.unit
class TestRichMetadata:
    """Examples, readOnly/writeOnly, deprecated(+note), oneOf/anyOf variants, all responses."""

    def test_error_responses_captured_with_descriptions(self, index_db: Path):
        """The AI learns what 429 means from the indexed response description."""
        con = sqlite3.connect(index_db)
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT r.description FROM responses r JOIN endpoints e ON r.endpoint_id=e.id "
            "WHERE e.platform='mist' AND r.status_code='429' AND r.description IS NOT NULL LIMIT 1"
        ).fetchone()
        assert row is not None and row["description"].strip()

    def test_field_examples_captured(self, index_db: Path):
        con = sqlite3.connect(index_db)
        (n,) = con.execute("SELECT COUNT(*) FROM fields WHERE example IS NOT NULL").fetchone()
        assert n > 1000  # widespread across greenlake/edgeconnect/central
        (n,) = con.execute("SELECT COUNT(*) FROM endpoints WHERE request_example IS NOT NULL").fetchone()
        assert n > 0

    def test_readonly_writeonly_captured(self, index_db: Path):
        con = sqlite3.connect(index_db)
        (n,) = con.execute("SELECT COUNT(*) FROM fields WHERE read_only=1").fetchone()
        assert n > 100  # mist alone has ~600

    def test_deprecated_flag_and_note(self, index_db: Path):
        con = sqlite3.connect(index_db)
        con.row_factory = sqlite3.Row
        (dep,) = con.execute("SELECT COUNT(*) FROM endpoints WHERE deprecated=1").fetchone()
        assert dep > 0
        note = con.execute("SELECT deprecated_note FROM endpoints WHERE deprecated_note IS NOT NULL LIMIT 1").fetchone()
        assert note is not None and note["deprecated_note"]

    def test_oneof_anyof_variants_captured(self, index_db: Path):
        con = sqlite3.connect(index_db)
        (n,) = con.execute("SELECT COUNT(*) FROM fields WHERE variants IS NOT NULL").fetchone()
        assert n > 0

    def test_device_types_captured(self, index_db: Path):
        """x-supportedDeviceType parity with the distilled Central artifact."""
        con = sqlite3.connect(index_db)
        (n,) = con.execute("SELECT COUNT(*) FROM fields WHERE device_types IS NOT NULL").fetchone()
        assert n > 1000  # 14k occurrences in central config specs

    def test_endpoint_exposes_responses_and_flags(self, idx: SpecIndex):
        ep = idx.endpoint("central", operation_id="updateDeviceNotesV1")
        assert ep is not None
        assert isinstance(ep["responses"], list) and ep["responses"]
        assert all("status" in r for r in ep["responses"])
        assert "deprecated" in ep and "request_example" in ep

    def test_schema_fields_expose_rich_attrs(self, idx: SpecIndex):
        fields = idx.schema_fields("mist", "wlan")
        assert fields
        for key in ("read_only", "write_only", "deprecated", "example", "variants", "constraints"):
            assert all(key in f for f in fields)


@pytest.mark.unit
class TestConfigBodyProvider:
    """The get_schema enrichment path for opaque payload:dict config tools (Mike's case)."""

    def test_config_body_resolves_system_info(self, idx: SpecIndex):
        body = idx.config_body("central", "system-info")
        assert body is not None
        names = {f["name"] for f in body["fields"]}
        assert "hostname" in names
        scope = {p["name"] for p in body["scope_parameters"]}
        assert {"scope-id", "object-type", "device-function"} <= scope

    def test_config_body_unknown_returns_none(self, idx: SpecIndex):
        assert idx.config_body("central", "no-such-resource-xyz") is None

    def test_payload_schema_for_config_tool(self, idx: SpecIndex, monkeypatch):
        monkeypatch.setattr(ts, "get_spec_index", lambda: idx)
        ps = ts.payload_schema_for_tool("central_manage_system_info")
        assert ps is not None and any(f["name"] == "hostname" for f in ps["fields"])
        # the get_* twin resolves the same body
        assert ts.payload_schema_for_tool("central_get_system_info") is not None

    def test_payload_schema_none_for_non_config_tool(self, idx: SpecIndex, monkeypatch):
        monkeypatch.setattr(ts, "get_spec_index", lambda: idx)
        assert ts.payload_schema_for_tool("mist_get_self") is None
        assert ts.payload_schema_for_tool("") is None

    def test_render_payload_schema_text(self, idx: SpecIndex):
        body = idx.config_body("central", "system-info")
        text = ts.render_payload_schema("central_manage_system_info", body)
        assert "PAYLOAD SCHEMA for central_manage_system_info" in text
        assert "hostname" in text
        assert "scope query params" in text


@pytest.mark.unit
class TestBodyResolutionParity:
    """The mapping fixes that reach 100% distilled-artifact parity (both modes)."""

    def test_allof_ref_flattening(self, idx: SpecIndex):
        """Pure ``allOf: [$ref Base]`` config bodies must flatten to the base's fields."""
        body = idx.config_body("central", "dsm")
        assert body is not None and body.get("fields")

    def test_config_body_via_renamed_segment(self, idx: SpecIndex):
        """A pluralized/renamed resource resolves (radios, not radio)."""
        assert idx.config_body("central", "radios")
        assert idx.config_body("central", "gw-cluster-intent-config")

    def test_mist_reverse_name_mapping(self, idx: SpecIndex, monkeypatch):
        monkeypatch.setattr(ts, "get_spec_index", lambda: idx)
        ps = ts.payload_schema_for_tool("mist_create_site_wlan")
        assert ps is not None and ps["object"] == "wlan"
        assert any(f["name"] for f in ps["fields"])

    def test_mist_map_body_root_descriptor(self, idx: SpecIndex, monkeypatch):
        """Free-form map body (additionalProperties) surfaces a root shape, not blank."""
        monkeypatch.setattr(ts, "get_spec_index", lambda: idx)
        ps = ts.payload_schema_for_tool("mist_set_site_device_iot_port")
        assert ps is not None and (ps.get("root") or ps.get("fields") or ps.get("variants"))

    def test_schema_body_shapes(self, idx: SpecIndex):
        assert "fields" in (idx.schema_body("mist", "wlan") or {})
        assert idx.schema_body("mist", "no_such_schema_xyz") is None

    def test_render_handles_root_and_variants(self):
        assert "array[string]" in ts.render_payload_schema("t", {"object": "x", "root": "array[string]"})
        assert "one of: A, B" in ts.render_payload_schema("t", {"object": "x", "variants": ["A", "B"]})


@pytest.mark.unit
class TestReactiveEnrichment:
    """Reactive all-non-2xx error enrichment (Phase 3)."""

    def test_response_description_representative(self, idx: SpecIndex):
        desc = idx.response_description("mist", "429")
        assert desc is not None and "many" in desc.lower()

    def test_response_description_skips_non_representative(self, idx: SpecIndex):
        # EdgeConnect documents per-endpoint 400s → no dominant description → skip.
        assert idx.response_description("edgeconnect", "400") is None

    def test_reactive_hint_status_meaning(self, idx: SpecIndex, monkeypatch):
        from hpe_networking_mcp.spec_index import error_help

        monkeypatch.setattr(error_help, "get_spec_index", lambda: idx)
        monkeypatch.setattr(ts, "get_spec_index", lambda: idx)
        hint = error_help.reactive_hint("mist_get_self", 429)
        assert hint and "429" in hint and "spec-index" in hint

    def test_reactive_hint_input_error_lists_fields(self, idx: SpecIndex, monkeypatch):
        from hpe_networking_mcp.spec_index import error_help

        monkeypatch.setattr(error_help, "get_spec_index", lambda: idx)
        monkeypatch.setattr(ts, "get_spec_index", lambda: idx)
        # Mist body tool (no registry needed) on a 400 lists its body fields.
        hint = error_help.reactive_hint("mist_create_site_wlan", 400)
        assert hint and "valid body fields" in hint

    def test_reactive_hint_none_cases(self, idx: SpecIndex, monkeypatch):
        from hpe_networking_mcp.spec_index import error_help

        monkeypatch.setattr(error_help, "get_spec_index", lambda: idx)
        monkeypatch.setattr(ts, "get_spec_index", lambda: idx)
        assert error_help.reactive_hint("mist_get_self", 200) is None  # not an error
        assert error_help.reactive_hint("unknown_tool", 500) is None  # no platform
        assert error_help.reactive_hint("", 500) is None


@pytest.mark.unit
class TestGracefulDegradation:
    """A missing index must never raise — enrichment degrades to 'no hint'."""

    def _absent(self, tmp_path: Path) -> SpecIndex:
        return SpecIndex(tmp_path / "does_not_exist.db")

    def test_reports_unavailable(self, tmp_path: Path):
        assert self._absent(tmp_path).available is False

    def test_all_queries_return_empty(self, tmp_path: Path):
        si = self._absent(tmp_path)
        assert si.schema_fields("central", "X") == []
        assert si.field_enum("central", "X", "y") is None
        assert si.endpoint("central", path="/x") is None
        assert si.search("hostname", kind="field") == []
