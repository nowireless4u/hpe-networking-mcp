"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated, Any

from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import mcp
from hpe_networking_mcp.platforms.mist.client import get_apisession
from hpe_networking_mcp.platforms.mist.tools import (
    schemas_data as _schemas_data_module,
)

# Pre-resolved schemas keyed by schema_name (= schemas_config.yaml entry key).
# Each entry: {"schema": <dict>, "_schema_name": <oas_schema_name>}
_SCHEMAS_DATA: dict = _schemas_data_module.SCHEMAS_DATA

# Enum of available schema names, built at import time from the
# pre-resolved data keys.
SchemaName = Enum(  # type: ignore[misc]
    "SchemaName",
    {name: name for name in _SCHEMAS_DATA},
)


def _compact_schema(schema: dict) -> dict:
    """Return a token-efficient summary of a JSON schema.

    Required fields are returned in full detail.  Optional fields are
    reduced to name, type, and description only -- nested sub-schemas
    and constraint keywords are omitted.  A hint key tells the caller
    how to obtain the full schema.
    """
    required_fields: set = set(schema.get("required", []))
    properties: dict = schema.get("properties", {})

    compact_required: dict = {}
    compact_optional: dict = {}

    for field_name, field_schema in properties.items():
        if field_name in required_fields:
            compact_required[field_name] = field_schema
        else:
            compact_entry: dict = {}
            if field_schema.get("type"):
                compact_entry["type"] = field_schema["type"]
            if field_schema.get("description"):
                compact_entry["description"] = field_schema["description"]
            compact_optional[field_name] = compact_entry

    result: dict = {}
    for key, value in schema.items():
        if key != "properties":
            result[key] = value

    result["properties"] = {**compact_required, **compact_optional}

    optional_count = len(compact_optional)
    if optional_count:
        result["x-hint"] = (
            f"{optional_count} optional field(s) shown in compact "
            "form (name + type + description only). Pass "
            "verbose=True for full schema."
        )

    return result


@mcp.tool(
    name="mist_get_configuration_object_schema",
    description=(
        "Retrieve the JSON schema for a Mist configuration object "
        "type. The schema is derived from the Mist OpenAPI "
        "specification and includes all properties with their "
        "types, descriptions, defaults, and constraints. Use this "
        "tool to understand the structure of a configuration object "
        "before creating or updating it. Pass verbose=True to get "
        "the full schema including all constraints and nested "
        "sub-schemas (default is compact summary)."
    ),
    tags={"configuration"},
    annotations={
        "title": "Get Configuration Object Schema",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
        "idempotentHint": True,
    },
)
async def get_configuration_object_schema(
    schema_name: Annotated[
        SchemaName,
        Field(description=("Name of the configuration object schema to retrieve.")),
    ],
    verbose: Annotated[
        bool,
        Field(
            description=(
                "Return the full schema with all constraints "
                "and nested sub-schemas. When False (default), "
                "returns a compact summary with required fields "
                "in full and optional fields as "
                "name+type+description only."
            )
        ),
    ] = False,
) -> dict[str, Any] | str:
    """Retrieve the pre-resolved JSON schema for a Mist config object."""

    logger.debug("Tool get_configuration_object_schema called")
    logger.debug(
        "Input Parameters: schema_name=%s, verbose=%s",
        schema_name,
        verbose,
    )

    _, response_format = await get_apisession()

    entry = _SCHEMAS_DATA.get(schema_name.value)
    if entry is None:
        raise ValueError(f"Schema '{schema_name.value}' not found. Re-run the generator to rebuild schemas_data.py.")

    resolved: dict = dict(entry["schema"])  # shallow copy

    if not resolved:
        raise ValueError(f"No schema found for '{schema_name.value}'. Re-run the generator to rebuild schemas_data.py.")

    resolved["x-schema-name"] = entry["_schema_name"]

    if not verbose:
        resolved = _compact_schema(resolved)

    return resolved
