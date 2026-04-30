"""Aruba Central alert configuration tools (v2.3.1.6+).

Manages alert *definitions* — the rules that determine what triggers an
alert, the threshold values, durations, and severity buckets. Distinct
from `alerts.py` which manages alert *instances* (clear / defer /
reactivate fired alerts).

The four endpoints under `/network-notifications/v1/alert-config`:

* GET  `/alert-config`         — list configs for a scope
* POST `/alert-config/create`  — create a custom config for a typeId+scope
* PUT  `/alert-config/update`  — update an existing config (partial — only
                                  fields in the body change)
* DEL  `/alert-config/delete`  — reset to inherited (removes the
                                  scope-level override; the parent
                                  scope's config takes effect again)

Scope semantics (from the spec):

* GLOBAL — applies to all sites and devices under the tenant. Default.
* SITE   — applies to a specific site identified by `scope_id`.
* DEVICE — applies to a specific device identified by `scope_id`.

The write tools are tagged `central_write_delete` (gated behind
`ENABLE_CENTRAL_WRITE_TOOLS`) and use `WRITE_DELETE` annotation —
different from the v2.3.1.5 alert-action tools (clear / defer / etc.)
which are operational. These four configure the alert *system itself*,
which is a config write equivalent to managing roles / policies / WLAN
profiles.
"""

from typing import Literal

from fastmcp import Context
from mcp.types import ToolAnnotations

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)

ScopeType = Literal["GLOBAL", "SITE", "DEVICE"]


def _scope_query_params(scope_id: str, scope_type: ScopeType) -> dict[str, str]:
    """Build the standard scope query-param dict shared by all four endpoints."""
    return {"scopeId": scope_id, "scopeType": scope_type}


def _typed_scope_query_params(type_id: str, scope_id: str, scope_type: ScopeType) -> dict[str, str]:
    """Same as ``_scope_query_params`` plus a ``typeId`` (used by create/update/delete)."""
    return {"typeId": type_id, "scopeId": scope_id, "scopeType": scope_type}


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------


@tool(annotations=READ_ONLY)
async def central_get_alert_configs(
    ctx: Context,
    scope_id: str,
    scope_type: ScopeType = "GLOBAL",
) -> list | dict | str:
    """
    Retrieve all alert configurations defined at the given scope.

    Returns alert *definitions* — the rules that determine when an alert
    fires (thresholds, durations, severity buckets). Distinct from
    `central_get_alerts` which returns currently fired/cleared/deferred
    alert instances.

    Each item carries `inherited: true/false` showing whether this scope
    has its own override (`false`) or is using a parent scope's config
    (`true`), plus `ruleSource: SYSTEM | USER` showing whether it's
    Central's built-in rule or an operator-customized one.

    Parameters:
        - scope_id: The scope identifier. Get scope IDs from
          `central_get_scope_tree(...)` or
          `central_get_scope_resources(...)`.
        - scope_type: One of `GLOBAL` (tenant-wide, default), `SITE`
          (per-site), or `DEVICE` (per-device).

    Returns:
        The raw response payload from Central (typically a list of
        AlertConfigItem objects). Common fields per item: `name`,
        `description`, `typeId`, `category`, `deviceType`, `enabled`,
        `ruleSource`, `clearTimeout`, `inherited`, `scopeId`,
        `scopeType`, `scopeName`, `rules` (response-shape: each rule has
        `rule_number`, `rule.duration`, `rule.condition[].severity`,
        `rule.condition[].expression.operator`, etc.).
    """
    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="GET",
        api_path="network-notifications/v1/alert-config",
        api_params=_scope_query_params(scope_id, scope_type),
    )
    msg = response.get("msg", response)
    return msg if msg else "No alert configurations returned"


