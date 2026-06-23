"""Translation orchestrator tests.

Cover plan() merging + depends_on re-basing, preview, unresolved detection, and
execute() ensure-or-create semantics against an in-memory fake Central client
(which mimics Central returning ``200 + {}`` for a GET on a missing object).
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations import orchestrator as orch

pytestmark = pytest.mark.unit

_CONFIG_ASSIGNMENTS = "network-config/v1alpha1/config-assignments"


class FakeCentral:
    """Minimal stand-in: stores library objects by path, assignments in a list."""

    def __init__(self) -> None:
        self.objects: dict[str, dict] = {}
        self.assignments: list[dict] = []
        self.calls: list[tuple[str, str]] = []

    async def command(self, method: str, path: str, api_params=None, api_data=None):
        self.calls.append((method, path))
        if path == _CONFIG_ASSIGNMENTS:
            if method == "GET":
                return {"code": 200, "msg": {"config-assignment": self.assignments}}
            if method == "POST":
                self.assignments.extend(api_data["config-assignment"])
                return {"code": 200, "msg": {"errorCode": "SUCC_001"}}
        if method == "GET":
            # Central returns 200 + {} for a missing named object (not 404).
            return {"code": 200, "msg": self.objects.get(path, {})}
        if method == "POST":
            self.objects[path] = {"name": path.split("/")[-1], **(api_data or {})}
            return {"code": 200, "msg": {"errorCode": "SUCC_001"}}
        if method == "DELETE":
            self.objects.pop(path, None)
            return {"code": 200, "msg": "OK"}
        return {"code": 400, "msg": "unhandled"}


def _eap_wlan() -> dict:
    return {
        "ssid": "EAP",
        "auth": {"type": "eap"},
        "auth_servers": [{"host": "10.1.1.1", "secret": "s"}, {"host": "{{RADIUS_PRIMARY}}", "secret": "s"}],
    }


def test_supported_lists_registry() -> None:
    s = orch.supported()
    assert "mist:wlan" in s["readers"]
    assert "central:wlan" in s["writers"]


def test_plan_merges_and_rebases_depends_on() -> None:
    p = orch.plan("mist", "central", orch.WLAN, _eap_wlan())
    paths = [c["path"].split("/")[-1] for c in p.calls]
    assert paths == ["RADIUS_PRIMARY", "EAP_nac_1", "EAP_nac_2", "EAP_nac", "EAP"]
    # the WLAN create (last) chains onto the server-group create (index 3)
    assert p.calls[-1]["depends_on"] == [3]
    # the variable auth-server (index 2) depends on its alias shell (index 0)
    assert 0 in p.calls[2]["depends_on"]


def test_plan_preview_is_readable() -> None:
    p = orch.plan("mist", "central", orch.WLAN, {"ssid": "G", "auth": {"type": "open"}})
    text = p.preview()
    assert "mist → central [wlan]" in text
    assert "wlan-ssids/G" in text


def test_plan_unknown_reader_raises() -> None:
    with pytest.raises(ValueError):
        orch.plan("nope", "central", orch.WLAN, {})


@pytest.mark.asyncio
async def test_execute_creates_then_skips_idempotent() -> None:
    fake = FakeCentral()
    p = orch.plan("mist", "central", orch.WLAN, _eap_wlan())

    run1 = await orch.execute(fake.command, p)
    assert {r["action"] for r in run1} == {"created"}

    run2 = await orch.execute(fake.command, p)
    assert {r["action"] for r in run2} == {"skipped_exists"}


@pytest.mark.asyncio
async def test_execute_dry_run_writes_nothing() -> None:
    fake = FakeCentral()
    p = orch.plan("mist", "central", orch.WLAN, _eap_wlan())
    res = await orch.execute(fake.command, p, dry_run=True)
    assert {r["action"] for r in res} == {"planned"}
    assert fake.objects == {}  # no writes


@pytest.mark.asyncio
async def test_execute_blocks_on_unresolved_scope() -> None:
    fake = FakeCentral()
    # site assignment with no resolver -> unresolved
    from hpe_networking_mcp.translations.canonical.wlan import Assignment, CanonicalWlan, KeyMgmt, Security

    canon = CanonicalWlan(ssid="X", security=Security(key_mgmt=KeyMgmt.OPEN), assignment=Assignment(sites=["GHOST"]))
    p = orch.TranslationPlan("mist", "central", orch.WLAN, canon, orch.from_canonical("central", orch.WLAN, canon))
    assert p.unresolved
    res = await orch.execute(fake.command, p)
    assert res[0]["action"] == "blocked_unresolved"
    assert fake.objects == {}


@pytest.mark.asyncio
async def test_execute_assignment_path() -> None:
    fake = FakeCentral()
    from hpe_networking_mcp.translations.canonical.wlan import Assignment, CanonicalWlan, KeyMgmt, Security

    canon = CanonicalWlan(ssid="X", security=Security(key_mgmt=KeyMgmt.OPEN), assignment=Assignment(org_wide=True))
    calls = orch.from_canonical("central", orch.WLAN, canon, global_scope_id="GID")
    p = orch.TranslationPlan("mist", "central", orch.WLAN, canon, calls)
    res = await orch.execute(fake.command, p)
    actions = [r["action"] for r in res]
    assert "created" in actions and "assigned" in actions
    assert fake.assignments[0]["scope-id"] == "GID"


@pytest.mark.asyncio
async def test_execute_blocks_on_unresolved_clusters() -> None:
    # Casey #1: a tunneled WLAN with no gateway cluster binding must block before
    # any write — unresolved clusters count toward plan.unresolved.
    from hpe_networking_mcp.translations.canonical.wlan import CanonicalWlan, ForwardMode, KeyMgmt, Security

    fake = FakeCentral()
    canon = CanonicalWlan(ssid="T", security=Security(key_mgmt=KeyMgmt.OPEN), forward=ForwardMode.TUNNELED)
    p = orch.TranslationPlan("mist", "central", orch.WLAN, canon, orch.from_canonical("central", orch.WLAN, canon))
    assert any(u["kind"] == "gateway_cluster" for u in p.unresolved)
    res = await orch.execute(fake.command, p)
    assert res[0]["action"] == "blocked_unresolved"
    assert fake.objects == {}


class FailingCentral(FakeCentral):
    """FakeCentral that fails POSTs to a given path substring."""

    def __init__(self, fail_substr: str) -> None:
        super().__init__()
        self.fail_substr = fail_substr

    async def command(self, method, path, api_params=None, api_data=None):
        if method == "POST" and self.fail_substr in path:
            self.calls.append((method, path))
            return {"code": 400, "msg": "boom"}
        return await super().command(method, path, api_params=api_params, api_data=api_data)


@pytest.mark.asyncio
async def test_execute_overlay_failure_blocks_assignment() -> None:
    # Casey round 2: a failed overlay-wlan must block the WLAN's scope assignment
    # (else a tunneled WLAN goes active with no gateway-cluster binding).
    from hpe_networking_mcp.translations.canonical.wlan import Assignment, CanonicalWlan, ForwardMode, KeyMgmt, Security

    gw = [
        {
            "cluster": "C1",
            "cluster-type": "CLUSTER_ID",
            "cluster-scope-id": "9",
            "cluster-redundancy-type": "PRIMARY",
            "tunnel-type": "GRE",
        }
    ]
    canon = CanonicalWlan(
        ssid="T",
        security=Security(key_mgmt=KeyMgmt.OPEN),
        forward=ForwardMode.TUNNELED,
        assignment=Assignment(org_wide=True),
    )
    calls = orch.from_canonical("central", orch.WLAN, canon, gateway_cluster_list=gw, global_scope_id="GID")
    p = orch.TranslationPlan("mist", "central", orch.WLAN, canon, calls)
    assert not p.unresolved  # clusters resolved -> not blocked up front
    fake = FailingCentral("overlay-wlan")
    res = await orch.execute(fake.command, p)
    actions = [r["action"] for r in res]
    assert "failed" in actions  # overlay create fails
    assert actions[-1] == "blocked_dependency_failed"  # assignment blocked
    assert fake.assignments == []  # nothing assigned


@pytest.mark.asyncio
async def test_execute_blocks_dependents_on_failure() -> None:
    # Casey #2: if a prerequisite (server-group) create fails, the dependent
    # WLAN create must NOT run — it is blocked_dependency_failed.
    fake = FailingCentral("server-groups")
    p = orch.plan("mist", "central", orch.WLAN, _eap_wlan())
    res = await orch.execute(fake.command, p)
    by = {r["path"].split("/")[-1]: r["action"] for r in res}
    assert by["EAP_nac"] == "failed"  # the server-group create fails
    assert by["EAP"] == "blocked_dependency_failed"  # WLAN depends on it → blocked
    # the WLAN was never POSTed
    assert "network-config/v1alpha1/wlan-ssids/EAP" not in [p for _, p in fake.calls]
