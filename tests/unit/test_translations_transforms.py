"""Unit tests for translation transforms.

Coverage focuses on the role-specific transforms added in v3.0.1.2 — the
older shared transforms (direct, direct_int, flag_to_bool,
split_csv_to_string_array, expand_vlan_id_csv) are exercised end-to-end via
the engine tests; we don't double up here.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.transforms import (
    aos8_field_present_to_true,
    aos8_reauth_minutes_value,
    aos8_reauth_seconds_value,
    aos8_role_bwc_app_filter_app,
    aos8_role_bwc_app_filter_appcategory,
    aos8_role_bwc_basic_to_central,
    aos8_role_bwc_excl_filter_app,
    aos8_role_bwc_excl_filter_appcategory,
    aos8_role_bwc_web_filter_category,
    aos8_role_bwc_web_filter_reputation,
    get_transform,
    vlanstr_to_id_if_numeric,
    vlanstr_to_name_if_nonnumeric,
    vlanstr_to_vlan_type,
)

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# VLAN-string disambiguation transforms
# --------------------------------------------------------------------------- #


class TestVlanstrTransforms:
    @pytest.mark.parametrize(
        ("source", "id_out", "name_out", "type_out"),
        [
            ("100", 100, None, "VLAN_ID"),
            ("4094", 4094, None, "VLAN_ID"),
            ("internal", None, "internal", "VLAN_NAME"),
            ("user-vlan", None, "user-vlan", "VLAN_NAME"),
            ("0007", 7, None, "VLAN_ID"),
            (None, None, None, None),
            ("", None, None, None),
            ("  ", None, None, None),
        ],
    )
    def test_vlanstr_disambiguation(
        self, source: str | None, id_out: int | None, name_out: str | None, type_out: str | None
    ) -> None:
        assert vlanstr_to_id_if_numeric(source) == id_out
        assert vlanstr_to_name_if_nonnumeric(source) == name_out
        assert vlanstr_to_vlan_type(source) == type_out

    def test_whitespace_stripped(self) -> None:
        assert vlanstr_to_id_if_numeric("  42  ") == 42
        assert vlanstr_to_name_if_nonnumeric("  guest  ") == "guest"
        assert vlanstr_to_vlan_type("  100  ") == "VLAN_ID"


# --------------------------------------------------------------------------- #
# aos8_field_present_to_true
# --------------------------------------------------------------------------- #


class TestFieldPresentToTrue:
    def test_pattern_b_empty_dict_means_configured(self) -> None:
        """role__enforce_dhcp: {} (live shape from configured 'parent' role) -> True."""
        assert aos8_field_present_to_true({}) is True

    def test_pattern_a_present_true_with_flags(self) -> None:
        """role__cp_acc: {_present: true, _flags: {default: true}} -> True."""
        assert aos8_field_present_to_true({"_present": True, "_flags": {"default": True}}) is True

    def test_none_input_drops_body_key(self) -> None:
        """Engine returned None means path lookup raised + optional path applies."""
        assert aos8_field_present_to_true(None) is None

    @pytest.mark.parametrize("value", [True, False, 0, 1, "string", [1, 2, 3]])
    def test_any_non_none_returns_true(self, value: object) -> None:
        """Reaching this transform implies the path resolved; treat any value as 'configured'."""
        assert aos8_field_present_to_true(value) is True


# --------------------------------------------------------------------------- #
# Reauthentication-interval disambiguator pair
# --------------------------------------------------------------------------- #


class TestReauthDisambiguator:
    def test_minutes_form_returns_value_when_seconds_absent(self) -> None:
        """Default form: {reauthperiod: N} (no 'seconds' key) -> minutes side gets N."""
        source = {"reauthperiod": 30}
        assert aos8_reauth_minutes_value(source) == 30
        assert aos8_reauth_seconds_value(source) is None

    def test_seconds_form_returns_value_only_on_seconds_side(self) -> None:
        """Live shape: {seconds: true, reauthperiod: 3600} -> seconds side gets 3600."""
        source = {"seconds": True, "reauthperiod": 3600}
        assert aos8_reauth_minutes_value(source) is None
        assert aos8_reauth_seconds_value(source) == 3600

    def test_seconds_false_treated_as_minutes(self) -> None:
        source = {"seconds": False, "reauthperiod": 15}
        assert aos8_reauth_minutes_value(source) == 15
        assert aos8_reauth_seconds_value(source) is None

    def test_zero_reauthperiod_preserved(self) -> None:
        """reauthperiod=0 (AOS 8 default) is still a real value, not None."""
        source = {"reauthperiod": 0}
        assert aos8_reauth_minutes_value(source) == 0
        assert aos8_reauth_seconds_value(source) is None

    def test_missing_reauthperiod_returns_none(self) -> None:
        assert aos8_reauth_minutes_value({"seconds": True}) is None
        assert aos8_reauth_seconds_value({}) is None

    def test_non_dict_input_returns_none(self) -> None:
        for bad in [None, "string", 42, [1, 2]]:
            assert aos8_reauth_minutes_value(bad) is None
            assert aos8_reauth_seconds_value(bad) is None


# --------------------------------------------------------------------------- #
# Bandwidth-contract transforms
# --------------------------------------------------------------------------- #


class TestBwcBasic:
    def test_live_shape_from_blacklisted_role(self) -> None:
        """Source shape from the 'blacklisted' role at /md/Campus/West."""
        source = [
            {"dir_type": "downstream", "name": "blacklisteddownstreamper-roleui"},
            {"dir_type": "upstream", "name": "blacklistedupstreamper-roleui"},
        ]
        assert aos8_role_bwc_basic_to_central(source) == [
            {"bwc-name": "blacklisteddownstreamper-roleui", "direction": "DOWNSTREAM"},
            {"bwc-name": "blacklistedupstreamper-roleui", "direction": "UPSTREAM"},
        ]

    def test_empty_input_returns_none(self) -> None:
        assert aos8_role_bwc_basic_to_central(None) is None
        assert aos8_role_bwc_basic_to_central([]) is None

    def test_entries_missing_required_fields_skipped(self) -> None:
        source = [{"dir_type": "downstream"}, {"dir_type": "upstream", "name": "ok"}]
        assert aos8_role_bwc_basic_to_central(source) == [{"bwc-name": "ok", "direction": "UPSTREAM"}]


class TestBwcAppFilters:
    def test_filter_app_only_returns_app_entries(self) -> None:
        """Live source from 'parent' role mixes app + appcategory in role__bwc_app."""
        source = [
            {"app_type": "app", "dir": "downstream", "appname": "youtube", "name": "parentyoutubedownstream"},
            {"app_type": "app", "dir": "upstream", "appname": "youtube", "name": "parentyoutubeupstream"},
            {
                "app_type": "appcategory",
                "dir": "downstream",
                "appname": "streaming",
                "name": "parentstreamingdownstream",
            },
        ]
        assert aos8_role_bwc_app_filter_app(source) == [
            {"appname": "youtube", "bwc-name": "parentyoutubedownstream", "direction": "DOWNSTREAM"},
            {"appname": "youtube", "bwc-name": "parentyoutubeupstream", "direction": "UPSTREAM"},
        ]

    def test_filter_appcategory_only_returns_appcategory_entries_uppercased(self) -> None:
        source = [
            {"app_type": "app", "dir": "downstream", "appname": "youtube", "name": "skip-me"},
            {
                "app_type": "appcategory",
                "dir": "downstream",
                "appname": "streaming",
                "name": "parentstreamingdownstream",
            },
            {
                "app_type": "appcategory",
                "dir": "upstream",
                "appname": "streaming",
                "name": "parentstreamingupstream",
            },
        ]
        assert aos8_role_bwc_app_filter_appcategory(source) == [
            {"category-name": "STREAMING", "bwc-name": "parentstreamingdownstream", "direction": "DOWNSTREAM"},
            {"category-name": "STREAMING", "bwc-name": "parentstreamingupstream", "direction": "UPSTREAM"},
        ]

    def test_filters_return_none_when_no_matching_entries(self) -> None:
        source_only_app = [{"app_type": "app", "dir": "downstream", "appname": "x", "name": "y"}]
        assert aos8_role_bwc_app_filter_appcategory(source_only_app) is None
        source_only_cat = [{"app_type": "appcategory", "dir": "downstream", "appname": "x", "name": "y"}]
        assert aos8_role_bwc_app_filter_app(source_only_cat) is None


class TestBwcWebFilters:
    def test_filter_web_category_uppercases_and_dashes(self) -> None:
        """Live shape: webcccatgname='streaming/media' -> 'STREAMING-MEDIA'.

        Note: this slash-and-uppercase mapping doesn't insert connective words
        some Central enums carry (e.g. 'ENTERTAINMENT-AND-ARTS'). Operators
        must spot-check categories with multi-word Central forms after
        migration.
        """
        source = [
            {
                "webcccatgname": "streaming/media",
                "web_opt": "web-cc-category",
                "dir": "downstream",
                "name": "parent-streaming-down",
            },
            {
                "webcccatgname": "streaming/media",
                "web_opt": "web-cc-category",
                "dir": "upstream",
                "name": "parent-streaming-up",
            },
            {"web_rep": "trustworthy", "web_opt": "web-cc-reputation", "dir": "downstream", "name": "skip-me"},
        ]
        assert aos8_role_bwc_web_filter_category(source) == [
            {
                "webcategory-name": "STREAMING-MEDIA",
                "bwc-name": "parent-streaming-down",
                "direction": "DOWNSTREAM",
            },
            {
                "webcategory-name": "STREAMING-MEDIA",
                "bwc-name": "parent-streaming-up",
                "direction": "UPSTREAM",
            },
        ]

    def test_filter_web_reputation_uppercases_and_underscores(self) -> None:
        source = [
            {"web_rep": "trustworthy", "web_opt": "web-cc-reputation", "dir": "downstream", "name": "n1"},
            {"web_rep": "low-risk", "web_opt": "web-cc-reputation", "dir": "upstream", "name": "n2"},
            {
                "webcccatgname": "skip",
                "web_opt": "web-cc-category",
                "dir": "downstream",
                "name": "skip-me",
            },
        ]
        assert aos8_role_bwc_web_filter_reputation(source) == [
            {"webrepname": "TRUSTWORTHY", "bwc-name": "n1", "direction": "DOWNSTREAM"},
            {"webrepname": "LOW_RISK", "bwc-name": "n2", "direction": "UPSTREAM"},
        ]

    def test_empty_or_no_match_returns_none(self) -> None:
        assert aos8_role_bwc_web_filter_category([]) is None
        assert aos8_role_bwc_web_filter_reputation(None) is None


class TestBwcExcludeFilters:
    def test_filter_exclude_app_returns_app_only(self) -> None:
        """Live shape: role__bwc_ex=[{app_type, appname}] (no dir, no name)."""
        source = [
            {"app_type": "app", "appname": "netflix"},
            {"app_type": "appcategory", "appname": "collaboration"},
        ]
        assert aos8_role_bwc_excl_filter_app(source) == [{"exclude-app-name": "netflix"}]

    def test_filter_exclude_appcategory_returns_uppercased(self) -> None:
        source = [
            {"app_type": "app", "appname": "skip-me"},
            {"app_type": "appcategory", "appname": "collaboration"},
            {"app_type": "appcategory", "appname": "streaming"},
        ]
        assert aos8_role_bwc_excl_filter_appcategory(source) == [
            {"exclude-app-category-name": "COLLABORATION"},
            {"exclude-app-category-name": "STREAMING"},
        ]

    def test_filters_return_none_when_no_matching_entries(self) -> None:
        source_only_app = [{"app_type": "app", "appname": "netflix"}]
        assert aos8_role_bwc_excl_filter_appcategory(source_only_app) is None

        source_only_cat = [{"app_type": "appcategory", "appname": "collaboration"}]
        assert aos8_role_bwc_excl_filter_app(source_only_cat) is None

    def test_empty_input_returns_none(self) -> None:
        assert aos8_role_bwc_excl_filter_app([]) is None
        assert aos8_role_bwc_excl_filter_appcategory(None) is None


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #


class TestRegistry:
    @pytest.mark.parametrize(
        "name",
        [
            "direct",
            "direct_str",
            "direct_int",
            "flag_to_bool",
            "split_csv_to_string_array",
            "expand_vlan_id_csv",
            "vlanstr_to_id_if_numeric",
            "vlanstr_to_name_if_nonnumeric",
            "vlanstr_to_vlan_type",
            "aos8_field_present_to_true",
            "aos8_reauth_minutes_value",
            "aos8_reauth_seconds_value",
            "aos8_role_bwc_basic_to_central",
            "aos8_role_bwc_app_filter_app",
            "aos8_role_bwc_app_filter_appcategory",
            "aos8_role_bwc_web_filter_category",
            "aos8_role_bwc_web_filter_reputation",
            "aos8_role_bwc_excl_filter_app",
            "aos8_role_bwc_excl_filter_appcategory",
        ],
    )
    def test_all_transforms_resolve(self, name: str) -> None:
        fn = get_transform(name)
        assert callable(fn)

    def test_unknown_transform_raises_with_known_list(self) -> None:
        with pytest.raises(KeyError, match="Unknown transform"):
            get_transform("does_not_exist")


# --------------------------------------------------------------------------- #
# aos8_server_group_members (central:server_group)
# --------------------------------------------------------------------------- #

from hpe_networking_mcp.translations.transforms import aos8_server_group_members  # noqa: E402


def test_server_group_members_ordered_positions() -> None:
    out = aos8_server_group_members([{"name": "RAD-1"}, {"name": "RAD-2"}])
    assert out == [
        {"server-name": "RAD-1", "position": 1},
        {"server-name": "RAD-2", "position": 2},
    ]


def test_server_group_members_inherited_flag_not_dropped() -> None:
    """Member _flags.inherited reflects group-level inheritance — keep the member."""
    out = aos8_server_group_members([{"name": "RAD-1", "_flags": {"inherited": True}}])
    assert out == [{"server-name": "RAD-1", "position": 1}]


def test_server_group_members_drops_nameless_and_non_dict() -> None:
    out = aos8_server_group_members([{"name": "RAD-1"}, {"fqdn": "x"}, "junk", {"name": "RAD-2"}])
    assert [s["server-name"] for s in out] == ["RAD-1", "RAD-2"]
    assert [s["position"] for s in out] == [1, 2]


def test_server_group_members_non_list_is_empty() -> None:
    assert aos8_server_group_members(None) == []
    assert aos8_server_group_members({}) == []
