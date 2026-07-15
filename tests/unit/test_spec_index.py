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
