"""Aruba Central ``Security`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``Security`` OpenAPI tag-group. Wrappers
delegate to ``_get_resource`` / ``_manage_resource`` in
``security_policy.py`` — the same shared helpers used by the
hand-curated Roles & Policy tools.
"""

# ruff: noqa: E501

from typing import Annotated

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.tools.security_policy import (
    _CONFIRMED_FIELD,
    _DEVICE_FUNCTION_FIELD,
    _SCOPE_ID_FIELD,
    _get_resource,
    _manage_resource,
)

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)

# ----- 802dot11k -----


@tool(annotations=READ_ONLY)
async def central_get__802dot11k(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``802dot11k`` configurations from Central.

    The 802.11k protocol provides mechanisms for APs and clients to dynamically measure the available radio resources. In an 802.11k enabled network, APs and clients can send neighbor reports, beacon reports, and link measurement reports to each other. This allows the APs and clients to take appropriate connection actions. This includes configuring channel-report, reference of Beacon Report Request profile and RRM IE Profile, etc.

    Parameters:
        name: Specific ``802dot11k`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dot11k-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage__802dot11k(
    ctx: Context,
    name: Annotated[str, Field(description="``802dot11k`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``802dot11k`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get__802dot11k`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``802dot11k`` configuration in Central.

    The 802.11k protocol provides mechanisms for APs and clients to dynamically measure the available radio resources. In an 802.11k enabled network, APs and clients can send neighbor reports, beacon reports, and link measurement reports to each other. This allows the APs and clients to take appropriate connection actions. This includes configuring channel-report, reference of Beacon Report Request profile and RRM IE Profile, etc.
    """
    return await _manage_resource(
        ctx,
        "dot11k-profiles",
        "802dot11k",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- 802dot11k-bcn-rpt-req -----


@tool(annotations=READ_ONLY)
async def central_get__802dot11k_bcn_rpt_req(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``802dot11k-bcn-rpt-req`` configurations from Central.

    The Beacon Report Requests are sent only to 802.11k-compliant clients that advertise Beacon Report Capability in their Radio Measurement (RM) Enabled Capabilities Information Element (IE). This includes configuring BSSID, Channel, Measurement Mode, Regulatory Class, etc.

    Parameters:
        name: Specific ``802dot11k-bcn-rpt-req`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "bcn-rpt-req-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage__802dot11k_bcn_rpt_req(
    ctx: Context,
    name: Annotated[str, Field(description="``802dot11k-bcn-rpt-req`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``802dot11k-bcn-rpt-req`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get__802dot11k_bcn_rpt_req`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``802dot11k-bcn-rpt-req`` configuration in Central.

    The Beacon Report Requests are sent only to 802.11k-compliant clients that advertise Beacon Report Capability in their Radio Measurement (RM) Enabled Capabilities Information Element (IE). This includes configuring BSSID, Channel, Measurement Mode, Regulatory Class, etc.
    """
    return await _manage_resource(
        ctx,
        "bcn-rpt-req-profiles",
        "802dot11k-bcn-rpt-req",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- 802dot11k-rrm-ie -----


@tool(annotations=READ_ONLY)
async def central_get__802dot11k_rrm_ie(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``802dot11k-rrm-ie`` configurations from Central.

    The Radio Resource Management (RRM) Information Element (IE) is essential for optimizing radio resource allocation in wireless networks. It enhances network performance by managing resources efficiently and ensuring quality of service.

    Parameters:
        name: Specific ``802dot11k-rrm-ie`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "rrm-ie-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage__802dot11k_rrm_ie(
    ctx: Context,
    name: Annotated[str, Field(description="``802dot11k-rrm-ie`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``802dot11k-rrm-ie`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get__802dot11k_rrm_ie`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``802dot11k-rrm-ie`` configuration in Central.

    The Radio Resource Management (RRM) Information Element (IE) is essential for optimizing radio resource allocation in wireless networks. It enhances network performance by managing resources efficiently and ensuring quality of service.
    """
    return await _manage_resource(
        ctx,
        "rrm-ie-profiles",
        "802dot11k-rrm-ie",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- aaa-captive-portal -----


@tool(annotations=READ_ONLY)
async def central_get_aaa_captive_portal(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aaa-captive-portal`` configurations from Central.

    Use this API to configure external captive portal profiles for guest users. For AP and GW, When the captive portal profile is applied to an SSID or a wired profile, the users connecting to the SSID or wired network are assigned a role with the captive portal rule. For CX, when the client is 802.1x or MAC authenticated through RADIUS-server, the redirect parameters in this profile can be applied through user-role, Downloadable User Role and RADIUS Vendor Specific Attribute. This feature is applicable for AP, CX and GW.

    Parameters:
        name: Specific ``aaa-captive-portal`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "captive-portal", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aaa_captive_portal(
    ctx: Context,
    name: Annotated[str, Field(description="``aaa-captive-portal`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aaa-captive-portal`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aaa_captive_portal`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aaa-captive-portal`` configuration in Central.

    Use this API to configure external captive portal profiles for guest users. For AP and GW, When the captive portal profile is applied to an SSID or a wired profile, the users connecting to the SSID or wired network are assigned a role with the captive portal rule. For CX, when the client is 802.1x or MAC authenticated through RADIUS-server, the redirect parameters in this profile can be applied through user-role, Downloadable User Role and RADIUS Vendor Specific Attribute. This feature is applicable for AP, CX and GW.
    """
    return await _manage_resource(
        ctx,
        "captive-portal",
        "aaa-captive-portal",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- aaa-dot1xauth -----


@tool(annotations=READ_ONLY)
async def central_get_aaa_dot1xauth(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aaa-dot1xauth`` configurations from Central.

    IEEE 802.1X is an IEEE Standard for port-based Network Access Control (PNAC). This standard provides an authentication mechanism to devices wishing to attach to a LAN or WLAN. IEEE 802.1X defines the encapsulation of the Extensible Authentication Protocol (EAP) over IEEE 802, which is known as EAP over LAN (EAPOL). 802.1X authentication involves three entities, a supplicant, an authenticator, and an authentication server. *Supplicant*: An entity that wants to get authenticated. *Authenticator*: A network device, such as an Ethernet switch that authenticates the Supplicant. *Authentication Server*: Typically a host running software supporting the RADIUS and EAP protocols that provides an authentication service to an authenticator. Until the Supplicant is authenticated, 802.1X Authenticator allows only EAPOL traffic through the port to which the Supplicant is connected. Only after the authentication is successful, the authenticator allows normal traffic from the Supplicant.

    Parameters:
        name: Specific ``aaa-dot1xauth`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dot1xauth", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aaa_dot1xauth(
    ctx: Context,
    name: Annotated[str, Field(description="``aaa-dot1xauth`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aaa-dot1xauth`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aaa_dot1xauth`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aaa-dot1xauth`` configuration in Central.

    IEEE 802.1X is an IEEE Standard for port-based Network Access Control (PNAC). This standard provides an authentication mechanism to devices wishing to attach to a LAN or WLAN. IEEE 802.1X defines the encapsulation of the Extensible Authentication Protocol (EAP) over IEEE 802, which is known as EAP over LAN (EAPOL). 802.1X authentication involves three entities, a supplicant, an authenticator, and an authentication server. *Supplicant*: An entity that wants to get authenticated. *Authenticator*: A network device, such as an Ethernet switch that authenticates the Supplicant. *Authentication Server*: Typically a host running software supporting the RADIUS and EAP protocols that provides an authentication service to an authenticator. Until the Supplicant is authenticated, 802.1X Authenticator allows only EAPOL traffic through the port to which the Supplicant is connected. Only after the authentication is successful, the authenticator allows normal traffic from the Supplicant.
    """
    return await _manage_resource(
        ctx,
        "dot1xauth",
        "aaa-dot1xauth",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- aaa-dot1xsupp -----


@tool(annotations=READ_ONLY)
async def central_get_aaa_dot1xsupp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aaa-dot1xsupp`` configurations from Central.

    802.1X supplicant configurations.

    Parameters:
        name: Specific ``aaa-dot1xsupp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "dot1xsupp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aaa_dot1xsupp(
    ctx: Context,
    name: Annotated[str, Field(description="``aaa-dot1xsupp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aaa-dot1xsupp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aaa_dot1xsupp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aaa-dot1xsupp`` configuration in Central.

    802.1X supplicant configurations.
    """
    return await _manage_resource(
        ctx,
        "dot1xsupp",
        "aaa-dot1xsupp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- aaa-macauth -----


@tool(annotations=READ_ONLY)
async def central_get_aaa_macauth(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aaa-macauth`` configurations from Central.

    The MAC Authentication method grants access to a secure network by authenticating devices for access to the network. The switch uses the MAC address of the client in the configured format as the identity to authenticate the client against a RADIUS server.

    Parameters:
        name: Specific ``aaa-macauth`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "macauth", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aaa_macauth(
    ctx: Context,
    name: Annotated[str, Field(description="``aaa-macauth`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aaa-macauth`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aaa_macauth`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aaa-macauth`` configuration in Central.

    The MAC Authentication method grants access to a secure network by authenticating devices for access to the network. The switch uses the MAC address of the client in the configured format as the identity to authenticate the client against a RADIUS server.
    """
    return await _manage_resource(
        ctx,
        "macauth",
        "aaa-macauth",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- aaa-profile -----


@tool(annotations=READ_ONLY)
async def central_get_aaa_profile(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aaa-profile`` configurations from Central.

    AAA profile configurations.

    Parameters:
        name: Specific ``aaa-profile`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "aaa-profile", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aaa_profile(
    ctx: Context,
    name: Annotated[str, Field(description="``aaa-profile`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aaa-profile`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aaa_profile`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aaa-profile`` configuration in Central.

    AAA profile configurations.
    """
    return await _manage_resource(
        ctx,
        "aaa-profile",
        "aaa-profile",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- aaa-stateful-dot1x -----


@tool(annotations=READ_ONLY)
async def central_get_aaa_stateful_dot1x(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``aaa-stateful-dot1x`` configurations from Central.

    Condigure a Stateful 802.1X profile. This feature when enabled allows the controller to learn the identity and role of a user connected to a third-party AP, and is useful for authenticating users to networks with APs from multiple vendors. This has been widely used in SDWAN branch gateways to learn the roles of clients connected to IAP. When any 801.1X authenticator sends RADIUS request to server, gateway inspects this request and its response from server to learn about the authentication state of the user. Gateway then applies an identity-based user role to the device.

    Parameters:
        name: Specific ``aaa-stateful-dot1x`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "stateful-dot1x-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_aaa_stateful_dot1x(
    ctx: Context,
    name: Annotated[str, Field(description="``aaa-stateful-dot1x`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``aaa-stateful-dot1x`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_aaa_stateful_dot1x`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``aaa-stateful-dot1x`` configuration in Central.

    Condigure a Stateful 802.1X profile. This feature when enabled allows the controller to learn the identity and role of a user connected to a third-party AP, and is useful for authenticating users to networks with APs from multiple vendors. This has been widely used in SDWAN branch gateways to learn the roles of clients connected to IAP. When any 801.1X authenticator sends RADIUS request to server, gateway inspects this request and its response from server to learn about the authentication state of the user. Gateway then applies an identity-based user role to the device.
    """
    return await _manage_resource(
        ctx,
        "stateful-dot1x-profiles",
        "aaa-stateful-dot1x",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ap-certificate-usage -----


@tool(annotations=READ_ONLY)
async def central_get_ap_certificate_usage(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ap-certificate-usage`` configurations from Central.

    Configure the certificate assignments on AP. Certificates must be installed before they can be assigned to an application. Use this API to configure certificates that should be used for an application. This feature is only applicable for AP.

    Parameters:
        name: Specific ``ap-certificate-usage`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificate-usage", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ap_certificate_usage(
    ctx: Context,
    name: Annotated[str, Field(description="``ap-certificate-usage`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ap-certificate-usage`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ap_certificate_usage`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ap-certificate-usage`` configuration in Central.

    Configure the certificate assignments on AP. Certificates must be installed before they can be assigned to an application. Use this API to configure certificates that should be used for an application. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "certificate-usage",
        "ap-certificate-usage",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- auth-server -----


@tool(annotations=READ_ONLY)
async def central_get_auth_server(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``auth-server`` configurations from Central.

    Use this API to configure an external RADIUS server for user authentication. You can configure parameters such as server IP, authentication port, accounting port, shared key, etc. This feature is applicable for all devices.

    Parameters:
        name: Specific ``auth-server`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-servers", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_auth_server(
    ctx: Context,
    name: Annotated[str, Field(description="``auth-server`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``auth-server`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_auth_server`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``auth-server`` configuration in Central.

    Use this API to configure an external RADIUS server for user authentication. You can configure parameters such as server IP, authentication port, accounting port, shared key, etc. This feature is applicable for all devices.
    """
    return await _manage_resource(
        ctx,
        "auth-servers",
        "auth-server",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- auth-server-global -----


@tool(annotations=READ_ONLY)
async def central_get_auth_server_global(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``auth-server-global`` configurations from Central.

    Global configurations for Auth servers.

    Parameters:
        name: Specific ``auth-server-global`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-server-global-config", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_auth_server_global(
    ctx: Context,
    name: Annotated[str, Field(description="``auth-server-global`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``auth-server-global`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_auth_server_global`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``auth-server-global`` configuration in Central.

    Global configurations for Auth servers.
    """
    return await _manage_resource(
        ctx,
        "auth-server-global-config",
        "auth-server-global",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- auth-survivability -----


@tool(annotations=READ_ONLY)
async def central_get_auth_survivability(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``auth-survivability`` configurations from Central.

    Configure the paramaters of authentication survivability. The authentication survivability feature requires ClearPass Policy Manager 6.0.2 or later, and is applicable only when external servers such as RADIUS are configured for the SSID. When enabled, AP authenticates the previously connected clients using EAP-TLS or MAC authentication even when connectivity to ClearPass Policy Manager is temporarily lost. The authentication survivability feature is not applicable when a RADIUS server is configured as an internal server. This feature is only applicable for GW.

    Parameters:
        name: Specific ``auth-survivability`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "auth-survivability", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_auth_survivability(
    ctx: Context,
    name: Annotated[str, Field(description="``auth-survivability`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``auth-survivability`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_auth_survivability`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``auth-survivability`` configuration in Central.

    Configure the paramaters of authentication survivability. The authentication survivability feature requires ClearPass Policy Manager 6.0.2 or later, and is applicable only when external servers such as RADIUS are configured for the SSID. When enabled, AP authenticates the previously connected clients using EAP-TLS or MAC authentication even when connectivity to ClearPass Policy Manager is temporarily lost. The authentication survivability feature is not applicable when a RADIUS server is configured as an internal server. This feature is only applicable for GW.
    """
    return await _manage_resource(
        ctx,
        "auth-survivability",
        "auth-survivability",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- certificate -----


@tool(annotations=READ_ONLY)
async def central_get_certificate(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``certificate`` configurations from Central.

    Certificate Objects API can be used to associate certificates from the certificate-store with their appropriate types for use in VPN authentication, web server SSL/TLS, OCSP validation, and other security features.

    Parameters:
        name: Specific ``certificate`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificates", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_certificate(
    ctx: Context,
    name: Annotated[str, Field(description="``certificate`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``certificate`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_certificate`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``certificate`` configuration in Central.

    Certificate Objects API can be used to associate certificates from the certificate-store with their appropriate types for use in VPN authentication, web server SSL/TLS, OCSP validation, and other security features.
    """
    return await _manage_resource(
        ctx,
        "certificates",
        "certificate",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- certificate-rcp -----


@tool(annotations=READ_ONLY)
async def central_get_certificate_rcp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``certificate-rcp`` configurations from Central.

    Configuration of Certificate TA (Trust Anchor) and Certificate RCP (Revocation-Check-Point).

    Parameters:
        name: Specific ``certificate-rcp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificate-rcp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_certificate_rcp(
    ctx: Context,
    name: Annotated[str, Field(description="``certificate-rcp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``certificate-rcp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_certificate_rcp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``certificate-rcp`` configuration in Central.

    Configuration of Certificate TA (Trust Anchor) and Certificate RCP (Revocation-Check-Point).
    """
    return await _manage_resource(
        ctx,
        "certificate-rcp",
        "certificate-rcp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- certificate-store -----


@tool(annotations=READ_ONLY)
async def central_get_certificate_store(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``certificate-store`` configurations from Central.

    Certificate store configurations.

    Parameters:
        name: Specific ``certificate-store`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "certificate-store", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_certificate_store(
    ctx: Context,
    name: Annotated[str, Field(description="``certificate-store`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``certificate-store`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_certificate_store`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``certificate-store`` configuration in Central.

    Certificate store configurations.
    """
    return await _manage_resource(
        ctx,
        "certificate-store",
        "certificate-store",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- copp -----


@tool(annotations=READ_ONLY)
async def central_get_copp(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``copp`` configurations from Central.

    A list of profiles defining the CoPP configuration.

    Parameters:
        name: Specific ``copp`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "copp", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_copp(
    ctx: Context,
    name: Annotated[str, Field(description="``copp`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``copp`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_copp`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``copp`` configuration in Central.

    A list of profiles defining the CoPP configuration.
    """
    return await _manage_resource(
        ctx,
        "copp",
        "copp",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- device-certificate -----


@tool(annotations=READ_ONLY)
async def central_get_device_certificate(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``device-certificate`` configurations from Central.

    Configuration of Device Certificate Attributes.

    Parameters:
        name: Specific ``device-certificate`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "device-certificates", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_device_certificate(
    ctx: Context,
    name: Annotated[str, Field(description="``device-certificate`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``device-certificate`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_device_certificate`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``device-certificate`` configuration in Central.

    Configuration of Device Certificate Attributes.
    """
    return await _manage_resource(
        ctx,
        "device-certificates",
        "device-certificate",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- est -----


@tool(annotations=READ_ONLY)
async def central_get_est(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``est`` configurations from Central.

    Configurate the parameters of Enrollment over Secure Transport(EST) Profile. EST supports automatic enrollment of certificates with the EST Server. The certificates can be enrolled or re-enrolled automatically by configuring an EST profile on the device. Certificate Enrollment with EST allows users to use their own PKI instead of the factory or self-signed certificates available on the Instant AP. This enables the user to have maximum visibility and control over the management of the PKI used and address any issues related to security by themselves in a scaled environment.This feature is applicable for all devices.

    Parameters:
        name: Specific ``est`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "est-profiles", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_est(
    ctx: Context,
    name: Annotated[str, Field(description="``est`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``est`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_est`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``est`` configuration in Central.

    Configurate the parameters of Enrollment over Secure Transport(EST) Profile. EST supports automatic enrollment of certificates with the EST Server. The certificates can be enrolled or re-enrolled automatically by configuring an EST profile on the device. Certificate Enrollment with EST allows users to use their own PKI instead of the factory or self-signed certificates available on the Instant AP. This enables the user to have maximum visibility and control over the management of the PKI used and address any issues related to security by themselves in a scaled environment.This feature is applicable for all devices.
    """
    return await _manage_resource(
        ctx,
        "est-profiles",
        "est",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- firewall -----


@tool(annotations=READ_ONLY)
async def central_get_firewall(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``firewall`` configurations from Central.

    Firewall monitors and controls incoming and outgoing network traffic based on predefined security rules. It protects against unauthorized access, cyberattacks, and malicious threats. Firewall is superset of several of its submodules which all together help in keeping traffic secure. This model defines the Aruba firewall profile hierarchy used by APs and Gateways to enforce stateful packet inspection and policy-based traffic controls. It organizes firewall configuration into reusable profiles with separate IPv4 and IPv6 subtrees, and exposes tunables for session handling, traffic classification, rate limiting/mitigation controls, multicast handling, and other datapath behaviors.

    Parameters:
        name: Specific ``firewall`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "firewall", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_firewall(
    ctx: Context,
    name: Annotated[str, Field(description="``firewall`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``firewall`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_firewall`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``firewall`` configuration in Central.

    Firewall monitors and controls incoming and outgoing network traffic based on predefined security rules. It protects against unauthorized access, cyberattacks, and malicious threats. Firewall is superset of several of its submodules which all together help in keeping traffic secure. This model defines the Aruba firewall profile hierarchy used by APs and Gateways to enforce stateful packet inspection and policy-based traffic controls. It organizes firewall configuration into reusable profiles with separate IPv4 and IPv6 subtrees, and exposes tunables for session handling, traffic classification, rate limiting/mitigation controls, multicast handling, and other datapath behaviors.
    """
    return await _manage_resource(
        ctx,
        "firewall",
        "firewall",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- gw-certificate-usage -----


@tool(annotations=READ_ONLY)
async def central_get_gw_certificate_usage(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``gw-certificate-usage`` configurations from Central.

    Gw-certificate-usage helps to assign server certificates, CA certificates, and configure revocation checking via CRL or OCSP. Supports primary/secondary revocation methods with configurable enforcement levels and timeouts. Includes built-in OCSP responder functionality, certificate groups for multiple VPN scenarios, and separate certificates for WebUI and captive portal.

    Parameters:
        name: Specific ``gw-certificate-usage`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "gw-certificate-usage", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_gw_certificate_usage(
    ctx: Context,
    name: Annotated[str, Field(description="``gw-certificate-usage`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``gw-certificate-usage`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_gw_certificate_usage`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``gw-certificate-usage`` configuration in Central.

    Gw-certificate-usage helps to assign server certificates, CA certificates, and configure revocation checking via CRL or OCSP. Supports primary/secondary revocation methods with configurable enforcement levels and timeouts. Includes built-in OCSP responder functionality, certificate groups for multiple VPN scenarios, and separate certificates for WebUI and captive portal.
    """
    return await _manage_resource(
        ctx,
        "gw-certificate-usage",
        "gw-certificate-usage",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- internal-user -----


@tool(annotations=READ_ONLY)
async def central_get_internal_user(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``internal-user`` configurations from Central.

    Manage the AP's local user database for RADIUS (employee) and captive portal (guest) access. The local database supports up to 512 users on APs. Use this API to retrieve the list of Internal User profiles. This feature is only applicable for AP.

    Parameters:
        name: Specific ``internal-user`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "internal-user", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_internal_user(
    ctx: Context,
    name: Annotated[str, Field(description="``internal-user`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``internal-user`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_internal_user`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``internal-user`` configuration in Central.

    Manage the AP's local user database for RADIUS (employee) and captive portal (guest) access. The local database supports up to 512 users on APs. Use this API to retrieve the list of Internal User profiles. This feature is only applicable for AP.
    """
    return await _manage_resource(
        ctx,
        "internal-user",
        "internal-user",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- keychain -----


@tool(annotations=READ_ONLY)
async def central_get_keychain(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``keychain`` configurations from Central.

    Keychain is a secure mechanism for storing and managing cryptographic keys and authentication credentials to facilitate secure access and communication between devices.

    Parameters:
        name: Specific ``keychain`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "keychains", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_keychain(
    ctx: Context,
    name: Annotated[str, Field(description="``keychain`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``keychain`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_keychain`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``keychain`` configuration in Central.

    Keychain is a secure mechanism for storing and managing cryptographic keys and authentication credentials to facilitate secure access and communication between devices.
    """
    return await _manage_resource(
        ctx,
        "keychains",
        "keychain",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mac-lockout -----


@tool(annotations=READ_ONLY)
async def central_get_mac_lockout(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mac-lockout`` configurations from Central.

    Manage MAC address lockout profiles for Aruba devices, enabling administrators to block specific MAC addresses from accessing the network. This API allows you to define and retrieve MAC lockout profiles, specifying which devices are denied access and for how long. Use this API to retrieve the list of MAC Lockout profiles.

    Parameters:
        name: Specific ``mac-lockout`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mac-lockout", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mac_lockout(
    ctx: Context,
    name: Annotated[str, Field(description="``mac-lockout`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mac-lockout`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mac_lockout`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mac-lockout`` configuration in Central.

    Manage MAC address lockout profiles for Aruba devices, enabling administrators to block specific MAC addresses from accessing the network. This API allows you to define and retrieve MAC lockout profiles, specifying which devices are denied access and for how long. Use this API to retrieve the list of MAC Lockout profiles.
    """
    return await _manage_resource(
        ctx,
        "mac-lockout",
        "mac-lockout",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- macsec -----


@tool(annotations=READ_ONLY)
async def central_get_macsec(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``macsec`` configurations from Central.

    MAC Security (MACsec) allows authorized systems that attach to and interconnect LANs in a network to maintain confidentiality of transmitted data and to take measures against frames transmitted or modified by unauthorized devices.

    Parameters:
        name: Specific ``macsec`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "macsec", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_macsec(
    ctx: Context,
    name: Annotated[str, Field(description="``macsec`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``macsec`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_macsec`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``macsec`` configuration in Central.

    MAC Security (MACsec) allows authorized systems that attach to and interconnect LANs in a network to maintain confidentiality of transmitted data and to take measures against frames transmitted or modified by unauthorized devices.
    """
    return await _manage_resource(
        ctx,
        "macsec",
        "macsec",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- mka -----


@tool(annotations=READ_ONLY)
async def central_get_mka(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``mka`` configurations from Central.

    The MACsec Key Agreement (MKA) protocol facilitates the secure management and exchange of cryptographic keys for establishing secure Ethernet communications.

    Parameters:
        name: Specific ``mka`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "mka", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_mka(
    ctx: Context,
    name: Annotated[str, Field(description="``mka`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``mka`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_mka`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``mka`` configuration in Central.

    The MACsec Key Agreement (MKA) protocol facilitates the secure management and exchange of cryptographic keys for establishing secure Ethernet communications.
    """
    return await _manage_resource(
        ctx,
        "mka",
        "mka",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- passpoint-identity -----


@tool(annotations=READ_ONLY)
async def central_get_passpoint_identity(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``passpoint-identity`` configurations from Central.

    This is used to define a Network Access Identifier (NAI) realm information that can be sent as an Access network Query Protocol (ANQP) information element in a GAS query response. The settings configured in this profile determine the NAI realm elements that are included as part of a GAS Response frame.

    Parameters:
        name: Specific ``passpoint-identity`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "passpoint-identity", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_passpoint_identity(
    ctx: Context,
    name: Annotated[str, Field(description="``passpoint-identity`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``passpoint-identity`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_passpoint_identity`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``passpoint-identity`` configuration in Central.

    This is used to define a Network Access Identifier (NAI) realm information that can be sent as an Access network Query Protocol (ANQP) information element in a GAS query response. The settings configured in this profile determine the NAI realm elements that are included as part of a GAS Response frame.
    """
    return await _manage_resource(
        ctx,
        "passpoint-identity",
        "passpoint-identity",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- port-security -----


@tool(annotations=READ_ONLY)
async def central_get_port_security(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``port-security`` configurations from Central.

    Port security enables a user to configure each switch port with a unique list of the MAC addresses of devices that are authorized to access the network through that port. This security enables individual ports to detect, prevent, and log attempts by unauthorized devices to communicate through the switch.

    Parameters:
        name: Specific ``port-security`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "port-security", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_port_security(
    ctx: Context,
    name: Annotated[str, Field(description="``port-security`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``port-security`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_port_security`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``port-security`` configuration in Central.

    Port security enables a user to configure each switch port with a unique list of the MAC addresses of devices that are authorized to access the network through that port. This security enables individual ports to detect, prevent, and log attempts by unauthorized devices to communicate through the switch.
    """
    return await _manage_resource(
        ctx,
        "port-security",
        "port-security",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- radius-modifiers -----


@tool(annotations=READ_ONLY)
async def central_get_radius_modifiers(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``radius-modifiers`` configurations from Central.

    Configure the RADIUS modifier profile to customize the attributes that are included, excluded and modified in the RADIUS request before it is sent to the authentication server. This feature is only applicable for AP and GW.

    Parameters:
        name: Specific ``radius-modifiers`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "radius-modifiers", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_radius_modifiers(
    ctx: Context,
    name: Annotated[str, Field(description="``radius-modifiers`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``radius-modifiers`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_radius_modifiers`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``radius-modifiers`` configuration in Central.

    Configure the RADIUS modifier profile to customize the attributes that are included, excluded and modified in the RADIUS request before it is sent to the authentication server. This feature is only applicable for AP and GW.
    """
    return await _manage_resource(
        ctx,
        "radius-modifiers",
        "radius-modifiers",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ----- ubt -----


@tool(annotations=READ_ONLY)
async def central_get_ubt(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """Get ``ubt`` configurations from Central.

    Configuration of UBT (User based Tunnel) Profiles. This feature creates UBT GRE tunnel between the switch and the controller when UBT users are present on the switch. It encapsulates incoming packets from end-hosts in GRE and forwards them to the Mobility Controller.The feature is enabled on a Per User Tunneled Node basis.

    Parameters:
        name: Specific ``ubt`` identifier (OpenAPI path param: ``name``). If omitted, returns all.
    """
    return await _get_resource(ctx, "ubt", name)


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_ubt(
    ctx: Context,
    name: Annotated[str, Field(description="``ubt`` identifier (OpenAPI path param: ``name``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``ubt`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_ubt`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``ubt`` configuration in Central.

    Configuration of UBT (User based Tunnel) Profiles. This feature creates UBT GRE tunnel between the switch and the controller when UBT users are present on the switch. It encapsulates incoming packets from end-hosts in GRE and forwards them to the Mobility Controller.The feature is enabled on a Per User Tunneled Node basis.
    """
    return await _manage_resource(
        ctx,
        "ubt",
        "ubt",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
