from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    ACCESS_POINT = "Access Point"
    SWITCH = "Switch"
    GATEWAY = "Gateway"
    WIRELESS_CLIENT = "Wireless Client"
    WIRED_CLIENT = "Wired Client"
    BRIDGE = "Bridge"


class SiteMetrics(BaseModel):
    """Standardized site metrics structure"""

    health: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Health score distribution: Poor/Fair/Good percentages plus a "
            "Summary score (0-100, weighted average where Good=1, Fair=0.5, Poor=0)."
        ),
    )
    devices: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Device counts for the site. Contains 'Summary' "
            "(Poor/Fair/Good/Total) and optional 'Details' broken down by "
            "device type (Access Points, Switches, Gateways, Bridges)."
        ),
    )
    clients: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Client counts for the site. Contains 'Summary' "
            "(Poor/Fair/Good/Total) and optional 'Details' broken down by "
            "medium (Wired, Wireless)."
        ),
    )
    alerts: dict[str, Any] | int = Field(
        default_factory=dict,
        description="Alert counts for the site: Critical (int) and Total (int).",
    )


class SiteData(BaseModel):
    """Standardized site data structure"""

    site_id: str = Field(
        description=("Unique identifier for the site in Central. Used to reference the site in other API calls.")
    )
    name: str = Field(description="Display name of the site.")
    address: dict = Field(description="Physical address: zipCode, address, city, state, country.")
    location: dict = Field(description="Geographic coordinates: lat and lng.")
    metrics: SiteMetrics = Field(description="Site performance metrics: health, devices, clients, alerts.")


class Device(BaseModel):
    """Device inventory data structure (duplicates removed)"""

    # Primary identifiers
    serial_number: str = Field(
        description=("Unique serial number. The most reliable way to identify and reference a device in Central.")
    )
    mac_address: str = Field(description="MAC address of the device.")

    # Device information
    device_type: str = Field(description="Category of device: ACCESS_POINT, SWITCH, or GATEWAY.")
    model: str = Field(description="Device model number (e.g., AP-735-RWF1).")
    part_number: str = Field(description="Manufacturer part number.")
    name: str = Field(description="Display name of the device. Configurable in Central.")
    function: str | None = Field(description=("Device function classification defining its role in the network."))

    # Status and configuration
    status: str | None = Field(description="Current operational status: ONLINE or OFFLINE.")
    is_provisioned: bool = Field(
        description=(
            "True if the device is configured and sending monitoring data "
            "to Central. False means it is not yet provisioned."
        )
    )
    role: str | None = Field(description="Device role in the network.")
    deployment: str | None = Field(description="Deployment mode (e.g., Standalone, Stack).")
    tier: str | None = Field(
        description=("License tier (e.g., ADVANCED_AP). Indicates which Central subscription covers this device.")
    )

    # Version information
    firmware_version: str | None = Field(description="Current firmware version installed on the device.")

    # Location and grouping
    site_id: str | None = Field(description="ID of the site where the device is located.")
    site_name: str | None = Field(description="Name of the site where the device is located.")
    device_group_name: str | None = Field(description="Name of the device group this device belongs to.")
    scope_id: str | None = Field(description=("Scope identifier required for configuration actions on this device."))

    # Network information
    ipv4: str | None = Field(description="IPv4 address of the device.")

    # Additional metadata
    stack_id: str | None = Field(description="Stack identifier for stack-capable devices.")


class Client(BaseModel):
    """Client device data structure"""

    # Primary identifiers
    mac: str | None = Field(description="MAC address of the client.")
    name: str | None = Field(description="Display name of the client.")
    ipv4: str | None = Field(description="IPv4 address of the client.")
    ipv6: str | None = Field(description="IPv6 address of the client.")
    hostname: str | None = Field(description="Hostname of the client.")

    # Client classification
    connection_type: str | None = Field(description="Client type (e.g., Wireless, Wired).")
    vendor: str | None = Field(description="Vendor name of the client device.")
    manufacturer: str | None = Field(description="Manufacturer of the client device.")
    category: str | None = Field(description="Category classification of the client.")
    function: str | None = Field(description="Functional role of the client in the network.")
    os: str | None = Field(description="Operating system or model of the client.")
    capabilities: str | None = Field(description="Client capability flags.")

    # Status and health
    status: str | None = Field(description="Current connection status of the client.")

    # Connection information
    connected_device_type: str | None = Field(description="Type of the device this client is connected to.")
    connected_device_serial: str | None = Field(description="Serial number of the device this client is connected to.")
    connected_to: str | None = Field(description="Name or identifier of the connected device.")
    connected_at: str | None = Field(description="Timestamp when the client connected.")
    last_seen_at: str | None = Field(description="Timestamp when the client was last seen.")
    port: str | None = Field(default=None, description="Port on the connected device.")  # Wired only

    # Network configuration
    vlan_id: str | None = Field(description="VLAN ID assigned to the client.")
    tunnel_type: str | None = Field(description="Tunnel type if applicable.")
    tunnel_id: int | None = Field(description="Tunnel identifier.")

    # Wireless-specific fields (omitted for wired clients)
    wlan_name: str | None = Field(
        default=None,
        description=("Name of the wireless network the client is connected to."),
    )  # Wireless only
    wireless_band: str | None = Field(default=None, description="Wireless band (e.g., 2.4GHz, 5GHz).")  # Wireless only
    wireless_channel: str | None = Field(default=None, description="Wireless channel in use.")  # Wireless only
    wireless_security: str | None = Field(default=None, description="Wireless security protocol.")  # Wireless only
    key_management: str | None = Field(default=None, description="Key management method.")  # Wireless only
    bssid: str | None = Field(
        default=None,
        description=("BSSID to which the client is connected on the device."),
    )  # Wireless only
    radio_mac: str | None = Field(
        default=None,
        description="MAC address of the radio serving this client.",
    )  # Wireless only

    # Authentication
    user_name: str | None = Field(description="Authenticated username if 802.1X is in use.")
    authentication: str | None = Field(description="Authentication method used.")

    # Site information
    site_id: str | None = Field(description="ID of the site where the client is located.")
    site_name: str | None = Field(description="Name of the site where the client is located.")

    # Additional metadata
    role: str | None = Field(description="Role assigned to the client (e.g., from policy).")
    tags: str | None = Field(description="Tags associated with the client.")


