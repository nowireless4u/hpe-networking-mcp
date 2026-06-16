"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``ospf``
Operations in this file: 11
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
    name="edgeconnect_get_ospf_config_all_vrfs_interfaces",
    description="GET /ospf/config/allVrfs/interfaces\n\nGetAllSegmentOSPFInterfacesConfig480\n\nGet OSPF interface configurations for all VRF segments",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_config_all_vrfs_interfaces(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool,
        Field(
            description="Data source selector. When true, retrieves cached data from Orchestrator database; when false, fetches live data directly from the appliance."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/config/allVrfs/interfaces",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_config_all_vrfs_system",
    description="GET /ospf/config/allVrfs/system\n\nGetAllSegmentOSPFConfig481\n\nGet OSPF system configuration for all VRFs/segments",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_config_all_vrfs_system(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Determines the data source. When true, retrieves cached data from Orchestrator database. When false or omitted, fetches live data directly from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/config/allVrfs/system",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_config_areas",
    description="GET /ospf/config/areas\n\nGetOSPFAreasConfig482\n\nGet OSPF areas configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_config_areas(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached configuration from Orchestrator database. When false or omitted, fetches live data directly from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/config/areas",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_config_interfaces",
    description="GET /ospf/config/interfaces\n\nGetInterfaceConfigDta483\n\nGet OSPF interfaces configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_config_interfaces(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool,
        Field(
            description="Data source selector. When true, returns cached configuration from Orchestrator database. When false, fetches live configuration directly from the appliance."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/config/interfaces",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_config_system",
    description="GET /ospf/config/system\n\nGetOSPFSystemConfig484\n\nGet appliance OSPF system-level configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_config_system(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool,
        Field(
            description="Data source selector. When true, retrieves cached data from GMS database. When false, fetches live data directly from the appliance."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/config/system",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_state_all_vrfs_interfaces",
    description="GET /ospf/state/allVrfs/interfaces\n\ngetAllVrfsOspfInterfacesState\n\nGet OSPF interface state for all VRFs",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_state_all_vrfs_interfaces(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, retrieves cached data from GMS database instead of querying the appliance directly. Useful for offline appliances or reducing appliance load.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/state/allVrfs/interfaces",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_state_all_vrfs_neighbors",
    description="GET /ospf/state/allVrfs/neighbors\n\ngetAllVrfsOspfNeighborsState\n\nGet OSPF neighbors state for all VRF segments",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_state_all_vrfs_neighbors(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, retrieves cached data from GMS database instead of querying the appliance directly. Defaults to false.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/state/allVrfs/neighbors",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_state_all_vrfs_system",
    description="GET /ospf/state/allVrfs/system\n\ngetAllVrfsOspfSystemState\n\nGet OSPF system state for all VRFs",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_state_all_vrfs_system(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, retrieves cached OSPF state from the GMS database instead of querying the appliance directly. Useful for offline appliances or reducing load.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/state/allVrfs/system",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_state_interfaces",
    description="GET /ospf/state/interfaces\n\ngetOspfInterfaceStateDetails\n\nGet OSPF interface state details",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_state_interfaces(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database. When false or omitted, fetches live data directly from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/state/interfaces",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_state_neighbors",
    description="GET /ospf/state/neighbors\n\ngetOspfNeighborState\n\nGet OSPF Neighbor State",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_state_neighbors(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, retrieves cached data from database. When false or omitted, fetches live data directly from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/state/neighbors",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_ospf_state_system",
    description="GET /ospf/state/system\n\ngetOspfStateSystem\n\nGet OSPF system state",
    capability=Capability.READ,
)
async def edgeconnect_get_ospf_state_system(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromGms: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, retrieves cached data from Orchestrator database. When false or omitted, fetches live data directly from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromGms is not None:
        query_params["fromGms"] = fromGms
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ospf/state/system",
        query_params=query_params or None,
    )
