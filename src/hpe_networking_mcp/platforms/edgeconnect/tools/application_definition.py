"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``applicationDefinition``
Operations in this file: 32
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
    name="edgeconnect_delete_application_definition_app_express_group_config",
    description="DELETE /applicationDefinition/appExpressGroup/config\n\nappExpressGroupDelete999\n\nDelete AppExpress group configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_app_express_group_config(
    ctx: Context,
    groupName: Annotated[
        str,
        Field(
            description="Name of the AppExpress group to delete. Case-insensitive (converted to lowercase). Group must exist and not be associated with any appliances."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if groupName is not None:
        query_params["groupName"] = groupName
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/appExpressGroup/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_application_definition_compound_classification",
    description="DELETE /applicationDefinition/compoundClassification\n\ncompoundDelete96\n\nDelete compound application definition",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_compound_classification(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the compound application definition to delete. Must be a positive integer greater than 0. IDs > 50000 represent portal-modified user records and require corresponding portal data to exist."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/compoundClassification",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_application_definition_dns_classification",
    description="DELETE /applicationDefinition/dnsClassification\n\ndnsDelete99\n\nDelete user-defined DNS classification by domain name",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_dns_classification(
    ctx: Context,
    domain: Annotated[
        str,
        Field(
            description="The domain name to delete from user-defined DNS classification. This is the DNS domain or hostname associated with the application definition."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if domain is not None:
        query_params["domain"] = domain
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/dnsClassification",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_application_definition_ip_intelligence_classification",
    description="DELETE /applicationDefinition/ipIntelligenceClassification\n\nipIntelligenceDelete104\n\nDelete user-defined Address Map entry by IP range",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_ip_intelligence_classification(
    ctx: Context,
    ipStart: Annotated[
        int,
        Field(
            description="Starting IPv4 address in 32-bit unsigned integer format. Must be less than or equal to ipEnd. Valid range: 0 to 4294967295."
        ),
    ],
    ipEnd: Annotated[
        int,
        Field(
            description="Ending IPv4 address in 32-bit unsigned integer format. Must be greater than or equal to ipStart. Valid range: 0 to 4294967295."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if ipStart is not None:
        query_params["ipStart"] = ipStart
    if ipEnd is not None:
        query_params["ipEnd"] = ipEnd
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/ipIntelligenceClassification",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_application_definition_ip_intelligence_confidence",
    description="DELETE /applicationDefinition/ipIntelligenceConfidence\n\ndeleteIpIntelligenceConfidence\n\nDelete user-defined IP Intelligence confidence override",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_ip_intelligence_confidence(
    ctx: Context,
    name: Annotated[
        str,
        Field(
            description="Application name to remove the confidence override for. Cannot be null or empty (whitespace-only values are rejected)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/ipIntelligenceConfidence",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_application_definition_meter_flow_classification",
    description="DELETE /applicationDefinition/meterFlowClassification\n\nmeterFlowDelete111\n\nDelete user-defined meter flow application definition",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_meter_flow_classification(
    ctx: Context,
    flowType: Annotated[
        str, Field(description="Meter flow type identifier. Must be 'MF' for meter flow applications.")
    ],
    mid: Annotated[
        int,
        Field(
            description="Unique meter flow identifier (mid) of the user-defined application to delete. This ID is assigned when the application is created."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if flowType is not None:
        query_params["flowType"] = flowType
    if mid is not None:
        query_params["mid"] = mid
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/meterFlowClassification",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_application_definition_port_protocol_classification",
    description="DELETE /applicationDefinition/portProtocolClassification\n\nportProtocolDelete114\n\nDelete user-defined port/protocol application classification",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_port_protocol_classification(
    ctx: Context,
    port: Annotated[
        str,
        Field(
            description="Port number identifying the application to delete. Use 0 for IP Protocol applications. Must be a non-negative integer."
        ),
    ],
    protocol: Annotated[
        int, Field(description="Protocol number: 6 for TCP, 17 for UDP, or any valid IP protocol number when port=0.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if port is not None:
        query_params["port"] = port
    if protocol is not None:
        query_params["protocol"] = protocol
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/portProtocolClassification",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_application_definition_saas_classification",
    description="DELETE /applicationDefinition/saasClassification\n\nsaasDelete117\n\nDelete user-defined SaaS cloud application definition",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_application_definition_saas_classification(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the user-defined SaaS application to delete. Must be >= 25000 as values below 25000 are reserved for Silver Peak defined SaaS applications."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/applicationDefinition/saasClassification",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_application_definition",
    description="GET /applicationDefinition\n\ngetApplicationDefinitionConfig\n\nRetrieve application definition configuration data",
    capability=Capability.READ,
)
async def edgeconnect_get_application_definition(
    ctx: Context,
    base: Annotated[
        str,
        Field(
            description="The classification type base path to query. Must not be empty. A forward slash is prepended automatically if not provided."
        ),
    ],
    resourceKey: Annotated[
        str | None,
        Field(
            default=None,
            description="The specific resource key to filter results. If empty or not provided, defaults to null (retrieves all matching base entries).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if base is not None:
        query_params["base"] = base
    if resourceKey is not None:
        query_params["resourceKey"] = resourceKey
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationDefinition",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_application_definition_app_express_app_config",
    description="GET /applicationDefinition/appExpressAppConfig\n\ngetAppExpressAppConfig\n\nGet AppExpress application configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_application_definition_app_express_app_config(
    ctx: Context,
    resourceKey: Annotated[
        str,
        Field(
            description="Specifies which configuration data to retrieve. Use 'userDefined' for custom user configurations or 'merged' for combined portal and user-defined settings."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if resourceKey is not None:
        query_params["resourceKey"] = resourceKey
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationDefinition/appExpressAppConfig",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_application_definition_app_express_group_association",
    description="GET /applicationDefinition/appExpressGroup/association\n\nappTagsGroupAssociationGet299\n\nGet AppExpress group to appliance associations",
    capability=Capability.READ,
)
async def edgeconnect_get_application_definition_app_express_group_association(
    ctx: Context,
    groupName: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of the AppExpress group to filter associations. When omitted, returns all associations for all groups.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if groupName is not None:
        query_params["groupName"] = groupName
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationDefinition/appExpressGroup/association",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_application_definition_app_express_group_config",
    description="GET /applicationDefinition/appExpressGroup/config\n\nappTagsGroupGet299\n\nGet all AppExpress group configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_application_definition_app_express_group_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationDefinition/appExpressGroup/config",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_application_definition_application_tags",
    description="GET /applicationDefinition/applicationTags\n\nappTagsGet89\n\nRetrieve user-defined application groups by resource key",
    capability=Capability.READ,
)
async def edgeconnect_get_application_definition_application_tags(
    ctx: Context,
    resourceKey: Annotated[
        str,
        Field(
            description="The key identifying which application groups data to retrieve. Use 'userDefined' to get user-defined application groups."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if resourceKey is not None:
        query_params["resourceKey"] = resourceKey
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationDefinition/applicationTags",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_application_definition_ip_intelligence_confidence",
    description="GET /applicationDefinition/ipIntelligenceConfidence\n\ngetIpIntelligenceConfidence\n\nRetrieve user-defined IP Intelligence confidence value",
    capability=Capability.READ,
)
async def edgeconnect_get_application_definition_ip_intelligence_confidence(
    ctx: Context,
    name: Annotated[
        str, Field(description="Application name to retrieve confidence value for. Must not be null or empty.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationDefinition/ipIntelligenceConfidence",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_application_definition_updated_time",
    description="GET /applicationDefinition/updatedTime\n\nupdateTimeRetriever119\n\nRetrieve modification times and hash codes for application definitions",
    capability=Capability.READ,
)
async def edgeconnect_get_application_definition_updated_time(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/applicationDefinition/updatedTime",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_application_definition_app_express_app_config",
    description="POST /applicationDefinition/appExpressAppConfig\n\ncreateOrUpdateAppExpressAppConfig\n\nCreate or update AppExpress application configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_app_express_app_config(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/appExpressAppConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_app_express_group_association",
    description="POST /applicationDefinition/appExpressGroup/association\n\nappTagsGroupAssociationPost290\n\nReplace all AppExpress group to appliance associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_app_express_group_association(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/appExpressGroup/association",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_app_express_group_config",
    description="POST /applicationDefinition/appExpressGroup/config\n\nappTagsGroupPost290\n\nCreate or update AppExpress group configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_app_express_group_config(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/appExpressGroup/config",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_application_tags",
    description="POST /applicationDefinition/applicationTags\n\nappTagsPost90\n\nCreate or update user-defined application groups or change application mode",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_application_tags(
    ctx: Context,
    mode: Annotated[
        str | None,
        Field(
            default=None,
            description="Switch application group mode. 'new' enables cloud-based groups from portal, 'old' uses legacy mode. Once switched to 'new', cannot revert to 'old'.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if mode is not None:
        query_params["mode"] = mode
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/applicationTags",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_application_tags_wildcard",
    description="POST /applicationDefinition/applicationTags/wildcard\n\nappGroupSearchPost91\n\nSearch application groups by wildcard pattern",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_application_tags_wildcard(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/applicationTags/wildcard",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_applications_wildcard",
    description="POST /applicationDefinition/applications/wildcard\n\nappSearchPost93\n\nSearch applications by wildcard pattern",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_applications_wildcard(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/applications/wildcard",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_auto_updates",
    description="POST /applicationDefinition/autoUpdates\n\ncreateOrUpdateAutoUpdateConfigData\n\nConfigure auto-update settings for application classification pipelines",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_auto_updates(
    ctx: Context,
    base: Annotated[
        str, Field(description='The auto-update configuration base path. Must be exactly "autoUpdateFromPortal".')
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if base is not None:
        query_params["base"] = base
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/autoUpdates",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_compound_classification",
    description="POST /applicationDefinition/compoundClassification\n\ncompoundPost97\n\nCreate or update compound application definition",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_compound_classification(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the compound application definition. Must be > 0 and match the id in the request body. IDs > 50000 are portal-modified user records requiring existing portal data."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/compoundClassification",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_compound_classification_reorder",
    description="POST /applicationDefinition/compoundClassification/reorder\n\ncompoundReorderPost95\n\nReorder user-defined compound application classification rules",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_compound_classification_reorder(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/compoundClassification/reorder",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_dns_classification",
    description="POST /applicationDefinition/dnsClassification\n\ndnsPost100\n\nCreate or update DNS-based application classification",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_dns_classification(
    ctx: Context,
    domain: Annotated[
        str, Field(description="The domain name to create or update. Must match the domain field in the request body.")
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if domain is not None:
        query_params["domain"] = domain
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/dnsClassification",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_dns_classification2_delete_domain",
    description="POST /applicationDefinition/dnsClassification2/deleteDomain\n\ndomainDeletePost101\n\nDelete user-defined DNS application definition by domain name",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_dns_classification2_delete_domain(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/dnsClassification2/deleteDomain",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_dns_classification2_domain",
    description="POST /applicationDefinition/dnsClassification2/domain\n\ndnsPost102\n\nCreate or modify a user-defined DNS application for domain name classification",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_dns_classification2_domain(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/dnsClassification2/domain",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_ip_intelligence_classification",
    description="POST /applicationDefinition/ipIntelligenceClassification\n\nipIntelligencePost105\n\nCreate or update user-defined Address Map entry",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_ip_intelligence_classification(
    ctx: Context,
    ipStart: Annotated[
        int,
        Field(
            description="Starting IPv4 address in 32-bit unsigned integer format. Must be less than or equal to ipEnd and match ip_start in request body. Valid range: 0 to 4294967295."
        ),
    ],
    ipEnd: Annotated[
        int,
        Field(
            description="Ending IPv4 address in 32-bit unsigned integer format. Must be greater than or equal to ipStart and match ip_end in request body. Valid range: 0 to 4294967295."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if ipStart is not None:
        query_params["ipStart"] = ipStart
    if ipEnd is not None:
        query_params["ipEnd"] = ipEnd
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/ipIntelligenceClassification",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_ip_intelligence_confidence",
    description="POST /applicationDefinition/ipIntelligenceConfidence\n\nipIntelligenceConfidencePost106\n\nCreate or update user-defined application confidence override",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_ip_intelligence_confidence(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/ipIntelligenceConfidence",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_meter_flow_classification",
    description="POST /applicationDefinition/meterFlowClassification\n\nmeterFlowPost112\n\nCreate or modify user-defined DPI meter flow application definition",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_meter_flow_classification(
    ctx: Context,
    flowType: Annotated[
        str,
        Field(
            description="Meter flow type identifier. Must be 'MF' for meter flow applications. This value must match the flowType in the request body."
        ),
    ],
    mid: Annotated[
        int,
        Field(
            description="Unique meter flow identifier (mid). Must match the mid value in the request body. This ID corresponds to an existing DPI application from the portal template data."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if flowType is not None:
        query_params["flowType"] = flowType
    if mid is not None:
        query_params["mid"] = mid
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/meterFlowClassification",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_port_protocol_classification",
    description="POST /applicationDefinition/portProtocolClassification\n\nportProtocolPost115\n\nCreate or modify user-defined port/protocol application classification",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_port_protocol_classification(
    ctx: Context,
    port: Annotated[
        str,
        Field(
            description="Port number for the application. Use 0 for IP Protocol applications. Must match the port value in the request body."
        ),
    ],
    protocol: Annotated[
        int,
        Field(
            description="Protocol number. Use 6 for TCP, 17 for UDP. For IP Protocol applications (port=0), any valid IP protocol number is accepted."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if port is not None:
        query_params["port"] = port
    if protocol is not None:
        query_params["protocol"] = protocol
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/portProtocolClassification",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_application_definition_saas_classification",
    description="POST /applicationDefinition/saasClassification\n\ncompoundPost118\n\nCreate or modify user-defined SaaS cloud application definition",
    capability=Capability.WRITE,
)
async def edgeconnect_post_application_definition_saas_classification(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="SaaS application ID. Use -1 to create a new application. For existing applications, must be >= 25000 (user-defined) and match the saasId in request body."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/applicationDefinition/saasClassification",
        query_params=query_params or None,
        body=body,
    )
