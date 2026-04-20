"""Firmware recommendation tool.

Reads `/network-services/v1/firmware-details` and applies an LSR-preferred
upgrade policy on top of Central's built-in `recommendedVersion`:

- APs and Gateways on an LSR train → trust Central's recommendation
  (latest in the same major.minor train).
- APs and Gateways on an SSR train → override Central and recommend moving
  to the next LSR train (Central will happily keep you on SSR otherwise).
- Legacy AOS 8 devices → pass Central's recommendation through unchanged.
- Switches and unknown trains → pass Central's recommendation through with
  a note, since the LSR/SSR concept in the bundled mapping only covers
  AP and Gateway AOS 10 trains.

LSR/SSR mapping is hand-maintained per Aruba's supported-devices-AOS10
documentation. Update `AOS10_AP_GW_RELEASE_TYPES` when new trains are
designated.
"""

import re
from typing import Annotated, Literal

from fastmcp import Context
from pydantic import BaseModel, Field

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

# AOS 10 release-type mapping for Access Points and Gateways.
# Source: Aruba supported-devices-AOS10 documentation. Switches and
# controllers have separate cadences not covered here.
AOS10_AP_GW_RELEASE_TYPES: dict[str, Literal["LSR", "SSR"]] = {
    "10.3": "SSR",
    "10.4": "LSR",
    "10.5": "SSR",
    "10.6": "SSR",
    "10.7": "SSR",
    "10.8": "LSR",
}

_AOS10_VERSION_RE = re.compile(r"^10\.(\d+)\.")
_AOS8_VERSION_RE = re.compile(r"^8\.\d+\.")


class FirmwareRecommendation(BaseModel):
    serial_number: str
    device_name: str
    device_type: str  # ACCESS_POINT, SWITCH, GATEWAY
    site_name: str | None = None
    current_version: str
    current_train: str | None = None  # major.minor, e.g. "10.8"
    release_type: Literal["LSR", "SSR", "AOS8", "UNKNOWN"]
    central_recommended_version: str | None = None
    our_recommended_version: str | None = None
    action: Literal[
        "up_to_date",
        "upgrade_in_place",
        "move_to_lsr_train",
        "follow_central",
        "unknown",
    ]
    rationale: str


class FirmwareRecommendationReport(BaseModel):
    lsr_train_reference: dict[str, str]
    total_devices_scanned: int
    up_to_date: int
    on_lsr_train: int
    on_ssr_train: int
    on_aos8: int
    unknown_train: int
    needs_action: int
    recommendations: list[FirmwareRecommendation]


def _parse_train(version: str | None) -> tuple[str | None, Literal["LSR", "SSR", "AOS8", "UNKNOWN"]]:
    """Return (major_minor_train, release_type) for a firmware version.

    Examples:
      "10.8.1010"        -> ("10.8", "LSR")
      "10.5.0.1_80123"   -> ("10.5", "SSR")
      "8.5.2.0_59123"    -> ("8.5", "AOS8")
      "garbage"          -> (None, "UNKNOWN")
    """
    if not version:
        return (None, "UNKNOWN")
    m = _AOS10_VERSION_RE.match(version)
    if m:
        train = f"10.{m.group(1)}"
        return (train, AOS10_AP_GW_RELEASE_TYPES.get(train, "UNKNOWN"))
    if _AOS8_VERSION_RE.match(version):
        # Grab "major.minor" for AOS 8 — LSR/SSR concept doesn't apply
        parts = version.split(".")
        return (f"{parts[0]}.{parts[1]}", "AOS8")
    return (None, "UNKNOWN")


def _next_lsr_train(current_train: str | None) -> str | None:
    """Return the next LSR train at or above the current train, or None."""
    if not current_train:
        return None
    # Sort trains by their minor number (we're inside AOS 10 here)
    try:
        current_minor = int(current_train.split(".")[1])
    except (IndexError, ValueError):
        return None
    lsr_trains = sorted(
        (t for t, rt in AOS10_AP_GW_RELEASE_TYPES.items() if rt == "LSR"),
        key=lambda t: int(t.split(".")[1]),
    )
    for train in lsr_trains:
        if int(train.split(".")[1]) >= current_minor:
            return train
    return None


