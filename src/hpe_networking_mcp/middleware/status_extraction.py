"""Shared HTTP-status extraction for the middleware chain (#522).

``RetryMiddleware`` (transient-failure decisions) and
``ResponseEnvelopeMiddleware`` (the envelope's ``status`` field) must read a
status code out of a raw tool-result dict the SAME way, or their views of the
same response drift — e.g. an envelope reporting ``status: null`` for a payload
Retry already classified as a 503. One helper, one key set, one place.

Platforms surface the code under different keys:
``status_code`` (Mist / GreenLake), ``code`` (Central), ``status`` (ClearPass).
``http_status`` is accepted defensively.
"""

from __future__ import annotations

from typing import Any

# Keys checked, in priority order, for an integer HTTP status code.
_STATUS_KEYS: tuple[str, ...] = ("status_code", "code", "status", "http_status")


def extract_http_status(value: Any) -> int | None:
    """Return the HTTP status code from a tool-result dict, or ``None``.

    Only accepts an integer in the valid HTTP range (100–599) — a string
    ``status`` (e.g. ClearPass ``"forbidden"`` control payloads) is ignored
    here and handled by the envelope's blocked-state path instead.
    """
    if not isinstance(value, dict):
        return None
    for key in _STATUS_KEYS:
        candidate = value.get(key)
        if isinstance(candidate, int) and 100 <= candidate < 600:
            return candidate
    return None
