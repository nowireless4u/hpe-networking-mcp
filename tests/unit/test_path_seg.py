"""Pin tests for the shared URL path-segment escaper (#476).

Two layers:

- ``TestPathSeg`` pins the encoding contract for the hostile characters
  that motivated the helper (``/`` restructures the route, ``?`` starts
  the query, ``#`` truncates to the fragment).
- ``TestNoRawPathInterpolation`` is the creep guard: an AST scan of every
  platform tool module asserting that f-string path arguments to HTTP
  request calls only interpolate values wrapped in ``path_seg(...)``.
  Partial adoption is how the inconsistency returns (#476 scope note).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import httpx
import pytest

from hpe_networking_mcp.platforms._common.url import path_seg

pytestmark = pytest.mark.unit

PLATFORMS_DIR = Path(__file__).resolve().parents[2] / "src" / "hpe_networking_mcp" / "platforms"


class TestPathSeg:
    def test_slash_cannot_restructure_route(self):
        assert path_seg("jon/adams") == "jon%2Fadams"

    def test_question_mark_cannot_start_query(self):
        assert path_seg("page?x=1") == "page%3Fx%3D1"

    def test_hash_cannot_truncate_path(self):
        assert path_seg("Policy #2") == "Policy%20%232"

    def test_space_encodes(self):
        assert path_seg("Guest Admin") == "Guest%20Admin"

    def test_percent_is_escaped_not_trusted(self):
        """Pre-encoded input is raw text, not a passthrough."""
        assert path_seg("a%2Fb") == "a%252Fb"

    def test_non_string_values_coerced(self):
        assert path_seg(42) == "42"

    def test_plain_identifiers_unchanged(self):
        for value in ("5f1c-uuid-4711", "CORP-WIFI", "ssid_prof"):
            assert path_seg(value) == value

    def test_mac_colons_percent_encode(self):
        """``safe=""`` encodes colons too — RFC 3986 servers decode path
        segments, so ``%3A`` reaches the API as ``:`` exactly as before."""
        assert path_seg("aa:bb:cc:dd:ee:ff") == "aa%3Abb%3Acc%3Add%3Aee%3Aff"

    def test_encoded_segment_survives_httpx_normalization(self):
        """The wire path targets ONE segment even for hostile input."""
        url = httpx.URL("https://cppm.example.com/api/admin-user/user-id/" + path_seg("frag#2/x"))
        assert url.raw_path.decode() == "/api/admin-user/user-id/frag%232%2Fx"


# --- creep guard -----------------------------------------------------------
#
# Scans EVERY f-string in the platform tree (not just request-call arguments —
# paths assigned to variables before the call would dodge any call-shape
# anchor). An f-string is treated as a URL path when its literal text starts
# with "/" or matches a `name/vN` API prefix AND contains no spaces (prose —
# error messages, log lines, prompts — virtually always has spaces).

_PATH_LITERAL = re.compile(r"^(/|[a-z][a-z0-9-]*/v\d)")

# Interpolated names that legitimately hold multi-segment path fragments
# (joined from constants or earlier-built paths), not operator selectors.
_MULTI_SEGMENT_NAMES = {
    "api_path",
    "full_path",
    "path",
    "path_suffix",
    "base_path",
    "url",
    "base_url",
    "uri",
    "base",
    "prefix",
    "suffix",
}


def _is_path_seg_call(node: ast.expr) -> bool:
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Name) and node.func.id == "path_seg")
        or (isinstance(node.func, ast.Attribute) and node.func.attr == "path_seg")
    )


def _interpolates_path_fragment(value: ast.expr) -> bool:
    """True when the interpolated expression names a multi-segment fragment.

    Token-based so it matches ``api_base``, ``secrets.api_base_url.rstrip('/')``
    etc. without false-skipping selectors like ``database_id``.
    """
    tokens = set(re.split(r"[^a-z]+", ast.unparse(value).lower()))
    return bool(tokens & (_MULTI_SEGMENT_NAMES | {"url"}))


def _fstring_path_violations(fstring: ast.JoinedStr, filename: str) -> list[str]:
    literal = "".join(str(part.value) for part in fstring.values if isinstance(part, ast.Constant))
    # A URL path literal has no spaces (prose does) and at least one letter
    # (CIDR suffixes like "/32" and pure-separator compositions don't).
    if not _PATH_LITERAL.match(literal) or " " in literal or not re.search(r"[a-z]", literal):
        return []
    violations: list[str] = []
    in_query = False
    for part in fstring.values:
        if isinstance(part, ast.Constant) and "?" in str(part.value):
            in_query = True  # query-string portion — httpx params territory, out of scope
        if not isinstance(part, ast.FormattedValue) or in_query:
            continue
        value = part.value
        if _is_path_seg_call(value) or _interpolates_path_fragment(value):
            continue
        violations.append(f"{filename}:{part.lineno}: {ast.unparse(value)!r} interpolated without path_seg()")
    return violations


class TestNoRawPathInterpolation:
    def test_all_platform_path_interpolations_use_path_seg(self):
        violations: list[str] = []
        for py_file in sorted(PLATFORMS_DIR.rglob("*.py")):
            if "_template" in py_file.parts:
                continue
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.JoinedStr):
                    violations.extend(_fstring_path_violations(node, str(py_file.relative_to(PLATFORMS_DIR))))
        assert not violations, "Raw f-string path interpolation (wrap with path_seg):\n" + "\n".join(violations)
