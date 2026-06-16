"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``idps``
Operations in this file: 15
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_ids_auto_signature_update_state",
    description="GET /ids/autoSignatureUpdateState\n\nidpsAutoUpdateGet\n\nRetrieve IDPS auto signature update state",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_auto_signature_update_state(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/autoSignatureUpdateState",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_ids_config",
    description="GET /ids/config\n\nidpsConfigGet\n\nRetrieve IDS/IPS global configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/config",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_ids_profilestate",
    description="GET /ids/profilestate\n\nidpsProfileStateGet\n\nGet IDS/IPS profile-to-appliance assignments",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_profilestate(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/profilestate",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_ids_reservedsignature",
    description="GET /ids/reservedsignature\n\nidpsReservedSignaturesGet\n\nGet IDPS reserved signatures",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_reservedsignature(
    ctx: Context,
    signature_family: Annotated[
        str | None,
        Field(
            default=None,
            description="The signature family version to filter reserved signatures. Determines which generation of signatures to retrieve.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if signature_family is not None:
        query_params["signature_family"] = signature_family
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/reservedsignature",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ids_signatures",
    description="GET /ids/signatures\n\nidpsSignaturesGet\n\nRetrieve all IDS/IPS signatures",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_signatures(
    ctx: Context,
    signature_family: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter signatures by family version. If omitted, returns all signatures across all families.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if signature_family is not None:
        query_params["signature_family"] = signature_family
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/signatures",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ids_signatures_diff",
    description="GET /ids/signatures/diff\n\nidpsSignaturesDiffGet\n\nGet IDS/IPS signature difference between two versions",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_signatures_diff(
    ctx: Context,
    sigVersion1: Annotated[
        str | None,
        Field(
            default=None,
            description="First signature version for comparison (e.g., '2.0.0.1'). Represents the baseline version.",
        ),
    ] = None,
    sigVersion2: Annotated[
        str | None,
        Field(
            default=None,
            description="Second signature version for comparison (e.g., '2.0.0.2'). Represents the target version to compare against.",
        ),
    ] = None,
    signatureFamily: Annotated[
        str | None,
        Field(default=None, description="Signature family to filter results. Defaults to '4.x' if not specified."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if sigVersion1 is not None:
        query_params["sigVersion1"] = sigVersion1
    if sigVersion2 is not None:
        query_params["sigVersion2"] = sigVersion2
    if signatureFamily is not None:
        query_params["signatureFamily"] = signatureFamily
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/signatures/diff",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ids_signatures_profiles",
    description="GET /ids/signatures/profiles\n\nidpsSignaturesProfilesGet\n\nRetrieve IDS/IPS signature profiles",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_signatures_profiles(
    ctx: Context,
    signature_family: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter profiles by signature family version. When specified, only profiles matching this family are returned. If omitted, all profiles are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if signature_family is not None:
        query_params["signature_family"] = signature_family
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/signatures/profiles",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ids_signatures_rules",
    description="GET /ids/signatures/rules\n\nidpsSignaturesRulesGet\n\nRetrieve IDPS signature rules",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_signatures_rules(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Text filter applied to signature rules. Converted to lowercase for case-insensitive matching.",
        ),
    ] = None,
    classtype: Annotated[
        str | None,
        Field(default=None, description="Filter rules by classification type. Use 'All' to include all class types."),
    ] = None,
    signatureAction: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by signature action type. When not 'all', rules are filtered based on the specified profile's action configuration. Valid values: 'all', 'drop', 'inspect', or custom profile actions.",
        ),
    ] = None,
    signature_family: Annotated[
        str | None,
        Field(
            default=None,
            description="The signature family version to filter rules. Defaults to '4.x' if not specified.",
        ),
    ] = None,
    severity: Annotated[
        str | None, Field(default=None, description="Filter rules by severity level (e.g., 'high', 'medium', 'low').")
    ] = None,
    affected_products: Annotated[
        str | None, Field(default=None, description="Filter rules by affected products or platforms.")
    ] = None,
    rule_category: Annotated[
        str | None, Field(default=None, description="Filter rules by category classification.")
    ] = None,
    profile: Annotated[
        str | None,
        Field(
            default=None,
            description="Signature profile name to use for action filtering. Must match 'Default' or 'Default_S[digit]' pattern for default profiles, and must correspond to the signature_family parameter.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if classtype is not None:
        query_params["classtype"] = classtype
    if signatureAction is not None:
        query_params["signatureAction"] = signatureAction
    if signature_family is not None:
        query_params["signature_family"] = signature_family
    if severity is not None:
        query_params["severity"] = severity
    if affected_products is not None:
        query_params["affected_products"] = affected_products
    if rule_category is not None:
        query_params["rule_category"] = rule_category
    if profile is not None:
        query_params["profile"] = profile
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/signatures/rules",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ids_state",
    description="GET /ids/state\n\nidpsStateGet\n\nRetrieve IDS/IPS state for all appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_state(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/state",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_ids_update_signature_from_portal",
    description="GET /ids/updateSignatureFromPortal\n\ntriggerSignatureUpdateFromPortal\n\nTrigger IDPS signature update from Cloud Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_ids_update_signature_from_portal(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ids/updateSignatureFromPortal",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_ids_signatures_profiles",
    description="POST /ids/signatures/profiles\n\nidpsSignaturesProfilesPost\n\nCreate or update IDS/IPS signature profiles",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ids_signatures_profiles(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ids/signatures/profiles",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_ids_auto_signature_update_state",
    description="PUT /ids/autoSignatureUpdateState\n\nidpsAutoUpdatePut\n\nUpdate IDPS auto signature update state",
    capability=Capability.WRITE,
)
async def edgeconnect_put_ids_auto_signature_update_state(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/ids/autoSignatureUpdateState",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_ids_config",
    description="PUT /ids/config\n\nidpsConfigPut\n\nUpdate IDS/IPS global configuration schedule",
    capability=Capability.WRITE,
)
async def edgeconnect_put_ids_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/ids/config",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_ids_profilestate",
    description="PUT /ids/profilestate\n\nidpsProfileStatePut\n\nUpdate IDS/IPS profile-to-appliance assignments",
    capability=Capability.WRITE,
)
async def edgeconnect_put_ids_profilestate(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/ids/profilestate",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_ids_state",
    description="PUT /ids/state\n\nidpsStatePut\n\nUpdate IDS/IPS mode for appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_put_ids_state(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/ids/state",
        query_params=None,
        body=body,
    )