def _recommend(
    device_type: str,
    current_version: str,
    central_recommended: str | None,
    upgrade_status: str | None,
) -> tuple[
    Literal["LSR", "SSR", "AOS8", "UNKNOWN"],
    str | None,
    str | None,
    Literal["up_to_date", "upgrade_in_place", "move_to_lsr_train", "follow_central", "unknown"],
    str,
]:
    """Apply the recommendation policy to one device's firmware status.

    Returns: (release_type, current_train, our_recommended_version, action, rationale)
    """
    train, release_type = _parse_train(current_version)
    already_up_to_date = (upgrade_status or "").strip().lower() == "up to date"

    if device_type not in ("ACCESS_POINT", "GATEWAY"):
        # LSR/SSR mapping only applies to AP/GW; pass through Central's view.
        if already_up_to_date:
            return (release_type, train, None, "up_to_date", "Already on Central's recommended version.")
        return (
            release_type,
            train,
            central_recommended,
            "follow_central",
            f"{device_type} is outside the LSR/SSR mapping — deferring to Central's recommendation.",
        )

    if release_type == "AOS8":
        if already_up_to_date:
            return (release_type, train, None, "up_to_date", "Legacy AOS 8 device already on Central's recommendation.")
        return (
            release_type,
            train,
            central_recommended,
            "follow_central",
            "Legacy AOS 8 device — LSR/SSR classification only applies to AOS 10. Deferring to Central.",
        )

    if release_type == "LSR":
        if already_up_to_date:
            return (
                release_type,
                train,
                None,
                "up_to_date",
                f"On LSR train {train} and current with Central's recommended version.",
            )
        return (
            release_type,
            train,
            central_recommended,
            "upgrade_in_place",
            (f"On LSR train {train}. Upgrade to latest in the same LSR train ({central_recommended})."),
        )

    if release_type == "SSR":
        next_lsr = _next_lsr_train(train)
        if next_lsr is None:
            return (
                release_type,
                train,
                central_recommended,
                "follow_central",
                (
                    f"On SSR train {train} and no newer LSR train is known in the bundled "
                    "mapping. Following Central's recommendation until the mapping is updated."
                ),
            )
        return (
            release_type,
            train,
            f"{next_lsr}.x (latest LSR build)",
            "move_to_lsr_train",
            (
                f"On SSR train {train}. Recommending move to next LSR train {next_lsr} — "
                f"Central's suggestion was '{central_recommended}'. "
                "Pick the latest available build in that train from Central's firmware catalog."
            ),
        )

    # UNKNOWN — either garbage version string or an AOS 10 train beyond the
    # bundled mapping. Defer but flag loudly.
    if already_up_to_date:
        return (
            release_type,
            train,
            None,
            "up_to_date",
            (
                "Current version isn't in the LSR/SSR mapping but Central considers it up to date. "
                "Update AOS10_AP_GW_RELEASE_TYPES if this train should be classified."
            ),
        )
    return (
        release_type,
        train,
        central_recommended,
        "unknown",
        (
            f"Current train {train} is not in the bundled LSR/SSR mapping. "
            "Update AOS10_AP_GW_RELEASE_TYPES to classify this train and re-run."
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


@mcp.tool(annotations=READ_ONLY)
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
                "Optional — limit to a single device type. The LSR/SSR policy "
                "only applies to ACCESS_POINT and GATEWAY; SWITCH entries are "
                "passed through with Central's recommendation."
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

    Central's built-in `recommendedVersion` will happily keep a device on an
    SSR train. This tool fetches `/network-services/v1/firmware-details` for
    every device, classifies the current version as LSR, SSR, AOS 8, or
    unknown, and returns a concrete recommendation:

    - On LSR → upgrade to Central's recommended version (latest in same train)
    - On SSR → move to the next LSR train at or above the current train
    - On AOS 8 or non-AP/GW → pass Central's recommendation through
    - Unknown train → flag the device so the user can extend the bundled
      LSR/SSR mapping (`AOS10_AP_GW_RELEASE_TYPES` in this module)

    The report includes counts by state and the LSR/SSR mapping used, so the
    user can see at a glance whether their fleet needs an LSR shift and which
    trains are classified.
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

    recommendations: list[FirmwareRecommendation] = []
    counts = {
        "up_to_date": 0,
        "on_lsr_train": 0,
        "on_ssr_train": 0,
        "on_aos8": 0,
        "unknown_train": 0,
    }

    for item in all_items:
        current_version = str(item.get("firmwareVersion", ""))
        central_rec = item.get("recommendedVersion") or None
        upgrade_status = item.get("upgradeStatus")
        dtype = str(item.get("deviceType", ""))

        release_type, train, our_rec, action, rationale = _recommend(
            dtype,
            current_version,
            central_rec,
            upgrade_status,
        )

        if action == "up_to_date":
            counts["up_to_date"] += 1
        if release_type == "LSR":
            counts["on_lsr_train"] += 1
        elif release_type == "SSR":
            counts["on_ssr_train"] += 1
        elif release_type == "AOS8":
            counts["on_aos8"] += 1
        elif release_type == "UNKNOWN":
            counts["unknown_train"] += 1

        if action == "up_to_date" and not include_up_to_date:
            continue

        recommendations.append(
            FirmwareRecommendation(
                serial_number=str(item.get("serialNumber", "")),
                device_name=str(item.get("deviceName", "")),
                device_type=dtype,
                site_name=item.get("siteName"),
                current_version=current_version,
                current_train=train,
                release_type=release_type,
                central_recommended_version=central_rec,
                our_recommended_version=our_rec,
                action=action,
                rationale=rationale,
            )
        )

    needs_action = sum(1 for r in recommendations if r.action != "up_to_date")

    return FirmwareRecommendationReport(
        lsr_train_reference={k: v for k, v in AOS10_AP_GW_RELEASE_TYPES.items()},
        total_devices_scanned=len(all_items),
        up_to_date=counts["up_to_date"],
        on_lsr_train=counts["on_lsr_train"],
        on_ssr_train=counts["on_ssr_train"],
        on_aos8=counts["on_aos8"],
        unknown_train=counts["unknown_train"],
        needs_action=needs_action,
        recommendations=recommendations,
    )
