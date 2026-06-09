"""Unit tests for ``coerce_enum`` — the case-insensitive / alias folding applied to
Central read-tool enum filters (issues #455, #456, #457).

The helper builds a Pydantic ``BeforeValidator`` that folds recognized case / alias
variants onto a canonical ``Literal`` value, while leaving the ``Literal`` itself
(and thus the JSON-schema ``enum`` + the rejection of genuinely invalid values)
intact. These tests validate the exact ``(canonical, aliases)`` sets the three tools
use, through a ``TypeAdapter`` over the same ``Annotated[Literal[...], coerce_enum(...)]``
shape the tool signatures declare.
"""

from __future__ import annotations

from typing import Annotated, Literal

import pytest
from pydantic import TypeAdapter, ValidationError

from hpe_networking_mcp.platforms.central.utils import coerce_enum

pytestmark = pytest.mark.unit


# central_get_clients.status
_ClientStatus = TypeAdapter(Annotated[Literal["Connected", "Failed"] | None, coerce_enum(("Connected", "Failed"))])
# central_get_alerts.status (with the "open" -> "Active" synonym)
_AlertStatus = TypeAdapter(
    Annotated[
        Literal["Active", "Cleared", "Deferred"] | None,
        coerce_enum(("Active", "Cleared", "Deferred"), {"open": "Active"}),
    ]
)
# central_get_top_aps_by_usage.metric (with the "combined" -> "usage" alias)
_UsageMetric = TypeAdapter(
    Annotated[Literal["wireless", "wired", "usage"], coerce_enum(("wireless", "wired", "usage"), {"combined": "usage"})]
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Connected", "Connected"),  # exact
        ("CONNECTED", "Connected"),  # upper
        ("connected", "Connected"),  # lower
        ("cOnNeCtEd", "Connected"),  # mixed
        ("Failed", "Failed"),
        ("FAILED", "Failed"),
        (None, None),  # optional passthrough
    ],
)
def test_client_status_case_folding(raw: str | None, expected: str | None) -> None:
    assert _ClientStatus.validate_python(raw) == expected


def test_client_status_rejects_unknown() -> None:
    with pytest.raises(ValidationError):
        _ClientStatus.validate_python("Disconnected")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Active", "Active"),
        ("active", "Active"),
        ("Open", "Active"),  # synonym (#457)
        ("OPEN", "Active"),  # synonym, any case
        ("Cleared", "Cleared"),
        ("deferred", "Deferred"),
    ],
)
def test_alert_status_synonym_and_case(raw: str, expected: str) -> None:
    assert _AlertStatus.validate_python(raw) == expected


def test_alert_status_rejects_unknown() -> None:
    with pytest.raises(ValidationError):
        _AlertStatus.validate_python("Snoozed")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("usage", "usage"),
        ("combined", "usage"),  # alias (#455) — the doc word that used to be rejected
        ("COMBINED", "usage"),
        ("wireless", "wireless"),
        ("WIRED", "wired"),
    ],
)
def test_usage_metric_combined_alias(raw: str, expected: str) -> None:
    assert _UsageMetric.validate_python(raw) == expected


def test_usage_metric_rejects_unknown() -> None:
    with pytest.raises(ValidationError):
        _UsageMetric.validate_python("bandwidth")


def test_schema_enum_preserved() -> None:
    """The Literal's enum must remain in the JSON schema (discoverability intact)."""
    schema = _UsageMetric.json_schema()
    assert schema.get("enum") == ["wireless", "wired", "usage"], schema


def test_non_string_passthrough() -> None:
    """Non-string inputs are returned untouched (no spurious coercion)."""
    ta = TypeAdapter(Annotated[int | None, coerce_enum(("Active",))])
    assert ta.validate_python(5) == 5
    assert ta.validate_python(None) is None