class Alert(BaseModel):
    summary: str = Field(description="Short summary of the alert.")
    cleared_reason: str | None = Field(description="Reason the alert was cleared, if applicable.")
    created_at: str = Field(description="Timestamp when the alert was created (RFC 3339).")
    priority: str = Field(description="Priority level of the alert.")
    updated_at: str | None = Field(description="Timestamp of the last update to the alert.")
    device_type: str | None = Field(description="Type of device that triggered the alert.")
    updated_by: str | None = Field(description="User or system that last updated the alert.")
    name: str | None = Field(description="Name/title of the alert.")
    status: str | None = Field(description="Current status of the alert (e.g., ACTIVE, CLEARED).")
    category: str | None = Field(description="Alert category.")
    severity: str | None = Field(description="Severity level (e.g., CRITICAL, MAJOR, MINOR).")


class ApplicationVisibility(BaseModel):
    experience: dict | None = Field(description="Application experience metrics.")
    dest_location: list[dict] | None = Field(description=("Destination location details for the application traffic."))
    risk: str | None = Field(description="Risk classification of the application.")
    application_host_type: str | None = Field(description="Host type (e.g., cloud, on-prem).")
    name: str | None = Field(description="Application name.")
    tx_bytes: int | None = Field(description="Total bytes transmitted by the application.")
    rx_bytes: int | None = Field(description="Total bytes received by the application.")
    last_used_time: str | None = Field(description="Timestamp when the application was last used.")
    tls_version: str | None = Field(description="TLS version used by the application.")
    certificate_expiry_date: str | None = Field(description="Expiry date of the application's TLS certificate.")
    categories: list[str] | None = Field(description="List of categories the application belongs to.")
    state: str | None = Field(description="Current state of the application visibility entry.")


class EventNameCount(BaseModel):
    event_id: str = Field(description="Event type identifier.")
    event_name: str = Field(description="Human-readable event name.")
    count: int = Field(description="Number of occurrences.")


class EventSourceTypeCount(BaseModel):
    source_type: str = Field(description="Source type (e.g. 'Wireless Client').")
    count: int = Field(description="Number of events from this source type.")


class EventCategoryCount(BaseModel):
    category: str = Field(description="Event category (e.g. 'Clients').")
    count: int = Field(description="Number of events in this category.")


class EventFilters(BaseModel):
    total: int = Field(description="Total event count (sum of all categories).")
    event_names: list[EventNameCount] = Field(description=("Per-event-type breakdown, sorted by count descending."))
    source_types: list[EventSourceTypeCount] = Field(description="Breakdown by source type.")
    categories: list[EventCategoryCount] = Field(description="Breakdown by event category.")


class Event(BaseModel):
    eventId: str = Field(description="The event type identifier.")
    eventIdentifier: str = Field(description="Unique identifier for the event.")
    serialNumber: str = Field(description=("Serial number of the device that generated the event."))
    timeAt: str = Field(description=("Timestamp when the event occurred at the source (RFC 3339 with milliseconds)."))
    eventName: str = Field(description="Name of the event.")
    category: str = Field(description="Event category.")
    sourceType: SourceType = Field(description="Type of source that generated the event.")
    sourceName: str = Field(description=("Name of the device or client that generated the event."))
    description: str = Field(description="Detailed description of the event.")
    clientMacAddress: str | None = Field(description="MAC address of the client involved in the event.")
    deviceMacAddress: str | None = Field(description="MAC address of the device that generated the event.")
    stackId: str | None = Field(description="Stack identifier for stack-capable devices.")
    bssid: str | None = Field(description="Basic Service Set Identifier for wireless events.")
    reason: str | None = Field(description="Reason or cause of the event.")
    severity: str | None = Field(description="Severity level of the event.")


class PaginatedAlerts(BaseModel):
    items: list[Alert] = Field(description="Page of alert records.")
    total: int = Field(description=("Total alerts matching the filter across all pages."))
    next_cursor: int | None = Field(
        default=None,
        description=("Cursor for the next page. Pass as `cursor` in the next call. None means no more pages."),
    )


class PaginatedEvents(BaseModel):
    items: list[Event] = Field(description="Page of event records.")
    total: int = Field(description=("Total events matching the filter across all pages."))
    next_cursor: int | None = Field(
        default=None,
        description=("Cursor for the next page. Pass as `cursor` in the next call. None means no more pages."),
    )
