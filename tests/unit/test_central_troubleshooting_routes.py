"""Wire-level route coverage for the Central troubleshooting helpers.

Regression coverage for issue #705: ``monitoring_api`` resolved the
``troubleshooting`` category to ``network-troubleshooting/v1alpha1``, which
Central retired — every show-command / ping / traceroute / cable-test /
bounce / disconnect call returned ``404 Route Not Found``.

Rather than pinning a version string, every helper is driven through a fake
connection that records each request, and each recorded (method, path) must
exist in the vendored New Central OAS. That catches a version move *and* a
renamed path segment, and keeps passing if a future spec sync is applied.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from hpe_networking_mcp.platforms.central import monitoring_api as api

pytestmark = pytest.mark.unit

_SPEC = Path(__file__).resolve().parents[2] / "vendor" / "central" / "mrt" / "troubleshooting.json"
_SN = "SN0000TEST"
_TASK = "task-0001"


def _spec_routes() -> set[tuple[str, str]]:
    paths = json.loads(_SPEC.read_text(encoding="utf-8"))["paths"]
    return {(method.upper(), path) for path, ops in paths.items() for method in ops}


def _to_template(path: str) -> str:
    """Map a concrete request path back to its OAS template form."""
    path = "/" + path.lstrip("/")
    path = path.replace(f"/{_SN}", "/{serial-number}")
    return re.sub(rf"/async-operations/{_TASK}$", "/async-operations/{task-id}", path)


class _RecordingConn:
    """Fake CentralClient: records requests, answers 202 to POST and 200 to GET."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def command(self, api_method: str, api_path: str, **_: Any) -> dict[str, Any]:
        self.calls.append((api_method.upper(), api_path))
        if api_method.upper() == "POST":
            return {"code": 202, "msg": {"location": f"{api_path}/async-operations/{_TASK}", "status": "INITIATED"}}
        return {"code": 200, "msg": {"status": "COMPLETED", "output": ""}}


# (helper, kwargs) — device_type values follow TROUBLESHOOTING_METHOD_DEVICE_MAPPING.
_CASES: list[tuple[str, dict[str, Any]]] = [
    *[
        ("initiate_show_commands", {"device_type": d, "commands": "show version"})
        for d in ("cx", "aos-s", "aps", "gateways")
    ],
    *[("get_show_commands_result", {"device_type": d}) for d in ("cx", "aos-s", "aps", "gateways")],
    ("initiate_ping_cx_test", {"destination": "192.0.2.1"}),
    ("initiate_ping_aps_test", {"destination": "192.0.2.1"}),
    ("initiate_ping_gateways_test", {"destination": "192.0.2.1"}),
    *[("get_ping_test_result", {"device_type": d}) for d in ("cx", "aps", "gateways")],
    ("initiate_traceroute_cx_test", {"destination": "192.0.2.1"}),
    ("initiate_traceroute_aps_test", {"destination": "192.0.2.1"}),
    ("initiate_traceroute_gateways_test", {"destination": "192.0.2.1"}),
    *[("get_traceroute_test_result", {"device_type": d}) for d in ("cx", "aps", "gateways")],
    *[("initiate_cable_test", {"device_type": d, "ports": ["1/1/1"]}) for d in ("cx", "aos-s")],
    *[("get_cable_test_result", {"device_type": d}) for d in ("cx", "aos-s")],
    *[("initiate_port_bounce_test", {"device_type": d, "ports": ["1/1/1"]}) for d in ("cx", "aos-s", "gateways")],
    *[("get_port_bounce_test_result", {"device_type": d}) for d in ("cx", "aos-s", "gateways")],
    *[("initiate_poe_bounce_test", {"device_type": d, "ports": ["1/1/1"]}) for d in ("cx", "aos-s", "gateways")],
    *[("get_poe_bounce_test_result", {"device_type": d}) for d in ("cx", "aos-s", "gateways")],
    ("disconnect_all_clients", {"device_type": "gateways"}),
    ("disconnect_client_mac_addr", {"device_type": "gateways", "mac_address": "02:00:00:00:00:01"}),
    ("disconnect_all_users", {"device_type": "aps"}),
    ("disconnect_user_mac_addr", {"device_type": "aps", "mac_address": "02:00:00:00:00:01"}),
    ("disconnect_all_users_ssid", {"device_type": "aps", "network": "CORP-WIFI"}),
]


@pytest.mark.parametrize(("helper", "kwargs"), _CASES, ids=[f"{h}-{k.get('device_type', 'x')}" for h, k in _CASES])
async def test_helper_calls_a_route_in_the_vendored_spec(helper: str, kwargs: dict[str, Any]) -> None:
    conn = _RecordingConn()
    extra = {"task_id": _TASK} if helper.startswith("get_") else {}
    await getattr(api, helper)(central_conn=conn, serial_number=_SN, **kwargs, **extra)

    assert conn.calls, f"{helper} made no request"
    spec = _spec_routes()
    for method, path in conn.calls:
        assert (method, _to_template(path)) in spec, f"{helper}: {method} {path} is not in {_SPEC.name}"


def test_troubleshooting_latest_is_v1() -> None:
    assert api._generate_url("cx/SN/ping", "troubleshooting") == "network-troubleshooting/v1/cx/SN/ping"


def test_spec_has_no_v1alpha1_troubleshooting_routes() -> None:
    # Guards the premise: if a future spec sync reintroduces v1alpha1, revisit _CATEGORIES.
    assert not any("/v1alpha1/" in path for _, path in _spec_routes())
