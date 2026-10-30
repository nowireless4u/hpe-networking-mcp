"""Read the Central scope hierarchy (global, site-collections, sites, device-groups, devices).

Produces the node list that scope_builder._build_tree turns into the scope tree. It
replaces the cnxdevice/v1/debug/get_scope_data route, which Central retired in
2026-10 (404 Route Not Found).
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from hpe_networking_mcp.platforms.central.utils import paginated_fetch, retry_central_command

# network-config/v1/hierarchy scopeType -> scope tree node type
_HIERARCHY_TYPES: dict[str, str] = {
    "org": "GLOBAL",
    "site_collection": "SITE_COLLECTION",
    "site": "SITE",
    "device_collection": "DEVICE_COLLECTION",
    "device": "DEVICE",
}

# Concurrent per-device hierarchy reads
_HIERARCHY_CONCURRENCY = 8


def _scope_node(scope_id: str, name: str, node_type: str, hier_path: list[str], **meta: Any) -> dict:
    """One scope entry in the shape _build_tree expects (hier_path is leaf-to-root)."""
    return {
        "scope_id": scope_id,
        "type": node_type,
        "hier_path": hier_path,
        "meta": {"scope_name": name, **meta},
    }


def _pick_device_path(paths: list[list[dict]]) -> list[dict]:
    """Pick the device's site path (device -> site -> [collection] -> org), else its first path."""
    site_paths = [p for p in paths if any(s.get("scopeType") == "site" for s in p)]
    if site_paths:
        return max(site_paths, key=len)
    return paths[0] if paths else []


async def _list_scopes(conn: Any, api_path: str) -> list[dict]:
    """Read every item of a network-config/v1 scope list (sites, site-collections, device-groups)."""
    items: list[dict] = []
    while True:
        resp = await retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=api_path,
            api_params={"limit": 100, "offset": len(items)},
        )
        page = resp.get("msg", {}).get("items") or []
        items.extend(page)
        if not page or len(items) >= (resp.get("msg", {}).get("total") or 0):
            return items


def _device_node(scope_id: str, device: dict, serial: str, hier_path: list[str], personas: dict[str, str]) -> dict:
    """DEVICE scope node, with model/MAC/persona from the monitoring inventory record."""
    node = _scope_node(
        scope_id,
        device.get("deviceName") or serial,
        "DEVICE",
        hier_path,
        device_type=device.get("deviceType", "N/A"),
        device_model=device.get("model", "N/A"),
        part_number=device.get("partNumber"),
        mac_address=device.get("macAddress"),
        serial_number=serial,
    )
    node["persona"] = personas.get((device.get("deviceFunction") or "").lower())
    return node


async def _device_paths_bulk(conn: Any, site_paths: dict[str, list[str]], global_id: str) -> dict[str, tuple]:
    """serial -> (device scope id, leaf-to-root path) from GET network-config/v1alpha1/devices (paged)."""
    out: dict[str, tuple] = {}
    for item in await _list_scopes(conn, "network-config/v1alpha1/devices"):
        serial, scope_id = item.get("scopeName"), str(item.get("scopeId") or item.get("id") or "")
        if not serial or not scope_id:
            continue
        if item.get("siteId") and str(item["siteId"]) in site_paths:
            path = [scope_id, *site_paths[str(item["siteId"])]]
        elif item.get("deviceGroupId"):
            path = [scope_id, str(item["deviceGroupId"]), global_id]
        else:
            path = [scope_id, global_id]
        out[serial] = (scope_id, path)
    return out


async def _device_paths_per_device(conn: Any, serials: list[str]) -> dict[str, tuple]:
    """serial -> (device scope id, leaf-to-root path), one GET network-config/v1/hierarchy per device."""
    semaphore = asyncio.Semaphore(_HIERARCHY_CONCURRENCY)

    async def one(serial: str) -> tuple[str, tuple] | None:
        async with semaphore:
            try:
                resp = await retry_central_command(
                    central_conn=conn,
                    api_method="GET",
                    api_path="network-config/v1/hierarchy",
                    api_params={"id": serial, "type": "device"},
                )
            except Exception as e:  # one unreadable device must not sink the whole tree
                logger.warning("Scope hierarchy unavailable for device {}: {}", serial, e)
                return None
        paths = [item.get("hierarchy") or [] for item in resp.get("msg", {}).get("items", [])]
        path = _pick_device_path([p for p in paths if p])
        if not path or path[0].get("scopeType") != "device":
            return None
        return serial, (str(path[0]["scopeId"]), [str(s["scopeId"]) for s in path])

    results = await asyncio.gather(*(one(s) for s in serials))
    return dict(r for r in results if r is not None)


