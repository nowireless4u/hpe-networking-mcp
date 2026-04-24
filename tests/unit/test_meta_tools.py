"""Unit tests for the shared meta-tool factory (v2.0 Phase 0, #158).

Verifies the three meta-tools installed by ``build_meta_tools`` against a
real FastMCP instance with stub ``ToolSpec`` entries. Integration with real
platform tool bodies is exercised in PR B (Phase 0 Apstra pilot).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from hpe_networking_mcp.config import ServerConfig
from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
from hpe_networking_mcp.platforms._common.tool_registry import (
    REGISTRIES,
    ToolSpec,
    clear_registry,
)

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)
WRITE_DELETE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=True)


@pytest.fixture(autouse=True)
def _clean_registry():
    clear_registry()
    yield
    clear_registry()


@pytest.fixture
def stub_apstra_registry():
    """Populate REGISTRIES['apstra'] with a few handcrafted ToolSpecs.

    The funcs are AsyncMocks so invoke_tool can dispatch to them and we can
    assert on call args without hitting any real vendor API.
    """
    get_blueprints = AsyncMock(return_value={"items": [{"id": "bp1", "label": "HQ"}]})
    get_blueprints.__name__ = "apstra_get_blueprints"  # type: ignore[attr-defined]
    create_vn = AsyncMock(return_value={"status": "created"})
    create_vn.__name__ = "apstra_create_virtual_network"  # type: ignore[attr-defined]

    REGISTRIES["apstra"]["apstra_get_blueprints"] = ToolSpec(
        name="apstra_get_blueprints",
        func=get_blueprints,
        platform="apstra",
        category="blueprints",
        description="List every Apstra datacenter blueprint.",
        tags=set(),
    )
    REGISTRIES["apstra"]["apstra_create_virtual_network"] = ToolSpec(
        name="apstra_create_virtual_network",
        func=create_vn,
        platform="apstra",
        category="manage_networks",
        description="Create a VXLAN or VLAN virtual network.",
        tags={"apstra_write"},
    )
    return {"get_blueprints": get_blueprints, "create_vn": create_vn}


@pytest.fixture
def mcp_with_meta_tools(stub_apstra_registry):
    mcp = FastMCP(name="test-server")
    build_meta_tools("apstra", mcp)
    return mcp


def _fake_ctx(config: ServerConfig) -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"config": config}
    return ctx


@pytest.mark.unit
class TestBuildMetaTools:
    def test_registers_three_tools(self, mcp_with_meta_tools):
        """Exactly the three meta-tools appear on the FastMCP instance."""
        import asyncio

        tools = asyncio.run(mcp_with_meta_tools.list_tools())
        names = sorted(t.name for t in tools)
        assert names == [
            "apstra_get_tool_schema",
            "apstra_invoke_tool",
            "apstra_list_tools",
        ]

    def test_unknown_platform_raises(self):
        mcp = FastMCP(name="test")
        with pytest.raises(ValueError, match="Unknown platform"):
            build_meta_tools("acme", mcp)


@pytest.mark.unit
class TestListTools:
    async def test_returns_read_tools_and_hides_write_when_disabled(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_list_tools")
        config = ServerConfig()  # writes disabled
        ctx = _fake_ctx(config)

        result = await tool.fn(ctx)
        names = [t["name"] for t in result["tools"]]
        assert "apstra_get_blueprints" in names
        assert "apstra_create_virtual_network" not in names
        assert result["total"] == 1

    async def test_returns_write_tools_when_enabled(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_list_tools")
        config = ServerConfig(enable_apstra_write_tools=True)
        ctx = _fake_ctx(config)

        result = await tool.fn(ctx)
        names = [t["name"] for t in result["tools"]]
        assert "apstra_get_blueprints" in names
        assert "apstra_create_virtual_network" in names
        assert result["total"] == 2

    async def test_filter_narrows_results(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_list_tools")
        config = ServerConfig(enable_apstra_write_tools=True)

        result = await tool.fn(_fake_ctx(config), filter="blueprints")
        names = [t["name"] for t in result["tools"]]
        assert names == ["apstra_get_blueprints"]

    async def test_category_filter(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_list_tools")
        config = ServerConfig(enable_apstra_write_tools=True)

        result = await tool.fn(_fake_ctx(config), category="blueprints")
        names = [t["name"] for t in result["tools"]]
        assert names == ["apstra_get_blueprints"]

    async def test_returns_categories_list(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_list_tools")
        config = ServerConfig(enable_apstra_write_tools=True)

        result = await tool.fn(_fake_ctx(config))
        assert sorted(result["categories"]) == ["blueprints", "manage_networks"]


@pytest.mark.unit
class TestGetToolSchema:
    async def test_returns_schema_for_known_tool(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_get_tool_schema")
        config = ServerConfig(enable_apstra_write_tools=True)

        result = await tool.fn(_fake_ctx(config), name="apstra_get_blueprints")
        assert result["status"] == "ok"
        assert result["name"] == "apstra_get_blueprints"
        assert result["category"] == "blueprints"
        assert "description" in result

    async def test_not_found(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_get_tool_schema")
        config = ServerConfig()

        result = await tool.fn(_fake_ctx(config), name="apstra_nonexistent")
        assert result["status"] == "not_found"

    async def test_forbidden_when_write_gated(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_get_tool_schema")
        config = ServerConfig()  # writes disabled

        result = await tool.fn(_fake_ctx(config), name="apstra_create_virtual_network")
        assert result["status"] == "forbidden"


@pytest.mark.unit
class TestInvokeTool:
    async def test_dispatches_to_registered_function(self, mcp_with_meta_tools, stub_apstra_registry):
        tool = await mcp_with_meta_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig()
        ctx = _fake_ctx(config)

        result = await tool.fn(ctx, name="apstra_get_blueprints")
        assert result == {"items": [{"id": "bp1", "label": "HQ"}]}
        stub_apstra_registry["get_blueprints"].assert_awaited_once()

    async def test_forwards_params_as_kwargs(self, mcp_with_meta_tools, stub_apstra_registry):
        tool = await mcp_with_meta_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig(enable_apstra_write_tools=True)
        ctx = _fake_ctx(config)

        await tool.fn(
            ctx,
            name="apstra_create_virtual_network",
            params={"blueprint_id": "bp1", "vn_name": "test"},
        )
        stub_apstra_registry["create_vn"].assert_awaited_once_with(
            ctx,
            blueprint_id="bp1",
            vn_name="test",
        )

    async def test_not_found(self, mcp_with_meta_tools):
        tool = await mcp_with_meta_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig()

        result = await tool.fn(_fake_ctx(config), name="apstra_does_not_exist")
        assert result["status"] == "not_found"

    async def test_forbidden_when_write_gated(self, mcp_with_meta_tools, stub_apstra_registry):
        tool = await mcp_with_meta_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig()  # writes disabled

        result = await tool.fn(
            _fake_ctx(config),
            name="apstra_create_virtual_network",
            params={"blueprint_id": "bp1"},
        )
        assert result["status"] == "forbidden"
        stub_apstra_registry["create_vn"].assert_not_awaited()

    async def test_invalid_params_reports_shape(self, mcp_with_meta_tools, stub_apstra_registry):
        tool = await mcp_with_meta_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig()

        # Configure the stub to raise TypeError (simulating wrong kwarg)
        stub_apstra_registry["get_blueprints"].side_effect = TypeError("unexpected keyword argument 'bogus'")
        result = await tool.fn(
            _fake_ctx(config),
            name="apstra_get_blueprints",
            params={"bogus": "yes"},
        )
        assert result["status"] == "invalid_params"
        assert "bogus" in result["message"]


# ---- Fixtures for coercion tests -----------------------------------------
# Tool functions and their types are defined at module level so
# ``get_type_hints`` can resolve annotations using this module's globals.
# Defining them inside test methods puts the types in a nested scope that
# Pydantic's string-annotation resolver can't see.

from enum import Enum  # noqa: E402
from typing import Annotated as _Annotated  # noqa: E402
from uuid import UUID as _UUID  # noqa: E402

from pydantic import Field as _Field  # noqa: E402


class _FakeEnumObjectType(Enum):
    ORG_SITES = "org_sites"
    SITE_DEVICES = "site_devices"


_coerce_received: dict = {}


async def _fake_enum_tool(
    ctx,
    object_type: _Annotated[_FakeEnumObjectType, _Field(description="what to fetch")],
) -> dict:
    # If coercion is missing, ``object_type`` is the raw string
    # ``'org_sites'`` and ``.value`` access raises AttributeError.
    _coerce_received["value"] = object_type.value
    _coerce_received["type"] = type(object_type).__name__
    return {"ok": True}


_fake_enum_tool.__name__ = "apstra_fake_enum_tool"  # type: ignore[attr-defined]


async def _fake_uuid_tool(
    ctx,
    blueprint_id: _Annotated[_UUID, _Field(description="bp id")],
) -> dict:
    _coerce_received["type"] = type(blueprint_id).__name__
    _coerce_received["value"] = blueprint_id
    return {"ok": True}


_fake_uuid_tool.__name__ = "apstra_fake_uuid_tool"  # type: ignore[attr-defined]


async def _fake_required_tool(
    ctx,
    required_field: _Annotated[str, _Field(description="required")],
) -> dict:
    return {"ok": True}


_fake_required_tool.__name__ = "apstra_fake_required_tool"  # type: ignore[attr-defined]


async def _fake_optional_tool(
    ctx,
    required: _Annotated[str, _Field(description="required")],
    optional_uuid: _Annotated[_UUID, _Field(default=None, description="optional")],
) -> dict:
    return {"optional_is_none": optional_uuid is None}


_fake_optional_tool.__name__ = "apstra_fake_optional_tool"  # type: ignore[attr-defined]


@pytest.fixture
def mcp_with_fake_tools():
    """Install the fake coercion-test tools in the apstra registry."""
    clear_registry("apstra")
    _coerce_received.clear()

    REGISTRIES["apstra"]["apstra_fake_enum_tool"] = ToolSpec(
        name="apstra_fake_enum_tool",
        func=_fake_enum_tool,
        platform="apstra",
        category="testing",
        description="Test tool with enum param.",
        tags=set(),
    )
    REGISTRIES["apstra"]["apstra_fake_uuid_tool"] = ToolSpec(
        name="apstra_fake_uuid_tool",
        func=_fake_uuid_tool,
        platform="apstra",
        category="testing",
        description="Test tool with UUID param.",
        tags=set(),
    )
    REGISTRIES["apstra"]["apstra_fake_required_tool"] = ToolSpec(
        name="apstra_fake_required_tool",
        func=_fake_required_tool,
        platform="apstra",
        category="testing",
        description="Test tool with required param.",
        tags=set(),
    )

    mcp = FastMCP(name="test-coercion")
    build_meta_tools("apstra", mcp)
    return mcp


@pytest.mark.unit
class TestInvokeToolCoercion:
    """Regression tests for Pydantic-based parameter coercion.

    v2.0.0.1 shipped with the meta-tool dispatching raw string params
    directly to tool functions — Enum-typed params failed with
    ``AttributeError: 'str' object has no attribute 'value'`` because
    FastMCP's normal Pydantic coercion was bypassed. v2.0.0.2 restores
    coercion inside ``_invoke_tool``.
    """

    async def test_enum_string_coerces_to_enum_instance(self, mcp_with_fake_tools):
        tool = await mcp_with_fake_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig()

        result = await tool.fn(
            _fake_ctx(config),
            name="apstra_fake_enum_tool",
            params={"object_type": "org_sites"},
        )

        assert result == {"ok": True}
        assert _coerce_received["type"] == "_FakeEnumObjectType"
        assert _coerce_received["value"] == "org_sites"

    async def test_uuid_string_coerces_to_uuid_instance(self, mcp_with_fake_tools):
        tool = await mcp_with_fake_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig()

        result = await tool.fn(
            _fake_ctx(config),
            name="apstra_fake_uuid_tool",
            params={"blueprint_id": "5f79daeb-8ae8-4b1b-a560-f8cfcbc51e76"},
        )

        assert result == {"ok": True}
        assert _coerce_received["type"] == "UUID"
        assert str(_coerce_received["value"]) == "5f79daeb-8ae8-4b1b-a560-f8cfcbc51e76"

    async def test_missing_required_param_returns_invalid_params(self, mcp_with_fake_tools):
        tool = await mcp_with_fake_tools.get_tool("apstra_invoke_tool")
        config = ServerConfig()

        result = await tool.fn(_fake_ctx(config), name="apstra_fake_required_tool", params={})

        assert result["status"] == "invalid_params"
        assert "required_field" in result["message"]

    async def test_explicit_null_for_optional_param_uses_default(self):
        """AI clients often pass ``null`` for optional params; should use the default.

        Mist tool signatures commonly use ``Annotated[UUID, Field(default=None)]``
        without the ``| None`` in the type. Passing ``{"site_id": null}`` should
        strip the None and let Pydantic apply the default.
        """
        clear_registry("apstra")
        REGISTRIES["apstra"]["apstra_fake_optional_tool"] = ToolSpec(
            name="apstra_fake_optional_tool",
            func=_fake_optional_tool,
            platform="apstra",
            category="testing",
            description="Test tool with optional UUID param.",
            tags=set(),
        )
        mcp = FastMCP(name="test-optional")
        build_meta_tools("apstra", mcp)
        tool = await mcp.get_tool("apstra_invoke_tool")
        config = ServerConfig()

        result = await tool.fn(
            _fake_ctx(config),
            name="apstra_fake_optional_tool",
            params={"required": "value", "optional_uuid": None},
        )
        assert result == {"optional_is_none": True}
