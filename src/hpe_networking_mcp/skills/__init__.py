"""Skills — markdown-defined multi-step procedures discoverable via two MCP tools.

A skill is a markdown file with YAML frontmatter describing a multi-step
network operations procedure (objective → prerequisites → numbered steps).
The AI calls ``skills_list()`` to browse and ``skills_load(name)`` to fetch
the full runbook body, then follows the steps. Closes #189.
"""

from hpe_networking_mcp.skills._engine import (
    SkillRegistry,
    SkillsListDiscoveryTool,
    SkillsLoadDiscoveryTool,
    register,
)

__all__ = [
    "SkillRegistry",
    "SkillsListDiscoveryTool",
    "SkillsLoadDiscoveryTool",
    "register",
]
