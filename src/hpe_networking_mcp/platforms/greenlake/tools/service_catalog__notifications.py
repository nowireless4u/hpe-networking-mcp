"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-provision-nbapi-v1beta1-service-provision-v1beta1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``notifications``   Operations: 1
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_post_service_catalog_v1beta1_notifications_provision_response",
    description="POST /service-catalog/v1beta1/notifications/provision-response\n\npostServiceProvisionResponse\n\nReceive a Notification from an internal service conveying the response for a Service Provision request",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1beta1_notifications_provision_response(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/service-catalog/v1beta1/notifications/provision-response",
        body=body,
    )
