"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Utilities Wi-Fi``
Operations in this file: 14
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
    name="mist_deauth_site_wireless_clients_connected_to_a_rogue",
    description="POST /api/v1/sites/{site_id}/rogues/{rogue_bssid}/deauth_clients\n\ndeauthSiteWirelessClientsConnectedToARogue\n\nSend Deauth frame to clients connected to a Rogue AP",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_deauth_site_wireless_clients_connected_to_a_rogue(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    rogue_bssid: Annotated[str, Field(description="path parameter 'rogue_bssid'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/rogues/{rogue_bssid}/deauth_clients",
        path_params={"site_id": site_id, "rogue_bssid": rogue_bssid},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_disconnect_site_multiple_clients",
    description="POST /api/v1/sites/{site_id}/clients/disconnect\n\ndisconnectSiteMultipleClients\n\nTo unauthorize multiple clients",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_disconnect_site_multiple_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/clients/disconnect",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_disconnect_site_wireless_client",
    description="POST /api/v1/sites/{site_id}/clients/{client_mac}/disconnect\n\ndisconnectSiteWirelessClient\n\nThis disconnect a client (and it’s likely to connect back)",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_disconnect_site_wireless_client(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/clients/{client_mac}/disconnect",
        path_params={"site_id": site_id, "client_mac": client_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_optimize_site_rrm",
    description="POST /api/v1/sites/{site_id}/rrm/optimize\n\noptimizeSiteRrm\n\nOptimize Site RRM",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_optimize_site_rrm(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/rrm/optimize",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_reauth_org_dot1x_wireless_client",
    description="POST /api/v1/orgs/{org_id}/clients/{client_mac}/coa\n\nreauthOrgDot1xWirelessClient\n\nTrigger a CoA (change of authorization) against a client",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_reauth_org_dot1x_wireless_client(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/clients/{client_mac}/coa",
        path_params={"org_id": org_id, "client_mac": client_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_reauth_site_dot1x_wireless_client",
    description="POST /api/v1/sites/{site_id}/clients/{client_mac}/coa\n\nreauthSiteDot1xWirelessClient\n\nTrigger a CoA (change of authorization) against a Wireless client",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_reauth_site_dot1x_wireless_client(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/clients/{client_mac}/coa",
        path_params={"site_id": site_id, "client_mac": client_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_reprovision_site_all_devices",
    description="POST /api/v1/sites/{site_id}/devices/reprovision\n\nreprovisionSiteAllDevices\n\nTo force all Devices to reprovision itself again.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_reprovision_site_all_devices(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/reprovision",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_reset_site_all_aps_to_use_rrm",
    description="POST /api/v1/sites/{site_id}/devices/reset_radio_config\n\nresetSiteAllApsToUseRrm\n\nReset all APs in the Site to use RRM",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_reset_site_all_aps_to_use_rrm(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/reset_radio_config",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_test_site_wlan_sms_global",
    description="POST /api/v1/utils/test_smsglobal\n\ntestSiteWlanSmsGlobal\n\nAllows validation of Global sms gateway credentials.\n\nIn case of success, a text message confirming successful setup should be received. In case of error, smsglobal error message are returned.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_test_site_wlan_sms_global(
    ctx: Context,
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/utils/test_smsglobal")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/utils/test_smsglobal",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_test_site_wlan_telstra_setup",
    description="POST /api/v1/utils/test_telstra\n\ntestSiteWlanTelstraSetup\n\nAllows validation of Telstra sms gateway credentials.\n\nIn case of success, a text message confirming successful setup should be received. In case of error, telstra error message are returned.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_test_site_wlan_telstra_setup(
    ctx: Context,
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/utils/test_telstra")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/utils/test_telstra",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_test_site_wlan_twilio_setup",
    description="POST /api/v1/utils/test_twilio\n\ntestSiteWlanTwilioSetup\n\nAllows validation of twilio setup\nIn case of success, a text message confirming successful setup should be received. In case of error, twilio error code and message are returned.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_test_site_wlan_twilio_setup(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/utils/test_twilio",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unauthorize_site_multiple_clients",
    description="POST /api/v1/sites/{site_id}/clients/unauthorize\n\nunauthorizeSiteMultipleClients\n\nThis unauthorize clients (if they are guest) and disconnect them. From the guest’s perspective, they will see the splash page again and go through the flow (e.g. Terms of Use) again.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_unauthorize_site_multiple_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/clients/unauthorize",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unauthorize_site_wireless_client",
    description="POST /api/v1/sites/{site_id}/clients/{client_mac}/unauthorize\n\nunauthorizeSiteWirelessClient\n\nThis unauthorize a client (if it’s a guest) and disconnect it. From the guest’s perspective, s/he will see the splash page again and go through the flow (e.g. Terms of Use) again.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_unauthorize_site_wireless_client(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/clients/{client_mac}/unauthorize",
        path_params={"site_id": site_id, "client_mac": client_mac},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_zeroize_site_fips_all_aps",
    description="POST /api/v1/sites/{site_id}/devices/zeroize\n\nzeroizeSiteFipsAllAps\n\nZeroize all FIPS APs in the Site",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_zeroize_site_fips_all_aps(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/zeroize",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )
