"""Shared, secret-safe summarization for error messages and logs.

Used by ``ValidationCatchMiddleware`` (#523/#534) and the elicitation
confirmation-prompt summary so model-visible error text AND debug logs never
echo raw secret-bearing or oversized validation inputs. One policy, one place —
the sensitive-key suffix list previously lived (duplicated) in
``middleware/elicitation.py``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

# Normalized suffixes whose VALUES are redacted. Keys are normalized
# (lowercased, non-alphanumerics stripped) before matching, so ``api_key`` /
# ``apiKey`` / ``api-key`` all redact; the suffix match catches compound names
# (``clientSecret``, ``radiusSharedSecret``). Over-redaction is acceptable;
# leaking is not.
_SENSITIVE_KEY_SUFFIXES: tuple[str, ...] = (
    "password",
    "secret",
    "token",
    "key",
    "psk",
    "passphrase",
    "community",
    "credential",
    "credentials",
)

REDACTED = "***redacted***"  # nosec B105 — redaction marker, not a credential

# Cap for a single rendered scalar value in error text / logs. Long inputs
# (huge payloads, base64 blobs) are elided so a validation failure can't dump
# an unbounded value into model-visible text or the logs.
_MAX_VALUE_LEN = 120


def is_sensitive_key(key: str) -> bool:
    """True when a (normalized) parameter key names secret material."""
    normalized = "".join(ch for ch in key.lower() if ch.isalnum())
    return any(normalized == suffix or normalized.endswith(suffix) for suffix in _SENSITIVE_KEY_SUFFIXES)


def safe_value_summary(value: Any, *, field_name: str | None = None, max_len: int = _MAX_VALUE_LEN) -> str:
    """Render a value compactly without leaking secrets or dumping huge blobs.

    - A sensitive ``field_name`` → ``REDACTED`` (regardless of value).
    - ``dict`` / list-like → a shape summary (type + size), never the contents.
    - Long scalars → capped with an elision marker.
    """
    if field_name is not None and is_sensitive_key(field_name):
        return REDACTED
    if isinstance(value, dict):
        return f"<dict: {len(value)} field(s)>"
    if isinstance(value, (list, tuple, set)):
        return f"<{type(value).__name__}: {len(value)} item(s)>"
    text = repr(value)
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text


def summarize_validation_errors(tool_name: str, errors: Sequence[Mapping[str, Any]]) -> str:
    """Build a readable, redacted validation-failure message.

    Shared by the model-visible response AND the debug log (#534) so the two
    can't diverge — neither echoes a raw secret-bearing or oversized rejected
    input. The rejected input is shown only via :func:`safe_value_summary`.
    """
    lines = [f"Error: validation failed for tool '{tool_name}':"]
    for err in errors:
        loc_parts = [str(x) for x in err.get("loc", [])]
        loc = ".".join(loc_parts)
        msg = err.get("msg", "invalid")
        err_input = err.get("input")
        if err_input is not None:
            field = loc_parts[-1] if loc_parts else None
            got = safe_value_summary(err_input, field_name=field)
            lines.append(f"  - {loc}: {msg} (got: {got})")
        else:
            lines.append(f"  - {loc}: {msg}")
    return "\n".join(lines)
