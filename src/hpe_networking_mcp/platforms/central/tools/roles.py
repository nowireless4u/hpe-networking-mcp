"""Aruba Central role+policy combined read tool.

The CRUD tool surface for roles (``central_get_roles`` /
``central_manage_role``) is owned by the generated ``roles_policy.py``
module. This file retains only the hand-curated
``central_get_role_with_policy`` convenience read, which bundles a
role's config with its access policy in a single call.

API: GET /network-config/v1alpha1/roles, GET /network-config/v1alpha1/policies
"""

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_role_with_policy(
    ctx: Context,
    name: str,
) -> dict | str:
    """
    Get a Central role's config bundled with its access policy.

    Pairs the two endpoints operators most often need together when
    asking "what does this role actually do?":

    - ``GET /network-config/v1alpha1/roles/{name}`` — the role definition
      (VLAN, session params, classification settings, etc.). Often
      skeletal (just ``{name, description}``) when the role's only
      purpose is to be referenced as a source in a security policy.
    - ``GET /network-config/v1alpha1/policies/{name}`` — the security
      policy named after the role. Contains the actual firewall rules
      that fire when a client carries this role: per-rule
      ``condition`` (rule-type, services, source/destination) and
      ``action`` (ALLOW / DENY / log / etc.).

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
        - ``policy`` — the security policy dict, or ``None`` if no
          policy named after the role exists.
        - ``not_found`` — list of which endpoints returned empty
          (``["role"]``, ``["policy"]``, ``["role", "policy"]``, or
          ``[]`` when both resolved).
        - ``errors`` — list of error messages for endpoints that
          errored (non-2xx, network failure). Empty on full success.

        Either resource being absent is NOT an error — many shared
        roles are skeletal and many roles have no separate policy.
        Surface ``not_found`` to the operator as informational.
    """
    conn = ctx.lifespan_context["central_conn"]

    result: dict = {
        "name": name,
        "role": None,
        "policy": None,
        "not_found": [],
        "errors": [],
    }

    for endpoint_label, api_path in (
        ("role", f"network-config/v1alpha1/roles/{name}"),
        ("policy", f"network-config/v1alpha1/policies/{name}"),
    ):
        try:
            response = retry_central_command(
                central_conn=conn,
                api_method="GET",
                api_path=api_path,
            )
            body = response.get("msg")
            # Central returns 200 + empty dict for "not present" on these
            # endpoints — treat that as not_found rather than a real result.
            if isinstance(body, dict) and body:
                result[endpoint_label] = body
            else:
                result["not_found"].append(endpoint_label)
        except Exception as e:
            result["errors"].append(f"{endpoint_label} ({api_path}): {e}")

    return result
