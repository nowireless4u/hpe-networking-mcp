"""Aruba Central MRT troubleshooting tools.

Wraps the ``network-troubleshooting/v1`` actions beyond the existing
hand-curated set (``central_ping`` / ``_traceroute`` / ``_cable_test`` /
``_show_commands`` / ``_port_bounce_*`` / ``_poe_bounce_*`` /
``_disconnect_*``).

Pattern notes:

* The MRT troubleshooting surface uniformly splits by device family:
  ``aos-s``, ``aps``, ``cx``, ``gateways``. Where an action is offered
  on multiple families, this module exposes one tool that takes a
  ``device_family`` Literal and routes internally — matches existing
  ``central_ping`` which also takes a ``device_type`` arg.
* Every action POST returns a ``task_id``; results are then polled via
  ``GET .../<action>/async-operations/<task_id>``. A shared helper
  (``central_get_troubleshooting_task_status``) wraps that poll for any
  family / action.
* ``list-tasks`` per family is wrapped by one shared
  ``central_list_troubleshooting_tasks``.
* Operational actions (reboot, halt, locate, disconnect) use the
  ``OPERATIONAL`` annotation — they run immediately without a confirmation
  prompt and are not gated behind ``ENABLE_CENTRAL_WRITE_TOOLS`` (matches
  the existing reboot / disconnect / port-bounce surface).
"""

from typing import Annotated, Literal

from fastmcp import Context
from fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

OPERATIONAL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

DeviceFamilyAll = Literal["aos-s", "aps", "cx", "gateways"]
DeviceFamilyApGwSw = Literal["aps", "cx", "gateways"]
DeviceFamilyApGw = Literal["aps", "gateways"]
DeviceFamilyApCx = Literal["aps", "cx"]
DeviceFamilySwitchGw = Literal["aos-s", "cx", "gateways"]


def _call(conn, method: str, path: str, params: dict | None = None, data: dict | None = None) -> dict | str:
    try:
        response = retry_central_command(
            central_conn=conn,
            api_method=method,
            api_path=path,
            api_params=params or {},
            api_data=data or {},
        )
    except ToolError:
        raise
    except Exception as e:
        # retry_central_command raises a bare Exception on 4xx/5xx; surface the
        # real upstream detail as a ToolError so it isn't masked to a generic
        # "Error calling tool" in code mode (the message carries the HTTP body).
        raise ToolError({"status_code": 502, "message": f"Central troubleshooting request failed: {e}"}) from e
    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    raise ToolError({"status_code": code, "message": f"Central API error (HTTP {code}): {response.get('msg')}"})


def _post_action(conn, family: str, serial: str, action: str, payload: dict | None) -> dict | str:
    return _call(
        conn,
        "POST",
        f"network-troubleshooting/v1/{family}/{serial}/{action}",
        data=payload or {},
    )


# ---------------------------------------------------------------------------
# Shared status pollers + listing
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_troubleshooting_task_status(
    ctx: Context,
    device_family: Annotated[
        DeviceFamilyAll,
        Field(description="Device family the original action was started on."),
    ],
    serial_number: Annotated[str, Field(description="Device serial number the task ran against.")],
    action: Annotated[
        str,
        Field(
            description=(
                "Action name as it appears in the URI — e.g. ``ping``, ``traceroute``, "
                "``poeBounce``, ``portBounce``, ``cableTest``, ``getArpTable``, "
                "``showCommands``, ``http``, ``https``, ``tcp``, ``iperf``, "
                "``speedtest``, ``nslookup``, ``aaa``, ``pingSweep``. "
                "Case-sensitive — match the original POST endpoint."
            ),
        ),
    ],
    task_id: Annotated[str, Field(description="Task identifier returned by the original action POST.")],
) -> dict | str:
    """Poll the status / result of a previously-initiated troubleshooting action.

    Every MRT troubleshooting POST returns a ``task_id``; results are
    asynchronous. Pass that ``task_id`` back here along with the device
    family, serial, and action name to fetch the completed result.
    """
    conn = ctx.lifespan_context["central_conn"]
    return _call(
        conn,
        "GET",
        f"network-troubleshooting/v1/{device_family}/{serial_number}/{action}/async-operations/{task_id}",
    )


