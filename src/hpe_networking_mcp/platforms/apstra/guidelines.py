"""Static formatting-guideline snippets returned alongside Apstra tool responses.

Ported from the source apstra_core.py module. Guidelines are concatenated with
live data so the MCP client renders consistent tables, icons, and change-
management messaging.
"""

from __future__ import annotations


def get_formatting_guidelines() -> str:
    """Comprehensive formatting guidelines for network infrastructure output."""
    return """
# OUTPUT FORMATTING GUIDELINES

When displaying network infrastructure information, always follow these formatting standards:

## Table Format for Device Information
Always present device/system information in well-structured tables with these standard columns:

### Device Overview Table
| Status | Device Name | IP Address | Loopback IP | ASN | Role | Model | OS Version |
|--------|-------------|------------|-------------|-----|------|-------|------------|
| Good | spine-01 | 192.168.1.10 | 10.0.0.1 | 65001 | Spine | QFX5200 | 21.4R1 |
| Failed | leaf-02 | 192.168.1.22 | 10.0.0.22 | 65002 | Leaf | EX4650 | 20.4R3 |

### Protocol Sessions Table
| Status | Local Device | Remote Device | Session Type | State | Uptime | Routes Rx/Tx |
|--------|--------------|---------------|--------------|-------|--------|---------------|
| Good | spine-01 | leaf-01 | eBGP | Established | 2d 14h | 150/75 |
| Warn | spine-02 | leaf-03 | eBGP | Connect | 0h 0m | 0/0 |

### Anomaly/Issues Table
| Severity | Device | Issue Type | Description | Duration | Actions |
|----------|--------|------------|-------------|----------|---------|
| Critical | leaf-01 | BGP | Session Down | 2h 15m | Check connectivity |
| Warning | spine-02 | Interface | High Utilization | 45m | Monitor traffic |

## Status Indicators
Use consistent status labels across all outputs:

### Health Status
- Good: Healthy / Up / Active / Connected
- Failed: Critical / Down / Disconnected
- Warn: Warning / Degraded / Flapping / Pending
- Syncing: In Progress / Syncing / Updating
- Paused: Maintenance / Suspended
- Unknown: Unmonitored

### Severity Levels
- Critical - Immediate attention required
- Warning - Attention needed
- Info - Informational only
- Debug - Troubleshooting info

## Response Structure
1. Quick Summary with key metrics
2. Detailed Tables with comprehensive information
3. Notable Issues highlighting problems requiring attention
4. Recommendations for next steps or actions needed

## CRITICAL: Tool Usage and Change Management
NEVER make configuration changes, deployments, or commits without explicit user confirmation.

### Prohibited Actions Without Confirmation:
- DO NOT use apstra_deploy without explicit user approval
- DO NOT use apstra_delete_blueprint without explicit user approval
- DO NOT create any network objects (apstra_create_virtual_network,
  apstra_create_remote_gateway, etc.) without explicit user approval
- DO NOT make any changes to production infrastructure without explicit user approval

### Required User Confirmation Format:
Before executing any change operation, you MUST:
1. Describe the exact change you plan to make
2. Show the specific command/tool that will be executed
3. Ask for explicit confirmation
4. Wait for clear user approval before proceeding

## MANDATORY: Post-Change Verification
ALWAYS verify the success of any change operation using appropriate query tools.

- After apstra_deploy: run apstra_get_diff_status, apstra_get_anomalies, apstra_get_protocol_sessions
- After apstra_create_virtual_network: run apstra_get_virtual_networks
- After apstra_create_remote_gateway: run apstra_get_remote_gateways and apstra_get_protocol_sessions
- After apstra_delete_blueprint: run apstra_get_blueprints to confirm removal
- After blueprint creation: run apstra_get_blueprints to confirm creation

## IMPORTANT: Post-Change Deployment Prompt
After any configuration changes that require deployment, ALWAYS ask the user if they want to deploy.
"""


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
