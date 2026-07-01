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
from fastmcp import Client, Context, FastMCP

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

            # The gate now elicits a REQUIRED boolean; a human who approves
            # supplies value=True.
            return ElicitResult(action="accept", content={"value": True})

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool(
                f"{_PLATFORM}_invoke_tool", {"name": "gatetest_manage_thing", "params": {"target": "HQ"}}
            )
        assert calls == [{"target": "HQ"}]
        assert len(prompts) == 1 and "gatetest_manage_thing" in prompts[0]
        assert result.data["status"] == "written"

    async def test_accept_without_value_fails_closed(self, gated_server):
        """SAFETY: a client that ACCEPTS the elicitation but supplies no payload
        (the Claude Desktop silent-auto-accept of the old empty schema) must NOT
        dispatch the write — the required `value` field is missing, server-side
        validation fails, and the gate fails closed."""
        server, calls = gated_server

        async def handler(message: str, response_type, params, context):
            from fastmcp.client.elicitation import ElicitResult

            return ElicitResult(action="accept")  # no content — empty auto-accept

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool(
                f"{_PLATFORM}_invoke_tool",
                {"name": "gatetest_manage_thing", "params": {"target": "HQ"}},
            )
        assert calls == []  # the write must NOT have run
        assert result.data["status"] != "written"

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

            return ElicitResult(action="accept", content={"value": True})

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


@pytest.fixture
def direct_gated_server():
    """Server with ElicitationMiddleware + the underlying tools registered as
    real FastMCP tools, so a Client can call them DIRECTLY by name (the #558
    bypass path). The middleware's structural on_call_tool gate must fire on
    that path just like the _invoke_tool dispatcher does.
    """
    from hpe_networking_mcp.middleware.elicitation import ElicitationMiddleware

    calls: list[dict[str, Any]] = []

    REGISTRIES[_PLATFORM] = {
        "gatetest_manage_thing": ToolSpec(
            name="gatetest_manage_thing",
            func=lambda ctx, **k: None,  # unused on the direct path
            platform=_PLATFORM,
            category="test",
            description="Fake gated write.",
            tags={f"{_PLATFORM}_write_delete", "requires_confirmation"},
            capability=Capability.WRITE_DELETE,
        ),
        "gatetest_get_thing": ToolSpec(
            name="gatetest_get_thing",
            func=lambda ctx, **k: None,
            platform=_PLATFORM,
            category="test",
            description="Fake read.",
            tags=set(),
            capability=Capability.READ,
        ),
    }

    config = SimpleNamespace(disable_elicitation=False)
    setattr(config, f"enable_{_PLATFORM}_write_tools", True)

    @asynccontextmanager
    async def lifespan(_server):
        yield {"config": config}

    server = FastMCP("gate-test-direct", lifespan=lifespan, middleware=[ElicitationMiddleware()])

    @server.tool(name="gatetest_manage_thing")
    async def _direct_write(target: str = "") -> dict:
        calls.append({"target": target})
        return {"status": "written", "target": target}

    @server.tool(name="gatetest_get_thing")
    async def _direct_read() -> dict:
        calls.append({"read": True})
        return {"status": "read"}

    yield server, calls
    REGISTRIES.pop(_PLATFORM, None)


class TestDirectCallGating:
    """#558: a write tool called DIRECTLY by name (not via _invoke_tool) must be
    gated by the structural on_call_tool middleware — on every dispatch path."""

    async def test_direct_write_blocks_on_decline(self, direct_gated_server):
        server, calls = direct_gated_server

        async def handler(message, response_type, params, context):
            from fastmcp.client.elicitation import ElicitResult

            return ElicitResult(action="decline")

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool("gatetest_manage_thing", {"target": "HQ"})
        assert calls == []  # the write must NOT have run
        assert result.data["ok"] is False
        assert result.data["data"]["status"] == "declined"

    async def test_direct_write_proceeds_on_approve(self, direct_gated_server):
        server, calls = direct_gated_server
        prompts: list[str] = []

        async def handler(message, response_type, params, context):
            from fastmcp.client.elicitation import ElicitResult

            prompts.append(message)
            return ElicitResult(action="accept", content={"value": True})

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool("gatetest_manage_thing", {"target": "HQ"})
        assert len(prompts) == 1 and "gatetest_manage_thing" in prompts[0]
        assert calls == [{"target": "HQ"}]
        assert result.data["status"] == "written"

    async def test_direct_write_empty_accept_fails_closed(self, direct_gated_server):
        """A client that accepts with no payload (Claude Desktop's silent
        auto-accept) fails the required-bool schema → the middleware fails
        closed → the direct write does NOT run."""
        server, calls = direct_gated_server

        async def handler(message, response_type, params, context):
            from fastmcp.client.elicitation import ElicitResult

            return ElicitResult(action="accept")  # no content

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool("gatetest_manage_thing", {"target": "HQ"})
        assert calls == []
        assert result.data["ok"] is False

    async def test_direct_read_never_prompts(self, direct_gated_server):
        server, calls = direct_gated_server
        prompts: list[str] = []

        async def handler(message, response_type, params, context):
            from fastmcp.client.elicitation import ElicitResult

            prompts.append(message)
            return ElicitResult(action="accept", content={"value": True})

        async with Client(server, elicitation_handler=handler) as client:
            result = await client.call_tool("gatetest_get_thing", {})
        assert prompts == []  # reads never prompt
        assert calls == [{"read": True}]
        assert result.data["status"] == "read"

    async def test_nested_fastmcp_call_tool_is_gated_like_the_sandbox(self, direct_gated_server):
        """The code-mode sandbox dispatches direct-by-name calls via
        ``ctx.fastmcp.call_tool(name, params)`` (run_middleware=True). This proves
        on_call_tool fires on that NESTED path too — i.e. an ``execute()`` block
        calling a write tool directly by name cannot bypass confirmation (#558)."""
        server, calls = direct_gated_server

        @server.tool(name="gatetest_sandbox_proxy")
        async def _proxy(ctx: Context, target: str = "") -> dict:
            # Mirror exactly what CodeMode's sandbox call_tool does.
            return await ctx.fastmcp.call_tool("gatetest_manage_thing", {"target": target})

        async def handler(message, response_type, params, context):
            from fastmcp.client.elicitation import ElicitResult

            return ElicitResult(action="decline")

        async with Client(server, elicitation_handler=handler) as client:
            await client.call_tool("gatetest_sandbox_proxy", {"target": "HQ"})
        assert calls == []  # the nested direct-by-name write was gated and blocked
