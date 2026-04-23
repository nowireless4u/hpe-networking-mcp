"""Firmware recommendation tool.

Reads `/network-services/v1/firmware-details` and applies an LSR-preferred
upgrade policy on top of Central's built-in `recommendedVersion`. The
LSR vs SSR classification comes directly from the `firmwareClassification`
field in the API response — no hand-maintained mapping.

Policy:

- APs/Gateways classified as LSR → trust Central's `recommendedVersion`
  (it will be latest-in-same-train, which is what we want).
- APs/Gateways classified as SSR → override Central and recommend the
  newest LSR version discovered elsewhere in the fleet for the same
  device type. Central would otherwise happily keep the device on SSR.
- Devices with an empty classification (legacy AOS 8 or anything the API
  doesn't classify) → pass Central's recommendation through unchanged.
- If no LSR devices exist in the fleet to mine a target from, SSR devices
  fall back to Central's recommendation with a note.
"""

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import BaseModel, Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


class FirmwareRecommendation(BaseModel):
    serial_number: str
    device_name: str
    device_type: str  # ACCESS_POINT, SWITCH, GATEWAY
    site_name: str | None = None
    current_version: str
    release_type: Literal["LSR", "SSR", "UNCLASSIFIED"]
    central_recommended_version: str | None = None
    our_recommended_version: str | None = None
    action: Literal[
        "up_to_date",
        "upgrade_in_place",
        "move_to_lsr_train",
        "follow_central",
    ]
    rationale: str


class FirmwareRecommendationReport(BaseModel):
    discovered_lsr_targets: dict[str, str]  # device_type -> newest LSR version seen in fleet
    total_devices_scanned: int
    up_to_date: int
    on_lsr: int
    on_ssr: int
    unclassified: int
    needs_action: int
    recommendations: list[FirmwareRecommendation]


def _parse_version_tuple(version: str) -> tuple[int, ...]:
    """Parse a firmware version string into a comparable tuple.

    Strips any build suffix after an underscore and splits on dots.
    Non-numeric segments terminate the parse (so "10.5.0.1_80123" → (10, 5, 0, 1)
    and "8.6.0.6_77023" → (8, 6, 0, 6)). Empty input → ().
    """
    if not version:
        return ()
    base = version.split("_", 1)[0]
    parts: list[int] = []
    for seg in base.split("."):
        try:
            parts.append(int(seg))
        except ValueError:
            break
    return tuple(parts)


def _classify(item: dict) -> Literal["LSR", "SSR", "UNCLASSIFIED"]:
    """Extract the release classification the API reports for this device."""
    raw = (item.get("firmwareClassification") or "").strip().upper()
    if raw == "LSR":
        return "LSR"
    if raw == "SSR":
        return "SSR"
    return "UNCLASSIFIED"


def _find_newest_lsr_per_type(items: list[dict]) -> dict[str, str]:
    """Mine the firmware-details records for the newest LSR version per deviceType.

    We look at both `firmwareVersion` (current install, for LSR-classified
    devices) and `recommendedVersion` (Central's latest-in-train suggestion
    for LSR-classified devices) since Central's recommendation for an LSR
    device will itself be an LSR version in the same train.
    """
    by_type: dict[str, str] = {}

    def _consider(device_type: str, version: str | None) -> None:
        if not device_type or not version:
            return
        existing = by_type.get(device_type)
        if existing is None or _parse_version_tuple(version) > _parse_version_tuple(existing):
            by_type[device_type] = version

    for item in items:
        if _classify(item) != "LSR":
            continue
        dtype = str(item.get("deviceType", ""))
        _consider(dtype, str(item.get("firmwareVersion") or ""))
        _consider(dtype, str(item.get("recommendedVersion") or ""))

    return by_type


def _recommend(
    item: dict,
    newest_lsr_by_type: dict[str, str],
) -> FirmwareRecommendation:
    """Apply the recommendation policy to one device's firmware record."""
    serial = str(item.get("serialNumber", ""))
    name = str(item.get("deviceName", ""))
    dtype = str(item.get("deviceType", ""))
    site_name = item.get("siteName")
    current_version = str(item.get("firmwareVersion", ""))
    central_rec = item.get("recommendedVersion") or None
    upgrade_status = (item.get("upgradeStatus") or "").strip().lower()
    release_type = _classify(item)
    already_up_to_date = upgrade_status == "up to date"

    def _build(
        our_rec: str | None,
        action: Literal["up_to_date", "upgrade_in_place", "move_to_lsr_train", "follow_central"],
        rationale: str,
    ) -> FirmwareRecommendation:
        return FirmwareRecommendation(
            serial_number=serial,
            device_name=name,
            device_type=dtype,
            site_name=site_name,
            current_version=current_version,
            release_type=release_type,
            central_recommended_version=central_rec,
            our_recommended_version=our_rec,
            action=action,
            rationale=rationale,
        )

    if release_type == "UNCLASSIFIED":
        if already_up_to_date:
            return _build(
                None,
                "up_to_date",
                (
                    "Already on Central's recommended version. No classification reported "
                    "(commonly AOS 8 or a non-classified build)."
                ),
            )
        return _build(
            central_rec,
            "follow_central",
            "API did not classify this build as LSR or SSR. Deferring to Central's recommendation.",
        )

    if release_type == "LSR":
        if already_up_to_date:
            return _build(None, "up_to_date", "On LSR and current with Central's recommended version.")
        return _build(
            central_rec,
            "upgrade_in_place",
            f"On LSR — upgrade in place to Central's recommended version ({central_rec}).",
        )

    # SSR
    target = newest_lsr_by_type.get(dtype)
    if target is None:
        return _build(
            central_rec,
            "follow_central",
            (
                "Classified as SSR but no LSR version was discovered for this device type "
                f"({dtype}) elsewhere in the fleet. Following Central's recommendation."
            ),
        )
    if _parse_version_tuple(current_version) >= _parse_version_tuple(target):
        return _build(
            central_rec,
            "follow_central",
            (
                f"Classified as SSR but current version {current_version} is at or above the "
                f"newest LSR seen in the fleet for {dtype} ({target}). Following Central."
            ),
        )
    return _build(
        target,
        "move_to_lsr_train",
        (
            f"On SSR. Recommending move to {target} — newest LSR seen in the fleet for "
            f"{dtype}. Central's suggestion was '{central_rec}'."
        ),
    )


