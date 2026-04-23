"""Unit tests for ``as_comma_separated`` helpers used by the Mist/Central
filter-parameter consistency sweep (#156).

Two copies of the helper exist — one in each platform's ``utils.py`` — so
each platform can ship without a cross-platform dependency. The tests below
exercise both to guarantee they stay behaviour-identical. When v2.0 Phase 0
introduces ``platforms/_common/``, the helpers collapse into one and these
tests consolidate.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.central.utils import (
    as_comma_separated as central_as_comma_separated,
)
from hpe_networking_mcp.platforms.mist.utils import (
    as_comma_separated as mist_as_comma_separated,
)


@pytest.fixture(params=[central_as_comma_separated, mist_as_comma_separated], ids=["central", "mist"])
def as_comma_separated(request):
    """Run every case against both platform helpers."""
    return request.param


@pytest.mark.unit
class TestAsCommaSeparated:
    def test_none_stays_none(self, as_comma_separated):
        assert as_comma_separated(None) is None

    def test_single_string_passes_through(self, as_comma_separated):
        assert as_comma_separated("AP43") == "AP43"

    def test_already_comma_separated_string_passes_through(self, as_comma_separated):
        # If the caller already supplied the comma-separated form, don't double-join.
        assert as_comma_separated("AP43,AP44") == "AP43,AP44"

    def test_list_joined_with_commas(self, as_comma_separated):
        assert as_comma_separated(["AP43", "AP44"]) == "AP43,AP44"

    def test_single_element_list_yields_bare_value(self, as_comma_separated):
        assert as_comma_separated(["Solo"]) == "Solo"

    def test_empty_list_yields_empty_string(self, as_comma_separated):
        # Intentional: ``""`` is distinct from ``None`` — the caller's decision
        # whether to filter on an empty string flows through.
        assert as_comma_separated([]) == ""

    def test_tuple_is_coerced_to_list_joined(self, as_comma_separated):
        assert as_comma_separated(("AP43", "AP44")) == "AP43,AP44"

    def test_non_string_elements_are_stringified(self, as_comma_separated):
        # Central's FilterField and mistapi both accept plain strings; a caller
        # passing raw ints is probably wrong but shouldn't crash the helper.
        assert as_comma_separated([1, 2]) == "1,2"
