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


def _resolve_service_name(
    services: list[dict],
    service_id: int | None,
    service_name: str | None,
) -> tuple[str | None, list[str]]:
    """Resolve a service identifier to its exact REST name.

    Tier order — first non-empty result wins:

    1. ``service_id`` exact match (unambiguous).
    2. ``service_name`` exact match (case-sensitive — what the UI shows).
    3. ``service_name`` case-insensitive exact match (handles casing slips).
    4. ``service_name`` case-insensitive substring match (handles
       operator phrasing like ``"ClearPass No Wireless For You"`` when
       the real name is ``"No Wireless For You Auth Service"``). One
       match → use it. Multiple matches → return them all as candidates
       so the caller can disambiguate.

    Returns:
        ``(target_name, candidates)`` — ``target_name`` is the resolved
        exact name (``None`` if zero or ambiguous matches), ``candidates``
        is the multi-match list (empty unless ambiguous).
    """
    if service_id is not None:
        for svc in services:
            if svc.get("id") == service_id:
                name = svc.get("name") or ""
                return (name, []) if name else (None, [])
        return (None, [])

    if service_name is None:
        return (None, [])

    # Tier 2: exact (case-sensitive)
    for svc in services:
        if svc.get("name") == service_name:
            return (svc["name"], [])

    # Tier 3: exact (case-insensitive)
    query_lower = service_name.lower()
    for svc in services:
        if (svc.get("name") or "").lower() == query_lower:
            return (svc["name"], [])

    # Tier 4: substring (case-insensitive)
    matches = [svc["name"] for svc in services if svc.get("name") and query_lower in svc["name"].lower()]
    if len(matches) == 1:
        return (matches[0], [])
    if len(matches) > 1:
        return (None, sorted(matches))
    return (None, [])


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

    Name resolution is fuzzy — exact match wins, then case-insensitive
    exact, then case-insensitive substring. So
    ``service_name="ClearPass No Wireless For You"`` will find the
    actual ``"No Wireless For You Auth Service"``. If the substring
    matches multiple services the response shape is
    ``{"status": "ambiguous", "candidates": [<name>, ...]}`` — surface
    the candidate names (NOT any numeric IDs) to the operator so they
    can pick.

    Args:
        service_id: ClearPass numeric service ID (e.g. ``1`` for
            ``[Policy Manager Admin Network Login Service]``).
            Internal — don't surface this in user-facing output.
        service_name: ClearPass service name. Accepts exact, casing
            variations, or a partial substring that uniquely identifies
            the service.
        include_details: When true, attaches an ``"details"`` block
            with per-rule action / linked-names data suitable for an
            inspector view alongside the rendered diagram.

    Returns:
        On success — dict with ``service_id`` (engine slug),
        ``service_name`` (the exact resolved name), ``service_type``,
        ``nodes``, ``edges``, ``warnings``, and optionally ``details``.
        Edge labels are one of ``""``, ``YES``, ``NO``, ``FAIL``,
        ``PASS``, ``CONTINUE``.

        On ambiguous match — ``{"status": "ambiguous", "query": ...,
        "candidates": [<name>, ...]}`` — caller should re-prompt with a
        more specific name.

        On no match — ``{"status": "service_not_found", "query": ...,
        "available_services": [<name>, ...], "available_count": <int>}``.
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

        target_name, candidates = _resolve_service_name(services, service_id, service_name)
        if candidates:
            return {
                "status": "ambiguous",
                "query": service_name,
                "candidates": candidates,
            }
        if target_name is None:
            available = sorted(s.get("name", "") for s in services if s.get("name"))
            return {
                "status": "service_not_found",
                "query": service_name if service_name is not None else f"id={service_id}",
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
