"""Per-session token keymap — sensitive process memory, never persisted.

The store lives on the FastMCP lifespan context as
``ctx.lifespan_context["token_store"]``. Each MCP session
(``Mcp-Session-Id``) gets its own ``SessionKeymap``, holding the
plaintext-to-token and token-to-plaintext mappings for that session.

Storage is in-memory only by design. Persisting plaintext secrets to
disk would dramatically expand blast radius — a stolen volume becomes
a stolen master keymap. The current trust boundary matches the
container's existing credential exposure (Mist API token, Central
client secret, etc. are already in process memory).

When the FastMCP session ends — explicit ``DELETE /mcp`` from the
client, idle timeout, or server restart — the keymap is purged. Saved
chat references to ``[[KIND:uuid]]`` from a dead session become
unresolvable on resurrection; the operator re-runs the workflow that
produced them.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field

from hpe_networking_mcp.redaction.rules import TokenKind


@dataclass(frozen=True)
class TokenEntry:
    """One token <-> plaintext mapping.

    Frozen so callers can't mutate the plaintext column accidentally.
    The plaintext is sensitive — never log this dataclass directly;
    the audit log uses ``kind`` + ``token`` only.
    """

    kind: TokenKind
    token: str  # rendered form: "[[KIND:uuid]]"
    plaintext: str


@dataclass
class SessionKeymap:
    """The bidirectional token map for one MCP session.

    Two indices for O(1) lookup in both directions:

    * ``by_plaintext[(kind, plaintext)]`` -> entry, used during
      tokenization so the same plaintext value gets the same token
      every time within a session ("same value, same token" — the user
      requirement from the v2.3.0.10 design).
    * ``by_token[token_string]`` -> entry, used during detokenization
      when the AI passes a token back into a write tool.
    """

    by_plaintext: dict[tuple[TokenKind, str], TokenEntry] = field(default_factory=dict)
    by_token: dict[str, TokenEntry] = field(default_factory=dict)

    # An asyncio lock per session — defensive against future code paths
    # that introduce an ``await`` mid-allocation. Today the operations
    # are all pure dict ops with no awaits, so they're atomic under
    # asyncio's cooperative scheduling. Belt and suspenders.
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False, compare=False)

    def __len__(self) -> int:
        return len(self.by_token)

    def kind_counts(self) -> dict[TokenKind, int]:
        """Return per-kind counts of entries — used by the audit tool to
        report coverage without revealing values.
        """
        counts: dict[TokenKind, int] = {}
        for entry in self.by_token.values():
            counts[entry.kind] = counts.get(entry.kind, 0) + 1
        return counts


class TokenStore:
    """Top-level, multi-session keymap.

    Sessions are allocated lazily on first ``get_or_create()`` call;
    explicit ``end_session()`` is called when FastMCP signals session
    teardown (or by the middleware when an InitializeRequest arrives
    with no prior session — a fresh client connection should never see
    stale keymap state).

    A soft cap (``max_entries_per_session``) prevents runaway memory.
    Cap-hit triggers a ``KeymapFullError``; the middleware logs the
    failure and returns the original value untokenized rather than
    erroring out the tool call. The cap is intentionally generous (10K
    by default — typical sessions tokenize hundreds of values).
    """

    def __init__(self, *, max_entries_per_session: int = 10_000) -> None:
        self._sessions: dict[str, SessionKeymap] = {}
        self._max_entries_per_session = max_entries_per_session

    @property
    def max_entries_per_session(self) -> int:
        return self._max_entries_per_session

    def get(self, session_id: str) -> SessionKeymap | None:
        """Return the keymap for ``session_id`` if one exists, else None."""
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: str) -> SessionKeymap:
        """Return the keymap for ``session_id``, creating it lazily."""
        keymap = self._sessions.get(session_id)
        if keymap is None:
            keymap = SessionKeymap()
            self._sessions[session_id] = keymap
        return keymap

    def end_session(self, session_id: str) -> int:
        """Purge ``session_id``'s keymap. Returns the number of entries dropped."""
        keymap = self._sessions.pop(session_id, None)
        return len(keymap) if keymap else 0

    def session_count(self) -> int:
        return len(self._sessions)

    def total_entries(self) -> int:
        return sum(len(km) for km in self._sessions.values())


class KeymapFullError(RuntimeError):
    """Raised when a session has hit ``max_entries_per_session``."""


def allocate_token(kind: TokenKind, plaintext: str) -> str:
    """Build a fresh ``[[KIND:uuid]]`` token. Pure function, no state.

    The keymap caller is responsible for collision detection (UUID4
    collisions are mathematically near-impossible at session scale, but
    the keymap re-rolls if the freshly generated UUID happens to
    already be in use — belt and suspenders).
    """
    return f"[[{kind.value}:{uuid.uuid4()}]]"
