"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``loopbackOrch``
Operations in this file: 7
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
    name="edgeconnect_delete_loopback_orch_pool_reclaim",
    description="DELETE /loopbackOrch/pool/reclaim\n\nreclaimAddrBySpecificId457\n\nReclaim a deleted loopback IP address by record ID",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_loopback_orch_pool_reclaim(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique database identifier of the deleted loopback history record to reclaim. Obtain this ID from the /loopbackOrch/pool/history endpoint response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/loopbackOrch/pool/reclaim",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_loopback_orch_pool_reclaim_by_seg",
    description="DELETE /loopbackOrch/pool/reclaimBySeg\n\nreclaimBySeg457\n\nReclaim all deleted loopback IP addresses by segment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_loopback_orch_pool_reclaim_by_seg(
    ctx: Context,
    segId: Annotated[
        int, Field(description="VRF segment ID to reclaim deleted addresses from. Use 0 for the default segment.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if segId is not None:
        query_params["segId"] = segId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/loopbackOrch/pool/reclaimBySeg",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_loopback_orch_pool_reclaim_by_seg_reg_subnet",
    description="DELETE /loopbackOrch/pool/reclaimBySegRegSubnet\n\nreclaimBySegRegSubnet457\n\nReclaim deleted loopback IP addresses by segment, region, and subnet",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_loopback_orch_pool_reclaim_by_seg_reg_subnet(
    ctx: Context,
    seg: Annotated[
        int, Field(description="VRF segment ID to filter deleted addresses. Use 0 for the default segment.")
    ],
    reg: Annotated[
        int, Field(description="Region ID to filter deleted addresses. Use 0 for the global/default region.")
    ],
    subnet: Annotated[
        str,
        Field(
            description="Loopback pool subnet in CIDR notation (IPv4 or IPv6). Must match an existing pool configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if seg is not None:
        query_params["seg"] = seg
    if reg is not None:
        query_params["reg"] = reg
    if subnet is not None:
        query_params["subnet"] = subnet
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/loopbackOrch/pool/reclaimBySegRegSubnet",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_loopback_orch",
    description="GET /loopbackOrch\n\nloopbackOrchGet453\n\nRetrieve loopback orchestration settings",
    capability=Capability.READ,
)
async def edgeconnect_get_loopback_orch(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/loopbackOrch",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_loopback_orch_pool",
    description="GET /loopbackOrch/pool\n\nloopbackPoolInfo455\n\nRetrieve loopback pool allocation summary",
    capability=Capability.READ,
)
async def edgeconnect_get_loopback_orch_pool(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/loopbackOrch/pool",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_loopback_orch_pool_history",
    description="GET /loopbackOrch/pool/history\n\nloopbackPoolInfoSeg456\n\nRetrieve deleted loopback IP allocation history by segment",
    capability=Capability.READ,
)
async def edgeconnect_get_loopback_orch_pool_history(
    ctx: Context,
    seg: Annotated[int, Field(description="VRF segment ID to filter history records. Use 0 for the default segment.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if seg is not None:
        query_params["seg"] = seg
    return await edgeconnect_request(
        ctx,
        "GET",
        "/loopbackOrch/pool/history",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_loopback_orch",
    description="POST /loopbackOrch\n\nloopbackOrchPost454\n\nSet loopback orchestration configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_loopback_orch(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/loopbackOrch",
        query_params=None,
        body=body,
    )
