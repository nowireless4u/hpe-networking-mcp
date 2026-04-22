"""Unit tests for Apstra normalization helpers in models.py."""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.apstra.models import (
    normalize_application_points,
    normalize_to_int_list,
    normalize_to_nested_list,
    normalize_to_string_list,
    parse_bool,
)


@pytest.mark.unit
class TestParseBool:
    @pytest.mark.parametrize(
        "value,expected",
        [
            (True, True),
            (False, False),
            ("true", True),
            ("false", False),
            ("TRUE", True),
            ("False", False),
            (1, True),
            (0, False),
            (None, None),
        ],
    )
    def test_coercions(self, value, expected):
        assert parse_bool(value) is expected

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError):
            parse_bool("maybe")


@pytest.mark.unit
class TestNormalizeToStringList:
    def test_none_returns_none(self):
        assert normalize_to_string_list(None) is None

    def test_empty_string_returns_none(self):
        assert normalize_to_string_list("") is None

    def test_single_string_wraps_in_list(self):
        assert normalize_to_string_list("sys1") == ["sys1"]

    def test_json_array_string(self):
        assert normalize_to_string_list('["a", "b"]') == ["a", "b"]

    def test_list_passes_through(self):
        assert normalize_to_string_list(["a", "b"]) == ["a", "b"]

    def test_not_bracketed_treated_as_literal(self):
        # A string that doesn't look like a JSON array is treated as a single
        # literal ID — matches source apstra_core behavior.
        assert normalize_to_string_list("[broken") == ["[broken"]
        assert normalize_to_string_list('{"not": "a list"}') == ['{"not": "a list"}']

    def test_malformed_json_array_raises(self):
        with pytest.raises(ValueError):
            normalize_to_string_list("[oops,]")

    def test_ints_in_array_coerced_to_str(self):
        # "[1]" parses as [1], each element cast to str.
        assert normalize_to_string_list("[1]") == ["1"]

    def test_json_object_in_brackets_coerces_via_str(self):
        # "[{"a":1}]" parses to [{}] — helper applies str() per element.
        assert normalize_to_string_list('[{"a":1}]') == ["{'a': 1}"]


@pytest.mark.unit
class TestNormalizeToIntList:
    def test_none_returns_none(self):
        assert normalize_to_int_list(None, 3) is None

    def test_single_int_repeats(self):
        assert normalize_to_int_list(400, 3) == [400, 400, 400]

    def test_single_string_int_repeats(self):
        assert normalize_to_int_list("400", 2) == [400, 400]

    def test_json_array_parsed(self):
        assert normalize_to_int_list("[400, 401]", 2) == [400, 401]

    def test_list_passes_through(self):
        assert normalize_to_int_list([300, 301], 2) == [300, 301]

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError):
            normalize_to_int_list("not-an-int", 1)


@pytest.mark.unit
class TestNormalizeToNestedList:
    def test_none_returns_empty_nested(self):
        assert normalize_to_nested_list(None, 2) == [[], []]

    def test_empty_string_returns_empty_nested(self):
        assert normalize_to_nested_list("", 3) == [[], [], []]

    def test_nested_json_passes_through(self):
        assert normalize_to_nested_list('[["a"],["b","c"]]', 2) == [["a"], ["b", "c"]]

    def test_flat_json_array_replicates(self):
        assert normalize_to_nested_list('["x","y"]', 2) == [["x", "y"], ["x", "y"]]

    def test_flat_list_replicates(self):
        assert normalize_to_nested_list(["x"], 3) == [["x"], ["x"], ["x"]]

    def test_nested_list_passes_through(self):
        assert normalize_to_nested_list([["a"], ["b"]], 2) == [["a"], ["b"]]

    def test_single_string_replicates(self):
        assert normalize_to_nested_list("node1", 2) == [["node1"], ["node1"]]


@pytest.mark.unit
class TestNormalizeApplicationPoints:
    _valid = [{"id": "i1", "policies": [{"policy": "p1", "used": True}]}]

    def test_list_of_dicts_passes(self):
        assert normalize_application_points(self._valid) == self._valid

    def test_single_dict_wraps(self):
        single = self._valid[0]
        assert normalize_application_points(single) == [single]

    def test_json_string_parsed(self):
        import json

        assert normalize_application_points(json.dumps(self._valid)) == self._valid

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError):
            normalize_application_points("{not-json}")

    def test_missing_id_raises(self):
        with pytest.raises(ValueError):
            normalize_application_points([{"policies": []}])

    def test_policies_not_list_raises(self):
        with pytest.raises(ValueError):
            normalize_application_points([{"id": "x", "policies": "oops"}])

    def test_policy_missing_fields_raises(self):
        with pytest.raises(ValueError):
            normalize_application_points([{"id": "x", "policies": [{"policy": "p"}]}])

    def test_used_must_be_bool(self):
        with pytest.raises(ValueError):
            normalize_application_points([{"id": "x", "policies": [{"policy": "p", "used": "yes"}]}])

    def test_unsupported_type_raises(self):
        with pytest.raises(ValueError):
            normalize_application_points(42)
