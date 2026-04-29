"""Recursive JSON walker — applies rules + tokenizer to tool responses.

Two top-level entry points:

* ``tokenize_response(structured_content, tokenizer)`` — walks the tool
  response tree and returns a NEW dict/list with sensitive values
  tokenized and MACs normalized. Idempotent: walking an already-walked
  structure is a no-op.

* ``detokenize_arguments(arguments, tokenizer)`` — walks the inbound
  tool argument tree and substitutes ``[[KIND:uuid]]`` references back
  to plaintext before the call hits the platform API. Returns
  ``(new_args, unknown_tokens)`` so the middleware can refuse the call
  if the model referenced a token that doesn't exist in the session
  keymap.

The walker never mutates inputs in place — every recursion returns a
new dict/list. This is intentional: tool responses can be referenced
elsewhere in FastMCP's pipeline, and silently editing them would
violate caller expectations.
"""

from __future__ import annotations

import ipaddress
from collections.abc import Iterable
from typing import TYPE_CHECKING

from hpe_networking_mcp.redaction.mac_normalizer import (
    canonicalize_mac,
    is_mac_address,
    normalize_macs_in_value,
)
from hpe_networking_mcp.redaction.rules import (
    EMAIL_RE,
    IPV4_RE,
    IPV6_RE,
    PEM_BLOCK_RE,
    PUBLIC_IP_ALLOWLIST,
    PUBLIC_IP_ALLOWLIST_RANGES,
    FieldClassification,
    TokenKind,
    classify_field,
)
from hpe_networking_mcp.redaction.tokenizer import (
    detokenize_string,
    tokenize_value,
)

if TYPE_CHECKING:
    from hpe_networking_mcp.redaction.tokenizer import Tokenizer


# Maximum recursion depth — defensive against pathologically nested input.
# Mist config payloads top out around 8 levels in practice; 32 gives us
# plenty of margin while still preventing stack-overflow on malformed input.
_MAX_DEPTH = 32

# Field names whose containing dict signals a MAC field — used to pull
# bare-12-hex MACs (no separators) out without false-positive risk.
_MAC_FIELD_HINTS: frozenset[str] = frozenset(
    {
        "mac",
        "device_mac",
        "client_mac",
        "ap_mac",
        "wired_mac",
        "bssid",
        "src_mac",
        "dst_mac",
        "switch_mac",
        "gateway_mac",
    }
)


def _is_public_allowlisted_ip(value: str) -> bool:
    """Return True when ``value`` is a well-known public IP we preserve."""
    if value in PUBLIC_IP_ALLOWLIST:
        return True
    try:
        addr = ipaddress.ip_address(value.split("/", 1)[0])
    except ValueError:
        return False
    return any(addr in ipaddress.ip_network(cidr) for cidr in PUBLIC_IP_ALLOWLIST_RANGES)


def _is_routable_ip(value: str) -> bool:
    """Return True when ``value`` parses as a valid IPv4/IPv6 address.

    The IP regex catches octet shapes that aren't valid IPs (e.g.
    ``999.999.999.999``); this guard runs ``ipaddress.ip_address()`` to
    confirm validity before tokenization.
    """
    try:
        ipaddress.ip_address(value.split("/", 1)[0])
        return True
    except ValueError:
        return False


