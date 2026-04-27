"""Skill engine — loads markdown skill files at startup, exposes them via two tools.

A *skill* is a markdown file with YAML frontmatter sitting in this directory.
The frontmatter carries metadata (name / title / description / platforms /
tags / tools); the body is the runbook the AI follows. The engine indexes
all ``*.md`` files at server startup, parses frontmatter, and exposes:

- ``skills_list(platform=..., tag=...)`` — metadata-only browse
- ``skills_load(name)`` — full body, with case-insensitive substring fallback
  if no exact match is found

Skills are always visible (in every ``MCP_TOOL_MODE``) — they're an entry
point, not an implementation detail.

Closes #189.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from fastmcp import Context, FastMCP
from loguru import logger

# Skills are bundled inside the package so they ship in the Docker image.
_SKILLS_DIR = Path(__file__).parent

# Files that aren't skills (template, future engine docs, etc.).
_RESERVED_FILENAMES = frozenset({"TEMPLATE.md"})


@dataclass(frozen=True)
class Skill:
    """A loaded skill — frontmatter metadata plus markdown body."""

    name: str
    title: str
    description: str
    platforms: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    body: str = ""

    def to_metadata(self) -> dict[str, Any]:
        """Return cheap-to-send metadata (no body) for ``skills_list``."""
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "platforms": list(self.platforms),
            "tags": list(self.tags),
            "tools": list(self.tools),
        }


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    """Coerce a frontmatter list-or-None field to a tuple of strings."""
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(str(v) for v in value if v)
    return ()


def _parse_skill(path: Path) -> Skill | None:
    """Parse a single ``.md`` file into a ``Skill``, or ``None`` if malformed.

    Frontmatter form::

        ---
        name: my-skill
        title: My skill
        description: One-line summary
        ---
        # body...

    Bad frontmatter (missing required fields, YAML errors, name/filename
    mismatch) is logged and skipped — the server boots with the rest of the
    catalog rather than crashing on a single malformed file.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        logger.warning("Skill {!r}: missing YAML frontmatter — skipping", path.name)
        return None
    # Split on the second '---' separator. ``maxsplit=2`` gives us
    # ['', frontmatter_block, body].
    try:
        _, frontmatter_block, body = text.split("---", 2)
    except ValueError:
        logger.warning("Skill {!r}: malformed frontmatter delimiter — skipping", path.name)
        return None

    try:
        meta = yaml.safe_load(frontmatter_block) or {}
    except yaml.YAMLError as e:
        logger.warning("Skill {!r}: YAML parse error — {}", path.name, e)
        return None
    if not isinstance(meta, dict):
        logger.warning("Skill {!r}: frontmatter must be a YAML mapping — skipping", path.name)
        return None

    name = meta.get("name", "")
    if not name or not isinstance(name, str):
        logger.warning("Skill {!r}: missing or non-string `name` field — skipping", path.name)
        return None
    expected_name = path.stem
    if name != expected_name:
        logger.warning(
            "Skill {!r}: frontmatter name {!r} != filename stem {!r} — skipping",
            path.name,
            name,
            expected_name,
        )
        return None

    title = meta.get("title")
    description = meta.get("description")
    if not title or not isinstance(title, str):
        logger.warning("Skill {!r}: missing or non-string `title` — skipping", path.name)
        return None
    if not description or not isinstance(description, str):
        logger.warning("Skill {!r}: missing or non-string `description` — skipping", path.name)
        return None

    return Skill(
        name=name,
        title=title.strip(),
        description=description.strip(),
        platforms=_as_str_tuple(meta.get("platforms")),
        tags=_as_str_tuple(meta.get("tags")),
        tools=_as_str_tuple(meta.get("tools")),
        body=body.lstrip("\n"),
    )


def _coerce_filter(value: str | list[str] | None) -> set[str] | None:
    """Normalize a filter argument to a set of strings (or None for 'no filter')."""
    if value is None:
        return None
    if isinstance(value, str):
        return {value}
    return {str(v) for v in value}


class SkillRegistry:
    """In-memory skill index built once at server startup."""

    def __init__(self, skills: list[Skill]):
        self._by_name: dict[str, Skill] = {s.name: s for s in skills}

    @classmethod
    def from_directory(cls, directory: Path = _SKILLS_DIR) -> SkillRegistry:
        skills: list[Skill] = []
        for path in sorted(directory.glob("*.md")):
            if path.name in _RESERVED_FILENAMES:
                continue
            parsed = _parse_skill(path)
            if parsed is not None:
                skills.append(parsed)
        return cls(skills)

    def all(self) -> list[Skill]:
        return list(self._by_name.values())

    def filter(
        self,
        platform: str | list[str] | None = None,
        tag: str | list[str] | None = None,
    ) -> list[Skill]:
        wanted_platforms = _coerce_filter(platform)
        wanted_tags = _coerce_filter(tag)
        results = self.all()
        if wanted_platforms is not None:
            results = [s for s in results if any(p in wanted_platforms for p in s.platforms)]
        if wanted_tags is not None:
            results = [s for s in results if any(t in wanted_tags for t in s.tags)]
        return results

    def lookup(self, name: str) -> Skill | list[Skill] | None:
        """Return one ``Skill`` on exact match, a list on multiple substring
        matches, or ``None`` if nothing matches.

        Lookup is case-insensitive throughout. Exact match wins; substring
        fallback only fires when no exact match is found.
        """
        normalized = name.strip().lower()
        if not normalized:
            return None
        for skill in self._by_name.values():
            if skill.name.lower() == normalized:
                return skill
        candidates = [s for s in self._by_name.values() if normalized in s.name.lower()]
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            return candidates
        return None


def register(mcp: FastMCP) -> None:
    """Register ``skills_list`` and ``skills_load`` on the FastMCP server.

    Skills are always-visible (no ``dynamic_managed`` tag) so they appear
    as top-level tools in every ``MCP_TOOL_MODE``.
    """
    registry = SkillRegistry.from_directory()
    skill_count = len(registry.all())
    logger.info("Skills: registered {} skill(s)", skill_count)

    @mcp.tool(
        name="skills_list",
        description=(
            "List available skills (markdown-defined multi-step procedures). "
            "Returns metadata only; call `skills_load(name)` for the full runbook. "
            "Optional `platform` / `tag` filters each accept a string or list of "
            "strings and narrow the result to skills tagged accordingly."
        ),
    )
    async def skills_list(
        ctx: Context,
        platform: str | list[str] | None = None,
        tag: str | list[str] | None = None,
    ) -> dict[str, Any]:
        results = registry.filter(platform=platform, tag=tag)
        return {
            "count": len(results),
            "skills": [s.to_metadata() for s in results],
        }

    @mcp.tool(
        name="skills_load",
        description=(
            "Load a skill's full markdown body — a step-by-step runbook for a "
            "multi-step network operations procedure. Pass the skill `name` "
            "(from `skills_list`); a case-insensitive substring match is tried "
            "if there's no exact match."
        ),
    )
    async def skills_load(ctx: Context, name: str) -> dict[str, Any]:
        match = registry.lookup(name)
        if match is None:
            return {"error": (f"No skill matches {name!r}. Call `skills_list()` to see available skills.")}
        if isinstance(match, list):
            return {
                "error": (
                    f"Multiple skills match {name!r}: "
                    f"{', '.join(sorted(s.name for s in match))}. "
                    "Use a more specific name."
                )
            }
        return {
            "name": match.name,
            "title": match.title,
            "description": match.description,
            "platforms": list(match.platforms),
            "tags": list(match.tags),
            "tools": list(match.tools),
            "body": match.body,
        }