async def fetch_scope_data(conn: Any) -> dict:
    """Build the scope node list from the network-config scope routes.

    Replaces the retired cnxdevice/v1/debug/get_scope_data route (404 Route Not Found
    since 2026-10). Reads the global scope, site-collections, sites and device-groups
    (network-config/v1), the device inventory (network-monitoring/v1/devices) and each
    device's scope. Device scopes come from the paged network-config/v1alpha1/devices
    list; if that route is unavailable, from one GET network-config/v1/hierarchy per
    device (documented, but rate-limited: about a minute for 700 devices).
    """
    global_resp = await retry_central_command(central_conn=conn, api_method="GET", api_path="network-config/v1/global")
    global_msg = global_resp.get("msg", {})
    global_id = str(global_msg.get("scopeId") or global_msg.get("id") or "")
    if not global_id:
        return {"devices": []}

    nodes, site_paths = await _container_scopes(conn, global_id)
    personas = await _persona_by_function(conn)
    inventory = {
        d.get("serialNumber") or d.get("id"): d
        for d in await paginated_fetch(conn, "network-monitoring/v1/devices", limit=100)
        if d.get("serialNumber") or d.get("id")
    }
    try:
        device_paths = await _device_paths_bulk(conn, site_paths, global_id)
    except Exception as e:
        logger.warning("Bulk device scope list unavailable ({}); reading each device's hierarchy", e)
        device_paths = await _device_paths_per_device(conn, list(inventory))
    for serial, (scope_id, path) in device_paths.items():
        nodes.append(_device_node(scope_id, inventory.get(serial, {}), serial, path, personas))
    return {"devices": nodes}


async def _container_scopes(conn: Any, global_id: str) -> tuple[list[dict], dict[str, list[str]]]:
    """Global, site-collection, site and device-group nodes, plus each site's leaf-to-root path."""
    nodes: list[dict] = [_scope_node(global_id, "Global", "GLOBAL", [global_id])]
    for sc in await _list_scopes(conn, "network-config/v1/site-collections"):
        sc_id = str(sc.get("scopeId") or sc.get("id"))
        nodes.append(_scope_node(sc_id, sc.get("scopeName", sc_id), "SITE_COLLECTION", [sc_id, global_id]))
    site_paths: dict[str, list[str]] = {}
    for site in await _list_scopes(conn, "network-config/v1/sites"):
        site_id = str(site.get("scopeId") or site.get("id"))
        parent = [str(site["collectionId"])] if site.get("collectionId") else []
        site_paths[site_id] = [site_id, *parent, global_id]
        nodes.append(_scope_node(site_id, site.get("scopeName", site_id), "SITE", site_paths[site_id]))
    for dg in await _list_scopes(conn, "network-config/v1/device-groups"):
        dg_id = str(dg.get("scopeId") or dg.get("id"))
        nodes.append(_scope_node(dg_id, dg.get("scopeName", dg_id), "DEVICE_COLLECTION", [dg_id, global_id]))
    return nodes, site_paths


async def _persona_by_function(conn: Any) -> dict[str, str]:
    """Map a device's deviceFunction (e.g. "Campus Access Point") to its config persona (CAMPUS_AP)."""
    try:
        resp = await retry_central_command(
            central_conn=conn, api_method="GET", api_path="network-config/v1alpha1/device-persona-mapping"
        )
    except Exception as e:
        logger.warning("Device persona mapping unavailable: {}", e)
        return {}
    mapping: dict[str, str] = {}
    for device_type in resp.get("msg", {}).get("device_type_list", []):
        for persona in device_type.get("supported-persona", []):
            for key in (persona.get("label"), persona.get("name")):
                if key and persona.get("value"):
                    mapping[key.lower()] = persona["value"]
    return mapping
