"""AOS8 write tools (WRITE-01..12).

Classified via ``capability=`` (see ``docs/tool-annotation-rubric.md``): the 9
``aos8_manage_*`` tools are WRITE_DELETE; ``aos8_disconnect_client`` /
``aos8_reboot_ap`` / ``aos8_write_memory`` are OPERATIONAL with
``enable_gated=True``. All carry the derived ``aos8_write_delete`` enable tag,
so all are gated behind ENABLE_AOS8_WRITE_TOOLS=true, and every tool runs
through the elicitation middleware (confirm_write) before executing.

Every tool except aos8_write_memory returns:
    {"result": <api response>, "requires_write_memory_for": [<config_path>]}
Operational tools (disconnect_client, reboot_ap) always return
requires_write_memory_for=[] because they produce no pending state.
aos8_write_memory itself returns just {"result": ...}.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

import httpx
from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.aos8._registry import tool
from hpe_networking_mcp.platforms.aos8.client import AOS8APIError, AOS8AuthError, get_aos8_client
from hpe_networking_mcp.platforms.aos8.tools._helpers import format_aos8_error, post_object, strip_meta

_ACTION_MAP = {"create": "add", "update": "modify", "delete": "delete"}

_AAA_SERVER_OBJECT_BY_TYPE: dict[str, str] = {
    "radius": "rad_server",
    "tacacs": "tacacs_server",
    "ldap": "ldap_server",
    "internal": "internal_db_server",
}

# Shared parameter type aliases to reduce boilerplate across the 9 manage_X tools.
_ConfigPath = Annotated[str, Field(description="AOS8 hierarchy node (e.g. '/md', '/md/branch1'). Required.")]
_ActionType = Annotated[str, Field(description="One of 'create', 'update', or 'delete'.")]
_Confirmed = Annotated[bool, Field(description="Set to true after the user confirms in chat.")]


async def _post_managed_object(
    *,
    ctx: Context,
    object_name: str,
    identifier_field: str,
    config_path: str,
    action_type: str,
    payload: dict[str, Any],
    confirmed: bool,
    pretty_label: str,
) -> dict[str, Any] | str:
    """Shared body for the 9 manage_X tools (WRITE-01..09)."""
    if action_type not in _ACTION_MAP:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type {action_type!r}. Must be 'create', 'update', or 'delete'.",
            }
        )
    if not payload.get(identifier_field):
        raise ToolError({"status_code": 400, "message": f"payload must include {identifier_field!r}."})

    action = _ACTION_MAP[action_type]
    identifier = payload[identifier_field]
    summary = f"{action_type} {pretty_label} {identifier!r} at {config_path}"

    if not confirmed:
        decision = await confirm_write(ctx, message=f"The LLM wants to {summary}. Do you accept?")
        if decision is not None:
            return decision  # type: ignore[return-value]

    body = {object_name: {**payload, "_action": action}}
    client = get_aos8_client(ctx)
    try:
        result = await post_object(client, object_name, body, config_path=config_path)
    except (AOS8APIError, AOS8AuthError, httpx.HTTPError) as exc:
        logger.warning("AOS8 {} {} failed: {}", object_name, action_type, exc)
        return {"result": {"error": format_aos8_error(exc, summary)}, "requires_write_memory_for": []}

    logger.info("AOS8 {} {} {!r} at {} OK", object_name, action_type, identifier, config_path)
    return {"result": result, "requires_write_memory_for": [config_path]}


@tool(name="aos8_manage_ssid_profile", capability=Capability.WRITE_DELETE)
async def aos8_manage_ssid_profile(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[
        dict,
        Field(description="SSID profile body. Must include 'profile-name'."),
    ],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete an SSID profile.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    Call ``aos8_write_memory`` afterwards to persist the change to startup-config.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="ssid_prof",
        identifier_field="profile-name",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="SSID profile",
    )


@tool(name="aos8_manage_virtual_ap", capability=Capability.WRITE_DELETE)
async def aos8_manage_virtual_ap(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[dict, Field(description="Virtual AP body. Must include 'profile-name'.")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete a virtual AP profile.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="virtual_ap",
        identifier_field="profile-name",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="virtual AP",
    )


@tool(name="aos8_manage_ap_group", capability=Capability.WRITE_DELETE)
async def aos8_manage_ap_group(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[dict, Field(description="AP group body. Must include 'profile-name'.")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete an AP group.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="ap_group",
        identifier_field="profile-name",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="AP group",
    )


@tool(name="aos8_manage_user_role", capability=Capability.WRITE_DELETE)
async def aos8_manage_user_role(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[dict, Field(description="User role body. Must include 'rolename'.")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete a user role.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="role",
        identifier_field="rolename",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="user role",
    )


@tool(name="aos8_manage_vlan", capability=Capability.WRITE_DELETE)
async def aos8_manage_vlan(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[dict, Field(description="VLAN body. Must include 'id' (integer VLAN ID).")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete a VLAN.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="vlan_id",
        identifier_field="id",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="VLAN",
    )


@tool(name="aos8_manage_aaa_server", capability=Capability.WRITE_DELETE)
async def aos8_manage_aaa_server(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    server_type: Annotated[
        Literal["radius", "tacacs", "ldap", "internal"],
        Field(
            description=(
                "AAA server protocol: radius -> rad_server, tacacs -> tacacs_server, "
                "ldap -> ldap_server, internal -> internal_db_server."
            )
        ),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "AAA server body. Must include the protocol-specific name field "
                "(rad_server_name / tacacs_server_name / ldap_server_name / internal_db_server_name)."
            )
        ),
    ],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete an AAA server (RADIUS/TACACS/LDAP/internal).

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    if server_type not in _AAA_SERVER_OBJECT_BY_TYPE:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid server_type {server_type!r}. Must be 'radius', 'tacacs', 'ldap', or 'internal'.",
            }
        )
    object_name = _AAA_SERVER_OBJECT_BY_TYPE[server_type]
    return await _post_managed_object(
        ctx=ctx,
        object_name=object_name,
        identifier_field=f"{object_name}_name",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label=f"{server_type.upper()} AAA server",
    )


@tool(name="aos8_manage_aaa_server_group", capability=Capability.WRITE_DELETE)
async def aos8_manage_aaa_server_group(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[dict, Field(description="AAA server group body. Must include 'sg_name'.")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete an AAA server group.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="server_group_prof",
        identifier_field="sg_name",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="AAA server group",
    )


@tool(name="aos8_manage_acl", capability=Capability.WRITE_DELETE)
async def aos8_manage_acl(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[dict, Field(description="Session ACL body. Must include 'accname'.")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete a session ACL.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="acl_sess",
        identifier_field="accname",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="session ACL",
    )


@tool(name="aos8_manage_netdestination", capability=Capability.WRITE_DELETE)
async def aos8_manage_netdestination(
    ctx: Context,
    config_path: _ConfigPath,
    action_type: _ActionType,
    payload: Annotated[dict, Field(description="Netdestination body. Must include 'dstname'.")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Create, update, or delete a netdestination.

    Returns ``{"result": ..., "requires_write_memory_for": [config_path]}`` on success.
    """
    return await _post_managed_object(
        ctx=ctx,
        object_name="netdst",
        identifier_field="dstname",
        config_path=config_path,
        action_type=action_type,
        payload=payload,
        confirmed=confirmed,
        pretty_label="netdestination",
    )


