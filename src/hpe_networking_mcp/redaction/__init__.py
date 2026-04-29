"""PII tokenization and MAC normalization for tool responses.

This package implements the response-side data protection layer described
in the v2.3.0.10 design discussion:

* **MAC normalization** — always-on. Every MAC address in a tool response
  is rewritten to canonical ``aa:bb:cc:dd:ee:ff`` form (lowercase,
  colon-separated) regardless of the upstream platform's preferred
  format, so the AI sees a single consistent representation across
  Mist / Central / etc.

* **PII tokenization** — opt-in via ``ENABLE_PII_TOKENIZATION=true``.
  Sensitive fields (PSKs, RADIUS secrets, certificates) and identifiers
  (platform UUIDs, hostnames, user identifiers, geographic data) are
  replaced with session-stable ``[[KIND:uuid]]`` tokens before reaching
  the AI. Tokens round-trip: when the AI passes a token into a write
  tool, the inbound side substitutes the real value back before the API
  call. The mapping is held in process memory keyed by Mcp-Session-Id;
  it never touches disk and dies with the process or session.

The middleware (`hpe_networking_mcp.middleware.pii_tokenization`) is the
single integration point — everything else here is pure functions that
the middleware composes.
"""

from hpe_networking_mcp.redaction.mac_normalizer import (
    canonicalize_mac,
    is_mac_address,
    normalize_macs_in_value,
)
from hpe_networking_mcp.redaction.rules import (
    SECRET_FIELD_NAMES,
    TOKENIZED_IDENTIFIER_FIELDS,
    TokenKind,
    classify_field,
)
from hpe_networking_mcp.redaction.token_store import (
    SessionKeymap,
    TokenEntry,
    TokenStore,
)
from hpe_networking_mcp.redaction.tokenizer import (
    Tokenizer,
    detokenize_string,
    tokenize_value,
)
from hpe_networking_mcp.redaction.walker import (
    detokenize_arguments,
    tokenize_response,
)

__all__ = [
    "SECRET_FIELD_NAMES",
    "TOKENIZED_IDENTIFIER_FIELDS",
    "SessionKeymap",
    "TokenEntry",
    "TokenKind",
    "TokenStore",
    "Tokenizer",
    "canonicalize_mac",
    "classify_field",
    "detokenize_arguments",
    "detokenize_string",
    "is_mac_address",
    "normalize_macs_in_value",
    "tokenize_response",
    "tokenize_value",
]
