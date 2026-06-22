"""Canonical RADIUS → Central server-group + auth-servers writer.

A separate translation from the WLAN writer (``central.py``): an enterprise /
MAC-auth WLAN only *references* a server-group by name (``{ssid}_nac``); this
module builds that group and its member RADIUS servers.

Model (confirmed against ``vendor/central/config/security.json`` + live tenant):

* ``auth-servers/{name}`` — one library object per **unique RADIUS host**. A
  single object carries auth + accounting + CoA for that host via ``auth-port`` /
  ``acct-port`` / ``radius-server-mode`` (AUTH_ONLY | COA_ONLY | AUTH_AND_COA) +
  ``dynamic-authorization-enable`` / ``-port``. So we consolidate by host rather
  than emit duplicate objects for the auth / acct / coa lists.
* ``server-groups/{name}`` — the ``{ssid}_nac`` group (``type: RADIUS``) with
  ``servers: [{server-name, position}]`` referencing the auth-servers in order.

Variables: the validated dynamic tool resolved Mist ``{{var}}`` hosts to literal
values before writing; an unresolved ``{{var}}`` is still accepted by
``auth-server-address`` (treated as an FQDN) but is not a true per-scope alias.
Resolution is the caller's job — this writer writes whatever host string it gets.

Naming: members are positional — ``{ssid}_nac_1``, ``{ssid}_nac_2`` …
"""

from __future__ import annotations

import re
from typing import Any

from hpe_networking_mcp.translations.canonical.wlan import CanonicalWlan
from hpe_networking_mcp.translations.writers.central import server_group_name

_AUTH_SERVERS = "network-config/v1alpha1/auth-servers"
_SERVER_GROUPS = "network-config/v1alpha1/server-groups"
_ALIASES = "network-config/v1alpha1/aliases"
_AUTH_ADDR_ALIAS_TYPE = "ALIAS_AUTH_SERVER_ADDRESS"

_DEFAULT_AUTH_PORT = 1812
_DEFAULT_ACCT_PORT = 1813
_DEFAULT_COA_PORT = 3799

# A Mist template variable, e.g. "{{RADIUS_PRIMARY}}".
_VAR_RE = re.compile(r"^\{\{\s*([A-Za-z0-9_\-.]+)\s*\}\}$")


def member_name(ssid: str, position: int) -> str:
    """Positional name for the Nth auth-server in a WLAN's ``{ssid}_nac`` group."""
    return f"{server_group_name(ssid)}_{position}"


def _var_name(host: str) -> str | None:
    """Return the bare variable name if ``host`` is a ``{{var}}``, else None.

    A Mist ``{{var}}`` RADIUS host maps to a Central ``ALIAS_AUTH_SERVER_ADDRESS``
    alias of the same name: a reusable per-scope variable. Central rejects the
    braces in ``auth-server-address`` (strict IP/FQDN), so the reference is the
    bare name and the value is supplied per scope (global = default, site /
    site-collection = override) — the Mist site-variable model.
    """
    m = _VAR_RE.match(host.strip()) if host else None
    return m.group(1) if m else None


def _consolidate_hosts(canon: CanonicalWlan) -> list[dict[str, Any]]:
    """Collapse the canonical auth/acct/coa lists into one record per unique host.

    Order: auth servers first (they define the primary list order), then any
    acct-only or coa-only hosts appended. Each record gathers the roles + ports
    + secret seen for that host across the three lists.
    """
    if not canon.security.radius:
        return []
    rad = canon.security.radius
    by_host: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    def rec(host: str) -> dict[str, Any]:
        if host not in by_host:
            by_host[host] = {
                "host": host,
                "auth": False,
                "acct": False,
                "coa": False,
                "auth_port": None,
                "acct_port": None,
                "coa_port": None,
                "secret": None,
            }
            order.append(host)
        return by_host[host]

    for s in rad.auth_servers:
        if not s.host:
            continue
        r = rec(s.host)
        r["auth"] = True
        r["auth_port"] = s.port or _DEFAULT_AUTH_PORT
        r["secret"] = r["secret"] or s.secret
    for s in rad.acct_servers:
        if not s.host:
            continue
        r = rec(s.host)
        r["acct"] = True
        r["acct_port"] = s.port or _DEFAULT_ACCT_PORT
        r["secret"] = r["secret"] or s.secret
    for c in rad.coa:
        if not c.ip:
            continue
        r = rec(c.ip)
        r["coa"] = True
        r["coa_port"] = c.port or _DEFAULT_COA_PORT
        r["secret"] = r["secret"] or c.secret

    return [by_host[h] for h in order]


