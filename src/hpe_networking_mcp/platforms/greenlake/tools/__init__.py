"""GreenLake tools package.

Imports the five per-service tool modules so their ``@tool(...)`` decorators
fire at module load. Also exposes a ``TOOLS`` dict mapping category -> tool
names so the platform ``register_tools`` entry point can iterate over them
and ``test_greenlake_dynamic_mode.py`` can assert the registry is fully
populated after import.
"""

from __future__ import annotations

# Categories are the short module names under ``platforms/greenlake/tools/``.
# Tool names match the ``name=...`` kwarg on each ``@tool(...)`` decorator.
TOOLS: dict[str, list[str]] = {
    "audit_logs": [
        "greenlake_get_audit_logs",
        "greenlake_get_audit_log_details",
    ],
    "devices": [
        "greenlake_get_devices",
        "greenlake_get_device_by_id",
    ],
    "subscriptions": [
        "greenlake_get_subscriptions",
        "greenlake_get_subscription_details",
    ],
    "users": [
        "greenlake_get_users",
        "greenlake_get_user_details",
    ],
    "workspaces": [
        "greenlake_get_workspace",
        "greenlake_get_workspace_details",
    ],
}
