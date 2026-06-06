"""AOS 8 ``show`` table parsers — operational inventory, not config.

These parse the fixed-width tables AOS 8 emits for ``show ap database long``
(AP inventory) and ``show openflow-controller switches`` (controller / gateway
inventory). Both feed the GreenLake capacity (A2) and onboarding (A3) checks in
the aos-migration skill: AP / gateway *serials* (to add to GreenLake), *models*
(license type), and *counts*.

The tables are NOT cleanly column-sliceable — ``Status`` carries an embedded
space (``Up 5d:21h:55m:26s``), trailing columns are blank or ``N/A``, values
overflow their header width, and the column SET varies by AOS build (the
Mobility Conductor layout has ``Standby IP`` + ``Port``; older controllers use
``Slot/Port`` with no ``Standby IP``). So both parsers are **type-anchored** —
they key on fields with unambiguous shapes (MAC, IPv4, the ``Up``/``Down``
keyword, the 8-octet dpid, the ``Aruba<model>`` token) and read the rest
positionally relative to those anchors. That survives both the embedded space
and the format variance without hard-coded column offsets.
"""

from __future__ import annotations

import re
from typing import Any

_IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
_MAC_RE = re.compile(r"^[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}$")
_IPPORT_RE = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}):\d+$")
_DPID_RE = re.compile(r"^[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){7}$")  # 8 octets
_MODEL_RE = re.compile(r"^Aruba\w+$")  # "Aruba7240" — not the bare word "Aruba"


def parse_ap_database(text: str) -> list[dict[str, Any]]:
    """Parse ``show ap database long`` into per-AP inventory records.

    Args:
        text: captured ``show ap database long`` output (text, not a screenshot
            — terminal-wrapped rows are not supported).

    Returns:
        One dict per AP: ``{name, group, model, ip, status, switch_ip,
        standby_ip, wired_mac, serial}``. ``standby_ip`` is ``None`` on builds
        whose table omits it. Header / separator / ``Flags:`` legend / ``Total
        APs:`` lines are skipped.
    """
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        t = line.split()
        # A data row has: name, group, model, AP-IP at [0..3] and a MAC + serial
        # later. Anchor on the AP IP at index 3 and a MAC token to reject header /
        # legend / total lines.
        if len(t) < 7 or not _IPV4_RE.match(t[3]):
            continue
        mac_idx = next((i for i, tok in enumerate(t) if _MAC_RE.match(tok)), None)
        if mac_idx is None or mac_idx + 1 >= len(t):
            continue

        status: str | None = None
        for i in range(4, mac_idx):
            if t[i] in ("Up", "Down"):
                status = t[i] + ((" " + t[i + 1]) if t[i] == "Up" and i + 1 < len(t) else "")
                break

        # IPv4 tokens between the status block and the MAC are Switch IP [+ Standby IP].
        ips = [tok for tok in t[4:mac_idx] if _IPV4_RE.match(tok)]
        rows.append(
            {
                "name": t[0],
                "group": t[1],
                "model": t[2],
                "ip": t[3],
                "status": status,
                "switch_ip": ips[0] if ips else None,
                "standby_ip": ips[1] if len(ips) > 1 else None,
                "wired_mac": t[mac_idx],
                "serial": t[mac_idx + 1],
            }
        )
    return rows


def parse_openflow_controllers(text: str) -> list[dict[str, Any]]:
    """Parse ``show openflow-controller switches`` into per-controller records.

    The controller serial is the **last** whitespace token of each row's
    ``Description`` (``Aruba Networks, Inc. Aruba7240 8.0.0.0-svcs-ctrl
    UCC-Sol-7240 BC0003370``); the model is the ``Aruba<model>`` token; the
    management MAC is the last 6 octets of the 8-octet ``Dpid``.

    Returns:
        One dict per controller: ``{dpid, mgmt_ip, model, name, serial, mac}``.
    """
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        t = line.split()
        if len(t) < 3 or not _DPID_RE.match(t[0]):
            continue
        ipport = next((tok for tok in t if _IPPORT_RE.match(tok)), None)
        model = next((tok for tok in t if _MODEL_RE.match(tok)), None)
        octets = t[0].split(":")
        rows.append(
            {
                "dpid": t[0],
                "mgmt_ip": ipport.split(":")[0] if ipport else None,
                "model": model,
                "name": t[-2],  # second-to-last token of the Description
                "serial": t[-1],  # last token of the Description
                "mac": ":".join(octets[-6:]),
            }
        )
    return rows