def _build_filter(
    serial_number: str | None,
    device_type: str | None,
    site_id: str | None,
    site_name: str | None,
) -> str | None:
    """Build an OData 4.0 filter for firmware-details (eq and and only)."""
    parts: list[str] = []
    if serial_number:
        parts.append(f"serialNumber eq '{serial_number}'")
    if device_type:
        parts.append(f"deviceType eq '{device_type}'")
    if site_id:
        parts.append(f"siteId eq '{site_id}'")
    if site_name:
        parts.append(f"siteName eq '{site_name}'")
    return " and ".join(parts) if parts else None


@tool(annotations=READ_ONLY)
async def central_recommend_firmware(
    ctx: Context,
    serial_number: Annotated[
        str | None,
        Field(
            description="Optional — recommend only for this device serial.",
            default=None,
        ),
    ] = None,
    device_type: Annotated[
        Literal["ACCESS_POINT", "SWITCH", "GATEWAY"] | None,
        Field(
            description=(
                "Optional — limit to a single device type. Note: filtering out "
                "ACCESS_POINT or GATEWAY reduces the pool used to mine the "
                "newest LSR target for SSR devices. Leave unset for best SSR "
                "recommendations."
            ),
            default=None,
        ),
    ] = None,
    site_id: Annotated[
        str | None,
        Field(description="Optional — limit to devices at this site.", default=None),
    ] = None,
    site_name: Annotated[
        str | None,
        Field(description="Optional — limit to devices at this site name.", default=None),
    ] = None,
    include_up_to_date: Annotated[
        bool,
        Field(
            description=(
                "If True, include devices already on Central's recommended version "
                "in the recommendations list. Default False keeps the output focused "
                "on actionable items."
            ),
            default=False,
        ),
    ] = False,
    max_pages: Annotated[
        int,
        Field(
            description=(
                "Safety cap on paginated fetches. 1000 items per page × max_pages "
                "is the hard ceiling on devices scanned."
            ),
            default=10,
            ge=1,
            le=50,
        ),
    ] = 10,
) -> FirmwareRecommendationReport:
    """Apply an LSR-preferred upgrade policy to every device's firmware.

    The tool calls `/network-services/v1/firmware-details`, classifies each
    device from the `firmwareClassification` field the API returns (LSR,
    SSR, or empty), and recommends accordingly:

    - On LSR → upgrade to Central's recommended version (latest in same train)
    - On SSR → move to the newest LSR version discovered elsewhere in the
      fleet for the same device type (Central would otherwise keep the
      device on SSR)
    - Unclassified (typically AOS 8) → pass Central's recommendation through

    The "newest LSR" target is mined live from the same response — no
    hand-maintained train mapping. If no LSR device of the same type exists
    in the fleet, SSR devices fall back to Central's recommendation with
    a note.
    """
    conn = ctx.lifespan_context["central_conn"]

    filter_str = _build_filter(serial_number, device_type, site_id, site_name)

    all_items: list[dict] = []
    next_cursor: str | None = None
    pages = 0

    while pages < max_pages:
        params: dict = {"limit": 1000}
        if filter_str:
            params["filter"] = filter_str
        if next_cursor:
            params["next"] = next_cursor

        resp = retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path="network-services/v1/firmware-details",
            api_params=params,
        )
        msg = resp.get("msg", {}) if isinstance(resp, dict) else {}
        items = msg.get("items", []) if isinstance(msg, dict) else []
        all_items.extend(items)

        next_cursor = msg.get("next") if isinstance(msg, dict) else None
        pages += 1
        if not next_cursor:
            break

    newest_lsr = _find_newest_lsr_per_type(all_items)

    recommendations: list[FirmwareRecommendation] = []
    counts = {"up_to_date": 0, "on_lsr": 0, "on_ssr": 0, "unclassified": 0}

    for item in all_items:
        rec = _recommend(item, newest_lsr)

        if rec.action == "up_to_date":
            counts["up_to_date"] += 1
        if rec.release_type == "LSR":
            counts["on_lsr"] += 1
        elif rec.release_type == "SSR":
            counts["on_ssr"] += 1
        else:
            counts["unclassified"] += 1

        if rec.action == "up_to_date" and not include_up_to_date:
            continue
        recommendations.append(rec)

    needs_action = sum(1 for r in recommendations if r.action != "up_to_date")

    return FirmwareRecommendationReport(
        discovered_lsr_targets=newest_lsr,
        total_devices_scanned=len(all_items),
        up_to_date=counts["up_to_date"],
        on_lsr=counts["on_lsr"],
        on_ssr=counts["on_ssr"],
        unclassified=counts["unclassified"],
        needs_action=needs_action,
        recommendations=recommendations,
    )