@tool(annotations=READ_ONLY)
async def central_list_troubleshooting_tasks(
    ctx: Context,
    device_family: Annotated[
        DeviceFamilyAll,
        Field(description="Device family to list tasks for."),
    ],
    serial_number: Annotated[str, Field(description="Device serial number.")],
) -> dict | str:
    """List recent troubleshooting tasks queued / running / completed on a device."""
    conn = ctx.lifespan_context["central_conn"]
    return _call(
        conn,
        "GET",
        f"network-troubleshooting/v1/{device_family}/{serial_number}/list-tasks",
    )


@tool(annotations=READ_ONLY)
async def central_list_supported_show_commands(
    ctx: Context,
    device_family: Annotated[
        DeviceFamilyAll,
        Field(description="Device family to list supported show commands for."),
    ],
    serial_number: Annotated[str, Field(description="Device serial number.")],
) -> dict | str:
    """List show commands supported on a device.

    Distinct from ``central_show_commands`` which executes a show command.
    This wraps ``GET /<family>/<serial>/show-commands`` (the catalogue
    of allowed commands).
    """
    conn = ctx.lifespan_context["central_conn"]
    return _call(
        conn,
        "GET",
        f"network-troubleshooting/v1/{device_family}/{serial_number}/show-commands",
    )


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_event_extra_attributes(
    ctx: Context,
    filter: str | None = None,
) -> dict | str:
    """Get the catalogue of extra attributes available on events.

    Drives the ``filter`` parameter you can pass to ``central_get_events``
    — each entry describes the attribute name, type, and example values.
    """
    conn = ctx.lifespan_context["central_conn"]
    params: dict = {}
    if filter:
        params["filter"] = filter
    return _call(
        conn,
        "GET",
        "network-troubleshooting/v1/event-extra-attributes",
        params=params,
    )


# ---------------------------------------------------------------------------
# Probes (HTTP / HTTPS / TCP / Iperf / Speedtest / Nslookup / AAA / ARP)
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_probe_http(
    ctx: Context,
    device_family: Annotated[DeviceFamilyApGwSw, Field(description="``'aps'``, ``'cx'``, or ``'gateways'``.")],
    serial_number: Annotated[str, Field(description="Device serial number.")],
    payload: Annotated[
        dict,
        Field(description="Probe request body — typically ``{url, count, timeout, ...}`` per Central docs."),
    ],
) -> dict | str:
    """Initiate an HTTP probe from a device.

    Returns a ``task_id`` to poll via ``central_get_troubleshooting_task_status``.
    """
    return _post_action(ctx.lifespan_context["central_conn"], device_family, serial_number, "http", payload)


@tool(annotations=READ_ONLY)
async def central_probe_https(
    ctx: Context,
    device_family: Annotated[DeviceFamilyApGwSw, Field(description="``'aps'``, ``'cx'``, or ``'gateways'``.")],
    serial_number: Annotated[str, Field(description="Device serial number.")],
    payload: Annotated[
        dict,
        Field(description="Probe request body — typically ``{url, count, timeout, ...}`` per Central docs."),
    ],
) -> dict | str:
    """Initiate an HTTPS probe from a device.

    Returns a ``task_id`` to poll via ``central_get_troubleshooting_task_status``.
    """
    return _post_action(ctx.lifespan_context["central_conn"], device_family, serial_number, "https", payload)


@tool(annotations=READ_ONLY)
async def central_probe_tcp(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number (TCP probe is only offered on APs).")],
    payload: Annotated[
        dict,
        Field(description="TCP probe body — typically ``{destination, port, count, ...}`` per Central docs."),
    ],
) -> dict | str:
    """Initiate a TCP probe from an AP. Returns a ``task_id`` to poll."""
    return _post_action(ctx.lifespan_context["central_conn"], "aps", serial_number, "tcp", payload)


