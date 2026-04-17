"""ClearPass tool registry -- holds the FastMCP instance that tools register against."""

from fastmcp import FastMCP

# Set by platforms.clearpass.register_tools() before tool modules are imported
mcp: FastMCP = None  # type: ignore[assignment]
