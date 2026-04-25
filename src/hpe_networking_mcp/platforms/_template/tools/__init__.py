"""Shared ToolAnnotations constants for tools in this platform.

Apply via the @tool decorator's ``annotations`` kwarg. MCP clients use
these hints to decide UX (e.g. Claude Desktop's confirmation dialog
fires for ``destructiveHint=True`` tools).
"""

from mcp.types import ToolAnnotations

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

WRITE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)
