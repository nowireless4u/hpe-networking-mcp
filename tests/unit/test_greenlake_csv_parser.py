from __future__ import annotations

from pathlib import Path

import pytest

from hpe_networking_mcp.platforms.greenlake.utils.csv_parser import parse_csv

pytestmark = pytest.mark.unit


class TestParseCsvFromFilePath:
    def test_valid_csv_returns_valid_rows(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "serialNumber,macAddress,partNumber\nABC123,11:22:33:44:55:66,JL123A\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert result.invalid_rows == []

    def test_bom_header_is_stripped(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "bom.csv"
        csv_file.write_bytes(b"\xef\xbb\xbfserialNumber,macAddress\nABC123,11:22:33:44:55:66\n")
        result = parse_csv(str(csv_file), None)
        assert result.error is None
        assert len(result.valid_rows) == 1

    def test_windows_crlf_no_spurious_carriage_return(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "crlf.csv"
        csv_file.write_bytes(b"serialNumber,macAddress\r\nABC123,11:22:33:44:55:66\r\n")
        result = parse_csv(str(csv_file), None)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert not result.valid_rows[0]["macAddress"].endswith("\r")

    def test_missing_serial_column_returns_error(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "no_serial.csv"
        csv_file.write_text(
            "macAddress,partNumber\n11:22:33:44:55:66,JL123A\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is not None
        assert "serialNumber" in result.error

    def test_missing_mac_column_returns_error(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "no_mac.csv"
        csv_file.write_text(
            "serialNumber,partNumber\nABC123,JL123A\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is not None
        assert "macAddress" in result.error

    def test_missing_both_mandatory_columns_returns_error(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "no_mandatory.csv"
        csv_file.write_text(
            "partNumber\nJL123A\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is not None
        assert "serialNumber" in result.error
        assert "macAddress" in result.error

    def test_row_missing_serial_value_goes_to_invalid_rows(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty_serial.csv"
        csv_file.write_text(
            "serialNumber,macAddress\n,11:22:33:44:55:66\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is None
        assert len(result.invalid_rows) == 1
        assert result.valid_rows == []

    def test_row_missing_mac_value_goes_to_invalid_rows(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty_mac.csv"
        csv_file.write_text(
            "serialNumber,macAddress\nABC123,\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is None
        assert len(result.invalid_rows) == 1
        assert result.valid_rows == []

    def test_mixed_valid_and_invalid_rows(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "mixed.csv"
        csv_file.write_text(
            "serialNumber,macAddress\nROW1,11:22:33:44:55:66\n,22:33:44:55:66:77\nROW3,33:44:55:66:77:88\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is None
        assert len(result.valid_rows) == 2
        assert len(result.invalid_rows) == 1

    def test_invalid_row_entry_contains_row_num_and_error(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "invalid_keys.csv"
        csv_file.write_text(
            "serialNumber,macAddress\n,11:22:33:44:55:66\n",
            encoding="utf-8",
        )
        result = parse_csv(str(csv_file), None)
        assert result.error is None
        assert len(result.invalid_rows) == 1
        entry = result.invalid_rows[0]
        assert "row_num" in entry
        assert "serial" in entry
        assert "error" in entry


class TestParseCsvFromInlineText:
    def test_inline_text_parses_identically_to_file(self, tmp_path: Path) -> None:
        csv_content = "serialNumber,macAddress,partNumber\nABC123,11:22:33:44:55:66,JL123A\n"
        csv_file = tmp_path / "identical.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        file_result = parse_csv(str(csv_file), None)
        text_result = parse_csv(None, csv_content)

        assert file_result.valid_rows == text_result.valid_rows
        assert file_result.invalid_rows == text_result.invalid_rows
        assert file_result.error == text_result.error

    def test_multiline_quoted_field_not_truncated(self) -> None:
        csv_text = 'serialNumber,macAddress,notes\nABC123,11:22:33:44:55:66,"line one\nline two"\n'
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1

    def test_exactly_one_source_required_both_none_returns_error(self) -> None:
        with pytest.raises(ValueError):
            parse_csv(None, None)

    def test_exactly_one_source_required_both_set_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_csv("some/path.csv", "serial,mac\nA,B")


class TestColumnAliasResolution:
    def _make_csv(self, header_col: str, value: str = "VAL,11:22:33:44:55:66") -> str:
        return f"{header_col},macAddress\n{value}\n"

    def _make_mac_csv(self, mac_col: str, value: str = "ABC123,11:22:33:44:55:66") -> str:
        return f"serialNumber,{mac_col}\n{value}\n"

    def test_serial_alias_maps_to_canonical(self) -> None:
        csv_text = "serial,macAddress\nABC123,11:22:33:44:55:66\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "serialNumber" in result.valid_rows[0]
        assert "serial" not in result.valid_rows[0]

    def test_sn_alias_maps_to_canonical(self) -> None:
        csv_text = "SN,macAddress\nABC123,11:22:33:44:55:66\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "serialNumber" in result.valid_rows[0]

    def test_serial_number_underscore_alias(self) -> None:
        csv_text = "serial_number,macAddress\nABC123,11:22:33:44:55:66\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "serialNumber" in result.valid_rows[0]

    def test_mac_alias_maps_to_canonical(self) -> None:
        csv_text = "serialNumber,mac\nABC123,11:22:33:44:55:66\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "macAddress" in result.valid_rows[0]
        assert "mac" not in result.valid_rows[0]

    def test_mac_address_underscore_alias(self) -> None:
        csv_text = "serialNumber,mac_address\nABC123,11:22:33:44:55:66\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "macAddress" in result.valid_rows[0]

    def test_case_insensitive_mixed_case_header(self) -> None:
        csv_text = "SerialNumber,macAddress\nABC123,11:22:33:44:55:66\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "serialNumber" in result.valid_rows[0]

    def test_header_with_surrounding_spaces(self) -> None:
        csv_text = " Serial Number ,macAddress\nABC123,11:22:33:44:55:66\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "serialNumber" in result.valid_rows[0]

    def test_unknown_column_preserved_as_trimmed_original(self) -> None:
        csv_text = "serialNumber,macAddress,  customField  \nABC123,11:22:33:44:55:66,custom_val\n"
        result = parse_csv(None, csv_text)
        assert result.error is None
        assert len(result.valid_rows) == 1
        assert "customField" in result.valid_rows[0]
