"""CSV ingestion and validation utilities for greenlake_bulk_add_devices."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field

MANDATORY_COLUMNS: frozenset[str] = frozenset({"serialNumber", "macAddress"})

ALIASES: dict[str, str] = {
    # serialNumber
    "serialnumber": "serialNumber",
    "serial": "serialNumber",
    "sn": "serialNumber",
    # macAddress
    "macaddress": "macAddress",
    "mac": "macAddress",
    # partNumber
    "partnumber": "partNumber",
    "part": "partNumber",
    # subscriptionKey — normalize_header strips underscores so "sub_key" → "subkey"
    "subscriptionkey": "subscriptionKey",
    "subkey": "subscriptionKey",
    "subscription": "subscriptionKey",
    # serviceId
    "serviceid": "serviceId",
    "service": "serviceId",
    # Optional enrichment columns — must be in ALIASES so case variants
    # (Location, LOCATION, Tags, TAGS, Region, REGION) normalise correctly.
    "location": "location",
    "loc": "location",
    "tags": "tags",
    "tag": "tags",
    "region": "region",
    "reg": "region",
}


@dataclass
class ParseResult:
    valid_rows: list[dict] = field(default_factory=list)
    invalid_rows: list[dict] = field(default_factory=list)
    error: str | None = None


_MAC_STRIP_RE = re.compile(r"[:\-\.\s]")
_MAC_HEX_RE = re.compile(r"^[0-9a-f]{12}$")


def normalize_mac(raw: str) -> str | None:
    """Normalize a MAC address to lowercase colon-separated form.

    Accepts colon, hyphen, dot, or no-delimiter formats and any case:

    * ``94:FF:06:CA:4B:07``  →  ``94:ff:06:ca:4b:07``
    * ``94-FF-06-CA-4B-07``  →  ``94:ff:06:ca:4b:07``
    * ``94ff.06ca.4b07``     →  ``94:ff:06:ca:4b:07``
    * ``94FF06CA4B07``        →  ``94:ff:06:ca:4b:07``

    Returns the normalized string, or ``None`` if the input cannot be
    interpreted as a valid 48-bit MAC address.
    """
    stripped = _MAC_STRIP_RE.sub("", raw.strip()).lower()
    if not _MAC_HEX_RE.match(stripped):
        return None
    return ":".join(stripped[i : i + 2] for i in range(0, 12, 2))


def normalize_header(h: str) -> str:
    """Normalize a CSV header to a canonical lookup key.

    Strips surrounding whitespace, lowercases, then removes spaces,
    underscores, and hyphens so that 'Serial Number', 'serial_number',
    and 'serialnumber' all map to the same key.
    """
    return h.strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def resolve_headers(fieldnames: list[str]) -> dict[str, str]:
    """Map each raw CSV header to its canonical column name.

    Uses ALIASES for known synonyms; falls back to the stripped original
    header for unknown columns.
    """
    return {h: ALIASES.get(normalize_header(h), h.strip()) for h in fieldnames}


def validate_schema(canonical_names: set[str]) -> str | None:
    """Return an error string if any mandatory columns are absent, else None."""
    missing = MANDATORY_COLUMNS - canonical_names
    if missing:
        return f"Missing mandatory columns: {', '.join(sorted(missing))}. Found: {', '.join(sorted(canonical_names))}"
    return None


def _open_csv_source(csv_path: str | None, csv_text: str | None):
    """Return a file-like object for the CSV source.

    Opens a real file (BOM-safe via utf-8-sig) when csv_path is given;
    wraps csv_text in an io.StringIO otherwise.
    """
    if csv_path is not None:
        return open(csv_path, encoding="utf-8-sig", newline="")
    return io.StringIO(csv_text)


def validate_row(row: dict, row_num: int) -> str | None:
    """Validate mandatory fields and normalize serialNumber and macAddress in-place.

    Normalizes ``serialNumber`` to uppercase (GreenLake rejects lowercase serials).
    Normalizes ``macAddress`` to lowercase colon-separated form so the POST
    payload is consistent regardless of what delimiter the operator used in
    the CSV (colon, hyphen, dot, or bare hex).

    Args:
        row: Canonical row dict (keys already resolved via ``resolve_headers``).
             Modified in-place if normalization succeeds.
        row_num: 1-based row number for error messages.

    Returns:
        An error string if any field is missing or the MAC is malformed,
        ``None`` on success.
    """
    errors = []
    sn_raw = row.get("serialNumber", "").strip()
    if not sn_raw:
        errors.append("missing serialNumber")
    else:
        row["serialNumber"] = sn_raw.upper()  # GreenLake requires uppercase serial numbers
    mac_raw = row.get("macAddress", "").strip()
    if not mac_raw:
        errors.append("missing macAddress")
    else:
        normalized = normalize_mac(mac_raw)
        if normalized is None:
            errors.append(
                f"invalid macAddress {mac_raw!r} — expected 12 hex digits with "
                "optional colon, hyphen, or dot separators (e.g. aa:bb:cc:dd:ee:ff)"
            )
        else:
            row["macAddress"] = normalized  # normalize in-place for POST payload
    return f"Row {row_num}: {', '.join(errors)}" if errors else None


def parse_csv(csv_path: str | None, csv_text: str | None) -> ParseResult:
    """Parse and validate a CSV of devices.

    Exactly one of csv_path or csv_text must be supplied.

    Args:
        csv_path: Absolute or relative path to a UTF-8 (or UTF-8-BOM) CSV file.
        csv_text: Raw CSV content as a string (inline mode).

    Returns:
        ParseResult with valid_rows, invalid_rows, and error fields populated.

    Raises:
        ValueError: When neither or both sources are provided.
    """
    if csv_path is None and csv_text is None:
        raise ValueError("provide either csv_path or csv_text, not neither")
    if csv_path is not None and csv_text is not None:
        raise ValueError("provide csv_path OR csv_text, not both")

    source = _open_csv_source(csv_path, csv_text)
    try:
        reader = csv.DictReader(source)
        header_map = resolve_headers(list(reader.fieldnames or []))
        schema_error = validate_schema(set(header_map.values()))
        if schema_error:
            return ParseResult(error=schema_error)

        result = ParseResult()
        for row_num, row in enumerate(reader, start=2):
            canonical_row = {header_map[k]: v for k, v in row.items() if k is not None}
            err = validate_row(canonical_row, row_num)
            if err:
                result.invalid_rows.append(
                    {
                        "row_num": row_num,
                        "serial": canonical_row.get("serialNumber"),
                        "error": err,
                    }
                )
            else:
                result.valid_rows.append(canonical_row)
        return result
    finally:
        if hasattr(source, "close"):
            source.close()