def _scan_free_text(text: str, tokenizer: Tokenizer) -> str:
    """Apply the secret-pattern + identifier-pattern sweep over ``text``.

    Order matters: PEM blocks first (they contain colons that would
    otherwise match IPv6 patterns), then emails, then IPs (so we don't
    re-scan IPs that are inside PEM signatures), then MACs.
    """
    if not isinstance(text, str) or not text:
        return text

    result = text

    # Tier 1 — PEM blocks. Any PEM-shaped block in free text is treated
    # as a CERT regardless of the kind; we don't try to distinguish
    # certificate from private-key in description fields.
    def _pem_sub(match: object) -> str:
        block = match.group(0)  # type: ignore[attr-defined]
        kind = TokenKind.PRIVATE_KEY if "PRIVATE KEY" in block else TokenKind.CERT
        replacement = tokenize_value(tokenizer, kind, block)
        return replacement if isinstance(replacement, str) else block

    result = PEM_BLOCK_RE.sub(_pem_sub, result)

    # Tier 2 identifiers — email, IP, MAC
    def _email_sub(match: object) -> str:
        addr = match.group(0)  # type: ignore[attr-defined]
        replacement = tokenize_value(tokenizer, TokenKind.EMAIL, addr)
        return replacement if isinstance(replacement, str) else addr

    result = EMAIL_RE.sub(_email_sub, result)

    def _ipv4_sub(match: object) -> str:
        addr = match.group(0)  # type: ignore[attr-defined]
        if not _is_routable_ip(addr) or _is_public_allowlisted_ip(addr):
            return addr
        replacement = tokenize_value(tokenizer, TokenKind.IP, addr)
        return replacement if isinstance(replacement, str) else addr

    result = IPV4_RE.sub(_ipv4_sub, result)

    def _ipv6_sub(match: object) -> str:
        addr = match.group(0)  # type: ignore[attr-defined]
        if not _is_routable_ip(addr) or _is_public_allowlisted_ip(addr):
            return addr
        replacement = tokenize_value(tokenizer, TokenKind.IP, addr)
        return replacement if isinstance(replacement, str) else addr

    result = IPV6_RE.sub(_ipv6_sub, result)

    # MACs — normalize in place (no tokenization per the v2.3.0.10 design)
    result = normalize_macs_in_value(result)

    return result


def _walk_dict(
    data: dict,
    tokenizer: Tokenizer | None,
    *,
    depth: int,
) -> dict:
    """Recursively walk a dict, applying classification rules to each pair.

    ``tokenizer`` is None when only MAC normalization is requested
    (tokenization disabled). In that mode the walker still recurses to
    apply MAC normalization but skips all tokenization paths.
    """
    if depth > _MAX_DEPTH:
        return data

    parent_keys = frozenset(data.keys()) if isinstance(data, dict) else frozenset()
    out: dict = {}

    for key, value in data.items():
        new_value = _walk_pair(
            key,
            value,
            tokenizer,
            depth=depth,
            parent_keys=parent_keys,
        )
        out[key] = new_value
    return out


def _walk_pair(
    key: object,
    value: object,
    tokenizer: Tokenizer | None,
    *,
    depth: int,
    parent_keys: frozenset[str],
) -> object:
    """Apply classification + recursion to one key/value pair."""
    # Recursion into nested structures comes first
    if isinstance(value, dict):
        return _walk_dict(value, tokenizer, depth=depth + 1)
    if isinstance(value, list):
        return _walk_list(key, value, tokenizer, depth=depth + 1, parent_keys=parent_keys)

    # MAC normalization — always-on regardless of tokenizer presence
    field_name_lower = str(key).lower() if isinstance(key, str) else ""
    if field_name_lower in _MAC_FIELD_HINTS and isinstance(value, str) and is_mac_address(value):
        value = canonicalize_mac(value)

    # Tokenization — only when a tokenizer was passed
    if tokenizer is None or not isinstance(key, str):
        return value

    classification, kind = classify_field(key, value, parent_keys=parent_keys)

    if classification == FieldClassification.SKIP:
        return value
    if classification == FieldClassification.TOKENIZE_SECRET and kind is not None:
        return tokenize_value(tokenizer, kind, value)
    if classification == FieldClassification.TOKENIZE_IDENTIFIER and kind is not None:
        # IPs need allowlist + validity check before tokenization
        if (
            kind == TokenKind.IP
            and isinstance(value, str)
            and (not _is_routable_ip(value) or _is_public_allowlisted_ip(value))
        ):
            return value
        return tokenize_value(tokenizer, kind, value)
    if classification == FieldClassification.SCAN_FREE_TEXT and isinstance(value, str):
        return _scan_free_text(value, tokenizer)

    return value


