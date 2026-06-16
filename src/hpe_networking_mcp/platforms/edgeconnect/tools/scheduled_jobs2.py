"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``scheduledJobs2``
Operations in this file: 12
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
    name="edgeconnect_delete_gms_job",
    description="DELETE /gms/job\n\nscheduledJobDelete301\n\nDelete a scheduled job",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_job(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the job to delete. Must reference an existing job that is not a system job or protected integration job."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gms/job",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_stats_collector_job",
    description="DELETE /statsCollector/job\n\ndeleteScScheduledJob724\n\nDelete a scheduled job from Stats Collector",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_stats_collector_job(
    ctx: Context,
    jobId: Annotated[
        int,
        Field(
            description="Unique identifier of the scheduled job to delete. Must reference an existing job in the Stats Collector."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if jobId is not None:
        query_params["jobId"] = jobId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/statsCollector/job",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_job",
    description="GET /gms/job\n\nscheduledJobsGet295\n\nRetrieve scheduled jobs from Orchestrator",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_job(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique job identifier. When provided, returns only the job with this ID. If the job doesn't exist, returns 400 Bad Request.",
        ),
    ] = None,
    currentlyRunningJob: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns only jobs that are currently executing. Can be combined with `jobCategory` and `jobType` filters. Default is false.",
        ),
    ] = None,
    noPreFireTime: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, skips fetching previous fire time from Quartz scheduler for faster response. Default is false.",
        ),
    ] = None,
    jobCategory: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter jobs by category type. Only applies when `currentlyRunningJob=true`. Valid values: 1=TestJob, 2=Orchestrator Report, 3=Orchestrator Backup, 4=Appliance Reboot/Shutdown, 5=Appliance QOS Scheduling, 6=IPsec Pre-shared Key Rotation, 7=Ikeless Seed Rotation, 8=Auto MTU Discover, 10=Azure Get Data, 11=Check Point Get Data, 12=Zscaler Get Data, 13=AWS TGNM Get Data, 14=IDS/IPS Signature Downloader, 15=ClearPass Policy Manager, 16=Stats Collector Backup, 20=IP Objects Merging, 21=Netskope Get Data, 22=HPE SSE Get Data, 23=Azure LAN Get Data, 24=SSE Connector Matrix.",
        ),
    ] = None,
    jobType: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter jobs by type. Only applies when `currentlyRunningJob=true`. Values: 1=User-defined job (created via API), 2=System job (auto-created by Orchestrator).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if currentlyRunningJob is not None:
        query_params["currentlyRunningJob"] = currentlyRunningJob
    if noPreFireTime is not None:
        query_params["noPreFireTime"] = noPreFireTime
    if jobCategory is not None:
        query_params["jobCategory"] = jobCategory
    if jobType is not None:
        query_params["jobType"] = jobType
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/job",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_job_debug",
    description="GET /gms/job/debug\n\nQuartzJobsGet305\n\nGet all scheduled jobs in Quartz scheduler",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_job_debug(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/job/debug",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_job_historical",
    description="GET /gms/job/historical\n\ngetHistoricalJobs\n\nRetrieve historical job execution records",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_job_historical(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of a specific historical job record. When provided, returns only that single job wrapped in an array. Takes precedence over all other parameters.",
        ),
    ] = None,
    lastXDays: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter jobs that ended within the last X days. Maximum allowed value is 180 days. Can be combined with scheduleId parameter.",
        ),
    ] = None,
    scheduleId: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter jobs by their associated scheduled job ID. Returns all historical executions for that schedule. Can be combined with lastXDays or latest parameters.",
        ),
    ] = None,
    latest: Annotated[
        str | None,
        Field(
            default=None,
            description="When set to 'true' with scheduleId, returns only the most recent execution. Cannot be used together with lastXDays parameter.",
        ),
    ] = None,
    from_: Annotated[
        int | None,
        Field(
            default=None,
            description="Start of time range filter as Unix epoch timestamp in seconds. Must be used together with 'to' parameter.",
        ),
    ] = None,
    to: Annotated[
        int | None,
        Field(
            default=None,
            description="End of time range filter as Unix epoch timestamp in seconds. Must be used together with 'from' parameter.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if lastXDays is not None:
        query_params["lastXDays"] = lastXDays
    if scheduleId is not None:
        query_params["scheduleId"] = scheduleId
    if latest is not None:
        query_params["latest"] = latest
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/job/historical",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_job_report_viewport",
    description="GET /gms/job/reportViewport\n\nreportViewportGet299\n\nGet report viewport configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_job_report_viewport(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/job/reportViewport",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_stats_collector_job_historical",
    description="GET /statsCollector/job/historical\n\ngetStatsCollectorHistoricalJobs\n\nRetrieve historical stats collector job records",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_collector_job_historical(
    ctx: Context,
    lastXDays: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter jobs that ended within the specified number of days. Maximum allowed value is 180 days. Can be combined with scheduleId parameter.",
        ),
    ] = None,
    scheduleId: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter historical jobs by the associated scheduled job ID (assocId). Returns jobs that were executed from the specified schedule.",
        ),
    ] = None,
    latest: Annotated[
        str | None,
        Field(
            default=None,
            description="When set to any non-empty value with scheduleId, returns only the most recent historical job for that schedule. Ignored if scheduleId is not provided.",
        ),
    ] = None,
    from_: Annotated[
        int | None,
        Field(
            default=None,
            description="Start time filter in Unix epoch seconds. Must be used together with 'to' parameter to define a time range. Returns jobs with end_time within the specified range.",
        ),
    ] = None,
    to: Annotated[
        int | None,
        Field(
            default=None,
            description="End time filter in Unix epoch seconds. Must be used together with 'from' parameter to define a time range. Returns jobs with end_time within the specified range.",
        ),
    ] = None,
    jobCategory: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by job category type. Valid values: 1=TestJob, 2=GMS Report, 3=GMS Backup, 4=Appliance Reboot/Shutdown, 5=Appliance QOS Scheduling, 6=IPsec Preshared Key Rotation, 7=IKEless Seed Rotation, 8=Auto MTU Discover, 14=IDS/IPS Signature Downloader, 16=Stats Collector Backup.",
        ),
    ] = None,
    scId: Annotated[
        int | None,
        Field(
            default=None,
            description="Stats collector ID to filter results from a specific stats collector instance. When used with jobCategory, returns the latest historical job for that category from the specified stats collector.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if lastXDays is not None:
        query_params["lastXDays"] = lastXDays
    if scheduleId is not None:
        query_params["scheduleId"] = scheduleId
    if latest is not None:
        query_params["latest"] = latest
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    if jobCategory is not None:
        query_params["jobCategory"] = jobCategory
    if scId is not None:
        query_params["scId"] = scId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/statsCollector/job/historical",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_stats_collector_job_scheduled",
    description="GET /statsCollector/job/scheduled\n\ngetStatsCollectorScheduledJobs\n\nRetrieve scheduled jobs from all Stats Collector instances",
    capability=Capability.READ,
)
async def edgeconnect_get_stats_collector_job_scheduled(
    ctx: Context,
    currentlyRunningJob: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns only jobs that are currently executing. When false or omitted, returns all scheduled jobs.",
        ),
    ] = None,
    jobCategory: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter currently running jobs by category. Only applies when `currentlyRunningJob=true`. Valid values: 1=TestJob, 2=OrchestratorReport, 3=OrchestratorBackup, 4=ApplianceReboot/Shutdown, 5=ApplianceQOSScheduling, 6=IPsecPre-sharedKeyRotation, 7=IkelessSeedRotation, 8=AutoMTUDiscover, 10=AzureGetData, 11=CheckPointGetData, 12=ZscalerGetData, 13=AWSTGNMGetData, 14=IDS/IPSSignatureDownloader, 15=ClearPassJob, 16=StatsCollectorBackup, 20=IPObjectsMergingJob, 21=NetskopeGetData, 22=HPESSEGetData, 23=AzureLANGetData, 24=SSEConnectorMatrix.",
        ),
    ] = None,
    jobType: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter currently running jobs by type. Only applies when `currentlyRunningJob=true`. Valid values: 1=User-defined job, 2=System job.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if currentlyRunningJob is not None:
        query_params["currentlyRunningJob"] = currentlyRunningJob
    if jobCategory is not None:
        query_params["jobCategory"] = jobCategory
    if jobType is not None:
        query_params["jobType"] = jobType
    return await edgeconnect_request(
        ctx,
        "GET",
        "/statsCollector/job/scheduled",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_job",
    description="POST /gms/job\n\nScheduledJob2Post296\n\nCreate a new scheduled job in Orchestrator",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_job(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/job",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_job_report_viewport",
    description="POST /gms/job/reportViewport\n\nreportViewportPost300\n\nSave report viewport configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_job_report_viewport(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/job/reportViewport",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_job_stop",
    description="POST /gms/job/stop\n\nstopJob304\n\nStop a scheduled job",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_job_stop(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the scheduled job to stop. Must reference an existing job in the system."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/job/stop",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_put_gms_job",
    description="PUT /gms/job\n\nscheduledJobModify303\n\nUpdate an existing scheduled job",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_job(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the job to update. Must reference an existing scheduled job that is not a runNow job."
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
        "/gms/job",
        query_params=query_params or None,
        body=body,
    )
