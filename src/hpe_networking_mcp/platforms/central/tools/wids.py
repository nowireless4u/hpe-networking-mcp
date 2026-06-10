"""Aruba Central WIDS (Wireless Intrusion Detection) tools.

Wraps the ``network-services/v1alpha1/wids-monitored-aps`` endpoint. The
endpoint is undocumented in the public Central API reference but tenant-
scoped (no cross-tenant exposure) and lives under the in-policy
``network-*/v1alpha1`` path family, so building it as a tool is allowed
per the 2026-05-15 build-policy guidance recorded in
``docs/central-undocumented-endpoints.md``.

Returns the caller's APs' reports of nearby APs they've detected,
classified as one of:

- ``ROGUE`` — confirmed unauthorized AP
- ``SUSPECT_ROGUE`` — suspected unauthorized AP
- ``INTERFERING`` — non-rogue but contributing to interference
- ``VALID`` — neighboring authorized AP

Records also carry a ``containmentStatus`` flag — ``CONTAINED`` when the
fabric is actively jamming/de-authing the BSSID.
"""

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_wids_monitored_aps(
    ctx: Context,
    classification: Annotated[
        Literal["ROGUE", "SUSPECT_ROGUE", "INTERFERING", "VALID"] | None,
        Field(
            description=(
                "Narrow to one WIDS classification: ``ROGUE`` (confirmed "
                "unauthorized), ``SUSPECT_ROGUE`` (suspected), ``INTERFERING`` "
                "(non-rogue but causing RF interference), or ``VALID`` "
                "(neighboring authorized AP). Omit for all classifications."
            ),
        ),
    ] = None,
    contained_only: Annotated[
        bool,
        Field(
            description=(
                "If True, narrow to APs whose ``containmentStatus == "
                "'CONTAINED'`` — i.e. the fabric is actively de-authing or "
                "jamming them. Composable with ``classification``."
            ),
        ),
    ] = False,
    site_id: Annotated[
        str | None,
        Field(
            description=(
                "Narrow to a specific Central site by ``siteId``. Get site "
                "IDs from ``central_get_site_name_id_mapping``."
            ),
        ),
    ] = None,
    odata_filter: Annotated[
        str | None,
        Field(
            description=(
                "Raw OData 4.0 filter passed through to the endpoint. Use "
                "this for filters not covered by ``classification`` / "
                "``contained_only`` / ``site_id`` (e.g. ``encryption eq "
                "'OPEN'``, ``signal gt -70``). Mutually exclusive with the "
                "structured args."
            ),
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=1000,
            description="Results per page (1-1000, default 100).",
        ),
    ] = 100,
    offset: Annotated[
        int,
        Field(
            ge=0,
            description=(
                "Pagination offset (default 0). Use the ``total`` field in the response to drive subsequent pages."
            ),
        ),
    ] = 0,
) -> dict | str:
    """Get WIDS monitored-AP records from Central.

    Reads the ``network-services/v1alpha1/wids-monitored-aps`` endpoint
    which lists neighbor / rogue / suspect / interfering APs detected by
    the caller's APs. Tenant-scoped.

    Each record carries: ``id``, ``bssid``, ``ssid``, ``classification``,
    ``classificationMethod``, ``classificationRule``, ``containmentStatus``,
    ``encryption``, ``signal``, ``macVendor``, ``type``, ``portData``,
    ``firstSeen`` / ``lastSeen`` timestamps, the detecting devices that
    first / most-recently saw it (``firstDetDeviceName`` /
    ``firstDetDeviceSerial`` / ``lastDetDeviceName`` /
    ``lastDetDeviceSerial``), and the ``siteId`` / ``siteName`` of the
    detecting AP.

    Returns:
        Envelope with ``items`` (list of records), ``offset``, ``total``,
        and ``count``. Page through via ``offset += count`` until
        ``offset + count >= total``.

    Examples:
        Get all confirmed rogue APs at a specific site::

            central_get_wids_monitored_aps(
                classification="ROGUE",
                site_id="<site-id>",
            )

        Get APs the fabric is currently containing (any classification)::

            central_get_wids_monitored_aps(contained_only=True)

        Custom OData filter::

            central_get_wids_monitored_aps(
                odata_filter="encryption eq 'OPEN' and signal gt -70",
            )
    """
    structured_args = (classification, contained_only, site_id)
    if odata_filter is not None and any(structured_args):
        return (
            "Error: pass either ``odata_filter`` (raw) OR the structured "
            "``classification`` / ``contained_only`` / ``site_id`` args, "
            "not both. The structured args compose into an OData filter "
            "under the hood; mixing the two is ambiguous."
        )

    if odata_filter is None:
        clauses: list[str] = []
        if classification:
            clauses.append(f"classification eq '{classification}'")
        if contained_only:
            clauses.append("containmentStatus eq 'CONTAINED'")
        if site_id:
            clauses.append(f"siteId eq '{site_id}'")
        odata_filter = " and ".join(clauses) if clauses else None

    api_params: dict = {"limit": limit, "offset": offset}
    if odata_filter:
        api_params["filter"] = odata_filter

    conn = get_central_conn(ctx)
    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-services/v1alpha1/wids-monitored-aps",
        api_params=api_params,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return response.get("msg", {})
    return {
        "status": "error",
        "code": code,
        "message": response.get("msg", "Unknown error"),
    }
