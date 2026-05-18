"""Boolean AST + canonical operator enum for ClearPass rule conditions.

Rules in ClearPass services / role-mapping policies / enforcement
policies carry a list of typed predicates plus a top-level
``match_type`` (``AND`` | ``OR``). The adapter converts that REST shape
into the ``raw_expression`` dict layout this module expects, then
``normalize()`` produces a canonical :data:`BooleanExpr` tree the flow
compiler can walk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum


class Op(StrEnum):
    """Canonical operator names used inside the Boolean AST.

    ClearPass returns operators as uppercase strings (``EQUALS``,
    ``MATCHES_REGEX``, ``MATCHES_ANY``, ...). :meth:`from_raw` maps them
    to these canonical values so downstream label / flow code only has
    to handle one spelling.
    """

    equals = "equals"
    not_equals = "not_equals"
    contains = "contains"
    not_contains = "not_contains"
    starts_with = "starts_with"
    ends_with = "ends_with"
    not_ends_with = "not_ends_with"
    regex = "regex"
    in_ = "in"
    matches_all = "matches_all"
    exists = "exists"
    not_exists = "not_exists"
    less_than = "less_than"
    less_than_or_equals = "less_than_or_equals"
    greater_than = "greater_than"
    greater_than_or_equals = "greater_than_or_equals"
    equals_ignore_case = "equals_ignore_case"
    not_equals_ignore_case = "not_equals_ignore_case"
    not_regex = "not_regex"
    belongs_to_group = "belongs_to_group"
    not_belongs_to_group = "not_belongs_to_group"
    not_starts_with = "not_starts_with"
    matches_exact = "matches_exact"
    not_matches_exact = "not_matches_exact"
    not_matches_all = "not_matches_all"
    not_matches_any = "not_matches_any"
    in_range = "in_range"

    @classmethod
    def from_raw(cls, raw: str) -> Op:
        """Map a ClearPass uppercase operator string to a canonical :class:`Op`."""
        mapping: dict[str, Op] = {
            "EQUALS": cls.equals,
            "NOT_EQUALS": cls.not_equals,
            "CONTAINS": cls.contains,
            "NOT_CONTAINS": cls.not_contains,
            "STARTS_WITH": cls.starts_with,
            "BEGINS_WITH": cls.starts_with,
            "ENDS_WITH": cls.ends_with,
            "NOT_ENDS_WITH": cls.not_ends_with,
            "REGEX_MATCH": cls.regex,
            "MATCHES_REGEX": cls.regex,
            "NOT_MATCHES_REGEX": cls.not_regex,
            "IN": cls.in_,
            # Per-predicate MATCHES_ANY means "attribute is member of set" → in
            "MATCHES_ANY": cls.in_,
            # Per-predicate MATCHES_ALL means "attribute must match all values"
            "MATCHES_ALL": cls.matches_all,
            "EXISTS": cls.exists,
            "NOT_EXISTS": cls.not_exists,
            "EQUALS_IGNORE_CASE": cls.equals_ignore_case,
            "LESS_THAN": cls.less_than,
            "LESS_THAN_OR_EQUALS": cls.less_than_or_equals,
            "GREATER_THAN": cls.greater_than,
            "GREATER_THAN_OR_EQUALS": cls.greater_than_or_equals,
            "BELONGS_TO_GROUP": cls.belongs_to_group,
            "BELONGS_TO": cls.belongs_to_group,
            "NOT_BELONGS_TO_GROUP": cls.not_belongs_to_group,
            "NOT_BELONGS_TO": cls.not_belongs_to_group,
            "NOT_BEGINS_WITH": cls.not_starts_with,
            "NOT_EQUALS_IGNORE_CASE": cls.not_equals_ignore_case,
            "MATCHES_EXACT": cls.matches_exact,
            "NOT_MATCHES_EXACT": cls.not_matches_exact,
            "NOT_MATCHES_ALL": cls.not_matches_all,
            "NOT_MATCHES_ANY": cls.not_matches_any,
            "IN_RANGE": cls.in_range,
        }
        upper = raw.upper()
        if upper not in mapping:
            raise ValueError(f"Unknown ClearPass operator: {raw!r}")
        return mapping[upper]


@dataclass
class Predicate:
    namespace: str
    attribute: str
    op: Op
    rhs_raw: str
    rhs_display: str
    raw_operator: str = ""


@dataclass
class And:
    operands: list[BooleanExpr] = field(default_factory=list)


@dataclass
class Or:
    operands: list[BooleanExpr] = field(default_factory=list)


@dataclass
class Not:
    operand: BooleanExpr


BooleanExpr = Predicate | And | Or | Not


def _normalize_predicate(raw_attr: dict) -> Predicate:
    return Predicate(
        namespace=raw_attr.get("type", ""),
        attribute=raw_attr.get("name", ""),
        op=Op.from_raw(raw_attr.get("operator", "EQUALS")),
        rhs_raw=raw_attr.get("value", ""),
        rhs_display=raw_attr.get("displayValue", ""),
        raw_operator=raw_attr.get("operator", ""),
    )


def normalize(raw_expression: dict | None) -> BooleanExpr | None:
    """Convert a raw expression dict into a canonical :data:`BooleanExpr`.

    Single-predicate wrappers are unwrapped to a bare :class:`Predicate`.
    Returns ``None`` if the expression is absent.

    Expected ``raw_expression`` shape::

        {
            "operator": "and" | "or",                # case-insensitive
            "displayOperator": "MATCHES_ALL" | "MATCHES_ANY",   # alternate signal
            "attributes": [
                {"type": ..., "name": ..., "operator": ..., "value": ..., "displayValue": ...},
                ...
            ],
        }
    """
    if raw_expression is None:
        return None

    operator = raw_expression.get("operator", "").lower()
    display_op = raw_expression.get("displayOperator", "").upper()
    attributes = raw_expression.get("attributes", [])

    use_and = operator in ("and",) or display_op in ("MATCHES_ALL",)
    use_or = operator in ("or",) or display_op in ("MATCHES_ANY",)

    predicates: list[BooleanExpr] = [_normalize_predicate(a) for a in attributes]

    if not predicates:
        return And(operands=[])

    if len(predicates) == 1:
        return predicates[0]

    if use_and:
        return And(operands=predicates)
    if use_or:
        return Or(operands=predicates)

    return And(operands=predicates)


def expr_to_label(expr: BooleanExpr | None, max_len: int = 60) -> str:
    """Render a single-line human-readable label for a :data:`BooleanExpr`."""
    if expr is None:
        return "(no condition)"

    def _render(e: BooleanExpr) -> str:
        if isinstance(e, Predicate):
            attr_short = e.attribute.split(":")[-1]
            rhs = e.rhs_display or e.rhs_raw
            return f"{attr_short} {e.op.value} {rhs!r}"
        if isinstance(e, And):
            return " AND ".join(_render(o) for o in e.operands)
        if isinstance(e, Or):
            return " OR ".join(_render(o) for o in e.operands)
        if isinstance(e, Not):
            return f"NOT ({_render(e.operand)})"
        return str(e)

    label = _render(expr)
    if len(label) > max_len:
        label = label[: max_len - 3] + "..."
    return label


_NUMERIC_CSV = re.compile(r"^\d+(?:,\d+)*$")
_INTERNAL_REF = re.compile(r"^[A-Za-z][A-Za-z0-9_]*:\d+(?:,[A-Za-z][A-Za-z0-9_]*:\d+)*$")


def expr_to_node_label(expr: BooleanExpr | None) -> str:
    """Render a multi-line label for a flowchart decision node.

    Each predicate becomes three lines (attribute / operator / value).
    Long values wrap at comma boundaries (suitable for AD DNs). AND/OR
    separators appear between predicates.
    """
    if expr is None:
        return "(no condition)"

    def _wrap_value(value: str, max_len: int = 35) -> str:
        if len(value) <= max_len:
            return value
        lines = []
        remaining = value
        while len(remaining) > max_len:
            break_at = remaining.rfind(",", 0, max_len)
            if break_at == -1:
                break_at = max_len
            else:
                break_at += 1  # include the comma
            lines.append(remaining[:break_at])
            remaining = remaining[break_at:].lstrip()
        if remaining:
            lines.append(remaining)
        return "\n".join(lines)

    def _pick_rhs(raw: str, display: str) -> str:
        """Prefer display when raw is a bare numeric ID, numeric CSV, or
        internal ClearPass reference token (e.g. ``NadGroup:3004``)."""
        raw_stripped = raw.strip()
        if display.strip() and (_NUMERIC_CSV.match(raw_stripped) or _INTERNAL_REF.match(raw_stripped)):
            return display.strip()
        return raw

    def _pred(e: Predicate) -> str:
        attr = f"{e.namespace}:{e.attribute}" if e.namespace else e.attribute
        op = e.raw_operator or e.op.value.upper()
        rhs = _wrap_value(_pick_rhs(e.rhs_raw, e.rhs_display))
        return f"{attr}\n{op}\n{rhs}"

    def _lines(e: BooleanExpr) -> list[str]:
        if isinstance(e, Predicate):
            return [_pred(e)]
        if isinstance(e, And):
            result: list[str] = []
            for i, operand in enumerate(e.operands):
                if i > 0:
                    result.append("--- AND ---")
                result.extend(_lines(operand))
            return result
        if isinstance(e, Or):
            result = []
            for i, operand in enumerate(e.operands):
                if i > 0:
                    result.append("--- OR ---")
                result.extend(_lines(operand))
            return result
        if isinstance(e, Not):
            return ["NOT"] + _lines(e.operand)
        return [str(e)]

    return "\n".join(_lines(expr))
