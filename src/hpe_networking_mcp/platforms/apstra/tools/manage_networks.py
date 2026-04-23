"""Apstra virtual-network and remote-gateway write tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.apstra import guidelines
from hpe_networking_mcp.platforms.apstra._registry import tool
from hpe_networking_mcp.platforms.apstra.client import format_http_error, get_apstra_client
from hpe_networking_mcp.platforms.apstra.models import (
    normalize_to_int_list,
    normalize_to_nested_list,
    normalize_to_string_list,
    parse_bool,
)
from hpe_networking_mcp.platforms.apstra.tools import WRITE
from hpe_networking_mcp.platforms.apstra.topology import get_individual_leafs_from_system_ids


@tool(annotations=WRITE, tags={"apstra_write"})
async def apstra_create_virtual_network(
    ctx: Context,
    blueprint_id: str,
    security_zone_id: str,
    vn_name: str,
    virtual_gateway_ipv4: str,
    ipv4_subnet: str,
    system_ids: str | list[str] | None = None,
    vlan_ids: str | int | list[int] | None = None,
    access_switch_node_ids: str | list[str] | list[list[str]] | None = None,
    svi_ips: str | list[dict[str, Any]] | None = None,
    vn_type: str = "vxlan",
    ipv4_enabled: str | bool = True,
    dhcp_service: str = "dhcpServiceDisabled",
    virtual_gateway_ipv4_enabled: str | bool = True,
    create_policy_tagged: str | bool | None = None,
    virtual_gateway_ipv6_enabled: str | bool = False,
    ipv6_enabled: str | bool = False,
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Create a virtual network via Apstra's ``virtual-networks-batch`` API.

    Accepts flexible input shapes (JSON strings or native types) for backward
    compatibility with existing callers. Bound_to uses ``system_ids`` as-is,
    while SVI IPs automatically expand redundancy-group IDs to individual
    leafs via ``apstra_get_system_info`` topology.

    Args:
        blueprint_id: Blueprint UUID (MANDATORY).
        security_zone_id: Routing zone / security zone UUID (MANDATORY).
        vn_name: Label for the new virtual network (MANDATORY).
        virtual_gateway_ipv4: Gateway IPv4 address, e.g. "10.1.1.1" (MANDATORY).
        ipv4_subnet: IPv4 CIDR, e.g. "10.1.1.0/24" (MANDATORY).
        system_ids: Single ID string, JSON array string, or list of IDs.
        vlan_ids: Single int, JSON array string, or list of ints.
        access_switch_node_ids: Flat or nested JSON string, or list of lists.
        svi_ips: JSON string or list; auto-generated from system_ids if omitted.
        vn_type: "vxlan" or "vlan" (default: "vxlan").
        ipv4_enabled: "true"/"false" or bool (default: True).
        dhcp_service: DHCP service setting (default: "dhcpServiceDisabled").
        virtual_gateway_ipv4_enabled: "true"/"false" or bool (default: True).
        create_policy_tagged: Optional "true"/"false" or bool (omitted if None).
        virtual_gateway_ipv6_enabled: "true"/"false" or bool (default: False).
        ipv6_enabled: "true"/"false" or bool (default: False).
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if vn_type not in ("vxlan", "vlan"):
        return f"Invalid vn_type '{vn_type}'. Must be 'vxlan' or 'vlan'."

    if not confirmed:
        decline = await confirm_write(
            ctx,
            f"Apstra: create virtual network '{vn_name}' ({vn_type}) in blueprint {blueprint_id}. Confirm?",
        )
        if decline:
            return decline

    try:
        ipv4_enabled_b = bool(parse_bool(ipv4_enabled))
        vgw_v4_enabled_b = bool(parse_bool(virtual_gateway_ipv4_enabled))
        vgw_v6_enabled_b = bool(parse_bool(virtual_gateway_ipv6_enabled))
        ipv6_enabled_b = bool(parse_bool(ipv6_enabled))
        policy_tagged_b = parse_bool(create_policy_tagged) if create_policy_tagged is not None else None
    except ValueError as e:
        return f"Invalid boolean parameter: {e}"

    try:
        normalized_system_ids = normalize_to_string_list(system_ids)
    except ValueError as e:
        return f"Invalid system_ids: {e}"

    if normalized_system_ids:
        target_len = len(normalized_system_ids)
        try:
            normalized_vlan_ids = normalize_to_int_list(vlan_ids, target_len) if vlan_ids is not None else None
            normalized_access = normalize_to_nested_list(access_switch_node_ids, target_len)
        except ValueError as e:
            return f"Invalid VLAN or access-switch input: {e}"
    else:
        normalized_vlan_ids = None
        normalized_access = None

    bound_to: list[dict[str, Any]] = []
    if normalized_system_ids:
        for i, sid in enumerate(normalized_system_ids):
            binding: dict[str, Any] = {
                "system_id": sid,
                "access_switch_node_ids": normalized_access[i] if normalized_access else [],
            }
            if normalized_vlan_ids and i < len(normalized_vlan_ids):
                binding["vlan_id"] = normalized_vlan_ids[i]
            bound_to.append(binding)

    try:
        client = await get_apstra_client()

        normalized_svi_ips: list[dict[str, Any]]
        if svi_ips is None and normalized_system_ids:
            leaf_ids = await get_individual_leafs_from_system_ids(client, blueprint_id, normalized_system_ids)
            normalized_svi_ips = [
                {
                    "system_id": leaf,
                    "ipv4_mode": "enabled" if ipv4_enabled_b else "disabled",
                    "ipv4_addr": None,
                    "ipv6_mode": "enabled" if ipv6_enabled_b else "disabled",
                    "ipv6_addr": None,
                }
                for leaf in leaf_ids
            ]
        elif isinstance(svi_ips, str):
            import json as _json

            try:
                parsed_svi = _json.loads(svi_ips)
            except _json.JSONDecodeError:
                parsed_svi = []
            normalized_svi_ips = parsed_svi if isinstance(parsed_svi, list) else []
        elif isinstance(svi_ips, list):
            normalized_svi_ips = svi_ips
        else:
            normalized_svi_ips = []

        vn_config: dict[str, Any] = {
            "label": vn_name,
            "vn_type": vn_type,
            "security_zone_id": security_zone_id,
            "virtual_gateway_ipv4": virtual_gateway_ipv4,
            "ipv4_subnet": ipv4_subnet,
            "svi_ips": normalized_svi_ips,
            "bound_to": bound_to,
            "virtual_gateway_ipv4_enabled": vgw_v4_enabled_b,
            "ipv4_enabled": ipv4_enabled_b,
            "dhcp_service": dhcp_service,
            "virtual_gateway_ipv6_enabled": vgw_v6_enabled_b,
            "ipv6_enabled": ipv6_enabled_b,
            "vn_id": None,
            "vni_ids": [],
            "rt_policy": {"import_RTs": None, "export_RTs": None},
            "reserved_vlan_id": None,
            "ipv6_subnet": None,
            "virtual_gateway_ipv6": None,
        }
        if policy_tagged_b is not None:
            vn_config["create_policy_tagged"] = policy_tagged_b

        response = await client.request(
            "POST",
            f"/api/blueprints/{blueprint_id}/virtual-networks-batch",
            params={"async": "full"},
            json_body={"virtual_networks": [vn_config]},
        )
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_change_mgmt_guidelines(),
            "data": response.json(),
        }
    except Exception as e:
        return f"Error creating virtual network: {format_http_error(e) if hasattr(e, 'response') else e}"


@tool(annotations=WRITE, tags={"apstra_write"})
async def apstra_create_remote_gateway(
    ctx: Context,
    blueprint_id: str,
    gw_ip: str,
    gw_asn: int,
    gw_name: str,
    local_gw_nodes: list[str] | str,
    evpn_route_types: str = "all",
    password: str | None = None,
    keepalive_timer: int = 10,
    evpn_interconnect_group_id: str | None = None,
    holdtime_timer: int = 30,
    ttl: int = 30,
    confirmed: bool = False,
) -> dict[str, Any] | str:
    """Create a remote EVPN gateway in a blueprint.

    Args:
        blueprint_id: Blueprint UUID (MANDATORY).
        gw_ip: Remote gateway IP address.
        gw_asn: Remote gateway ASN.
        gw_name: Label for the new gateway.
        local_gw_nodes: Local gateway node IDs (list or single string).
        evpn_route_types: EVPN route types accepted (default: "all").
        password: Optional BGP MD5 password.
        keepalive_timer: BGP keepalive seconds (default: 10).
        evpn_interconnect_group_id: Optional interconnect-group UUID.
        holdtime_timer: BGP hold time seconds (default: 30).
        ttl: BGP TTL (default: 30).
        confirmed: Set true after user confirms.
    """
    if not confirmed:
        decline = await confirm_write(
            ctx,
            f"Apstra: create remote EVPN gateway '{gw_name}' ({gw_ip}) in blueprint {blueprint_id}. Confirm?",
        )
        if decline:
            return decline

    try:
        client = await get_apstra_client()
        payload: dict[str, Any] = {
            "gw_name": gw_name,
            "gw_ip": gw_ip,
            "gw_asn": gw_asn,
            "evpn_route_types": evpn_route_types,
            "local_gw_nodes": (local_gw_nodes if isinstance(local_gw_nodes, list) else [local_gw_nodes]),
            "keepalive_timer": keepalive_timer,
            "holdtime_timer": holdtime_timer,
            "ttl": ttl,
        }
        if password is not None:
            payload["password"] = password
        if evpn_interconnect_group_id is not None:
            payload["evpn_interconnect_group_id"] = evpn_interconnect_group_id

        response = await client.request(
            "POST",
            f"/api/blueprints/{blueprint_id}/remote_gateways",
            json_body=payload,
        )
        return {
            "guidelines": guidelines.get_base_guidelines() + guidelines.get_change_mgmt_guidelines(),
            "data": response.json(),
        }
    except Exception as e:
        return f"Error creating remote gateway: {format_http_error(e) if hasattr(e, 'response') else e}"
