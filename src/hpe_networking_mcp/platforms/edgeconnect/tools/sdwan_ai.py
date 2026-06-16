"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``SdwanAI``
Operations in this file: 6
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_sdwanai_chat_logs",
    description="GET /sdwanai/chat/logs\n\nsdwanAIChatLogs\n\nRetrieve chat conversation history",
    capability=Capability.READ,
)
async def edgeconnect_get_sdwanai_chat_logs(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/sdwanai/chat/logs",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sdwanai_enable_sase_copilot",
    description="GET /sdwanai/enableSaseCopilot\n\ngetEnableSaseCopilot\n\nGet SASE Copilot enabled status",
    capability=Capability.READ,
)
async def edgeconnect_get_sdwanai_enable_sase_copilot(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/sdwanai/enableSaseCopilot",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_sdwanai_context_clear",
    description="POST /sdwanai/context/clear\n\nsdwanAIClearContext\n\nClear chat context and reset conversation",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sdwanai_context_clear(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sdwanai/context/clear",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_sdwanai_feedback",
    description="POST /sdwanai/feedback\n\nsdwanAIFeedback\n\nSubmit feedback on an AI response",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sdwanai_feedback(
    ctx: Context,
    Authorization: Annotated[
        str,
        Field(description="Session authentication token used to identify the user and retrieve active chat session."),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    header_params: dict[str, Any] = {}
    if Authorization is not None:
        header_params["Authorization"] = Authorization
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sdwanai/feedback",
        query_params=None,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sdwanai_search",
    description="POST /sdwanai/search\n\nsdwanAISearch\n\nQuery the SD-WAN AI assistant with natural language",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sdwanai_search(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sdwanai/search",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sdwanai_stop",
    description="POST /sdwanai/stop\n\nsdwanAIStop\n\nStop a SASE Copilot streaming response",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sdwanai_stop(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/sdwanai/stop",
        query_params=None,
        body=body,
    )
