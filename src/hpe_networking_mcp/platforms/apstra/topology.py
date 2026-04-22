"""Apstra topology helpers — redundancy-group expansion for SVI configuration."""

from __future__ import annotations

from typing import Any

from loguru import logger

from hpe_networking_mcp.platforms.apstra.client import ApstraClient


async def get_individual_leafs_from_system_ids(
    client: ApstraClient,
    blueprint_id: str,
    system_ids: list[str],
) -> list[str]:
    """Expand a list of system IDs so that redundancy groups resolve to individual leafs.

    Apstra's ``bound_to`` field accepts leaf-pair (redundancy-group) IDs as-is,
    but ``svi_ips`` must reference each physical leaf individually. This helper
    consults ``/experience/web/system-info`` to map redundancy-group IDs back
    to their constituent leafs; other IDs pass through unchanged.

    Args:
        client: Authenticated Apstra client.
        blueprint_id: Blueprint under which to resolve systems.
        system_ids: IDs possibly referencing redundancy groups.

    Returns:
        List of individual leaf IDs. On any error, the original ``system_ids``
        are returned unchanged so callers still receive a best-effort value.
    """
    try:
        response = await client.request("GET", f"/api/blueprints/{blueprint_id}/experience/web/system-info")
        payload: Any = response.json()
    except Exception as e:
        logger.error("Apstra: failed to resolve system-info for leaf expansion — {}", e)
        return list(system_ids)

    systems: list[dict[str, Any]] = payload.get("data", []) if isinstance(payload, dict) else []

    individual_leafs: list[str] = []
    for system_id in system_ids:
        is_redundancy_group = any(s.get("id") == system_id and s.get("role") == "redundancy_group" for s in systems)
        if is_redundancy_group:
            members = [
                s["id"]
                for s in systems
                if s.get("role") == "leaf" and s.get("redundancy_group_id") == system_id and "id" in s
            ]
            if members:
                individual_leafs.extend(members)
            else:
                # No members resolved — preserve the original ID as a fallback
                individual_leafs.append(system_id)
        else:
            individual_leafs.append(system_id)

    logger.debug("Apstra: expanded system_ids {} to individual leafs {}", system_ids, individual_leafs)
    return individual_leafs
