"""Aruba ClearPass platform module."""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Tool categories mapped to module names and their tool names.
# Read tools load unconditionally; write categories are gated on config.
TOOLS: dict[str, list[str]] = {
    # ── Read-only tool files ──────────────────────────────────────
    "network_devices": [
        "clearpass_get_network_devices",
        "clearpass_get_network_device_stats",
        "clearpass_test_device_connectivity",
        "clearpass_validate_device_config",
    ],
    "guests": ["clearpass_get_guest_users"],
    "guest_config": [
        "clearpass_get_pass_templates",
        "clearpass_get_print_templates",
        "clearpass_get_weblogin_pages",
        "clearpass_get_guest_auth_settings",
        "clearpass_get_guest_manager_settings",
    ],
    "endpoints": [
        "clearpass_get_endpoints",
        "clearpass_get_endpoint_profiler",
    ],
    "endpoint_visibility": [
        "clearpass_get_onguard_activity",
        "clearpass_get_fingerprint_dictionary",
        "clearpass_get_network_scan",
        "clearpass_get_onguard_settings",
    ],
    "certificate_authority": [
        "clearpass_get_certificates",
        "clearpass_get_onboard_devices",
    ],
    "sessions": [
        "clearpass_get_sessions",
        "clearpass_get_session_action_status",
        "clearpass_get_reauth_profiles",
    ],
    "roles": [
        "clearpass_get_roles",
        "clearpass_get_role_mappings",
    ],
    "enforcement": [
        "clearpass_get_enforcement_policies",
        "clearpass_get_enforcement_profiles",
        "clearpass_get_profile_templates",
    ],
    "auth": [
        "clearpass_get_auth_sources",
        "clearpass_get_auth_source_status",
        "clearpass_test_auth_source",
        "clearpass_get_auth_methods",
    ],
    "certificates": [
        "clearpass_get_trust_list",
        "clearpass_get_client_certificates",
        "clearpass_get_server_certificates",
        "clearpass_get_service_certificates",
        "clearpass_get_revocation_list",
    ],
    "audit": [
        "clearpass_get_audit_logs",
        "clearpass_get_system_events",
        "clearpass_get_insight_alerts",
        "clearpass_get_insight_reports",
        "clearpass_get_endpoint_insights",
    ],
    "server_config": [
        "clearpass_get_admin_users",
        "clearpass_get_admin_privileges",
        "clearpass_get_operator_profiles",
        "clearpass_get_licenses",
        "clearpass_get_cluster_params",
        "clearpass_get_password_policies",
        "clearpass_get_attributes",
        "clearpass_get_data_filters",
        "clearpass_get_file_backup_servers",
        "clearpass_get_messaging_setup",
        "clearpass_get_snmp_trap_receivers",
        "clearpass_get_policy_manager_zones",
        "clearpass_get_oauth_privileges",
    ],
    "local_config": [
        "clearpass_get_access_controls",
        "clearpass_get_ad_domains",
        "clearpass_get_server_version",
        "clearpass_get_fips_status",
        "clearpass_get_server_services",
        "clearpass_get_server_snmp",
        "clearpass_get_cluster_servers",
    ],
    "identities": [
        "clearpass_get_api_clients",
        "clearpass_get_local_users",
        "clearpass_get_static_host_lists",
        "clearpass_get_devices",
        "clearpass_get_deny_listed_users",
        "clearpass_get_external_accounts",
    ],
    "policy_elements": [
        "clearpass_get_services",
        "clearpass_get_posture_policies",
        "clearpass_get_device_groups",
        "clearpass_get_proxy_targets",
        "clearpass_get_radius_dictionaries",
        "clearpass_get_tacacs_dictionaries",
        "clearpass_get_application_dictionaries",
        "clearpass_get_radius_dynamic_authorization_template",
    ],
    "integrations": [
        "clearpass_get_extensions",
        "clearpass_get_syslog_targets",
        "clearpass_get_syslog_export_filters",
        "clearpass_get_event_sources",
        "clearpass_get_context_servers",
        "clearpass_get_endpoint_context_servers",
        "clearpass_get_extension_log",
    ],
    "utilities": [
        "clearpass_generate_random_password",
    ],
    # ── Write tool files (gated) ──────────────────────────────────
    "manage_network_devices": ["clearpass_manage_network_device"],
    "manage_guests": [
        "clearpass_manage_guest_user",
        "clearpass_send_guest_credentials",
        "clearpass_generate_guest_pass",
        "clearpass_process_sponsor_action",
    ],
    "manage_guest_config": [
        "clearpass_manage_pass_template",
        "clearpass_manage_print_template",
        "clearpass_manage_weblogin_page",
        "clearpass_manage_guest_settings",
    ],
    "manage_endpoints": ["clearpass_manage_endpoint"],
    "manage_sessions": [
        "clearpass_disconnect_session",
        "clearpass_perform_coa",
    ],
    "manage_roles": [
        "clearpass_manage_role",
        "clearpass_manage_role_mapping",
    ],
    "manage_enforcement": [
        "clearpass_manage_enforcement_policy",
        "clearpass_manage_enforcement_profile",
    ],
    "manage_auth": [
        "clearpass_manage_auth_source",
        "clearpass_manage_auth_method",
    ],
    "manage_certificates": [
        "clearpass_manage_certificate",
        "clearpass_create_csr",
    ],
    "manage_audit": [
        "clearpass_manage_insight_alert",
        "clearpass_manage_insight_report",
        "clearpass_create_system_event",
    ],
    "manage_server_config": [
        "clearpass_manage_admin_user",
        "clearpass_manage_admin_privilege",
        "clearpass_manage_operator_profile",
        "clearpass_manage_license",
        "clearpass_manage_cluster_params",
        "clearpass_manage_password_policy",
        "clearpass_manage_attribute",
        "clearpass_manage_data_filter",
        "clearpass_manage_file_backup_server",
        "clearpass_manage_messaging_setup",
        "clearpass_manage_snmp_trap_receiver",
        "clearpass_manage_policy_manager_zone",
    ],
    "manage_local_config": [
        "clearpass_manage_access_control",
        "clearpass_manage_ad_domain",
        "clearpass_manage_cluster_server",
        "clearpass_manage_server_service",
        "clearpass_manage_service_params",
    ],
    "manage_certificate_authority": [
        "clearpass_manage_certificate_authority",
        "clearpass_manage_onboard_device",
    ],
    "manage_identities": [
        "clearpass_manage_api_client",
        "clearpass_manage_local_user",
        "clearpass_manage_static_host_list",
        "clearpass_manage_device",
        "clearpass_manage_deny_listed_user",
    ],
    "manage_policy_elements": [
        "clearpass_manage_service",
        "clearpass_manage_device_group",
        "clearpass_manage_posture_policy",
        "clearpass_manage_proxy_target",
        "clearpass_manage_radius_dictionary",
        "clearpass_manage_tacacs_dictionary",
        "clearpass_manage_application_dictionary",
    ],
    "manage_integrations": [
        "clearpass_manage_extension",
        "clearpass_manage_syslog_target",
        "clearpass_manage_syslog_export_filter",
        "clearpass_manage_endpoint_context_server",
    ],
}


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load all ClearPass tool modules and register them with FastMCP.

    Always imports every category so ``REGISTRIES["clearpass"]`` is fully
    populated; runtime write-gating is handled by the Visibility transform
    (static mode) and ``is_tool_enabled`` (dynamic mode, via the meta-tools).

    Returns the count of individual underlying tools that registered.
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms.clearpass import _registry

    _registry.mcp = mcp

    loaded: list[str] = []
    for category, tool_names in TOOLS.items():
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms.clearpass.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("ClearPass: loaded module {}", category)
        except Exception as e:
            logger.warning("ClearPass: failed to load module {} -- {}", category, e)

    if config.tool_mode == "dynamic":
        build_meta_tools("clearpass", mcp)
        logger.info(
            "ClearPass: {} underlying tools + 3 meta-tools registered (dynamic mode)",
            len(loaded),
        )
    else:
        logger.info("ClearPass: {} underlying tools registered (code mode)", len(loaded))

    return len(loaded)
