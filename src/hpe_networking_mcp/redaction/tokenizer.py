"""Bidirectional tokenize/detokenize against a session keymap.

The tokenizer operates on **single string values**. The walker
(``walker.py``) handles the recursive structure traversal; this module
just answers "what's the token for this string?" and "what's the
plaintext behind this token?".

Tokenization is idempotent: re-tokenizing an already-tokenized string
returns it unchanged. Detokenization on an unknown token returns None,
which the middleware uses to decide whether to error out the call.

Audit logging happens here too — every allocation logs ``kind`` +
``token`` + truncated ``value_hash`` (SHA-256 of the plaintext, first
16 hex chars) so an operator can verify "the same plaintext consistently
mapped to the same token" without ever seeing the plaintext column.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from loguru import logger

from hpe_networking_mcp.redaction.rules import TOKEN_RE, TokenKind
from hpe_networking_mcp.redaction.token_store import (
    KeymapFullError,
    SessionKeymap,
    TokenEntry,
    allocate_token,
)

if TYPE_CHECKING:
    pass


def _value_hash(plaintext: str) -> str:
    """Truncated SHA-256 of the plaintext for audit-log fingerprinting."""
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()[:16]


class Tokenizer:
    """Stateful tokenizer bound to one ``SessionKeymap``.

    The session keymap is a constructor argument so the walker can
    keep a single tokenizer instance for the duration of one tool call
    (avoids passing the keymap around as a separate parameter).

    Args:
        keymap: The per-session ``SessionKeymap``.
        session_id: For audit logging — keeps logs scoped per session.
        max_entries: Soft cap from ``TokenStore.max_entries_per_session``.
            Hitting the cap raises ``KeymapFullError`` once per call;
            subsequent calls in the same tool response return plaintext
            unchanged so the response still goes through.
    """

    def __init__(
        self,
        keymap: SessionKeymap,
        *,
        session_id: str,
        max_entries: int,
    ) -> None:
        self._keymap = keymap
        self._session_id = session_id
        self._max_entries = max_entries
        self._cap_hit_logged = False

    @property
    def keymap(self) -> SessionKeymap:
        return self._keymap

    def tokenize(self, kind: TokenKind, plaintext: str) -> str:
        """Return the token for ``(kind, plaintext)``, allocating if new.

        Idempotent on already-tokenized inputs: passing
        ``"[[PSK:550e8400-...]]"`` back in returns it unchanged (the
        regex match short-circuits).

        Raises ``KeymapFullError`` when the session has hit the soft cap
        on a *new* allocation. Existing tokens still round-trip even
        post-cap.
        """
        if not isinstance(plaintext, str) or not plaintext:
            return plaintext

        # Idempotency: don't double-tokenize a string that already is one.
        if TOKEN_RE.fullmatch(plaintext):
            return plaintext

        key = (kind, plaintext)
        existing = self._keymap.by_plaintext.get(key)
        if existing is not None:
            return existing.token

        # Need to allocate. Soft-cap check.
        if len(self._keymap) >= self._max_entries:
            if not self._cap_hit_logged:
                logger.warning(
                    "pii.cap_hit session={} entries={} max={} — "
                    "further values pass through untokenized for the rest of this call",
                    self._session_id[:12],
                    len(self._keymap),
                    self._max_entries,
                )
                self._cap_hit_logged = True
            raise KeymapFullError(f"Session keymap full ({len(self._keymap)}/{self._max_entries})")

        # Allocate a fresh token. UUID4 collisions are mathematically
        # near-impossible, but re-roll defensively.
        for _ in range(8):
            token = allocate_token(kind, plaintext)
            if token not in self._keymap.by_token:
                break
        else:  # pragma: no cover — collision in 8 UUID4 draws is statistically impossible
            raise RuntimeError("UUID4 collision in 8 attempts; entropy source compromised?")

        entry = TokenEntry(kind=kind, token=token, plaintext=plaintext)
        self._keymap.by_plaintext[key] = entry
        self._keymap.by_token[token] = entry

        logger.info(
            "pii.tokenize session={} kind={} token={} value_hash={} entries={}",
            self._session_id[:12],
            kind.value,
            token,
            _value_hash(plaintext),
            len(self._keymap),
        )
        return token

    def detokenize(self, token: str) -> str | None:
        """Return the plaintext for ``token``, or None if unknown.

        Logs the lookup attempt — successful detokenization is the
        critical audit event because that's when a real secret leaves
        the MCP container's memory and goes to a platform API.
        """
        entry = self._keymap.by_token.get(token)
        if entry is None:
            logger.warning(
                "pii.detokenize_unknown session={} token={}",
                self._session_id[:12],
                token,
            )
            return None
        return entry.plaintext


def tokenize_value(
    tokenizer: Tokenizer,
    kind: TokenKind,
    value: object,
) -> object:
    """Convenience wrapper: tokenize when ``value`` is a non-empty string.

    Returns the value unchanged for None / non-string / empty / already-token
    inputs. Used by the walker so it doesn't have to inline these guards
    at every call site.
    """
    if not isinstance(value, str) or not value:
        return value
    try:
        return tokenizer.tokenize(kind, value)
    except KeymapFullError:
        return value


def detokenize_string(tokenizer: Tokenizer, value: str) -> tuple[str, list[str]]:
    """Replace every ``[[KIND:uuid]]`` occurrence in ``value`` with plaintext.

    Returns ``(replaced_string, unknown_tokens)`` so the caller can
    distinguish between "fully detokenized" (empty list) and "model
    referenced a token from a different session" (non-empty list — the
    middleware should error the tool call rather than passing literal
    bracket text downstream).

    Idempotent on inputs that contain no tokens (returns unchanged with
    empty unknown list).
    """
    if not isinstance(value, str) or not value:
        return value, []

    unknown: list[str] = []

    def _sub(match: object) -> str:
        full = match.group(0)  # type: ignore[attr-defined]
        plaintext = tokenizer.detokenize(full)
        if plaintext is None:
            unknown.append(full)
            return full
        return plaintext

    replaced = TOKEN_RE.sub(_sub, value)
    return replaced, unknown
