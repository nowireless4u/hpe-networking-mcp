"""Unit tests for AOS 8 tool helpers — focus on the transposed-table flattener.

The flattener was added in v3.0.0.5 to fix a PII tokenization gap (issue #235):
AOS 8 ``show <thing> detail`` commands return their content as a transposed
key/value table with literal ``Parameter`` / ``Value`` field names. The
walker classifies by JSON field name and so cannot see the *semantic*
field name hidden in the ``Parameter`` column. The flattener detects the
shape and rewrites it into a regular dict so identifier-field rules can
fire normally on the semantic names.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from hpe_networking_mcp.platforms.aos8.tools._helpers import (
    flatten_param_value_lists,
    run_show,
)

pytestmark = pytest.mark.unit

_FIXTURES = Path(__file__).parent / "fixtures" / "aos8"


def _load(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text())


class TestFlattenParamValueLists:
    def test_transposed_list_flattens_to_dict(self):
        body = [
            {"Parameter": "Host", "Value": "192.168.20.70"},
            {"Parameter": "Key", "Value": "********"},
            {"Parameter": "Auth Port", "Value": "1812"},
        ]
        assert flatten_param_value_lists(body) == {
            "Host": "192.168.20.70",
            "Key": "********",
            "Auth Port": "1812",
        }

    def test_nested_transposed_list_flattens_in_place(self):
        body = {
            "RADIUS Server ClearPass70": [
                {"Parameter": "Host", "Value": "192.168.20.70"},
                {"Parameter": "Key", "Value": "********"},
            ]
        }
        result = flatten_param_value_lists(body)
        assert result == {
            "RADIUS Server ClearPass70": {
                "Host": "192.168.20.70",
                "Key": "********",
            }
        }

    def test_non_transposed_list_passes_through(self):
        # Regular AOS 8 list of records — every row has rich fields, not
        # just ``Parameter`` and ``Value``. Don't touch it.
        body = [
            {"Name": "ClearPass70", "Profile Status": None, "References": "2"},
            {"Name": "ClearPass75", "Profile Status": None, "References": "1"},
        ]
        assert flatten_param_value_lists(body) == body

    def test_empty_list_passes_through(self):
        assert flatten_param_value_lists([]) == []

    def test_scalar_passes_through(self):
        assert flatten_param_value_lists("hello") == "hello"
        assert flatten_param_value_lists(42) == 42
        assert flatten_param_value_lists(None) is None

    def test_list_with_mixed_shapes_passes_through(self):
        # Conservative: even one non-Parameter/Value row preserves the list as-is.
        body = [
            {"Parameter": "Host", "Value": "192.168.20.70"},
            {"some_other": "shape"},
        ]
        # Recurses into elements; first row is a dict (not a transposed list),
        # so it stays a list of dicts.
        assert flatten_param_value_lists(body) == body

    def test_real_radius_detail_fixture_flattens(self):
        body = _load("show_aaa_radius_server_detail.json")
        flat = flatten_param_value_lists(body)

        # Wrapping key preserved; its value is now a dict, not a list
        assert isinstance(flat["RADIUS Server ClearPass70"], dict)
        # Semantic field names now visible at the JSON field level
        assert flat["RADIUS Server ClearPass70"]["Host"] == "192.168.20.70"
        assert flat["RADIUS Server ClearPass70"]["Key"] == "********"
        assert flat["RADIUS Server ClearPass70"]["Auth Port"] == "1812"
        # _meta key (not a transposed list) untouched
        assert flat["_meta"] == ["Parameter", "Value"]

    def test_idempotent_on_already_flattened_dict(self):
        body = {"RADIUS Server X": {"Host": "1.2.3.4", "Key": "********"}}
        assert flatten_param_value_lists(body) == body


class TestRunShowAppliesFlatten:
    """run_show should pipe the response through both strip_meta and the flattener."""

    async def test_run_show_flattens_radius_detail_response(self):
        body = _load("show_aaa_radius_server_detail.json")
        response = MagicMock(spec=httpx.Response)
        response.json.return_value = body
        response.text = json.dumps(body)
        client = MagicMock()
        client.request = AsyncMock(return_value=response)

        result = await run_show(client, "show aaa authentication-server radius ClearPass70")

        # _meta stripped (existing strip_meta behavior)
        assert "_meta" not in result
        # Transposed list flattened into a dict
        assert isinstance(result["RADIUS Server ClearPass70"], dict)
        assert result["RADIUS Server ClearPass70"]["Host"] == "192.168.20.70"
