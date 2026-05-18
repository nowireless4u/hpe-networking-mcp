"""Shared ID validation for UXI tool path parameters.

A single canonical source for ``_VALID_ID`` and ``_validate_id`` used by all
UXI write tools (and ``uxi_get_sensor_status``). Prevents the four-file
duplication that would allow the allowlist to silently diverge.
"""

from __future__ import annotations

import re

from fastmcp.exceptions import ToolError

_VALID_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def validate_id(value: str, label: str) -> None:
    """Raise ToolError if *value* is not a safe UXI resource ID.

    Enforces the allowlist ``^[A-Za-z0-9_-]{1,128}$`` to prevent path
    traversal when IDs are interpolated into URL paths (CR-01 / D-07).
    """
    if not _VALID_ID.match(value):
        raise ToolError({"status_code": 400, "message": f"Invalid {label}: {value!r}"})
