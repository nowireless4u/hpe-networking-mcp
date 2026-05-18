"""ClearPass policy-visualizer tools.

Two read-only tools backed by the :mod:`hpe_networking_mcp.platforms.clearpass.policy_visualizer`
engine:

- :func:`clearpass_list_policy_services` — slim summary list, suitable as
  a service picker before drilling in.
- :func:`clearpass_compile_policy_flow` — for a chosen service, returns
  a FlowGraph (nodes + edges) with first-applicable / evaluate-all /
  implicit-deny semantics baked in.

The compiler fetches the full reference set (services, role mappings,
enforcement policies + profiles, roles, auth methods + sources) on every
call so cross-references resolve correctly. On a typical tenant this is
~7 API calls totalling well under a second.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.api_adapter import adapt
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import compile_service
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_details import build_details
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import build
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY
from hpe_networking_mcp.platforms.clearpass.utils import build_query_string, clearpass_get

# High default fan-out limit for the compile path. ClearPass tenants
# rarely exceed this for any single category; if a real tenant gets
# truncated the warning surfaces in model.warnings as missing references.
_BULK_LIMIT = 1000


def _unwrap_items(response: Any) -> list[dict]:
    """Extract the ``items`` list from a ClearPass HAL collection response.

    Handles both ``{"_embedded": {"items": [...]}}`` (the documented
    HAL shape) and the bare ``{"items": [...]}`` shape some endpoints
    return. Returns an empty list on anything else.
    """
    if not isinstance(response, dict):
        return []
    embedded = response.get("_embedded")
    if isinstance(embedded, dict) and isinstance(embedded.get("items"), list):
        return embedded["items"]
    if isinstance(response.get("items"), list):
        return response["items"]
    return []


def _bulk_get(client: Any, path: str) -> list[dict]:
    """Fetch a full collection in one call (no pagination loop in v1)."""
    query = build_query_string(filter=None, sort=None, offset=0, limit=_BULK_LIMIT, calculate_count=False)
    return _unwrap_items(clearpass_get(client, path + query))


@tool(annotations=READ_ONLY)
async def clearpass_list_policy_services(
    ctx: Context,
    filter: str | None = None,
    sort: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict] | str:
    """List ClearPass policy services as a slim picker-ready summary.

    Returns one entry per service with the fields most useful for
    deciding which service to drill into with
    ``clearpass_compile_policy_flow``: ``id``, ``name``, ``type``,
    ``template``, ``enabled``, ``role_mapping_policy``, ``enf_policy``,
    ``description``, ``hit_count``, ``monitor_mode``.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. ``"+name"`` or ``"-order_no"``).
        limit: Max results per page (default 100).
        offset: Pagination offset (default 0).
    """
    try:
        from pyclearpass.api_policyelements import ApiPolicyElements

        client = await get_clearpass_session(ApiPolicyElements)
        query = build_query_string(filter, sort, offset, limit, calculate_count=False)
        items = _unwrap_items(clearpass_get(client, "/config/service" + query))
        return [
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "type": s.get("type"),
                "template": s.get("template"),
                "enabled": s.get("enabled"),
                "role_mapping_policy": s.get("role_mapping_policy"),
                "enf_policy": s.get("enf_policy"),
                "description": s.get("description"),
                "hit_count": s.get("hit_count"),
                "monitor_mode": s.get("monitor_mode"),
                "order_no": s.get("order_no"),
            }
            for s in items
        ]
    except Exception as e:
        return f"Error listing policy services: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_compile_policy_flow(
    ctx: Context,
    service_id: int | None = None,
    service_name: str | None = None,
    include_details: bool = False,
) -> dict | str:
    """Compile a ClearPass policy service into a FlowGraph for rendering.

    Fetches every dependency (services, role mappings, enforcement
    policies, enforcement profiles, roles, auth methods, auth sources),
    builds a cross-referenced policy model, then compiles the chosen
    service into a node + edge graph that an AI client can render as a
    Mermaid flowchart.

    Exactly one of ``service_id`` or ``service_name`` must be provided.

    Args:
        service_id: ClearPass numeric service ID (e.g. ``1`` for
            ``[Policy Manager Admin Network Login Service]``).
        service_name: ClearPass service name as it appears in the UI
            (e.g. ``"[AirGroup Authorization Service]"``).
        include_details: When true, attaches an ``"details"`` block
            with per-rule action / linked-names data suitable for an
            inspector view alongside the rendered diagram.

    Returns:
        Dict with ``service_id`` (engine slug), ``service_name``,
        ``service_type``, ``nodes`` (list of ``{id, type, label,
        sub_label, trace_rule_id, rank_group}``), ``edges`` (list of
        ``{from_id, to_id, label, reason}``), ``warnings`` (list of
        unresolved-reference messages), and optionally ``details``.
        Edge labels are one of ``""`` (unconditional), ``YES``, ``NO``,
        ``FAIL``, ``PASS``, ``CONTINUE``.
    """
    if (service_id is None) == (service_name is None):
        return "Error: provide exactly one of service_id or service_name"

    try:
        from pyclearpass.api_enforcementprofile import ApiEnforcementProfile
        from pyclearpass.api_policyelements import ApiPolicyElements

        client_pe = await get_clearpass_session(ApiPolicyElements)
        client_ep = await get_clearpass_session(ApiEnforcementProfile)

        services = _bulk_get(client_pe, "/config/service")
        role_mappings = _bulk_get(client_pe, "/role-mapping")
        enforcement_policies = _bulk_get(client_pe, "/enforcement-policy")
        enforcement_profiles = _bulk_get(client_ep, "/enforcement-profile")
        roles = _bulk_get(client_pe, "/role")
        auth_methods = _bulk_get(client_pe, "/auth-method")
        auth_sources = _bulk_get(client_pe, "/auth-source")

        # Resolve target by REST id/name (model uses slug-hashed internal IDs)
        target_name: str | None = None
        for svc in services:
            if service_id is not None and svc.get("id") == service_id:
                target_name = svc.get("name")
                break
            if service_name is not None and svc.get("name") == service_name:
                target_name = svc.get("name")
                break
        if target_name is None:
            available = sorted(s.get("name", "") for s in services)
            return {
                "status": "service_not_found",
                "service_id": service_id,
                "service_name": service_name,
                "available_services": available[:25],
                "available_count": len(available),
            }

        raw = adapt(
            services=services,
            role_mappings=role_mappings,
            enforcement_policies=enforcement_policies,
            enforcement_profiles=enforcement_profiles,
            roles=roles,
            auth_methods=auth_methods,
            auth_sources=auth_sources,
        )
        model = build(raw)
        target = next((s for s in model.services.values() if s.name == target_name), None)
        if target is None:
            return f"Internal error: service '{target_name}' resolved from REST but not present in compiled model"

        flow = compile_service(target, model)
        result: dict[str, Any] = {
            "service_id": flow.service_id,
            "service_name": flow.service_name,
            "service_type": flow.service_type,
            "nodes": [asdict(n) for n in flow.nodes],
            "edges": [asdict(e) for e in flow.edges],
            "warnings": list(model.warnings),
        }
        if include_details:
            result["details"] = build_details(target, model)
        return result
    except Exception as e:
        return f"Error compiling policy flow: {e}"
