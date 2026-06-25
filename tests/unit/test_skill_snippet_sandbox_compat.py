"""Regression test: shipped skill snippets must be runnable inside the
MCP code-mode sandbox.

The sandbox uses ``pydantic-monty`` for its Python parser, which rejects
several constructs that are valid Python 3 but not yet implemented in
the sandbox grammar. Skill snippets that hit any of these constructs
fail at runtime with a sandbox error, breaking the skill silently.

The blocking incident: ``central-scope-walker.md`` shipped a recursive
generator using ``yield`` / ``yield from``; the sandbox returned
``NotImplementedError: The monty syntax parser does not yet support yield
expressions``. Reported by Zach via ChatGPT regression testing of v3.0.1.9.

This test scans every shipped skill markdown under ``src/.../skills/``,
extracts ``python`` fenced code blocks, and rejects any that contain
patterns the sandbox can't run. Patterns are documented per-rule below
with the runtime error they produce.

Adding new forbidden patterns: extend ``_FORBIDDEN_PATTERNS`` with the
regex AND a human-readable message that references the upstream sandbox
limitation. Keep the message specific so authors know what to substitute.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# (regex_pattern, short_name, human-readable explanation)
_FORBIDDEN_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (
        # Bare 'yield' or 'yield from' on its own statement / expression.
        # Matches "yield ", "yield\n", "yield(", "yield from ".
        re.compile(r"\byield(?:\s+from)?\b"),
        "yield",
        "The monty sandbox parser does not support `yield` / `yield from` "
        "(reported in #289 and again in v3.0.1.9 regression testing). "
        "Rewrite the snippet to use an explicit stack/list loop and `return`.",
    ),
    (
        # `async def run()` (or any async def) inside execute() creates an
        # unawaited coroutine — the sandbox's `execute()` is already async,
        # so wrapping is a footgun. Documented in INSTRUCTIONS.md as of v3.0.1.5.
        re.compile(r"\basync\s+def\b"),
        "async def",
        "`execute()` already runs in an async context; wrapping in "
        "`async def run(): ...` creates an unawaited coroutine and the AI "
        "fabricates output because no real data came back. Inline the "
        "code at the top level inside execute() instead.",
    ),
    (
        # `import hashlib` (and a couple of other stdlib modules confirmed
        # blocked by the sandbox in Zach's continued report). Add as encountered.
        re.compile(r"^\s*import\s+hashlib\b", re.MULTILINE),
        "import hashlib",
        "The sandbox blocks `import hashlib` (verified in Zach's continued "
        "OpenClaw + Qwen3 4B test report). If a skill needs hashing, accept "
        "a pre-computed digest as an input parameter instead.",
    ),
    (
        # Internal-module imports. The sandbox blocks imports of the
        # hpe_networking_mcp package — that's the whole reason
        # central_translation_preview exists as a bridge tool. Catch
        # any direct imports in skill snippets.
        re.compile(r"^\s*(?:import|from)\s+hpe_networking_mcp\b", re.MULTILINE),
        "import hpe_networking_mcp",
        "Skill snippets cannot `import hpe_networking_mcp.*` — the "
        "sandbox blocks internal-module imports. Use platform tools via "
        "`await call_tool(name, params)` instead.",
    ),
    (
        # OS-access functions explicitly listed as blocked in
        # `server.py:execute_description`. These are the most-cited offenders.
        # NOTE: `datetime.now()` is NOT banned — the clock-enabled sandbox
        # provider (code_sandbox.py) makes it work. `datetime.utcnow()` and
        # `time.time()` stay banned (monty has no utcnow / no time module).
        re.compile(r"\b(?:datetime\.utcnow|time\.time|os\.environ|subprocess\b|asyncio\.gather)\b"),
        "OS-access / asyncio.gather",
        "The sandbox blocks `datetime.utcnow()`, `time.time()`, `os.environ`, "
        "`subprocess`, and `asyncio.gather()`. Use `datetime.now(datetime.timezone.utc)` "
        "for UTC and `datetime.now().timestamp()` for epoch; use sequential "
        "`await` calls for parallelism.",
    ),
]

_SKILLS_DIR = Path(__file__).resolve().parents[2] / "src" / "hpe_networking_mcp" / "skills"


_COMMENT_RE = re.compile(r"#[^\n]*")


def _strip_comments(code: str) -> str:
    """Replace Python `#` comments with whitespace of the same length.

    Preserves line offsets (so violation line numbers stay accurate) while
    removing comment text from the regex search surface. Without this, a
    rationale-comment like ``# sandbox parser rejects yield`` would fire
    the ``yield`` rule even though the executable code is fine.

    Naive (doesn't handle ``#`` inside strings) but safe for shipped skill
    snippets — they don't embed ``#`` in strings.
    """
    return _COMMENT_RE.sub(lambda m: " " * len(m.group(0)), code)


def _extract_python_blocks(markdown: str) -> list[tuple[int, str]]:
    """Return [(starting_line, code), ...] for every ```python``` block.

    Markdown fenced code blocks use ``` ``` ``` with optional language.
    We only check blocks tagged ``python`` (case-insensitive) — JSON / shell /
    other languages have different rules.
    """
    blocks: list[tuple[int, str]] = []
    lines = markdown.splitlines()
    in_block = False
    block_start = 0
    block_lines: list[str] = []
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not in_block:
            if stripped.startswith("```") and stripped.lower().lstrip("`").strip() == "python":
                in_block = True
                block_start = i
                block_lines = []
        else:
            if stripped.startswith("```"):
                blocks.append((block_start, "\n".join(block_lines)))
                in_block = False
            else:
                block_lines.append(line)
    return blocks


def _shipped_skill_paths() -> list[Path]:
    """All shipped skill markdown files except the TEMPLATE."""
    if not _SKILLS_DIR.is_dir():
        return []
    return sorted(p for p in _SKILLS_DIR.glob("*.md") if p.name != "TEMPLATE.md")


@pytest.mark.unit
@pytest.mark.parametrize(
    "skill_path",
    _shipped_skill_paths(),
    ids=lambda p: p.name,
)
def test_skill_python_snippets_are_sandbox_compatible(skill_path: Path) -> None:
    """Every ```python``` code block in a shipped skill must be runnable
    inside the MCP code-mode sandbox.

    Catches sandbox-rejected constructs at CI time so they don't ship to
    operators (and to AI clients running the skill blind).
    """
    text = skill_path.read_text()
    blocks = _extract_python_blocks(text)

    violations: list[str] = []
    for start_line, code in blocks:
        scan_target = _strip_comments(code)
        for pattern, short_name, explanation in _FORBIDDEN_PATTERNS:
            for match in pattern.finditer(scan_target):
                # Compute approximate line number within the file.
                offset_lines = scan_target[: match.start()].count("\n")
                file_line = start_line + offset_lines
                violations.append(f"{skill_path.name}:{file_line}: forbidden pattern {short_name!r} — {explanation}")

    assert violations == [], f"Skill {skill_path.name} contains sandbox-incompatible Python:\n  - " + "\n  - ".join(
        violations
    )


@pytest.mark.unit
def test_extractor_handles_skills_directory_present() -> None:
    """Sanity check: the skills directory exists and contains markdown files."""
    paths = _shipped_skill_paths()
    assert paths, f"No skill markdown files found under {_SKILLS_DIR}"
    # Ensure the lint actually ran across at least one block somewhere — if
    # all skills lack python blocks the test would silently pass.
    total_blocks = sum(len(_extract_python_blocks(p.read_text())) for p in paths)
    assert total_blocks > 0, "No python code blocks found in any shipped skill"
