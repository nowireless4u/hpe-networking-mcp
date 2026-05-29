"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Clients - NAC``
Operations in this file: 5
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_org_nac_client_events",
    description="GET /api/v1/orgs/{org_id}/nac_clients/events/count\n\ncountOrgNacClientEvents\n\nCount by Distinct Attributes of NAC Client-Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_nac_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listNacEventsDefinitions)")
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nac_clients/events/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_nac_clients",
    description="GET /api/v1/orgs/{org_id}/nac_clients/count\n\ncountOrgNacClients\n\nCount by Distinct Attributes of NAC Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_nac_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="NAC Policy Rule ID, if matched")] = None,
    last_nacrule_id: Annotated[str | None, Field(description="NAC Policy Rule ID, if matched")] = None,
    nacrule_matched: Annotated[bool | None, Field(description="NAC Policy Rule Matched")] = None,
    auth_type: Annotated[
        str | None,
        Field(
            description='Authentication type, e.g. "eap-tls", "eap-peap", "eap-ttls", "eap-teap", "mab", "psk", "device-auth"'
        ),
    ] = None,
    last_vlan_id: Annotated[str | None, Field(description="Vlan ID")] = None,
    last_nas_vendor: Annotated[str | None, Field(description="Vendor of NAS device")] = None,
    idp_id: Annotated[str | None, Field(description="SSO ID, if present and used")] = None,
    last_ssid: Annotated[str | None, Field(description="SSID")] = None,
    last_username: Annotated[str | None, Field(description="Username presented by the client")] = None,
    timestamp: Annotated[float | None, Field(description="Start time, in epoch")] = None,
    site_id: Annotated[str | None, Field(description="Site id if assigned, null if not assigned")] = None,
    last_ap: Annotated[str | None, Field(description="AP MAC connected to by client")] = None,
    mac: Annotated[str | None, Field(description="MAC address")] = None,
    last_status: Annotated[
        str | None, Field(description='Connection status of client i.e "permitted", "denied, "session_ended"')
    ] = None,
    type: Annotated[str | None, Field(description='Client type i.e. "wireless", "wired" etc.')] = None,
    mdm_compliance_status: Annotated[
        str | None, Field(description='MDM compliance of client i.e "compliant", "not compliant"')
    ] = None,
    mdm_provider: Annotated[
        str | None, Field(description='MDM provider of client’s organization eg "intune", "jamf"')
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nac_clients/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "last_nacrule_id": last_nacrule_id,
            "nacrule_matched": nacrule_matched,
            "auth_type": auth_type,
            "last_vlan_id": last_vlan_id,
            "last_nas_vendor": last_nas_vendor,
            "idp_id": idp_id,
            "last_ssid": last_ssid,
            "last_username": last_username,
            "timestamp": timestamp,
            "site_id": site_id,
            "last_ap": last_ap,
            "mac": mac,
            "last_status": last_status,
            "type": type,
            "mdm_compliance_status": mdm_compliance_status,
            "mdm_provider": mdm_provider,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_nac_client_events",
    description="GET /api/v1/orgs/{org_id}/nac_clients/events/search\n\nsearchOrgNacClientEvents\n\nSearch NAC Client Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_nac_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listNacEventsDefinitions)")
    ] = None,
    nacrule_id: Annotated[str | None, Field(description="NAC Policy Rule ID, if matched")] = None,
    nacrule_matched: Annotated[bool | None, Field(description="NAC Policy Rule Matched")] = None,
    dryrun_nacrule_id: Annotated[
        str | None, Field(description="NAC Policy Dry Run Rule ID, if present and matched")
    ] = None,
    dryrun_nacrule_matched: Annotated[
        bool | None,
        Field(
            description="True - if dryrun rule present and matched with priority, False - if not matched or not present"
        ),
    ] = None,
    auth_type: Annotated[
        str | None,
        Field(
            description='Authentication type, e.g. "eap-tls", "eap-peap", "eap-ttls", "eap-teap", "mab", "psk", "device-auth"'
        ),
    ] = None,
    vlan: Annotated[int | None, Field(description="Vlan name or ID assigned to the client")] = None,
    nas_vendor: Annotated[str | None, Field(description="Vendor of NAS device")] = None,
    bssid: Annotated[str | None, Field(description="BSSID")] = None,
    idp_id: Annotated[str | None, Field(description="SSO ID, if present and used")] = None,
    idp_role: Annotated[str | None, Field(description="IDP returned roles/groups for the user")] = None,
    idp_username: Annotated[str | None, Field(description="Username presented to the Identity Provider")] = None,
    resp_attrs: Annotated[Any | None, Field(description="Radius attributes returned by NAC to NAS derive")] = None,
    ssid: Annotated[str | None, Field(description="SSID")] = None,
    username: Annotated[str | None, Field(description="Username presented by the client")] = None,
    site_id: Annotated[str | None, Field(description="Site id")] = None,
    ap: Annotated[str | None, Field(description="AP MAC")] = None,
    random_mac: Annotated[bool | None, Field(description="AP random macMAC")] = None,
    mac: Annotated[str | None, Field(description="MAC address")] = None,
    timestamp: Annotated[float | None, Field(description="Start time, in epoch")] = None,
    usermac_label: Annotated[str | None, Field(description="Labels derived from usermac entry")] = None,
    text: Annotated[str | None, Field(description="Partial / full MAC address, username, device_mac or ap")] = None,
    nas_ip: Annotated[str | None, Field(description="IP address of NAS device")] = None,
    ingress_vlan: Annotated[str | None, Field(description="Vendor specific Vlan ID in radius requests")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order.")
    ] = "wxid",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nac_clients/events/search",
        path_params={"org_id": org_id},
        query_params={
            "type": type,
            "nacrule_id": nacrule_id,
            "nacrule_matched": nacrule_matched,
            "dryrun_nacrule_id": dryrun_nacrule_id,
            "dryrun_nacrule_matched": dryrun_nacrule_matched,
            "auth_type": auth_type,
            "vlan": vlan,
            "nas_vendor": nas_vendor,
            "bssid": bssid,
            "idp_id": idp_id,
            "idp_role": idp_role,
            "idp_username": idp_username,
            "resp_attrs": resp_attrs,
            "ssid": ssid,
            "username": username,
            "site_id": site_id,
            "ap": ap,
            "random_mac": random_mac,
            "mac": mac,
            "timestamp": timestamp,
            "usermac_label": usermac_label,
            "text": text,
            "nas_ip": nas_ip,
            "ingress_vlan": ingress_vlan,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_nac_clients",
    description="GET /api/v1/orgs/{org_id}/nac_clients/search\n\nsearchOrgNacClients\n\nSearch Org NAC Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_nac_clients(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    ap: Annotated[str | None, Field(description="MAC Address of the AP the client is/was connected to")] = None,
    auth_type: Annotated[
        str | None,
        Field(
            description='Authentication type, e.g. "eap-tls", "eap-peap", "eap-ttls", "eap-teap", "mab", "psk", "device-auth"'
        ),
    ] = None,
    cert_expiry_duration: Annotated[
        str | None,
        Field(
            description='Filter by certificate expiry within a specific duration from now (e.g., "7d" for 7 days, "1m" for 1 month)'
        ),
    ] = None,
    edr_managed: Annotated[
        bool | None, Field(description="Filters NAC clients that are integrated with EDR providers")
    ] = None,
    edr_provider: Annotated[Any | None, Field(description="EDR provider of client's organization")] = None,
    edr_status: Annotated[Any | None, Field(description="EDR Status of the NAC client")] = None,
    family: Annotated[
        str | None,
        Field(
            description='Partial / full Client family (e.g. "Phone/Tablet/Wearable", "Access Point"). Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `Surveillance*` and `*urveillance*` match `Surveillance Camera`). Suffix-only wildcar...'
        ),
    ] = None,
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Client hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are not supported"
        ),
    ] = None,
    idp_id: Annotated[str | None, Field(description="SSO ID, if present and used")] = None,
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported"
        ),
    ] = None,
    mdm_compliance: Annotated[
        str | None, Field(description='MDM compliance of client i.e "compliant", "not compliant"')
    ] = None,
    mdm_provider: Annotated[
        str | None, Field(description='MDM provider of client’s organization eg "intune", "jamf"')
    ] = None,
    mdm_managed: Annotated[
        bool | None, Field(description="Filters NAC clients that are managed by MDM providers")
    ] = None,
    mfg: Annotated[
        str | None,
        Field(
            description='Partial / full Client manufacturer (e.g. "apple", "cisco", "juniper"). Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `Raspberry Pi*` and `*Pi*` match `Raspberry Pi Trading Ltd`). Suffix-only wildcards (e.g. `...'
        ),
    ] = None,
    model: Annotated[str | None, Field(description='Client model, e.g. "iPhone 12", "MX100"')] = None,
    nacrule_name: Annotated[str | None, Field(description="NAC Policy Rule Name matched")] = None,
    nacrule_id: Annotated[str | None, Field(description="NAC Policy Rule ID, if matched")] = None,
    nacrule_matched: Annotated[bool | None, Field(description="NAC Policy Rule Matched")] = None,
    nas_vendor: Annotated[str | None, Field(description="Vendor of NAS device")] = None,
    nas_ip: Annotated[str | None, Field(description="IP address of NAS device")] = None,
    ingress_vlan: Annotated[str | None, Field(description="Vendor specific Vlan ID in radius requests")] = None,
    os: Annotated[str | None, Field(description='Client OS, e.g. "iOS 18.1", "Android", "Windows", "Linux"')] = None,
    ssid: Annotated[str | None, Field(description="SSID")] = None,
    status: Annotated[
        Any | None,
        Field(description='Connection status of client i.e "permitted", "denied, "session_started", "session_stopped"'),
    ] = None,
    text: Annotated[
        str | None, Field(description="partial / full MAC address, last_username, device_mac, nas_ip or last_ap")
    ] = None,
    timestamp: Annotated[float | None, Field(description="Start time, in epoch")] = None,
    type: Annotated[str | None, Field(description='Client type i.e. "wireless", "wired" etc.')] = None,
    usermac_label: Annotated[Any | None, Field(description="Labels derived from usermac entry")] = None,
    username: Annotated[str | None, Field(description="Username presented by the client")] = None,
    vlan: Annotated[str | None, Field(description="Vlan name or ID assigned to the client")] = None,
    site_id: Annotated[str | None, Field(description="Site id if assigned, null if not assigned")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order.")
    ] = "wxid",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nac_clients/search",
        path_params={"org_id": org_id},
        query_params={
            "ap": ap,
            "auth_type": auth_type,
            "cert_expiry_duration": cert_expiry_duration,
            "edr_managed": edr_managed,
            "edr_provider": edr_provider,
            "edr_status": edr_status,
            "family": family,
            "hostname": hostname,
            "idp_id": idp_id,
            "mac": mac,
            "mdm_compliance": mdm_compliance,
            "mdm_provider": mdm_provider,
            "mdm_managed": mdm_managed,
            "mfg": mfg,
            "model": model,
            "nacrule_name": nacrule_name,
            "nacrule_id": nacrule_id,
            "nacrule_matched": nacrule_matched,
            "nas_vendor": nas_vendor,
            "nas_ip": nas_ip,
            "ingress_vlan": ingress_vlan,
            "os": os,
            "ssid": ssid,
            "status": status,
            "text": text,
            "timestamp": timestamp,
            "type": type,
            "usermac_label": usermac_label,
            "username": username,
            "vlan": vlan,
            "site_id": site_id,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_send_org_nac_client_co_a",
    description="POST /api/v1/orgs/{org_id}/nac_clients/{client_mac}/coa\n\nsendOrgNacClientCoA\n\nSends CoA (Change of Authorization) command to a NAC client.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_send_org_nac_client_co_a(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/nac_clients/{client_mac}/coa",
        path_params={"org_id": org_id, "client_mac": client_mac},
        query_params=None,
        body=body,
    )