@tool(annotations=READ_ONLY)
async def central_iperf_test(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number (iperf is only offered on gateways).")],
    payload: Annotated[
        dict,
        Field(description="iperf body — typically ``{server, port, protocol, duration, ...}`` per Central docs."),
    ],
) -> dict | str:
    """Initiate an iperf bandwidth test from a gateway. Returns a ``task_id`` to poll."""
    return _post_action(ctx.lifespan_context["central_conn"], "gateways", serial_number, "iperf", payload)


@tool(annotations=READ_ONLY)
async def central_speedtest(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number (speedtest is only offered on APs).")],
    payload: Annotated[
        dict | None,
        Field(description="Optional speedtest body (e.g. server hints). Omit for defaults."),
    ] = None,
) -> dict | str:
    """Initiate an Internet speed test from an AP. Returns a ``task_id`` to poll."""
    return _post_action(ctx.lifespan_context["central_conn"], "aps", serial_number, "speedtest", payload)


@tool(annotations=READ_ONLY)
async def central_nslookup(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number (nslookup is only offered on APs).")],
    payload: Annotated[
        dict,
        Field(description="nslookup body — typically ``{hostname, dns_server, ...}`` per Central docs."),
    ],
) -> dict | str:
    """Initiate an nslookup from an AP. Returns a ``task_id`` to poll."""
    return _post_action(ctx.lifespan_context["central_conn"], "aps", serial_number, "nslookup", payload)


@tool(annotations=READ_ONLY)
async def central_test_aaa(
    ctx: Context,
    device_family: Annotated[DeviceFamilyApCx, Field(description="``'aps'`` or ``'cx'``.")],
    serial_number: Annotated[str, Field(description="Device serial number.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "AAA test body — typically ``{server_group, username, password, ...}`` "
                "per Central docs. NOTE: credentials in the payload are subject to "
                "existing PII tokenization; verify the server-side flow before "
                "running against tenants with untrusted AI clients."
            ),
        ),
    ],
) -> dict | str:
    """Initiate an AAA authentication test from an AP or CX switch. Returns a ``task_id`` to poll."""
    return _post_action(ctx.lifespan_context["central_conn"], device_family, serial_number, "aaa", payload)


@tool(annotations=READ_ONLY)
async def central_get_arp_table(
    ctx: Context,
    device_family: Annotated[
        Literal["aos-s", "aps", "gateways"],
        Field(
            description=(
                "Device family (``'aos-s'``, ``'aps'``, or ``'gateways'`` — CX uses the show-commands path instead)."
            )
        ),
    ],
    serial_number: Annotated[str, Field(description="Device serial number.")],
    payload: Annotated[
        dict | None,
        Field(description="Optional ARP-table filter body. Omit for the full table."),
    ] = None,
) -> dict | str:
    """Retrieve the device's ARP table. Returns a ``task_id`` to poll."""
    return _post_action(
        ctx.lifespan_context["central_conn"],
        device_family,
        serial_number,
        "getArpTable",
        payload,
    )


@tool(annotations=READ_ONLY)
async def central_ping_sweep(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number (pingSweep is only offered on gateways).")],
    payload: Annotated[
        dict,
        Field(description="Ping-sweep body — typically ``{subnet, count, timeout, ...}`` per Central docs."),
    ],
) -> dict | str:
    """Initiate a ping sweep across a subnet from a gateway. Returns a ``task_id`` to poll."""
    return _post_action(ctx.lifespan_context["central_conn"], "gateways", serial_number, "pingSweep", payload)


# ---------------------------------------------------------------------------
# Operational — reboot, locate, halt, rebootSwarm, disconnect-extras
# ---------------------------------------------------------------------------


@tool(annotations=OPERATIONAL)
async def central_reboot_device(
    ctx: Context,
    device_family: Annotated[DeviceFamilyAll, Field(description="Device family.")],
    serial_number: Annotated[str, Field(description="Device serial number.")],
    payload: Annotated[
        dict | None,
        Field(description="Optional reboot body (vendor-specific flags). Omit for defaults."),
    ] = None,
) -> dict | str:
    """Reboot a device (operational — runs immediately, no confirmation). Returns a ``task_id`` to poll."""
    return _post_action(
        ctx.lifespan_context["central_conn"],
        device_family,
        serial_number,
        "reboot",
        payload,
    )


