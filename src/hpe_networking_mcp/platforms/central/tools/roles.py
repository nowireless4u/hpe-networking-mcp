"""Aruba Central role+policy combined read tool.

The CRUD tool surface for roles (``central_get_roles`` /
``central_manage_roles``) is owned by the generated ``roles_policy.py``
module. This file retains only the hand-curated
``central_get_role_with_policy`` convenience read, which bundles a
role's config with the security policies it is actually bound to in a
single call.

API: GET /network-config/v1alpha1/roles/{name},
     GET /network-config/v1alpha1/policies/{name}
"""

from fastmcp import Context

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


def _extract_policy_names(role_body: dict) -> list[str]:
    """Pull bound-policy names out of a role's ``policies[]`` back-reference.

    The role GET response carries a ``policies`` array enumerating the
    security policies the role is bound to. Each entry is normally an
    object with a ``name`` field, but tolerate bare strings too. Returns
    a de-duplicated, order-preserving list of policy names.

    Args:
        role_body: The decoded role object from
            ``GET /roles/{name}``.

    Returns:
        List of policy names referenced by the role (possibly empty).
    """
    raw = role_body.get("policies")
    if not isinstance(raw, list):
        return []

    names: list[str] = []
    seen: set[str] = set()
    for entry in raw:
        name: str | None = None
        if isinstance(entry, dict):
            candidate = entry.get("name")
            if isinstance(candidate, str) and candidate:
                name = candidate
        elif isinstance(entry, str) and entry:
            name = entry
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


@tool(capability=Capability.READ)
async def central_get_role_with_policy(
    ctx: Context,
    name: str,
) -> dict | str:
    """
    Get a Central role's config bundled with its bound access policies.

    Resolves the two things operators most often need together when
    asking "what does this role actually do?":

    - ``GET /network-config/v1alpha1/roles/{name}`` — the role definition
      (VLAN, session params, classification settings, etc.). Its
      ``policies[]`` array back-references the security policies the role
      is bound to.
    - For each referenced policy,
      ``GET /network-config/v1alpha1/policies/{policy-name}`` — the
      security policy that fires when a client carries this role:
      per-rule ``condition`` (rule-type, services, source/destination)
      and ``action`` (ALLOW / DENY / log / etc.).

    Use this from the ClearPass policy visualizer: when an enforcement
    profile pushes ``Aruba-User-Role: night-night``, call this with
    ``name="night-night"`` to surface what access that role actually
    grants/denies.

    Parameters:
        name: Role name as it appears in Central (case-sensitive in the
            REST path). Matches the value pushed by ClearPass via the
            ``Aruba-User-Role`` RADIUS attribute.

    Returns:
        Dict with keys:
        - ``name`` — the queried role name.
        - ``role`` — the role config dict, or ``None`` if not found.
        - ``policies`` — list of the security policy dicts the role is
          bound to (in role ``policies[]`` order). Empty when the role
          has no bound policies, or when the role itself was not found.
        - ``not_found`` — list of which resources returned empty:
          ``"role"`` when the role itself is absent, and
          ``"policy:<name>"`` for each referenced policy that returned
          empty. ``[]`` when everything resolved.
        - ``errors`` — list of error messages for resources that errored
          (non-2xx, network failure). Empty on full success.

        A resource being absent is NOT an error — many shared roles are
        skeletal and a role may legitimately reference no policies.
        Surface ``not_found`` to the operator as informational.
    """
    conn = get_central_conn(ctx)

    result: dict = {
        "name": name,
        "role": None,
        "policies": [],
        "not_found": [],
        "errors": [],
    }

    # --- 1. Fetch the role ---
    role_path = f"network-config/v1alpha1/roles/{path_seg(name)}"
    role_body: dict = {}
    try:
        response = await retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=role_path,
        )
        body = response.get("msg")
        # Central returns 200 + empty dict for "not present" on this endpoint.
        if isinstance(body, dict) and body:
            result["role"] = body
            role_body = body
        else:
            result["not_found"].append("role")
    except Exception as e:
        result["errors"].append(f"role ({role_path}): {e}")

    # --- 2. Resolve each policy the role is bound to ---
    for policy_name in _extract_policy_names(role_body):
        policy_path = f"network-config/v1alpha1/policies/{path_seg(policy_name)}"
        try:
            response = await retry_central_command(
                central_conn=conn,
                api_method="GET",
                api_path=policy_path,
            )
            body = response.get("msg")
            if isinstance(body, dict) and body:
                result["policies"].append(body)
            else:
                result["not_found"].append(f"policy:{policy_name}")
        except Exception as e:
            result["errors"].append(f"policy:{policy_name} ({policy_path}): {e}")

    return result
