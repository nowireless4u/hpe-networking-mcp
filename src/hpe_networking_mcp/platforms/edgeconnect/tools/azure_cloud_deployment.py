"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``azureCloudDeployment``
Operations in this file: 33
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_cloud_deployment_azure_accounts",
    description="DELETE /cloudDeployment/azure/accounts\n\ndeleteAzureAccount175\n\nDelete Azure subscription account",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_azure_accounts(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Orchestrator-assigned Azure account UUID to delete. Must be a valid non-empty UUID string that corresponds to an existing account."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/azure/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_cloud_deployment_azure_edgeconnects",
    description="DELETE /cloudDeployment/azure/edgeconnects\n\ndestroyDeploymentById180\n\nTerminate Azure Cloud Hub deployment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_azure_edgeconnects(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID. Identifies which Azure Cloud Hub deployment to terminate."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/azure/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_cloud_deployment_azure_load_balancer",
    description="DELETE /cloudDeployment/azure/load-balancer\n\ndestroyDeploymentByIdAzureIlb\n\nDelete Azure Load Balancer Deployment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_azure_load_balancer(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique Orchestrator-assigned deployment ID. Must reference an existing azure_load_balancer deployment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/azure/load-balancer",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_cloud_deployment_azure_nva_edgeconnects",
    description="DELETE /cloudDeployment/azure-nva/edgeconnects\n\ndestroyDeploymentByIdAzureNVA\n\nDestroy Azure NVA EdgeConnect deployment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_azure_nva_edgeconnects(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID to destroy. Must reference an existing azure_nva deployment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/azure-nva/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_cloud_deployment_azure_route_server",
    description="DELETE /cloudDeployment/azure/route-server\n\ndestroyDeploymentByIdAzureRouteServer\n\nDelete Azure Route Server Deployment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_azure_route_server(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique Orchestrator-assigned deployment ID. Identifies the Azure Route Server deployment to delete."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/azure/route-server",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_accounts",
    description="GET /cloudDeployment/azure/accounts\n\ngetAzureAccounts176\n\nRetrieve Azure cloud deployment accounts",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_accounts(
    ctx: Context,
    id: Annotated[
        str | None,
        Field(
            default=None,
            description="Orchestrator-assigned Azure account UUID. When omitted, all configured accounts are returned. When provided, returns only the matching account or 204 if not found.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_edgeconnects",
    description="GET /cloudDeployment/azure/edgeconnects\n\ngetConfigById181\n\nGet Azure Cloud Hub deployment configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_edgeconnects(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Orchestrator-assigned deployment ID. Omit to retrieve all Azure deployments, or provide a specific ID to retrieve a single deployment.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_edgeconnects_cloud_resources",
    description="GET /cloudDeployment/azure/edgeconnects/cloud-resources\n\ngetCloudResourcesById182\n\nGet Azure Cloud Hub deployment cloud resources",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_edgeconnects_cloud_resources(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique Orchestrator-assigned deployment identifier. Must be a valid Azure deployment ID returned from the deployment creation endpoint."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/edgeconnects/cloud-resources",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_edgeconnects_deploy_status",
    description="GET /cloudDeployment/azure/edgeconnects/deploy-status\n\ngetDeploymentStatusById183\n\nGet Azure EdgeConnect deployment status",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_edgeconnects_deploy_status(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique Orchestrator-assigned deployment identifier. Must be a valid positive integer referencing an existing Azure deployment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/edgeconnects/deploy-status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_edgeconnects_log",
    description="GET /cloudDeployment/azure/edgeconnects/log\n\ngetAzureCloudDeploymentLog\n\nDownload Azure Cloud Hub deployment log",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_edgeconnects_log(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="The unique deployment identifier assigned by the Orchestrator. This ID is returned when creating a new Azure deployment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/edgeconnects/log",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_load_balancer",
    description="GET /cloudDeployment/azure/load-balancer\n\ngetConfigByIdAzureIlb\n\nGet Azure Load Balancer Deployment Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_load_balancer(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique Orchestrator-assigned deployment ID. Optional parameter - when omitted, returns all azure_load_balancer deployments.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/load-balancer",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_load_balancer_cloud_resources",
    description="GET /cloudDeployment/azure/load-balancer/cloud-resources\n\ngetCloudResourcesByIdIlb\n\nGet Azure ILB cloud resources",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_load_balancer_cloud_resources(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID for the Azure load balancer. Must be a valid deployment ID returned from a previous deployment creation."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/load-balancer/cloud-resources",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_load_balancer_deploy_status",
    description="GET /cloudDeployment/azure/load-balancer/deploy-status\n\ngetDeploymentStatusByIdIlb\n\nGet deployment status for Azure load balancer",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_load_balancer_deploy_status(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Orchestrator-assigned deployment identifier. If omitted, returns status for all Azure load balancer deployments.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/load-balancer/deploy-status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_load_balancer_log",
    description="GET /cloudDeployment/azure/load-balancer/log\n\ngetAzureCloudDeploymentLogIlb\n\nDownload deployment log for Azure load balancer",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_load_balancer_log(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="The unique Orchestrator-assigned deployment ID for the Azure load balancer. Must be a valid positive integer corresponding to an existing deployment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/load-balancer/log",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_nva_edgeconnects",
    description="GET /cloudDeployment/azure-nva/edgeconnects\n\ngetConfigByIdAzureNVA\n\nGet Azure NVA deployment configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_nva_edgeconnects(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Orchestrator-assigned deployment ID to retrieve a specific deployment. Omit to retrieve all azure_nva deployments. Must be a positive integer referencing an existing deployment.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure-nva/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_nva_edgeconnects_cloud_resources",
    description="GET /cloudDeployment/azure-nva/edgeconnects/cloud-resources\n\ngetCloudResourcesByIdAzureNVA\n\nGet Azure NVA cloud resources for a Virtual WAN Hub deployment",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_nva_edgeconnects_cloud_resources(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique deployment identifier assigned by the Orchestrator. Use GET /cloudDeployment/azure-nva/edgeconnects to retrieve available deployment IDs."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure-nva/edgeconnects/cloud-resources",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_nva_edgeconnects_deploy_status",
    description="GET /cloudDeployment/azure-nva/edgeconnects/deploy-status\n\ngetDeploymentStatusByIdAzureNVA\n\nGet deployment status for Azure NVA EdgeConnect in Virtual WAN hub",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_nva_edgeconnects_deploy_status(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier for the Azure NVA deployment assigned by Orchestrator. Obtain this ID from the POST /cloudDeployment/azure-nva/edgeconnects response or GET /cloudDeployment/azure-nva/edgeconnects endpoint."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure-nva/edgeconnects/deploy-status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_nva_edgeconnects_log",
    description="GET /cloudDeployment/azure-nva/edgeconnects/log\n\ngetAzureCloudDeploymentLogAzureNVA\n\nDownload deployment log for Azure NVA cloud hub in virtual WAN",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_nva_edgeconnects_log(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique deployment identifier assigned by the Orchestrator. This ID is returned when creating a new Azure NVA deployment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure-nva/edgeconnects/log",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_route_server",
    description="GET /cloudDeployment/azure/route-server\n\ngetConfigByIdAzureRouteServer\n\nRetrieve Azure Route Server Deployment Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_route_server(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Orchestrator-assigned deployment ID. When omitted, returns all Azure Route Server deployments.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/route-server",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_route_server_cloud_resources",
    description="GET /cloudDeployment/azure/route-server/cloud-resources\n\ngetCloudResourcesByIdAzureRouteServer\n\nRetrieve Azure Route Server cloud resources",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_route_server_cloud_resources(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID for the Azure Route Server. Must be a valid deployment ID that exists and is of type 'azure_route_server'."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/route-server/cloud-resources",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_route_server_deploy_status",
    description="GET /cloudDeployment/azure/route-server/deploy-status\n\ngetDeploymentStatusByIdRouteServer\n\nGet deployment status for Azure Route Server",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_route_server_deploy_status(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Orchestrator-assigned deployment ID. If omitted, returns status for all Azure Route Server deployments.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/route-server/deploy-status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_azure_route_server_log",
    description="GET /cloudDeployment/azure/route-server/log\n\ngetAzureCloudDeploymentLogRouteServer\n\nDownload Azure Route Server deployment log file",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_azure_route_server_log(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the Azure Route Server deployment. Obtained from POST /cloudDeployment/azure/route-server or GET /cloudDeployment/azure/route-server."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/azure/route-server/log",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_azure_accounts",
    description="POST /cloudDeployment/azure/accounts\n\naddAzureAccount174\n\nAdd Azure account for cloud deployment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_azure_accounts(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/azure/accounts",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_azure_edgeconnects",
    description="POST /cloudDeployment/azure/edgeconnects\n\ndeployAzureAppliances179\n\nDeploy Cloud Hub(s) in Azure",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_azure_edgeconnects(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/azure/edgeconnects",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_azure_edgeconnects_instance",
    description="POST /cloudDeployment/azure/edgeconnects/instance\n\naddAzureInstance\n\nAdd instance to an existing Azure cloud deployment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_azure_edgeconnects_instance(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID for the existing Azure cloud deployment. Must be a valid deployment ID that exists and belongs to the Azure provider."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/azure/edgeconnects/instance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_azure_load_balancer",
    description="POST /cloudDeployment/azure/load-balancer\n\ndeployAzureIlb\n\nDeploy Azure Internal Load Balancer",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_azure_load_balancer(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/azure/load-balancer",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_azure_nva_edgeconnects",
    description="POST /cloudDeployment/azure-nva/edgeconnects\n\ndeployAzureAppliancesInVirtualWANHub\n\nDeploy EdgeConnect appliances in Azure Virtual WAN hub",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_azure_nva_edgeconnects(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    deploy: Annotated[
        bool | None,
        Field(default=None, description="Flag to trigger deployment. When true, deployment is queued for execution."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if deploy is not None:
        query_params["deploy"] = deploy
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/azure-nva/edgeconnects",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_azure_route_server",
    description="POST /cloudDeployment/azure/route-server\n\ndeployAzureRouteServer\n\nDeploy Azure Route Server",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_azure_route_server(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    deploy: Annotated[
        bool | None,
        Field(default=None, description="Flag to trigger deployment. When true, initiates the deployment process."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if deploy is not None:
        query_params["deploy"] = deploy
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/azure/route-server",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_azure_accounts",
    description="PUT /cloudDeployment/azure/accounts\n\nputAzureAccount177\n\nUpdate Azure subscription account",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_azure_accounts(
    ctx: Context,
    id: Annotated[
        str,
        Field(description="Orchestrator-assigned Azure account UUID to update. Must not be null or whitespace-only."),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/azure/accounts",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_azure_edgeconnects",
    description="PUT /cloudDeployment/azure/edgeconnects\n\nazureDeploymentCommentUpdate\n\nUpdate Azure Cloud Hub deployment comment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_azure_edgeconnects(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID. Identifies which Azure Cloud Hub deployment to update."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/azure/edgeconnects",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_azure_load_balancer",
    description="PUT /cloudDeployment/azure/load-balancer\n\nazureDeploymentCommentUpdateIlb\n\nUpdate Azure Load Balancer Deployment Configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_azure_load_balancer(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned unique deployment ID. Must reference an existing azure_load_balancer deployment."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/azure/load-balancer",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_azure_nva_edgeconnects",
    description="PUT /cloudDeployment/azure-nva/edgeconnects\n\nazureDeploymentCommentUpdateAzureNVA\n\nUpdate Azure NVA deployment comment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_azure_nva_edgeconnects(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID to update. Must reference an existing azure_nva deployment."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/azure-nva/edgeconnects",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_azure_route_server",
    description="PUT /cloudDeployment/azure/route-server\n\nazureDeploymentCommentUpdateRouteServer\n\nUpdate Azure Route Server Deployment Comment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_azure_route_server(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique Orchestrator-assigned deployment ID. Identifies the Azure Route Server deployment to update."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/azure/route-server",
        query_params=query_params or None,
        body=body,
    )
