"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``customCerts``
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
    name="edgeconnect_delete_custom_cert",
    description="DELETE /customCert\n\nDeleteCustomCert207\n\nDelete custom CA certificate",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_custom_cert(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the custom CA certificate to delete. Must be a valid existing certificate ID."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/customCert",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_custom_cert",
    description="GET /customCert\n\nGetCustomCerts200\n\nGet all custom CA certificates",
    capability=Capability.READ,
)
async def edgeconnect_get_custom_cert(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/customCert",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_custom_cert_ca_certs_from_default_trust_store",
    description="GET /customCert/caCertsFromDefaultTrustStore\n\nGetCaCertsFromDefaultTrustStore\n\nRetrieve CA certificates from Portal's default trust store",
    capability=Capability.READ,
)
async def edgeconnect_get_custom_cert_ca_certs_from_default_trust_store(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/customCert/caCertsFromDefaultTrustStore",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_custom_cert_enable",
    description="GET /customCert/enable\n\nGetCustomCertsEnabled203\n\nGet custom CA certificate trust store status",
    capability=Capability.READ,
)
async def edgeconnect_get_custom_cert_enable(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/customCert/enable",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_custom_cert_settings",
    description="GET /customCert/settings\n\nretrieveSettings\n\nGet custom CA certificate trust store settings",
    capability=Capability.READ,
)
async def edgeconnect_get_custom_cert_settings(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/customCert/settings",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_custom_cert",
    description="POST /customCert\n\nAddCustomCert201\n\nAdd or update custom CA certificate",
    capability=Capability.WRITE,
)
async def edgeconnect_post_custom_cert(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/customCert",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_custom_cert_appliance_connectivity",
    description="POST /customCert/applianceConnectivity\n\nCustomCertsGetApplianceConnectivity202\n\nTest appliance connectivity to Portal and Orchestrator",
    capability=Capability.WRITE,
)
async def edgeconnect_post_custom_cert_appliance_connectivity(
    ctx: Context,
    custom: Annotated[
        bool,
        Field(
            description="When true, tests connectivity using custom CA certificates. When false, uses the default trust store."
        ),
    ],
    body: Annotated[list[Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if custom is not None:
        query_params["custom"] = custom
    return await edgeconnect_request(
        ctx,
        "POST",
        "/customCert/applianceConnectivity",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_custom_cert_auto_sync",
    description="POST /customCert/autoSync\n\ntoggleAutoSyncMode\n\nEnable or disable automatic certificate synchronization from the Cloud Portal",
    capability=Capability.WRITE,
)
async def edgeconnect_post_custom_cert_auto_sync(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/customCert/autoSync",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_custom_cert_enable",
    description="POST /customCert/enable\n\nUpdateCustomCertsEnabled204\n\nEnable or disable custom CA certificate trust store",
    capability=Capability.WRITE,
)
async def edgeconnect_post_custom_cert_enable(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/customCert/enable",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_custom_cert_enable_restart_orchestrator",
    description="POST /customCert/enableRestartOrchestrator\n\nenableRestartOrchestrator\n\nFlag Orchestrator for restart to apply custom certificate changes",
    capability=Capability.WRITE,
)
async def edgeconnect_post_custom_cert_enable_restart_orchestrator(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/customCert/enableRestartOrchestrator",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_custom_cert_orchestrator_connectivity",
    description="POST /customCert/orchestratorConnectivity\n\nCustomCertsGetOrchestratorConnectivity205\n\nTest Orchestrator connectivity to Portal",
    capability=Capability.WRITE,
)
async def edgeconnect_post_custom_cert_orchestrator_connectivity(
    ctx: Context,
    custom: Annotated[
        bool,
        Field(
            description="When true, uses custom CA certificates for the connectivity test. When false, uses the default system trust store."
        ),
    ],
    body: Annotated[list[Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if custom is not None:
        query_params["custom"] = custom
    return await edgeconnect_request(
        ctx,
        "POST",
        "/customCert/orchestratorConnectivity",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_custom_cert_verify",
    description="POST /customCert/verify\n\nCustomCertsVerification206\n\nVerify and validate a custom CA certificate",
    capability=Capability.WRITE,
)
async def edgeconnect_post_custom_cert_verify(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/customCert/verify",
        query_params=None,
        body=body,
    )