def _walk_list(
    parent_key: object,
    data: list,
    tokenizer: Tokenizer | None,
    *,
    depth: int,
    parent_keys: frozenset[str],
) -> list:
    """Recursively walk a list. Lists inherit the parent's field name for
    classification purposes — e.g. ``ip_addresses: ["10.1.1.1", "10.1.1.2"]``
    each element is treated as if it were under ``ip_addresses``.
    """
    if depth > _MAX_DEPTH:
        return data

    out: list = []
    for item in data:
        if isinstance(item, dict):
            out.append(_walk_dict(item, tokenizer, depth=depth + 1))
        elif isinstance(item, list):
            out.append(_walk_list(parent_key, item, tokenizer, depth=depth + 1, parent_keys=parent_keys))
        else:
            # Apply the parent key's classification to the list element
            out.append(
                _walk_pair(
                    parent_key,
                    item,
                    tokenizer,
                    depth=depth,
                    parent_keys=parent_keys,
                )
            )
    return out


def tokenize_response(
    data: object,
    tokenizer: Tokenizer | None,
) -> object:
    """Return a new structure with PII tokenized and MACs normalized.

    Pass ``tokenizer=None`` to apply MAC normalization only — useful in
    the default configuration where ``ENABLE_PII_TOKENIZATION=false``
    but normalization is still on.

    Idempotent: walking already-tokenized output produces the same
    output.
    """
    if isinstance(data, dict):
        return _walk_dict(data, tokenizer, depth=0)
    if isinstance(data, list):
        return _walk_list("", data, tokenizer, depth=0, parent_keys=frozenset())
    return data


def _detokenize_walk(
    data: object,
    tokenizer: Tokenizer,
    unknown: list[str],
    *,
    depth: int,
) -> object:
    """Recursive helper for detokenizing inbound arguments."""
    if depth > _MAX_DEPTH:
        return data

    if isinstance(data, dict):
        return {key: _detokenize_walk(value, tokenizer, unknown, depth=depth + 1) for key, value in data.items()}
    if isinstance(data, list):
        return [_detokenize_walk(item, tokenizer, unknown, depth=depth + 1) for item in data]
    if isinstance(data, str):
        replaced, missing = detokenize_string(tokenizer, data)
        unknown.extend(missing)
        return replaced
    return data


def detokenize_arguments(
    arguments: dict | None,
    tokenizer: Tokenizer,
) -> tuple[dict, list[str]]:
    """Replace token references in inbound arguments with plaintext.

    Returns ``(new_arguments, unknown_tokens)``. The middleware checks
    ``unknown_tokens`` and refuses the call (returns a JSON-RPC error)
    if it is non-empty — passing literal ``[[KIND:uuid]]`` strings to a
    platform API would be confusing at best and silently accept them as
    real values at worst.
    """
    if not arguments:
        return arguments or {}, []

    unknown: list[str] = []
    new_args = _detokenize_walk(arguments, tokenizer, unknown, depth=0)
    if not isinstance(new_args, dict):  # pragma: no cover — arguments always a dict
        return arguments, []
    return new_args, unknown


def iter_kinds_in_string(value: str) -> Iterable[str]:
    """Yield every ``KIND`` string in ``value`` — used by audit tooling.

    Returns the bare kind names (e.g. ``"PSK"``), one per token
    occurrence, in order. Useful for "the AI passed N tokens, of these
    kinds" telemetry without revealing the token IDs themselves.
    """
    from hpe_networking_mcp.redaction.rules import TOKEN_RE  # local to avoid cycle

    if not isinstance(value, str):
        return
    for match in TOKEN_RE.finditer(value):
        yield match.group(1)