def _auth_server_body(rec: dict[str, Any]) -> dict[str, Any]:
    """Build one ``auth-servers`` body from a consolidated host record."""
    if rec["coa"] and rec["auth"]:
        mode = "AUTH_AND_COA"
    elif rec["coa"]:
        mode = "COA_ONLY"
    else:
        mode = "AUTH_ONLY"

    # A {{var}} host references a Central alias by its bare name; a literal
    # host (IP or FQDN) is written directly.
    address = _var_name(rec["host"]) or rec["host"]
    body: dict[str, Any] = {
        "type": "RADIUS",
        "auth-server-address": address,
        "radius-server-mode": mode,
    }
    if rec["auth"]:
        body["auth-port"] = rec["auth_port"]
    if rec["acct"]:
        body["acct-port"] = rec["acct_port"]
    if rec["coa"]:
        body["dynamic-authorization-enable"] = True
        body["dynamic-authorization-port"] = rec["coa_port"]
    if rec["secret"]:
        # secret arrives tokenized; the PII layer detokenizes on the way out.
        body["shared-secret-config"] = {"secret-type": "PLAIN_TEXT", "plaintext-value": rec["secret"]}
    return body


def central_write_server_group(canon: CanonicalWlan) -> list[dict[str, Any]]:
    """Emit the calls to create a WLAN's ``{ssid}_nac`` RADIUS server-group.

    Returns an empty list when the WLAN has no external RADIUS (e.g. open / PSK,
    or an enterprise WLAN whose auth_source is NAC — that is a separate writer).

    The consuming orchestrator ensures-or-creates by name: if ``{ssid}_nac``
    already exists it skips these calls; otherwise it runs them before the WLAN
    create (the WLAN's ``auth-server-group`` references this group).

    Call order: alias shells (for ``{{var}}`` hosts) first, then member
    auth-servers, then the group that references them. Each ``{{var}}`` host
    becomes one ``ALIAS_AUTH_SERVER_ADDRESS`` shell (deduped across servers);
    the per-scope value (operator default at global, override per site) is set
    by the consuming skill — the shell alone is what the auth-server references.

    Returns:
        Ordered call descriptors ``{method, path, query, body, purpose, depends_on}``.
    """
    hosts = _consolidate_hosts(canon)
    if not hosts:
        return []

    ssid = canon.ssid
    group = server_group_name(ssid)
    calls: list[dict[str, Any]] = []

    # 1) alias shells for variable hosts (deduped, order-preserving)
    alias_names: list[str] = []
    for rec in hosts:
        var = _var_name(rec["host"])
        if var and var not in alias_names:
            alias_names.append(var)
            calls.append(
                {
                    "method": "POST",
                    "path": f"{_ALIASES}/{var}",
                    "query": {},
                    "body": {"type": _AUTH_ADDR_ALIAS_TYPE},
                    "purpose": f"Create auth-server-address alias '{var}' (value set per scope)",
                    "depends_on": [],
                }
            )

    # 2) member auth-servers (each depends on its alias shell, if any)
    members: list[dict[str, Any]] = []
    auth_server_indices: list[int] = []
    for i, rec in enumerate(hosts, start=1):
        name = member_name(ssid, i)
        var = _var_name(rec["host"])
        depends = [alias_names.index(var)] if var else []
        calls.append(
            {
                "method": "POST",
                "path": f"{_AUTH_SERVERS}/{name}",
                "query": {},
                "body": _auth_server_body(rec),
                "purpose": f"Create RADIUS auth-server '{name}' ({rec['host']})",
                "depends_on": depends,
            }
        )
        auth_server_indices.append(len(calls) - 1)
        members.append({"server-name": name, "position": i})

    # 3) the server-group referencing all members
    calls.append(
        {
            "method": "POST",
            "path": f"{_SERVER_GROUPS}/{group}",
            "query": {},
            "body": {"type": "RADIUS", "servers": members},
            "purpose": f"Create RADIUS server-group '{group}'",
            "depends_on": auth_server_indices,
        }
    )
    return calls
