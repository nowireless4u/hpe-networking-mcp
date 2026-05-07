"""Unit tests for translation transforms.

Coverage focuses on the role-specific transforms added in v3.0.1.2 — the
older shared transforms (direct, direct_int, flag_to_bool,
split_csv_to_string_array, expand_vlan_id_csv) are exercised end-to-end via
the engine tests; we don't double up here.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.transforms import (
    aos8_present_flag_to_bool,
    aos8_role_acl_to_central_policies,
    get_transform,
    vlanstr_to_id_if_numeric,
    vlanstr_to_name_if_nonnumeric,
    vlanstr_to_vlan_type,
)

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# aos8_role_acl_to_central_policies
# --------------------------------------------------------------------------- #


class TestAclToPolicies:
    def test_user_customized_acls_pass_through_with_renamed_field(self) -> None:
        source = [
            {"acl_type": "session", "pname": "camera_role_ubt"},
            {"acl_type": "session", "pname": "allowall"},
        ]
        assert aos8_role_acl_to_central_policies(source) == [
            {"name": "camera_role_ubt"},
            {"name": "allowall"},
        ]

    def test_system_default_inherited_readonly_entries_filtered(self) -> None:
        source = [
            {
                "acl_type": "session",
                "pname": "global-sacl",
                "_flags": {"system": True, "readonly": True, "default": True},
            },
            {"acl_type": "session", "pname": "user-customized"},
            {"acl_type": "session", "pname": "another-default", "_flags": {"default": True, "inherited": True}},
        ]
        assert aos8_role_acl_to_central_policies(source) == [{"name": "user-customized"}]

    def test_eth_and_mac_acl_types_pass_through(self) -> None:
        source = [
            {"acl_type": "session", "pname": "session-acl"},
            {"acl_type": "eth", "pname": "eth-acl"},
            {"acl_type": "mac", "pname": "mac-acl"},
        ]
        assert aos8_role_acl_to_central_policies(source) == [
            {"name": "session-acl"},
            {"name": "eth-acl"},
            {"name": "mac-acl"},
        ]

    def test_empty_input_returns_none(self) -> None:
        """None return lets the engine drop the body 'policies' key entirely."""
        assert aos8_role_acl_to_central_policies(None) is None
        assert aos8_role_acl_to_central_policies([]) is None

    def test_all_filtered_returns_none(self) -> None:
        """When every entry is system / default, return None so the key drops."""
        source = [
            {"acl_type": "session", "pname": "global-sacl", "_flags": {"system": True}},
            {"acl_type": "session", "pname": "default-acl", "_flags": {"default": True}},
        ]
        assert aos8_role_acl_to_central_policies(source) is None

    def test_entries_without_pname_skipped(self) -> None:
        source = [{"acl_type": "session"}, {"acl_type": "session", "pname": "real"}]
        assert aos8_role_acl_to_central_policies(source) == [{"name": "real"}]


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
            ("0007", 7, None, "VLAN_ID"),  # leading zeros still parse as int
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
# aos8_present_flag_to_bool
# --------------------------------------------------------------------------- #


class TestPresentFlagToBool:
    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            (True, True),
            (False, False),
            ("true", True),
            ("yes", True),
            ("1", True),
            ("enabled", True),
            ("false", False),
            ("no", False),
            ("disabled", False),
            (None, None),  # None propagates so optional drops the key
        ],
    )
    def test_aos8_present_flag_to_bool(self, source, expected) -> None:  # noqa: ANN001
        assert aos8_present_flag_to_bool(source) == expected


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
            "aos8_role_acl_to_central_policies",
            "vlanstr_to_id_if_numeric",
            "vlanstr_to_name_if_nonnumeric",
            "vlanstr_to_vlan_type",
            "aos8_present_flag_to_bool",
        ],
    )
    def test_all_transforms_resolve(self, name: str) -> None:
        fn = get_transform(name)
        assert callable(fn)

    def test_unknown_transform_raises_with_known_list(self) -> None:
        with pytest.raises(KeyError, match="Unknown transform"):
            get_transform("does_not_exist")
