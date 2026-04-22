"""Unit tests for Apstra topology helper (redundancy-group expansion)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from hpe_networking_mcp.platforms.apstra.topology import (
    get_individual_leafs_from_system_ids,
)


def _mock_client_returning(data):
    """Build an ApstraClient mock whose ``request`` returns a response with ``data`` JSON."""
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = data
    client.request = AsyncMock(return_value=response)
    return client


@pytest.mark.unit
class TestGetIndividualLeafs:
    async def test_pass_through_for_non_redundancy_systems(self):
        client = _mock_client_returning(
            {
                "data": [
                    {"id": "leafA", "role": "leaf"},
                    {"id": "leafB", "role": "leaf"},
                ]
            }
        )
        result = await get_individual_leafs_from_system_ids(client, "bp1", ["leafA", "leafB"])
        assert result == ["leafA", "leafB"]

    async def test_expands_redundancy_group_to_members(self):
        client = _mock_client_returning(
            {
                "data": [
                    {"id": "rg-1", "role": "redundancy_group"},
                    {"id": "leaf1", "role": "leaf", "redundancy_group_id": "rg-1"},
                    {"id": "leaf2", "role": "leaf", "redundancy_group_id": "rg-1"},
                    {"id": "leaf3", "role": "leaf"},
                ]
            }
        )
        result = await get_individual_leafs_from_system_ids(client, "bp1", ["rg-1", "leaf3"])
        assert sorted(result) == ["leaf1", "leaf2", "leaf3"]

    async def test_error_falls_back_to_original_ids(self):
        client = MagicMock()
        client.request = AsyncMock(side_effect=RuntimeError("boom"))
        result = await get_individual_leafs_from_system_ids(client, "bp1", ["a", "b"])
        assert result == ["a", "b"]

    async def test_redundancy_group_without_members_preserves_id(self):
        client = _mock_client_returning({"data": [{"id": "rg-empty", "role": "redundancy_group"}]})
        result = await get_individual_leafs_from_system_ids(client, "bp1", ["rg-empty"])
        assert result == ["rg-empty"]
