"""Static formatting-guideline snippets returned alongside Apstra tool responses.

Per-tool snippets (``get_base_guidelines``, ``get_device_guidelines``, etc.) are
concatenated into individual tool responses so the MCP client renders consistent
tables, icons, and change-management messaging. The full-document
``get_formatting_guidelines`` helper was removed in v2.0 together with the
``apstra_formatting_guidelines`` tool — that content now lives in
``src/hpe_networking_mcp/INSTRUCTIONS.md`` under the Juniper Apstra section,
where it reaches the model at session init without a dedicated tool call.
"""

from __future__ import annotations


def get_base_guidelines() -> str:
    """Base formatting guidelines with essential structure."""
    return """
# OUTPUT FORMATTING GUIDELINES

## Status Labels
- Good: Healthy / Up / Active
- Failed: Critical / Down
- Warn: Warning / Degraded
- Syncing: In Progress / Syncing
- Unknown

## Response Structure
1. Quick Summary with key metrics
2. Detailed Information as needed
3. Notable Issues if any exist
"""


def get_device_guidelines() -> str:
    """Device/system specific formatting guidelines."""
    return """
## Device Information Table Format
| Status | Device Name | IP Address | Role | Model | OS Version |
|--------|-------------|------------|------|-------|------------|
| Good | spine-01 | 192.168.1.10 | Spine | QFX5200 | 21.4R1 |

Include ASN, loopback IP, and other relevant device details as columns.
"""


def get_network_guidelines() -> str:
    """Network-configuration formatting guidelines."""
    return """
## Network Configuration Display
- Virtual Networks: show VN name, ID, routing zone, VNI
- Routing Zones: display zone name, VRF, VNI range
- Remote Gateways: show GW name, IP, ASN, status

Use tables for multiple items, structured JSON for single items.
"""


def get_status_guidelines() -> str:
    """Status and protocol-session formatting guidelines."""
    return """
## Protocol Sessions Table
| Status | Local | Remote | Type | State | Uptime |
|--------|-------|--------|------|-------|--------|
| Good | spine-01 | leaf-01 | eBGP | Established | 2d 14h |

## Configuration Status
- Show active vs staging versions clearly
- Highlight pending changes
- Display deployment history if relevant
"""


def get_anomaly_guidelines() -> str:
    """Anomaly and issue-reporting guidelines."""
    return """
## Anomaly Display Format
| Severity | Device | Issue | Duration | Impact |
|----------|--------|-------|----------|---------|
| Critical | leaf-01 | BGP Down | 2h 15m | Traffic loss |
| Warning | spine-02 | High CPU | 45m | Performance |

Severity Levels:
- Critical - Immediate action required
- Warning - Attention needed
- Info - Informational only
"""


def get_change_mgmt_guidelines() -> str:
    """Change-management and deployment guidelines."""
    return """
## CRITICAL: Change Management Requirements
NEVER make changes without explicit user confirmation.

Before ANY change operation:
1. Describe the exact change
2. Show the command to be executed
3. Ask for explicit confirmation
4. Wait for explicit approval

## Post-Change Actions
1. Verify the change succeeded
2. Check for any anomalies
3. Ask if the user wants to deploy (if applicable)
"""


def get_auth_guidelines() -> str:
    """Authentication-specific formatting guidelines."""
    return """
## Authentication Response Format
- Show session status clearly
- Include expiration time if applicable
- Display transport mode (stdio/http)
- Indicate credential source
"""


def get_blueprint_guidelines() -> str:
    """Blueprint-specific formatting guidelines."""
    return """
## Blueprint Information Display
| Status | Name | ID | Design | Version |
|--------|------|----|--------|---------|
| Good | prod-dc | uuid-123 | two_stage | v5 |

Include creation date, last modified, and node count when available.
"""
