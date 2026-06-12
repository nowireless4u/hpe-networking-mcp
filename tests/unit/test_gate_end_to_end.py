"""End-to-end test of the universal confirmation gate over a real MCP session.

Builds a minimal FastMCP server with one platform's meta-tools and a fake
registry, then drives ``<platform>_invoke_tool`` through an in-memory
``fastmcp.Client`` whose elicitation handler plays the human. This exercises
the REAL dispatch path (registry lookup → enable check → gate → elicit
round-trip → tool call), not mocks of it.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any

import pytest
from fastmcp import Client, FastMCP

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, ToolSpec

pytestmark = pytest.mark.unit

_PLATFORM = "gatetest"


@pytest.fixture
def gated_server():
    """A FastMCP server exposing gatetest_invoke_tool over a fake registry."""
    calls: list[dict[str, Any]] = []

    async def fake_write_tool(ctx, target: str = "", confirmed: bool = False) -> dict:
        calls.append({"target": target})
        return {"status": "written", "target": target}

    async def fake_read_tool(ctx) -> dict:
        calls.append({"read": True})
        return {"status": "read"}

    REGISTRIES[_PLATFORM] = {
        "gatetest_manage_thing": ToolSpec(
            name="gatetest_manage_thing",
            func=fake_write_tool,
            platform=_PLATFORM,
            category="test",
            description="Fake gated write.",
            tags={f"{_PLATFORM}_write_delete", "requires_confirmation"},
            capability=Capability.WRITE_DELETE,
        ),
        "gatetest_get_thing": ToolSpec(
            name="gatetest_get_thing",
            func=fake_read_tool,
            platform=_PLATFORM,
            category="test",
            description="Fake read.",
            tags=set(),
            capability=Capability.READ,
        ),
    }

    config = SimpleNamespace(disable_elicitation=False)
    # is_tool_enabled consults the config flags; expose the write flag as on.
    setattr(config, f"enable_{_PLATFORM}_write_tools", True)

    @asynccontextmanager
    async def lifespan(_server):
        yield {"config": config}

    server = FastMCP("gate-test", lifespan=lifespan)
    build_meta_tools(_PLATFORM, server)

    yield server, calls
    REGISTRIES.pop(_PLATFORM, None)


class TestGateEndToEnd:
    async def test_accept_prompts_then_dispatches(self, gated_server):
        server, calls = gated_server
        prompts: list[str] = []

        async def handler(message: str, response_type, params, context):
            prompts.append(message)
            from fastmcp.client.elicitation import ElicitResult

            return ElicitResult(action="accept")

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool(
                f"{_PLATFORM}_invoke_tool", {"name": "gatetest_manage_thing", "params": {"target": "HQ"}}
            )
        assert calls == [{"target": "HQ"}]
        assert len(prompts) == 1 and "gatetest_manage_thing" in prompts[0]
        assert result.data["status"] == "written"

    async def test_decline_blocks_dispatch_even_with_confirmed_true(self, gated_server):
        """#415: confirmed=true must not bypass a live prompt the human declined."""
        server, calls = gated_server

        async def handler(message: str, response_type, params, context):
            from fastmcp.client.elicitation import ElicitResult

            return ElicitResult(action="decline")

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool(
                f"{_PLATFORM}_invoke_tool",
                {"name": "gatetest_manage_thing", "params": {"target": "HQ", "confirmed": True}},
            )
        assert calls == []  # tool never ran
        assert result.data["status"] == "declined"

    async def test_read_tool_never_prompts(self, gated_server):
        server, calls = gated_server
        prompts: list[str] = []

        async def counting_handler(message: str, response_type, params, context):
            prompts.append(message)
            from fastmcp.client.elicitation import ElicitResult

            return ElicitResult(action="accept")

        async with Client(server, elicitation_handler=counting_handler) as client:
            result = await client.call_tool(f"{_PLATFORM}_invoke_tool", {"name": "gatetest_get_thing", "params": {}})
        assert prompts == []
        assert calls == [{"read": True}]
        assert result.data["status"] == "read"

    async def test_no_elicitation_client_requires_chat_confirm_then_fallback(self, gated_server):
        """A client with NO elicitation handler: first call returns
        confirmation_required; the confirmed=true retry proceeds."""
        server, calls = gated_server

        async with Client(server) as client:  # no elicitation_handler
            first = await client.call_tool(
                f"{_PLATFORM}_invoke_tool", {"name": "gatetest_manage_thing", "params": {"target": "HQ"}}
            )
            assert first.data["status"] == "confirmation_required"
            assert calls == []

            second = await client.call_tool(
                f"{_PLATFORM}_invoke_tool",
                {"name": "gatetest_manage_thing", "params": {"target": "HQ", "confirmed": True}},
            )
        assert second.data["status"] == "written"
        assert calls == [{"target": "HQ"}]