# ---------------------------------------------------------------------------
# WRITE — create, update, reset (delete)
# ---------------------------------------------------------------------------


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_create_alert_config(
    ctx: Context,
    type_id: str,
    scope_id: str,
    enabled: bool,
    clear_timeout: str | None = None,
    rules: list[dict] | None = None,
    scope_type: ScopeType = "GLOBAL",
) -> dict | str:
    """
    Create a custom alert configuration for a specific alert type at a scope.

    Defines threshold rules that determine when this alert type fires.
    Use this to override Central's built-in (`SYSTEM`) rules for a
    particular site/device, or to enable/disable an alert at a non-global
    scope.

    Parameters:
        - type_id: The alert type identifier. Numeric for built-in types
          (e.g. `1250`) or string for custom types (e.g.
          `CUSTOM-AP-CPU-HIGH`). Find type IDs by listing existing
          configs with `central_get_alert_configs(scope_type="GLOBAL")`
          and reading each item's `typeId`.
        - scope_id: Where to apply the config. From `central_get_scope_tree`.
        - enabled: Whether the alert fires when conditions are met.
          Required by Central on create.
        - clear_timeout: How long after the condition clears before the
          alert auto-clears. Format `<number><unit>` where unit is
          `H`/`h` (hours), `D`/`d` (days), or `M`/`m` (minutes) —
          examples: `1H`, `30D`, `15m`. Pass `None` (the default) to
          omit auto-clear; pass `null` from the AI side as a literal
          `None` to disable an existing auto-clear on update.
        - rules: Ordered list of threshold rules. Each rule has the shape:

          ```python
          {
              "ruleNumber": 0,                # zero-based index
              "duration": 300,                # seconds metric must stay over threshold
              "conditions": [
                  {"severity": "CRITICAL", "operator": "GT", "threshold": 90.0},
                  {"severity": "MAJOR",    "operator": "GT", "threshold": 80.0},
              ],
              "additionalConditions": [
                  # Optional extra filters; same operator set, plus
                  # value_number / value_string / value_bool. Each entry
                  # also has `index` (zero-based, non-negative).
              ],
          }
          ```

          Severity values: `CRITICAL`, `MAJOR`, `MINOR`, `INFO`.
          Operator values: `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `IN`, `NIN`.
        - scope_type: One of `GLOBAL` (default), `SITE`, `DEVICE`.

    Returns: A mutation response — `{success, message, name, typeId}` on
    success.
    """
    body: dict = {"enabled": enabled}
    if clear_timeout is not None:
        body["clearTimeout"] = clear_timeout
    if rules is not None:
        body["rules"] = rules

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="POST",
        api_path="network-notifications/v1/alert-config/create",
        api_params=_typed_scope_query_params(type_id, scope_id, scope_type),
        api_data=body,
    )
    msg = response.get("msg", response)
    return msg if msg else f"Alert config create submitted for typeId={type_id}; response was empty"


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_update_alert_config(
    ctx: Context,
    type_id: str,
    scope_id: str,
    enabled: bool | None = None,
    clear_timeout: str | None = None,
    rules: list[dict] | None = None,
    scope_type: ScopeType = "GLOBAL",
) -> dict | str:
    """
    Update an existing alert configuration. Partial — fields you omit are
    left unchanged.

    Despite using HTTP PUT, the API behaves like PATCH: only the fields
    you include in the request body overwrite the current configuration;
    fields you don't include are preserved.

    Parameters:
        - type_id: Alert type identifier of the config to update.
        - scope_id: Scope where the config currently lives.
        - enabled: Toggle the alert on/off. Omit to leave unchanged.
        - clear_timeout: New auto-clear duration (`<number><unit>`,
          e.g. `2H`). Omit to leave unchanged.
        - rules: Replace the rule set. Omit to leave the rules
          unchanged. See `central_create_alert_config` for the rule
          shape.
        - scope_type: One of `GLOBAL` (default), `SITE`, `DEVICE`.

    Returns: A mutation response — `{success, message, name, typeId}`.
    """
    body: dict = {}
    if enabled is not None:
        body["enabled"] = enabled
    if clear_timeout is not None:
        body["clearTimeout"] = clear_timeout
    if rules is not None:
        body["rules"] = rules

    if not body:
        return "No fields to update — pass at least one of `enabled`, `clear_timeout`, or `rules`."

    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="PUT",
        api_path="network-notifications/v1/alert-config/update",
        api_params=_typed_scope_query_params(type_id, scope_id, scope_type),
        api_data=body,
    )
    msg = response.get("msg", response)
    return msg if msg else f"Alert config update submitted for typeId={type_id}; response was empty"


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_reset_alert_config(
    ctx: Context,
    type_id: str,
    scope_id: str,
    scope_type: ScopeType = "GLOBAL",
) -> dict | str:
    """
    Reset an alert configuration back to its inherited (parent-scope) state.

    Removes the custom override at the given scope. The alert type itself
    is NOT deleted — the parent scope's config takes effect again
    (typically the GLOBAL config). Use this to "undo" a site/device-level
    customization and return to the inherited rule.

    Parameters:
        - type_id: Alert type identifier of the config to reset.
        - scope_id: Scope where the override currently lives.
        - scope_type: One of `GLOBAL` (default), `SITE`, `DEVICE`.

    Returns: A mutation response. Note: this endpoint typically does NOT
    return `name` in the response (per the Central spec).
    """
    response = retry_central_command(
        ctx.lifespan_context["central_conn"],
        api_method="DELETE",
        api_path="network-notifications/v1/alert-config/delete",
        api_params=_typed_scope_query_params(type_id, scope_id, scope_type),
    )
    msg = response.get("msg", response)
    return msg if msg else f"Alert config reset submitted for typeId={type_id}; response was empty"
