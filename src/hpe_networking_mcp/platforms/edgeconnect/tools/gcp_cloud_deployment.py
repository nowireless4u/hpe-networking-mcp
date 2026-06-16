"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gcpCloudDeployment``
Operations in this file: 14
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
    name="edgeconnect_delete_cloud_deployment_gcp_accounts",
    description="DELETE /cloudDeployment/gcp/accounts\n\ndeleteGCPAccounts186\n\nDelete a registered GCP service account",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_gcp_accounts(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The GCP project ID of the account to delete. This is the project_id extracted from the service account key when the account was registered."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/gcp/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_cloud_deployment_gcp_edgeconnects",
    description="DELETE /cloudDeployment/gcp/edgeconnects\n\ndestroyGCPDeploymentById192\n\nDestroy all Cloud Hub instances in a GCP deployment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_gcp_edgeconnects(
    ctx: Context,
    id: Annotated[
        float,
        Field(
            description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment that is not currently in DEPLOYING (2) or DESTROYING (5) status."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/gcp/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_cloud_deployment_gcp_edgeconnects_instance",
    description="DELETE /cloudDeployment/gcp/edgeconnects/instance\n\ndestroyGCPInstance191\n\nDestroy a deployed GCP Cloud Hub instance",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_gcp_edgeconnects_instance(
    ctx: Context,
    deploymentId: Annotated[
        float,
        Field(
            description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment that is not currently deploying or destroying."
        ),
    ],
    instanceId: Annotated[
        str,
        Field(
            description="UUID of the instance to terminate. Must match an existing instance within the specified deployment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if deploymentId is not None:
        query_params["deploymentId"] = deploymentId
    if instanceId is not None:
        query_params["instanceId"] = instanceId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/gcp/edgeconnects/instance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_gcp_accounts",
    description="GET /cloudDeployment/gcp/accounts\n\ngetgcpAccounts187\n\nRetrieve GCP service accounts",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_gcp_accounts(
    ctx: Context,
    id: Annotated[
        str | None,
        Field(default=None, description="GCP project ID to filter by. If omitted, returns all registered accounts."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/gcp/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_gcp_edgeconnects",
    description="GET /cloudDeployment/gcp/edgeconnects\n\ngetConfigById193\n\nRetrieve GCP Cloud Hub deployment configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_gcp_edgeconnects(
    ctx: Context,
    id: Annotated[
        float | None,
        Field(
            default=None,
            description="Orchestrator-assigned deployment ID. If omitted or -1, returns all GCP deployments. If specified, returns only the matching deployment.",
        ),
    ] = None,
    retryApply: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, retries a failed deployment. Requires a valid deployment ID. Deployment must not be in DEPLOYING or DESTROYING status.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if retryApply is not None:
        query_params["retryApply"] = retryApply
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/gcp/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_gcp_edgeconnects_cloud_resources",
    description="GET /cloudDeployment/gcp/edgeconnects/cloud-resources\n\ngetCloudResourcesById194\n\nRetrieve GCP Cloud Hub deployment cloud resources",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_gcp_edgeconnects_cloud_resources(
    ctx: Context,
    id: Annotated[
        float,
        Field(
            description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment with Terraform state."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/gcp/edgeconnects/cloud-resources",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_gcp_edgeconnects_deploy_status",
    description="GET /cloudDeployment/gcp/edgeconnects/deploy-status\n\ngetDeploymentStatusById195\n\nGet GCP Cloud Hub deployment status",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_gcp_edgeconnects_deploy_status(
    ctx: Context,
    id: Annotated[
        float, Field(description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/gcp/edgeconnects/deploy-status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_gcp_edgeconnects_log",
    description="GET /cloudDeployment/gcp/edgeconnects/log\n\ngetgcpCloudDeploymentLog\n\nDownload GCP Cloud Hub deployment Terraform log",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_gcp_edgeconnects_log(
    ctx: Context,
    id: Annotated[
        float, Field(description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/gcp/edgeconnects/log",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_gcp_accounts",
    description="POST /cloudDeployment/gcp/accounts\n\naddGCPAccount185\n\nRegister a GCP service account for cloud deployment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_gcp_accounts(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/gcp/accounts",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_gcp_edgeconnects",
    description="POST /cloudDeployment/gcp/edgeconnects\n\ndeployGCPAppliances190\n\nDeploy Cloud Hub(s) in GCP",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_gcp_edgeconnects(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/gcp/edgeconnects",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_gcp_edgeconnects_instance",
    description="POST /cloudDeployment/gcp/edgeconnects/instance\n\naddGCPInstance196\n\nAdd Cloud Hub instance(s) to an existing GCP deployment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_gcp_edgeconnects_instance(
    ctx: Context,
    id: Annotated[
        float,
        Field(
            description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment that is not currently deploying or destroying."
        ),
    ],
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/gcp/edgeconnects/instance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_gcp_accounts",
    description="PUT /cloudDeployment/gcp/accounts\n\nputGCPAccount188\n\nUpdate GCP service account credentials",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_gcp_accounts(
    ctx: Context,
    id: Annotated[
        str,
        Field(description="The GCP project ID of the account to update. Must match an existing registered account."),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/gcp/accounts",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_gcp_edgeconnects",
    description="PUT /cloudDeployment/gcp/edgeconnects\n\ngcpDeploymentCommentUpdate\n\nUpdate GCP deployment comment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_gcp_edgeconnects(
    ctx: Context,
    id: Annotated[
        float, Field(description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment.")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/gcp/edgeconnects",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_gcp_edgeconnects_instance",
    description="PUT /cloudDeployment/gcp/edgeconnects/instance\n\nputGCPInstanceComment\n\nUpdate GCP instance comment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_gcp_edgeconnects_instance(
    ctx: Context,
    deploymentId: Annotated[
        float, Field(description="Orchestrator-assigned deployment ID. Must reference an existing GCP deployment.")
    ],
    instanceId: Annotated[
        str,
        Field(description="Unique instance identifier (UUID) assigned by Orchestrator when the instance was created."),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if deploymentId is not None:
        query_params["deploymentId"] = deploymentId
    if instanceId is not None:
        query_params["instanceId"] = instanceId
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/gcp/edgeconnects/instance",
        query_params=query_params or None,
        body=body,
    )
