"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``webhooks_v1beta1``   Operations: 7
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_delete_compute_ops_mgmt_v1beta1_webhooks_webhook_id",
    description="DELETE /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}\n\ndelete_webhook\n\nDelete a saved webhook",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_mgmt_v1beta1_webhooks_webhook_id(
    ctx: Context,
    webhook_id: Annotated[str, Field(description="Webhook ID")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/webhooks/{path_seg(webhook_id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_webhooks",
    description="GET /compute-ops-mgmt/v1beta1/webhooks\n\nget_v1beta1_webhooks\n\nRetrieve all webhooks",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_webhooks(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta1/webhooks",
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_webhooks_webhook_id",
    description="GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}\n\nget_v1beta1_webhooks_by_id\n\nGet a webhook",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_webhooks_webhook_id(
    ctx: Context,
    webhook_id: Annotated[str, Field(description="Webhook ID")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/webhooks/{path_seg(webhook_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_webhooks_webhook_id_deliveries",
    description="GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries\n\nget_v1beta1_webhooks_deliveries\n\nGet details on all webhook deliveries.",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_webhooks_webhook_id_deliveries(
    ctx: Context,
    webhook_id: Annotated[str, Field(description="Webhook ID")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/webhooks/{path_seg(webhook_id)}/deliveries"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_webhooks_webhook_id_deliveries_delivery_id",
    description="GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries/{delivery_id}\n\nget_v1beta1_webhooks_delivery_by_id\n\nGet details for a specific delivery",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_webhooks_webhook_id_deliveries_delivery_id(
    ctx: Context,
    webhook_id: Annotated[str, Field(description="Webhook ID")],
    delivery_id: Annotated[str, Field(description="Delivery ID")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/webhooks/{path_seg(webhook_id)}/deliveries/{path_seg(delivery_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1beta1_webhooks_webhook_id",
    description="PATCH /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}\n\npatch_v1beta1_webhook_by_id\n\nPatch a webhook",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1beta1_webhooks_webhook_id(
    ctx: Context,
    webhook_id: Annotated[str, Field(description="Webhook ID")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/webhooks/{path_seg(webhook_id)}"
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta1_webhooks",
    description="POST /compute-ops-mgmt/v1beta1/webhooks\n\npost_v1beta1_webhooks\n\nCreate a webhook",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta1_webhooks(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1beta1/webhooks",
        body=body,
    )
