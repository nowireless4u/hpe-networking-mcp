"""MAC address normalization — always-on, regardless of tokenization toggle.

Every MAC the AI sees is rewritten to canonical ``aa:bb:cc:dd:ee:ff``
form (lowercase, colon-separated, six groups of two hex digits).
Reasons:

* Most universal in network-engineering tooling (Linux / macOS /
  Wireshark / ``arp`` / ``ip neigh`` all default to this form).
* Mist's API accepts colon-separated MACs in write paths.
* Lets the AI correlate the same physical NIC across audits without
  wondering whether ``aabb.ccdd.eeff`` and ``aa:bb:cc:dd:ee:ff`` are the
  same device.

Per the v2.3.0.10 design, MACs are explicitly **not tokenized** — they
are observable by anyone in radio range, so privacy-tokenizing them
would add cost (tokens in the AI context) without security gain. The
normalization step IS still useful for consistency.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# MAC format detection
# ---------------------------------------------------------------------------

# Accepts the four common MAC formats:
#   aa:bb:cc:dd:ee:ff  (colon-separated, lowercase or uppercase)
#   aa-bb-cc-dd-ee-ff  (hyphen-separated)
#   aabb.ccdd.eeff     (Cisco dot-separated)
#   aabbccddeeff       (no separators)
#
# Anchored with word boundaries so it doesn't match the middle of a UUID
# (UUIDs contain stretches of hex that could otherwise match
# ``aabbccddeeff``-style MACs as a substring).
_MAC_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})\b"),
    re.compile(r"\b([0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5})\b"),
    re.compile(r"\b([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})\b"),
    re.compile(r"\b([0-9a-fA-F]{12})\b"),
)


def is_mac_address(value: str) -> bool:
    """Return True if ``value`` is exactly a MAC address in any common format.

    The whole string must match — partial matches return False so we
    don't classify ``"aa:bb:cc:dd:ee:ff is offline"`` as a bare MAC.
    """
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    for pattern in _MAC_PATTERNS:
        match = pattern.fullmatch(stripped)
        if match:
            # Plain-12-hex needs an additional sanity check — guard against
            # matching a 12-character hex string that's actually part of a
            # serial number or random hash. We accept it as a MAC only when
            # the surrounding context (caller) thinks it should be one. The
            # walker calls this only on values from MAC-named fields, so
            # the additional check happens implicitly.
            return True
    return False


def canonicalize_mac(value: str) -> str:
    """Normalize ``value`` to canonical ``aa:bb:cc:dd:ee:ff`` form.

    If the value isn't a recognizable MAC, it is returned unchanged so
    callers can chain this safely.
    """
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    hex_only = "".join(c for c in stripped if c.isalnum())
    if len(hex_only) != 12 or not all(c in "0123456789abcdefABCDEF" for c in hex_only):
        return value
    lower = hex_only.lower()
    return ":".join(lower[i : i + 2] for i in range(0, 12, 2))


def normalize_macs_in_value(value: str) -> str:
    """Find every MAC inside ``value`` and rewrite it to canonical form.

    Used for free-text fields where a MAC might be embedded in a larger
    string like ``"client aa:bb:cc:dd:ee:ff failed auth"``. Only
    rewrites *the matched span*; surrounding text is preserved.

    The bare-12-hex pattern is intentionally NOT applied here because it
    has too many false positives in free text (any 12-char hex string in
    a description would get rewritten). The structured-field path
    (``canonicalize_mac``) handles bare-hex MACs because the caller
    already knows it's a MAC field.
    """
    if not isinstance(value, str) or not value:
        return value

    result = value
    # Apply the formats with explicit separators only — they have low
    # false-positive rates inside free text.
    for pattern in _MAC_PATTERNS[:3]:
        result = pattern.sub(lambda m: canonicalize_mac(m.group(1)), result)
    return result
