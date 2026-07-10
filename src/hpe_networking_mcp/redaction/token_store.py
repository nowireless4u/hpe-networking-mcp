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

Keymaps are purged by an **idle-TTL sweep**: every ``get_or_create()``
first drops any session not accessed within ``session_ttl_seconds``
(default 1h), so a long-running server never accumulates plaintext
keymaps for dead sessions (issue #586). ``end_session()`` remains for an
explicit teardown signal, and a server restart clears everything. Saved
chat references to ``[[KIND:uuid]]`` from a purged session become
unresolvable on resurrection; the operator re-runs the workflow that
produced them.
"""

from __future__ import annotations

import asyncio
import time
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

    Three indices for O(1) lookup in every direction we need:

    * ``by_plaintext[(kind, plaintext)]`` -> entry, used during
      tokenization so the same plaintext value gets the same token
      every time within a session ("same value, same token" — the user
      requirement from the v2.3.0.10 design).
    * ``by_token[token_string]`` -> entry, used during detokenization
      when the AI passes a token back into a write tool.
    * ``by_plaintext_value[plaintext]`` -> entry, used by the walker's
      keymap-replay pass (issue #291) AND by ``Tokenizer.tokenize``
      kind-agnostic dedup (v3.0.1.12). When a plaintext that was
      previously allocated under one kind is later seen under a
      different kind (e.g. CoA secret reusing the RADIUS secret), the
      tokenizer returns the existing token rather than allocating a
      second one. Because tokenize() consults this index *before*
      allocating, the index is effectively single-writer per plaintext
      within a session; the "multiple kinds for the same plaintext"
      race condition is impossible in practice.
    """

    by_plaintext: dict[tuple[TokenKind, str], TokenEntry] = field(default_factory=dict)
    by_token: dict[str, TokenEntry] = field(default_factory=dict)
    by_plaintext_value: dict[str, TokenEntry] = field(default_factory=dict)

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

    Sessions are allocated lazily on first ``get_or_create()`` call and
    reaped by the idle-TTL sweep that runs at the start of every
    ``get_or_create()`` (``purge_expired``): any session not touched within
    ``session_ttl_seconds`` is dropped, bounding memory + plaintext-secret
    lifetime without a background task (issue #586). ``end_session()`` is
    also exposed for an explicit teardown caller.

    A soft cap (``max_entries_per_session``) prevents runaway memory.
    Cap-hit triggers a ``KeymapFullError``; the middleware logs the
    failure and returns the original value untokenized rather than
    erroring out the tool call. The cap is intentionally generous (10K
    by default — typical sessions tokenize hundreds of values).
    """

    def __init__(
        self,
        *,
        max_entries_per_session: int = 10_000,
        session_ttl_seconds: float | None = 3600.0,
    ) -> None:
        self._sessions: dict[str, SessionKeymap] = {}
        # Monotonic last-access timestamp per session, for the idle-TTL sweep.
        self._last_seen: dict[str, float] = {}
        self._max_entries_per_session = max_entries_per_session
        # Idle TTL for opportunistic purge of dead sessions. ``None`` disables
        # TTL cleanup (keymaps then live until process exit / explicit
        # end_session) — used by tests that want deterministic lifecycles.
        self._session_ttl_seconds = session_ttl_seconds

    @property
    def max_entries_per_session(self) -> int:
        return self._max_entries_per_session

    def get(self, session_id: str) -> SessionKeymap | None:
        """Return the keymap for ``session_id`` if one exists, else None.

        Touches the session's last-seen clock when found so an actively-read
        session is not reaped by the idle-TTL sweep.
        """
        keymap = self._sessions.get(session_id)
        if keymap is not None:
            self._last_seen[session_id] = time.monotonic()
        return keymap

    def get_or_create(self, session_id: str, *, now: float | None = None) -> SessionKeymap:
        """Return the keymap for ``session_id``, creating it lazily.

        Every call first opportunistically purges idle-expired sessions, so a
        long-running server bounds keymap memory (and the lifetime of the
        plaintext secrets held in it) without a background task or a FastMCP
        teardown hook (#586). ``now`` is injectable for deterministic tests.
        """
        now = time.monotonic() if now is None else now
        self.purge_expired(now=now)
        keymap = self._sessions.get(session_id)
        if keymap is None:
            keymap = SessionKeymap()
            self._sessions[session_id] = keymap
        self._last_seen[session_id] = now
        return keymap

    def purge_expired(self, *, now: float | None = None) -> int:
        """Drop keymaps idle longer than ``session_ttl_seconds``.

        Returns the total number of entries purged across reaped sessions.
        A no-op when TTL is disabled (``session_ttl_seconds is None``).
        """
        if self._session_ttl_seconds is None:
            return 0
        now = time.monotonic() if now is None else now
        cutoff = now - self._session_ttl_seconds
        stale = [sid for sid, seen in self._last_seen.items() if seen < cutoff]
        return sum(self.end_session(sid) for sid in stale)

    def end_session(self, session_id: str) -> int:
        """Purge ``session_id``'s keymap. Returns the number of entries dropped.

        Available for explicit FastMCP session teardown; the idle-TTL sweep in
        ``get_or_create`` is the always-on safety net for sessions that never
        signal a clean teardown.
        """
        self._last_seen.pop(session_id, None)
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
