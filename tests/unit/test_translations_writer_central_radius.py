"""Canonical RADIUS → Central server-group writer tests.

Cover host consolidation (one auth-server per unique host carrying auth/acct/CoA),
positional ``{ssid}_nac_N`` naming, radius-server-mode selection, the
``{{var}}`` → ``ALIAS_AUTH_SERVER_ADDRESS`` shell + bare-name reference, and the
empty-list result for non-RADIUS WLANs.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.canonical.wlan import (
    CanonicalWlan,
    CoaServer,
    RadiusConfig,
    RadiusServer,
    Security,
    SecurityMode,
)
from hpe_networking_mcp.translations.writers.central_radius import central_write_server_group, member_name

pytestmark = pytest.mark.unit


def _eap(radius: RadiusConfig | None) -> CanonicalWlan:
    return CanonicalWlan(ssid="EAP", security=Security(mode=SecurityMode.ENTERPRISE, radius=radius))


def _by_path(calls: list[dict]) -> dict[str, dict]:
    return {c["path"].split("/")[-1]: c for c in calls}


def test_no_radius_returns_empty() -> None:
    assert central_write_server_group(_eap(None)) == []
    assert central_write_server_group(CanonicalWlan(ssid="OPEN", security=Security(mode=SecurityMode.OPEN))) == []


def test_single_auth_server_basic() -> None:
    calls = central_write_server_group(_eap(RadiusConfig(auth_servers=[RadiusServer(host="10.1.1.1", secret="s")])))
    by = _by_path(calls)
    assert "EAP_nac_1" in by
    body = by["EAP_nac_1"]["body"]
    assert body["type"] == "RADIUS"
    assert body["auth-server-address"] == "10.1.1.1"
    assert body["radius-server-mode"] == "AUTH_ONLY"
    assert body["shared-secret-config"] == {"secret-type": "PLAIN_TEXT", "plaintext-value": "s"}
    grp = by["EAP_nac"]["body"]
    assert grp["type"] == "RADIUS"
    assert grp["servers"] == [{"server-name": "EAP_nac_1", "position": 1}]


def test_consolidation_by_host_auth_acct_coa() -> None:
    rad = RadiusConfig(
        auth_servers=[RadiusServer(host="10.1.1.1", port=1812, secret="s")],
        acct_servers=[RadiusServer(host="10.1.1.1", port=1813, secret="s")],
        coa=[CoaServer(ip="10.1.1.1", port=3799, secret="s")],
    )
    calls = central_write_server_group(_eap(rad))
    # one host -> one auth-server with all three roles
    auth_servers = [c for c in calls if "/auth-servers/" in c["path"]]
    assert len(auth_servers) == 1
    body = auth_servers[0]["body"]
    assert body["radius-server-mode"] == "AUTH_AND_COA"
    assert body["auth-port"] == 1812
    assert body["acct-port"] == 1813
    assert body["dynamic-authorization-enable"] is True
    assert body["dynamic-authorization-port"] == 3799


def test_coa_only_host() -> None:
    rad = RadiusConfig(coa=[CoaServer(ip="10.9.9.9", port=3799)])
    body = [c for c in central_write_server_group(_eap(rad)) if "/auth-servers/" in c["path"]][0]["body"]
    assert body["radius-server-mode"] == "COA_ONLY"


def test_positional_naming_multiple_hosts() -> None:
    rad = RadiusConfig(auth_servers=[RadiusServer(host="10.1.1.1"), RadiusServer(host="10.1.1.2")])
    calls = central_write_server_group(_eap(rad))
    names = [c["path"].split("/")[-1] for c in calls if "/auth-servers/" in c["path"]]
    assert names == ["EAP_nac_1", "EAP_nac_2"]
    assert member_name("EAP", 2) == "EAP_nac_2"
    grp = [c for c in calls if "/server-groups/" in c["path"]][0]["body"]
    assert [m["position"] for m in grp["servers"]] == [1, 2]


def test_variable_host_creates_alias_shell_and_references_it() -> None:
    rad = RadiusConfig(auth_servers=[RadiusServer(host="{{RADIUS_PRIMARY}}", secret="s")])
    calls = central_write_server_group(_eap(rad))
    alias = [c for c in calls if "/aliases/" in c["path"]]
    assert len(alias) == 1
    assert alias[0]["path"].endswith("/aliases/RADIUS_PRIMARY")
    assert alias[0]["body"] == {"type": "ALIAS_AUTH_SERVER_ADDRESS"}
    # the auth-server references the alias by bare name; alias precedes it
    as_call = [c for c in calls if "/auth-servers/" in c["path"]][0]
    assert as_call["body"]["auth-server-address"] == "RADIUS_PRIMARY"
    assert as_call["depends_on"] == [0]


def test_duplicate_variable_dedupes_alias() -> None:
    rad = RadiusConfig(auth_servers=[RadiusServer(host="{{SHARED}}"), RadiusServer(host="{{SHARED}}")])
    calls = central_write_server_group(_eap(rad))
    aliases = [c for c in calls if "/aliases/" in c["path"]]
    assert len(aliases) == 1  # deduped


def test_alias_ordering_before_auth_servers() -> None:
    rad = RadiusConfig(auth_servers=[RadiusServer(host="{{V}}")])
    calls = central_write_server_group(_eap(rad))
    paths = [c["path"] for c in calls]
    assert "/aliases/" in paths[0]
    assert "/auth-servers/" in paths[1]
    assert "/server-groups/" in paths[2]
