"""Unit tests for the AOS 8 ``show`` table parsers (operational inventory).

Fixtures replicate the two real column layouts — the Mobility-Conductor format
(``Standby IP`` + ``Port``) and the older controller format (``Slot/Port``, no
``Standby IP``) — with GENERIC placeholder data only (AP-1, LAB-7240,
TESTSN…, 10.0.0.x, 00:11:22:… MACs).
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.aos8.show_parser import (
    parse_ap_database,
    parse_openflow_controllers,
)

pytestmark = pytest.mark.unit

# Mobility-Conductor layout: Standby IP + Port columns; Status has an embedded
# space on "Up", trailing Port/FQLN/Outer-IP/User are blank or N/A.
_AP_DB_MM = """AP Database
-----------
Name  Group  AP Type  IP Address  Status         Flags  Switch IP   Standby IP  Wired MAC Address  Serial #    Port  FQLN  Outer IP  User
----  -----  -------  ----------  ------         -----  ---------   ----------  -----------------  --------    ----  ----  --------  ----
AP-1  lab    315      10.0.0.11   Up 7h:25m:29s  2      10.0.0.250  0.0.0.0     00:11:22:33:44:55  TESTSN0001        N/A   N/A
AP-2  lab    305      10.0.0.12   Down           2      10.0.0.250  0.0.0.0     00:11:22:33:44:66  TESTSN0002        N/A   N/A
Flags: U = Unprovisioned; N = Duplicate name; L = Unlicensed
Total APs:2"""

# Older controller layout: Slot/Port, no Standby IP, FQLN populated.
_AP_DB_OLD = """AP Database
-----------
Name  Group    AP Type  IP Address  Status             Flags  Switch IP   Wired MAC Address  Serial #    Slot/Port  FQLN
----  -----    -------  ----------  ------             -----  ---------   -----------------  --------    ---------  ----
AP-3  default  105      10.0.0.13   Up 5d:21h:55m:26s  2      10.0.0.251  00:11:22:33:44:77  TESTSN0003  1/2        AP-3.Floor 1.Bldg
AP-4  default  93       10.0.0.14   Down               2      10.0.0.251  00:11:22:33:44:88  TESTSN0004             N/A
Total APs:2"""


def test_ap_database_mobility_conductor_layout() -> None:
    aps = parse_ap_database(_AP_DB_MM)
    assert len(aps) == 2
    assert aps[0] == {
        "name": "AP-1",
        "group": "lab",
        "model": "315",
        "ip": "10.0.0.11",
        "status": "Up 7h:25m:29s",
        "switch_ip": "10.0.0.250",
        "standby_ip": "0.0.0.0",
        "wired_mac": "00:11:22:33:44:55",
        "serial": "TESTSN0001",
    }
    assert aps[1]["status"] == "Down"
    assert aps[1]["serial"] == "TESTSN0002"


def test_ap_database_older_controller_layout() -> None:
    """No Standby IP column; Status with multi-unit uptime; trailing FQLN."""
    aps = parse_ap_database(_AP_DB_OLD)
    assert len(aps) == 2
    assert aps[0]["serial"] == "TESTSN0003"
    assert aps[0]["status"] == "Up 5d:21h:55m:26s"
    assert aps[0]["switch_ip"] == "10.0.0.251"
    assert aps[0]["standby_ip"] is None  # column absent on this build
    assert aps[1]["status"] == "Down"


def test_ap_database_skips_legend_and_total_lines() -> None:
    aps = parse_ap_database(_AP_DB_MM)
    assert all(a["name"].startswith("AP-") for a in aps)
    assert {a["serial"] for a in aps} == {"TESTSN0001", "TESTSN0002"}


_OPENFLOW = """Switches
--------
Dpid                     IP                Version  Status  Auxiliary-Status/Id  Capabilities                                      Description
----                     --                -------  ------  -------------------  ------------                                      -----------
00:00:00:0b:86:9a:4e:77  10.0.0.250:43364  v1.3     Up      Down/0               Flow stats, Table stats, Port stats, Queue Stats  Aruba Networks, Inc. Aruba7240 8.0.0.0-svcs-ctrl LAB-7240 TESTSN1001
00:00:00:0b:86:9a:4e:88  10.0.0.251:45570  v1.3     Up      Down/0               Flow stats, Table stats, Port stats, Queue Stats  Aruba Networks, Inc. Aruba7010 8.0.0.0-svcs-ctrl LAB-BOC1 TESTSN1002
Total number of switches: 2"""


def test_openflow_controllers() -> None:
    ctrls = parse_openflow_controllers(_OPENFLOW)
    assert len(ctrls) == 2
    assert ctrls[0] == {
        "dpid": "00:00:00:0b:86:9a:4e:77",
        "mgmt_ip": "10.0.0.250",
        "model": "Aruba7240",
        "name": "LAB-7240",
        "serial": "TESTSN1001",  # last token of Description
        "mac": "00:0b:86:9a:4e:77",  # last 6 octets of the 8-octet dpid
    }
    assert ctrls[1]["model"] == "Aruba7010"
    assert ctrls[1]["serial"] == "TESTSN1002"


def test_openflow_skips_header_and_total() -> None:
    ctrls = parse_openflow_controllers(_OPENFLOW)
    assert {c["serial"] for c in ctrls} == {"TESTSN1001", "TESTSN1002"}
