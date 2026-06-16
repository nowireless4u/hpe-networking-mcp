"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``awsCloudDeployment``
Operations in this file: 12
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
    name="edgeconnect_delete_cloud_deployment_aws_accounts",
    description="DELETE /cloudDeployment/aws/accounts\n\ndeleteAwsAccount\n\nDelete AWS account by ID",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_aws_accounts(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="UUID of the AWS account to delete. Obtained from GET /cloudDeployment/aws/accounts or POST response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/aws/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_cloud_deployment_aws_edgeconnects",
    description="DELETE /cloudDeployment/aws/edgeconnects\n\ndestroyDeploymentById169\n\nTerminate AWS Cloud Hub deployment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cloud_deployment_aws_edgeconnects(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID to terminate. Obtain from GET /cloudDeployment/aws/edgeconnects or POST response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cloudDeployment/aws/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_aws_accounts",
    description="GET /cloudDeployment/aws/accounts\n\ngetAWSAccounts165\n\nRetrieve AWS accounts",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_aws_accounts(
    ctx: Context,
    id: Annotated[
        str | None,
        Field(
            default=None,
            description="UUID of a specific AWS account to retrieve. If omitted, all registered AWS accounts are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/aws/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_aws_edgeconnects",
    description="GET /cloudDeployment/aws/edgeconnects\n\ngetConfigById170\n\nRetrieve AWS Cloud Hub deployment configuration(s)",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_aws_edgeconnects(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Orchestrator-assigned deployment ID. If omitted, all AWS deployments are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/aws/edgeconnects",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_aws_edgeconnects_cloud_resources",
    description="GET /cloudDeployment/aws/edgeconnects/cloud-resources\n\ngetCloudResourcesById171\n\nRetrieve AWS Cloud Hub deployment cloud resources",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_aws_edgeconnects_cloud_resources(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID. Obtain from GET /cloudDeployment/aws/edgeconnects or POST response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/aws/edgeconnects/cloud-resources",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_aws_edgeconnects_deploy_status",
    description="GET /cloudDeployment/aws/edgeconnects/deploy-status\n\ngetDeploymentStatusById172\n\nRetrieve AWS Cloud Hub deployment status",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_aws_edgeconnects_deploy_status(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID. Obtain from GET /cloudDeployment/aws/edgeconnects or POST response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/aws/edgeconnects/deploy-status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cloud_deployment_aws_edgeconnects_log",
    description="GET /cloudDeployment/aws/edgeconnects/log\n\ngetCloudDeploymentLog\n\nDownload AWS Cloud Hub deployment log file",
    capability=Capability.READ,
)
async def edgeconnect_get_cloud_deployment_aws_edgeconnects_log(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID. Obtain from GET /cloudDeployment/aws/edgeconnects or POST response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cloudDeployment/aws/edgeconnects/log",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_aws_accounts",
    description="POST /cloudDeployment/aws/accounts\n\naddAwsAccount163\n\nRegister a new AWS account for cloud deployment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_aws_accounts(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/aws/accounts",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_aws_edgeconnects",
    description="POST /cloudDeployment/aws/edgeconnects\n\ndeployAwsAppliances168\n\nDeploy Cloud Hub(s) in AWS",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_aws_edgeconnects(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cloudDeployment/aws/edgeconnects",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cloud_deployment_aws_edgeconnects_instance",
    description="POST /cloudDeployment/aws/edgeconnects/instance\n\naddAwsInstance\n\nAdd instance to existing AWS Cloud Hub deployment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cloud_deployment_aws_edgeconnects_instance(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID. Obtain from GET /cloudDeployment/aws/edgeconnects or POST response."
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
        "/cloudDeployment/aws/edgeconnects/instance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_aws_accounts",
    description="PUT /cloudDeployment/aws/accounts\n\nputAwsAccount166\n\nUpdate an existing AWS account",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_aws_accounts(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="UUID of the AWS account to update. Obtained from GET /cloudDeployment/aws/accounts or POST response."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/aws/accounts",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cloud_deployment_aws_edgeconnects",
    description="PUT /cloudDeployment/aws/edgeconnects\n\nawsDeploymentCommentUpdate\n\nUpdate AWS deployment comment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cloud_deployment_aws_edgeconnects(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Orchestrator-assigned deployment ID. Obtain from GET /cloudDeployment/aws/edgeconnects or POST response."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cloudDeployment/aws/edgeconnects",
        query_params=query_params or None,
        body=body,
    )