@tool(name="aos8_disconnect_client", capability=Capability.OPERATIONAL, enable_gated=True)
async def aos8_disconnect_client(
    ctx: Context,
    mac: Annotated[str, Field(description="Client MAC address (e.g. 'aa:bb:cc:dd:ee:ff').")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Force-disconnect a wireless client by MAC address.

    Issues 'aaa user delete mac <mac>' via the operational POST endpoint.
    The client may immediately re-associate; this is NOT a blacklist.
    Returns ``{"result": ..., "requires_write_memory_for": []}`` —
    operational actions produce no pending config state.
    """
    if not confirmed:
        decision = await confirm_write(ctx, message=f"The LLM wants to disconnect client {mac}. Do you accept?")
        if decision is not None:
            return decision  # type: ignore[return-value]

    body = {"aaa_user_delete": {"mac": mac}}
    client = get_aos8_client(ctx)
    try:
        result = await post_object(client, "aaa_user_delete", body)
    except (AOS8APIError, AOS8AuthError, httpx.HTTPError) as exc:
        err = format_aos8_error(exc, f"disconnect client {mac}")
        return {"result": {"error": err}, "requires_write_memory_for": []}
    logger.info("AOS8 disconnect client {} OK", mac)
    return {"result": result, "requires_write_memory_for": []}


@tool(name="aos8_reboot_ap", capability=Capability.OPERATIONAL, enable_gated=True)
async def aos8_reboot_ap(
    ctx: Context,
    ap_name: Annotated[str, Field(description="AP hostname (as shown by aos8_get_ap_database).")],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Reboot a specific AP by name via the apboot endpoint.

    Calling this tool twice issues two reboot commands.
    Returns ``{"result": ..., "requires_write_memory_for": []}``.
    """
    if not confirmed:
        decision = await confirm_write(ctx, message=f"The LLM wants to reboot AP {ap_name}. Do you accept?")
        if decision is not None:
            return decision  # type: ignore[return-value]

    body = {"apboot": {"ap-name": ap_name}}
    client = get_aos8_client(ctx)
    try:
        result = await post_object(client, "apboot", body)
    except (AOS8APIError, AOS8AuthError, httpx.HTTPError) as exc:
        return {"result": {"error": format_aos8_error(exc, f"reboot AP {ap_name}")}, "requires_write_memory_for": []}
    logger.info("AOS8 reboot AP {} OK", ap_name)
    return {"result": result, "requires_write_memory_for": []}


@tool(name="aos8_write_memory", capability=Capability.OPERATIONAL, enable_gated=True)
async def aos8_write_memory(
    ctx: Context,
    config_path: Annotated[
        str,
        Field(
            description=(
                "Hierarchy node whose pending changes should be persisted "
                "(e.g. '/md'). Run once per affected config_path returned by manage_X tools."
            )
        ),
    ],
    confirmed: _Confirmed = False,
) -> dict[str, Any] | str:
    """Persist staged AOS8 config to startup-config for one config_path.

    AOS8 stages config per hierarchy node; nothing survives reboot until
    ``write memory`` is issued for that node. Run after each set of
    config-object writes — once per affected config_path.

    Returns ``{"result": ...}``. Does NOT include ``requires_write_memory_for``
    — that field would be circular here.
    """
    if not confirmed:
        decision = await confirm_write(ctx, message=f"The LLM wants to write memory at {config_path}. Do you accept?")
        if decision is not None:
            return decision  # type: ignore[return-value]

    client = get_aos8_client(ctx)
    try:
        response = await client.request(
            "POST",
            "/v1/configuration/object/write_memory",
            params={"config_path": config_path},
            json_body={},
        )
        result = strip_meta(response.json())
    except (AOS8APIError, AOS8AuthError, httpx.HTTPError) as exc:
        return {"result": {"error": format_aos8_error(exc, f"write memory at {config_path}")}}

    logger.info("AOS8 write_memory at {} OK", config_path)
    return {"result": result}
