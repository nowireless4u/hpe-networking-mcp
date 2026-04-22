"""Apstra tool registry -- holds the FastMCP instance that tools register against."""

from fastmcp import FastMCP

# Set by platforms.apstra.register_tools() before tool modules are imported
mcp: FastMCP = None  # type: ignore[assignment]
