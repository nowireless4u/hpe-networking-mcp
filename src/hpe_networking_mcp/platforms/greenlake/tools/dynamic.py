# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake dynamic meta-tools.

Provides 3 tools that allow an LLM to discover and invoke any GreenLake API
endpoint at runtime, without needing a dedicated tool per endpoint.

Consolidated from the 5 original per-service dynamic tool implementations
(audit-logs, devices, subscriptions, users, workspaces).
"""

from __future__ import annotations

import copy
from typing import Annotated, Any

from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.greenlake._registry import mcp
from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient

# ---------------------------------------------------------------------------
# Unified endpoint registry — compiled from all 5 original services
# ---------------------------------------------------------------------------

# The list used by greenlake_list_endpoints (sorted order)
ALL_ENDPOINTS: list[str] = sorted(
    [
        # Audit Logs
        "GET:/audit-log/v1/logs",
        "GET:/audit-log/v1/logs/{id}/detail",
        # Devices
        "GET:/devices/v1/devices",
        "GET:/devices/v1/devices/{id}",
        # Subscriptions
        "GET:/subscriptions/v1/subscriptions",
        "GET:/subscriptions/v1/subscriptions/{id}",
        # Users
        "GET:/identity/v1/users",
        "GET:/identity/v1/users/{id}",
        # Workspaces
        "GET:/workspaces/v1/workspaces/{workspaceId}",
        "GET:/workspaces/v1/workspaces/{workspaceId}/contact",
    ]
)

# Full schemas used by greenlake_get_endpoint_schema (rich descriptions)
ENDPOINT_SCHEMAS: dict[str, dict[str, Any]] = {
    # -----------------------------------------------------------------------
    # Audit Logs
    # -----------------------------------------------------------------------
    "GET:/audit-log/v1/logs": {
        "path": "/audit-log/v1/logs",
        "method": "GET",
        "summary": "getauditlogs",
        "description": "Retrieve HPE GreenLake audit logs with optional filtering and pagination.",
        "operationId": "getauditlogs",
        "tags": ["audit-logs"],
        "deprecated": False,
        "parameters": [
            {
                "name": "filter",
                "type": "str",
                "description": (
                    "OData filter expression. Example: category eq 'User Management' "
                    "and contains(description, 'logged out').\n\n"
                    "**Important**: All filter values must be enclosed in single quotes.\n\n"
                    "Filterable properties: additionalInfo, application, category, createdAt, "
                    "description, generation, hasDetails, id, region, type, updatedAt, user, workspace"
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "select",
                "type": "str",
                "description": (
                    "Comma-separated list of properties to include in the response. "
                    "Supported: additionalInfo, createdAt, category, hasDetails, "
                    "workspace/workspaceName, description, user/username."
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "all",
                "type": "str",
                "description": "Free-text search across all audit log properties.",
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "limit",
                "type": "int",
                "description": "Maximum number of items to return (max 2000).",
                "required": False,
                "location": "query",
                "default": 50,
                "schema": {"type": "integer", "default": 50},
            },
            {
                "name": "offset",
                "type": "int",
                "description": "Zero-based offset for pagination.",
                "required": False,
                "location": "query",
                "schema": {"type": "integer"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    "GET:/audit-log/v1/logs/{id}/detail": {
        "path": "/audit-log/v1/logs/{id}/detail",
        "method": "GET",
        "summary": "getauditlogdetails",
        "description": "Get additional detail for an HPE GreenLake audit log entry.",
        "operationId": "getauditlogdetails",
        "tags": ["audit-logs"],
        "deprecated": False,
        "parameters": [
            {
                "name": "id",
                "type": "str",
                "description": (
                    "ID of the audit log record whose hasDetails value is true."
                ),
                "required": True,
                "location": "path",
                "schema": {"type": "string"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    # -----------------------------------------------------------------------
    # Devices
    # -----------------------------------------------------------------------
    "GET:/devices/v1/devices": {
        "path": "/devices/v1/devices",
        "method": "GET",
        "summary": "getdevicesv1",
        "description": "List all devices registered in HPE GreenLake.",
        "operationId": "getdevicesv1",
        "tags": ["devices"],
        "deprecated": False,
        "parameters": [
            {
                "name": "filter",
                "type": "str",
                "description": (
                    "Filter expressions using comparison operators (eq, ne, gt, ge, lt, le, in) "
                    "joined by logical operators (and, or, not).\n\n"
                    "**Important**: All filter values must be enclosed in single quotes.\n\n"
                    "Filterable properties: application, archived, assignedState, createdAt, "
                    "deviceType, id, location, macAddress, model, partNumber, region, "
                    "serialNumber, subscription, tags, tenantWorkspaceId, type, updatedAt, warranty"
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "filter-tags",
                "type": "str",
                "description": (
                    "Filter expressions applied to assigned tags or their values. "
                    "Uses comparison operators (eq, ne, in) with logical operators (and, or, not).\n\n"
                    "**Important**: All filter values must be enclosed in single quotes."
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "sort",
                "type": "str",
                "description": (
                    "Comma-separated list of sort expressions. Optionally followed by "
                    "asc or desc. Default is ascending. Example: serialNumber,macAddress desc"
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "select",
                "type": "str",
                "description": (
                    "Comma-separated list of properties to include in the response. "
                    "Example: serialNumber,macAddress"
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "limit",
                "type": "int",
                "description": "Maximum number of results to return. Default 2000.",
                "required": False,
                "location": "query",
                "default": 2000,
                "schema": {"type": "integer", "default": 2000},
            },
            {
                "name": "offset",
                "type": "int",
                "description": "Zero-based resource offset. Default 0.",
                "required": False,
                "location": "query",
                "schema": {"type": "integer"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    "GET:/devices/v1/devices/{id}": {
        "path": "/devices/v1/devices/{id}",
        "method": "GET",
        "summary": "getdevicebyidv1",
        "description": "Get a single device by its unique identifier.",
        "operationId": "getdevicebyidv1",
        "tags": ["devices"],
        "deprecated": False,
        "parameters": [
            {
                "name": "id",
                "type": "str",
                "description": "The unique identifier of the device.",
                "required": True,
                "location": "path",
                "schema": {"type": "string"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    # -----------------------------------------------------------------------
    # Subscriptions
    # -----------------------------------------------------------------------
    "GET:/subscriptions/v1/subscriptions": {
        "path": "/subscriptions/v1/subscriptions",
        "method": "GET",
        "summary": "getsubscriptionsv1",
        "description": "List all subscriptions in HPE GreenLake.",
        "operationId": "getsubscriptionsv1",
        "tags": ["subscriptions"],
        "deprecated": False,
        "parameters": [
            {
                "name": "filter",
                "type": "str",
                "description": (
                    "Filter expressions using comparison operators (eq, ne, gt, ge, lt, le, in) "
                    "joined by logical operators (and, or, not).\n\n"
                    "**Important**: All filter values must be enclosed in single quotes.\n\n"
                    "Filterable properties: availableQuantity, contract, createdAt, endTime, id, "
                    "isEval, key, productType, quantity, sku, skuDescription, startTime, "
                    "subscriptionStatus, subscriptionType, tags, tier, type, updatedAt"
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "filter-tags",
                "type": "str",
                "description": (
                    "Filter expressions applied to assigned tags or their values. "
                    "Uses comparison operators (eq, ne) with logical operators (and, or).\n\n"
                    "**Important**: All filter values must be enclosed in single quotes."
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "sort",
                "type": "str",
                "description": (
                    "Comma-separated sort expressions, optionally followed by asc or desc. "
                    "Example: key, quote desc"
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "select",
                "type": "str",
                "description": (
                    "Comma-separated list of properties to include in the response. "
                    "Example: id,key"
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "limit",
                "type": "int",
                "description": "Maximum number of results to return. Default 50.",
                "required": False,
                "location": "query",
                "default": 50,
                "schema": {"type": "integer", "default": 50},
            },
            {
                "name": "offset",
                "type": "int",
                "description": "Zero-based resource offset. Default 0.",
                "required": False,
                "location": "query",
                "schema": {"type": "integer"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    "GET:/subscriptions/v1/subscriptions/{id}": {
        "path": "/subscriptions/v1/subscriptions/{id}",
        "method": "GET",
        "summary": "getsubscriptiondetailsbyidv1",
        "description": "Get subscription details by its unique identifier.",
        "operationId": "getsubscriptiondetailsbyidv1",
        "tags": ["subscriptions"],
        "deprecated": False,
        "parameters": [
            {
                "name": "id",
                "type": "str",
                "description": "The unique identifier of the subscription.",
                "required": True,
                "location": "path",
                "schema": {"type": "string"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    # -----------------------------------------------------------------------
    # Users
    # -----------------------------------------------------------------------
    "GET:/identity/v1/users": {
        "path": "/identity/v1/users",
        "method": "GET",
        "summary": "get_users",
        "description": "List all users in the HPE GreenLake workspace.",
        "operationId": "get_users_identity_v1_users_get",
        "tags": ["users"],
        "deprecated": False,
        "parameters": [
            {
                "name": "filter",
                "type": "str",
                "description": (
                    "OData 4.0 filter expression. Supported operators: eq, ne, gt, ge, lt "
                    "with logical expressions and, or, not.\n\n"
                    "Filterable properties: id, username, userStatus, createdAt, updatedAt, lastLogin.\n\n"
                    "userStatus values: UNVERIFIED, VERIFIED, BLOCKED, DELETE_IN_PROGRESS, "
                    "DELETED, SUSPENDED (case-sensitive).\n\n"
                    "**Important**: All filter values must be enclosed in single quotes."
                ),
                "required": False,
                "location": "query",
                "schema": {"type": "string"},
            },
            {
                "name": "offset",
                "type": "int",
                "description": "Pagination offset (number of pages to skip).",
                "required": False,
                "location": "query",
                "schema": {"type": "integer"},
            },
            {
                "name": "limit",
                "type": "int",
                "description": "Maximum number of entries per page. Max 600, default 300.",
                "required": False,
                "location": "query",
                "default": 300,
                "schema": {"type": "integer", "default": 300},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    "GET:/identity/v1/users/{id}": {
        "path": "/identity/v1/users/{id}",
        "method": "GET",
        "summary": "get_user_detailed",
        "description": "Get detailed information for a single user by ID.",
        "operationId": "get_user_detailed_identity_v1_users_id_get",
        "tags": ["users"],
        "deprecated": False,
        "parameters": [
            {
                "name": "id",
                "type": "str",
                "description": (
                    "The unique identifier of the user. "
                    "Example: 7600415a-8876-5722-9f3c-b0fd11112283"
                ),
                "required": True,
                "location": "path",
                "schema": {"type": "string"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    # -----------------------------------------------------------------------
    # Workspaces
    # -----------------------------------------------------------------------
    "GET:/workspaces/v1/workspaces/{workspaceId}": {
        "path": "/workspaces/v1/workspaces/{workspaceId}",
        "method": "GET",
        "summary": "get_workspace",
        "description": "Get workspace information by its unique identifier.",
        "operationId": "get_workspace_workspaces_v1_workspaces_workspaceid_get",
        "tags": ["workspaces"],
        "deprecated": False,
        "parameters": [
            {
                "name": "workspaceId",
                "type": "str",
                "description": (
                    "The unique identifier of the workspace. "
                    "Example: 7600415a-8876-5722-9f3c-b0fd11112283"
                ),
                "required": True,
                "location": "path",
                "schema": {"type": "string"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
    "GET:/workspaces/v1/workspaces/{workspaceId}/contact": {
        "path": "/workspaces/v1/workspaces/{workspaceId}/contact",
        "method": "GET",
        "summary": "get_workspace_contact",
        "description": "Get workspace contact information.",
        "operationId": "get_workspace_detailed_info_workspaces_v1_workspaces_wo_5c14f2bc",
        "tags": ["workspaces"],
        "deprecated": False,
        "parameters": [
            {
                "name": "workspaceId",
                "type": "str",
                "description": (
                    "The unique identifier of the workspace. "
                    "Example: 7600415a-8876-5722-9f3c-b0fd11112283"
                ),
                "required": True,
                "location": "path",
                "schema": {"type": "string"},
            },
        ],
        "responses": {"200": {"description": "Successful response", "content_type": "application/json"}},
    },
}

# Compact schemas used by greenlake_invoke_endpoint for validation and URL building.
# These only contain the fields needed at invocation time (name, type, required, location).
INVOKE_SCHEMAS: dict[str, dict[str, Any]] = {
    "GET:/audit-log/v1/logs": {
        "path": "/audit-log/v1/logs",
        "method": "GET",
        "parameters": [
            {"name": "filter", "type": "str", "required": False, "location": "query"},
            {"name": "select", "type": "str", "required": False, "location": "query"},
            {"name": "all", "type": "str", "required": False, "location": "query"},
            {"name": "limit", "type": "int", "required": False, "location": "query", "default": 50},
            {"name": "offset", "type": "int", "required": False, "location": "query"},
        ],
    },
    "GET:/audit-log/v1/logs/{id}/detail": {
        "path": "/audit-log/v1/logs/{id}/detail",
        "method": "GET",
        "parameters": [
            {"name": "id", "type": "str", "required": True, "location": "path"},
        ],
    },
    "GET:/devices/v1/devices": {
        "path": "/devices/v1/devices",
        "method": "GET",
        "parameters": [
            {"name": "filter", "type": "str", "required": False, "location": "query"},
            {"name": "filter-tags", "type": "str", "required": False, "location": "query"},
            {"name": "sort", "type": "str", "required": False, "location": "query"},
            {"name": "select", "type": "str", "required": False, "location": "query"},
            {"name": "limit", "type": "int", "required": False, "location": "query", "default": 2000},
            {"name": "offset", "type": "int", "required": False, "location": "query"},
        ],
    },
    "GET:/devices/v1/devices/{id}": {
        "path": "/devices/v1/devices/{id}",
        "method": "GET",
        "parameters": [
            {"name": "id", "type": "str", "required": True, "location": "path"},
        ],
    },
    "GET:/subscriptions/v1/subscriptions": {
        "path": "/subscriptions/v1/subscriptions",
        "method": "GET",
        "parameters": [
            {"name": "filter", "type": "str", "required": False, "location": "query"},
            {"name": "filter-tags", "type": "str", "required": False, "location": "query"},
            {"name": "sort", "type": "str", "required": False, "location": "query"},
            {"name": "select", "type": "str", "required": False, "location": "query"},
            {"name": "limit", "type": "int", "required": False, "location": "query", "default": 50},
            {"name": "offset", "type": "int", "required": False, "location": "query"},
        ],
    },
    "GET:/subscriptions/v1/subscriptions/{id}": {
        "path": "/subscriptions/v1/subscriptions/{id}",
        "method": "GET",
        "parameters": [
            {"name": "id", "type": "str", "required": True, "location": "path"},
        ],
    },
    "GET:/identity/v1/users": {
        "path": "/identity/v1/users",
        "method": "GET",
        "parameters": [
            {"name": "filter", "type": "str", "required": False, "location": "query"},
            {"name": "offset", "type": "int", "required": False, "location": "query"},
            {"name": "limit", "type": "int", "required": False, "location": "query", "default": 300},
        ],
    },
    "GET:/identity/v1/users/{id}": {
        "path": "/identity/v1/users/{id}",
        "method": "GET",
        "parameters": [
            {"name": "id", "type": "str", "required": True, "location": "path"},
        ],
    },
    "GET:/workspaces/v1/workspaces/{workspaceId}": {
        "path": "/workspaces/v1/workspaces/{workspaceId}",
        "method": "GET",
        "parameters": [
            {"name": "workspaceId", "type": "str", "required": True, "location": "path"},
        ],
    },
    "GET:/workspaces/v1/workspaces/{workspaceId}/contact": {
        "path": "/workspaces/v1/workspaces/{workspaceId}/contact",
        "method": "GET",
        "parameters": [
            {"name": "workspaceId", "type": "str", "required": True, "location": "path"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _coerce_int(value: Any, name: str) -> int:
    """Coerce a string or int value to int."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Parameter '{name}' must be an integer, got '{value}'") from e
    raise ValueError(f"Parameter '{name}' must be an integer, got {type(value).__name__}")