@tool(annotations=OPERATIONAL)
async def central_reboot_swarm(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Swarm conductor AP serial number.")],
    payload: Annotated[
        dict | None,
        Field(description="Optional reboot body. Omit for defaults."),
    ] = None,
) -> dict | str:
    """Reboot an entire IAP / Instant swarm (operational — runs immediately, no confirmation)."""
    return _post_action(ctx.lifespan_context["central_conn"], "aps", serial_number, "rebootSwarm", payload)


@tool(annotations=OPERATIONAL)
async def central_locate_device(
    ctx: Context,
    device_family: Annotated[
        Literal["aos-s", "aps", "cx"],
        Field(description="Device family (locate isn't offered on gateways)."),
    ],
    serial_number: Annotated[str, Field(description="Device serial number.")],
    payload: Annotated[
        dict | None,
        Field(description="Optional locate body — typically ``{duration_seconds}``."),
    ] = None,
) -> dict | str:
    """Blink a device's locator LED (operational). Returns a ``task_id`` to poll."""
    return _post_action(
        ctx.lifespan_context["central_conn"],
        device_family,
        serial_number,
        "locate",
        payload,
    )


@tool(annotations=OPERATIONAL)
async def central_halt_gateway(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    payload: Annotated[
        dict | None,
        Field(description="Optional halt body. Omit for defaults."),
    ] = None,
) -> dict | str:
    """Halt (graceful shutdown) a gateway (operational — runs immediately, no confirmation)."""
    return _post_action(ctx.lifespan_context["central_conn"], "gateways", serial_number, "halt", payload)


@tool(annotations=OPERATIONAL)
async def central_disconnect_user_by_network(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    network_name: Annotated[str, Field(description="Network name (SSID) to disconnect users from.")],
) -> dict | str:
    """Disconnect users on a specific network/SSID on an AP (operational — runs immediately, no confirmation)."""
    return _post_action(
        ctx.lifespan_context["central_conn"],
        "aps",
        serial_number,
        "disconnectUserByNetwork",
        {"networkName": network_name},
    )


@tool(annotations=OPERATIONAL)
async def central_disconnect_user_by_mac_on_ap(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
    user_mac_address: Annotated[str, Field(description="MAC address of the user/client to disconnect.")],
) -> dict | str:
    """Disconnect a specific user/client by MAC address from an AP (operational — runs immediately, no confirmation)."""
    return _post_action(
        ctx.lifespan_context["central_conn"],
        "aps",
        serial_number,
        "disconnectUserByMacAddress",
        {"userMacAddress": user_mac_address},
    )


@tool(annotations=OPERATIONAL)
async def central_disconnect_user_all_on_ap(
    ctx: Context,
    serial_number: Annotated[str, Field(description="AP serial number.")],
) -> dict | str:
    """Disconnect ALL users on an AP (operational — runs immediately, no confirmation).

    Service-affecting — every associated client gets bounced. Use only
    during planned maintenance windows.
    """
    return _post_action(
        ctx.lifespan_context["central_conn"],
        "aps",
        serial_number,
        "disconnectUserAll",
        None,
    )


@tool(annotations=OPERATIONAL)
async def central_disconnect_client_all_on_gateway(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
) -> dict | str:
    """Disconnect ALL clients terminating on a gateway (operational — runs immediately, no confirmation).

    Service-affecting — every client connected through the gateway gets
    bounced. Use only during planned maintenance windows.
    """
    return _post_action(
        ctx.lifespan_context["central_conn"],
        "gateways",
        serial_number,
        "disconnectClientAll",
        None,
    )


@tool(annotations=OPERATIONAL)
async def central_disconnect_client_by_mac_on_gateway(
    ctx: Context,
    serial_number: Annotated[str, Field(description="Gateway serial number.")],
    client_mac_address: Annotated[str, Field(description="MAC address of the client to disconnect.")],
) -> dict | str:
    """Disconnect a specific client by MAC address from a gateway (operational — runs immediately, no confirmation)."""
    return _post_action(
        ctx.lifespan_context["central_conn"],
        "gateways",
        serial_number,
        "disconnectClientByMacAddress",
        {"clientMacAddress": client_mac_address},
    )