def _validate_parameters(
    parameters: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    """Validate parameters against the endpoint schema. Returns a list of error strings."""
    errors: list[str] = []
    schema_params = {p["name"]: p for p in schema.get("parameters", [])}

    # Check required parameters
    for param_name, param_def in schema_params.items():
        if param_def["required"] and param_name not in parameters:
            errors.append(f"Required parameter '{param_name}' is missing")

    # Validate known parameters
    for param_name, param_value in parameters.items():
        if param_name not in schema_params:
            errors.append(f"Unknown parameter '{param_name}' not defined in schema")
            continue

        param_def = schema_params[param_name]
        expected_type = param_def["type"]

        if expected_type == "int" and not isinstance(param_value, int):
            try:
                int(param_value)
            except (ValueError, TypeError):
                errors.append(f"Parameter '{param_name}' should be an integer")
        elif expected_type == "boolean" and not isinstance(param_value, bool):
            if str(param_value).lower() not in ("true", "false", "1", "0"):
                errors.append(f"Parameter '{param_name}' should be a boolean")

    return errors


def _build_request_url(
    base_path: str,
    parameters: dict[str, Any],
    schema: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Build the final URL (with path params substituted) and separate query params."""
    url = base_path
    query_params: dict[str, Any] = {}
    schema_params = {p["name"]: p for p in schema.get("parameters", [])}

    for param_name, param_value in parameters.items():
        if param_name not in schema_params:
            continue

        param_def = schema_params[param_name]
        location = param_def.get("location", "query")
        param_type = param_def.get("type", "str")

        if location == "path":
            url = url.replace("{" + param_name + "}", str(param_value))
        else:
            # Query parameter -- coerce integers
            if param_type == "int":
                try:
                    param_value = _coerce_int(param_value, param_name)
                except ValueError:
                    pass  # validation already caught this
            query_params[param_name] = param_value

    return url, query_params


# ---------------------------------------------------------------------------
# Tool 1: greenlake_list_endpoints
# ---------------------------------------------------------------------------


@mcp.tool(
    name="greenlake_list_endpoints",
    description=(
        "Lists all available HPE GreenLake API endpoints across all 5 services "
        "(audit-logs, devices, subscriptions, users, workspaces) as simple "
        "identifiers in METHOD:PATH format for fast discovery.\n\n"
        "Use this tool first to discover what endpoints are available, then use "
        "greenlake_get_endpoint_schema to get parameter details, and finally "
        "greenlake_invoke_endpoint to call the endpoint."
    ),
    tags={"greenlake", "dynamic"},
    annotations={
        "title": "List GreenLake API endpoints",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def greenlake_list_endpoints(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Optional keyword filter (case-insensitive substring match). "
                "Example: 'devices' returns only device-related endpoints."
            ),
        ),
    ] = None,
) -> dict[str, Any]:
    """List all available GreenLake API endpoints."""
    logger.debug("greenlake_list_endpoints called, filter={}", filter)

    filter_term = (filter or "").lower()

    if filter_term:
        endpoints = [ep for ep in ALL_ENDPOINTS if filter_term in ep.lower()]
    else:
        endpoints = list(ALL_ENDPOINTS)

    return {
        "success": True,
        "total": len(endpoints),
        "endpoints": endpoints,
    }


# ---------------------------------------------------------------------------
# Tool 2: greenlake_get_endpoint_schema
# ---------------------------------------------------------------------------


@mcp.tool(
    name="greenlake_get_endpoint_schema",
    description=(
        "Retrieves detailed parameter schema for a specific HPE GreenLake API "
        "endpoint, including path parameters, query parameters, types, descriptions, "
        "and validation rules.\n\n"
        "Provide the endpoint identifier in METHOD:PATH format as returned by "
        "greenlake_list_endpoints (e.g. 'GET:/audit-log/v1/logs')."
    ),
    tags={"greenlake", "dynamic"},
    annotations={
        "title": "Get GreenLake endpoint schema",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def greenlake_get_endpoint_schema(
    ctx: Context,
    endpoint: Annotated[
        str,
        Field(
            description=(
                "Endpoint identifier in METHOD:PATH format. "
                "Example: 'GET:/audit-log/v1/logs' or 'GET:/devices/v1/devices/{id}'"
            ),
        ),
    ],
    include_examples: Annotated[
        bool | None,
        Field(
            default=False,
            description="Include example parameter values in the response.",
        ),
    ] = False,
) -> dict[str, Any]:
    """Get the parameter schema for a single GreenLake API endpoint."""
    logger.debug("greenlake_get_endpoint_schema called, endpoint={}", endpoint)

    endpoint = endpoint.strip()
    if not endpoint:
        return {
            "success": False,
            "error": "endpoint is required",
            "message": "Please provide an endpoint identifier in METHOD:PATH format.",
        }

    if endpoint not in ENDPOINT_SCHEMAS:
        return {
            "success": False,
            "error": f"Endpoint not found: {endpoint}",
            "available_endpoints": ALL_ENDPOINTS,
        }

    # Return a deep copy so callers cannot mutate the registry
    schema = copy.deepcopy(ENDPOINT_SCHEMAS[endpoint])

    if include_examples:
        _example_map = {
            "str": "example-value",
            "int": 123,
            "boolean": True,
            "List[str]": ["example1", "example2"],
        }
        for param in schema.get("parameters", []):
            if "example" not in param:
                param["example"] = _example_map.get(param["type"], "example-value")

    return {
        "success": True,
        "endpoint": endpoint,
        "schema": schema,
    }


# ---------------------------------------------------------------------------
# Tool 3: greenlake_invoke_endpoint
# ---------------------------------------------------------------------------


@mcp.tool(
    name="greenlake_invoke_endpoint",
    description=(
        "Executes any HPE GreenLake GET API endpoint dynamically with parameter "
        "validation. Supports all 10 endpoints across audit-logs, devices, "
        "subscriptions, users, and workspaces.\n\n"
        "Provide the endpoint identifier in METHOD:PATH format and a params dict "
        "containing the path and query parameters for that endpoint. Use "
        "greenlake_get_endpoint_schema first to discover required parameters."
    ),
    tags={"greenlake", "dynamic"},
    annotations={
        "title": "Invoke GreenLake API endpoint",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_invoke_endpoint(
    ctx: Context,
    endpoint: Annotated[
        str,
        Field(
            description=(
                "Endpoint identifier in METHOD:PATH format. "
                "Example: 'GET:/devices/v1/devices'"
            ),
        ),
    ],
    params: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description=(
                "Request parameters dict. Keys are parameter names, values are their "
                "values. Path parameters (e.g. id, workspaceId) are substituted into "
                "the URL; query parameters are appended as query string."
            ),
        ),
    ] = None,
) -> dict[str, Any]:
    """Invoke a GreenLake API endpoint dynamically."""
    logger.debug("greenlake_invoke_endpoint called, endpoint={}", endpoint)

    endpoint = endpoint.strip()
    params = params or {}

    # --- Validate endpoint identifier format ---
    if not endpoint:
        return {
            "success": False,
            "error": "endpoint is required",
            "message": "Please provide an endpoint identifier in METHOD:PATH format.",
        }

    if ":" not in endpoint:
        return {
            "success": False,
            "error": "Invalid endpoint identifier format",
            "message": "Expected format: METHOD:PATH (e.g., 'GET:/devices/v1/devices')",
        }

    method, path = endpoint.split(":", 1)
    method = method.upper()

    # Only GET is supported
    if method != "GET":
        return {
            "success": False,
            "error": f"Unsupported HTTP method: {method}",
            "message": "Only GET endpoints are supported in read-only mode.",
        }

    # --- Look up the schema ---
    if endpoint not in INVOKE_SCHEMAS:
        return {
            "success": False,
            "error": f"Endpoint not found: {endpoint}",
            "available_endpoints": ALL_ENDPOINTS,
        }

    schema = INVOKE_SCHEMAS[endpoint]

    # --- Validate parameters ---
    validation_errors = _validate_parameters(params, schema)
    if validation_errors:
        return {
            "success": False,
            "error": "Parameter validation failed",
            "validation_errors": validation_errors,
            "schema": schema,
        }

    # --- Build URL and query params ---
    final_url, query_params = _build_request_url(path, params, schema)

    # --- Execute the request ---
    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    try:
        async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
            response_data = await client.get(
                final_url,
                params=query_params if query_params else None,
            )

        return {
            "success": True,
            "endpoint": endpoint,
            "request": {
                "url": final_url,
                "method": method,
                "query_params": query_params,
            },
            "response": response_data,
        }
    except Exception as e:
        logger.error("greenlake_invoke_endpoint failed: {}", str(e))
        return {
            "success": False,
            "error": f"Request failed: {str(e)}",
            "endpoint": endpoint,
            "request": {
                "url": final_url,
                "method": method,
                "query_params": query_params,
            },
        }
