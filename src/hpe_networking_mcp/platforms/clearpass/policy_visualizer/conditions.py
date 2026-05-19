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


# ---------------------------------------------------------------------------
# Predicate evaluator (simulation engine)
# ---------------------------------------------------------------------------


# Attributes that ClearPass treats as multi-valued — when an operator passes
# a list for these, the predicate matches if ANY value in the list satisfies
# the condition. For a scalar value (string) we treat it as a single-element
# list, so callers can pass strings interchangeably for unambiguous attributes.
MULTI_VALUED_ATTRIBUTE_NAMES = frozenset({"Role"})


def _attribute_path(predicate: Predicate) -> str:
    """Return the canonical lookup key for a predicate's attribute.

    Example: ``Predicate(namespace='Tips', attribute='Role')`` →
    ``'Tips:Role'``. Matches the shape callers should use for keys in
    the ``simulated_attributes`` dict.
    """
    if predicate.namespace and predicate.attribute:
        return f"{predicate.namespace}:{predicate.attribute}"
    return predicate.attribute or predicate.namespace or ""


def _values_for(predicate: Predicate, context: dict[str, str | list[str]]) -> list[str] | None:
    """Look up the simulated value(s) for a predicate.

    Returns ``None`` if no value is provided (the simulation cannot
    evaluate this predicate — callers MUST treat ``None`` as
    "uncertain", never as a false match). Returns a list (possibly
    single-element) when a value is present.
    """
    key = _attribute_path(predicate)
    if key not in context:
        return None
    value = context[key]
    if isinstance(value, list):
        # Preserve empty list as a present-but-empty attribute (matters for
        # exists/not_exists). Callers can still pass `[]` to mean "this
        # attribute is known to have no values."
        return list(value)
    # Scalar — wrap so the multi-valued comparators have a uniform shape.
    return [value]


def _eval_predicate_against_value(op: Op, value: str, rhs: str) -> bool:
    """Apply a single Op to a single (value, rhs) pair.

    Pure boolean — returns True/False only. Callers handle the
    multi-value case (any-match for multi-valued attributes).
    """
    if op is Op.equals or op is Op.matches_exact:
        return value == rhs
    if op is Op.not_equals or op is Op.not_matches_exact:
        return value != rhs
    if op is Op.equals_ignore_case:
        return value.lower() == rhs.lower()
    if op is Op.not_equals_ignore_case:
        return value.lower() != rhs.lower()
    if op is Op.contains:
        return rhs in value
    if op is Op.not_contains:
        return rhs not in value
    if op is Op.starts_with:
        return value.startswith(rhs)
    if op is Op.not_starts_with:
        return not value.startswith(rhs)
    if op is Op.ends_with:
        return value.endswith(rhs)
    if op is Op.not_ends_with:
        return not value.endswith(rhs)
    if op is Op.regex:
        try:
            return re.search(rhs, value) is not None
        except re.error:
            return False
    if op is Op.not_regex:
        try:
            return re.search(rhs, value) is None
        except re.error:
            return False
    if op is Op.in_:
        # RHS is comma-separated list of allowed values
        allowed = {v.strip() for v in rhs.split(",")}
        return value in allowed
    if op is Op.matches_all:
        # MATCHES_ALL on a per-predicate basis with a single value is
        # effectively equality against each item in the comma-separated
        # rhs — we treat it as "value equals every item" which is only
        # true when rhs is a single item equal to value.
        items = [v.strip() for v in rhs.split(",")]
        return all(value == item for item in items)
    if op is Op.belongs_to_group:
        # No way to evaluate group membership without group data — return
        # False conservatively. Operators should supply explicit role
        # membership through `Tips:Role` instead of relying on group
        # lookups.
        return False
    if op is Op.not_belongs_to_group:
        return False
    if op is Op.less_than:
        return _numeric_compare(value, rhs, lambda a, b: a < b)
    if op is Op.less_than_or_equals:
        return _numeric_compare(value, rhs, lambda a, b: a <= b)
    if op is Op.greater_than:
        return _numeric_compare(value, rhs, lambda a, b: a > b)
    if op is Op.greater_than_or_equals:
        return _numeric_compare(value, rhs, lambda a, b: a >= b)
    if op is Op.in_range:
        # rhs is typically "start-end" — interpret leniently
        try:
            start, end = rhs.split("-", 1)
            return _numeric_compare(start.strip(), value, lambda a, b: a <= b) and _numeric_compare(
                value, end.strip(), lambda a, b: a <= b
            )
        except ValueError:
            return False
    # exists / not_exists are handled at the caller level (they don't need
    # the value, just the presence). If we get here for one, fail safe.
    if op is Op.exists:
        return True  # value was present to get here
    if op is Op.not_exists:
        return False
    return False


def _numeric_compare(a: str, b: str, cmp) -> bool:
    """Try numeric comparison, fall back to string. False on non-numeric coercion failure."""
    try:
        return cmp(float(a), float(b))
    except (ValueError, TypeError):
        try:
            return cmp(a, b)
        except TypeError:
            return False


def evaluate(expr: BooleanExpr | None, context: dict[str, str | list[str]]) -> bool | None:
    """Evaluate a :data:`BooleanExpr` against a simulated attribute context.

    Returns ``True`` / ``False`` / ``None`` (three-valued logic):

    - ``True``: condition is satisfied by the context.
    - ``False``: condition is contradicted by the context.
    - ``None``: at least one referenced attribute is missing from the
      context — the result is genuinely unknown.

    Callers MUST treat ``None`` as uncertainty and never present it as
    a confident outcome. This is load-bearing for correctness — the
    prior fake-simulator burned the operator by presenting unevaluable
    rules as confident DENYs.

    Boolean propagation:

    - ``And``: True if all True; False if any False; otherwise None.
    - ``Or``: True if any True; False if all False; otherwise None.
    - ``Not``: inverts True/False; passes through None.

    Multi-valued attribute semantics: when the context supplies a list
    for an attribute (e.g. ``Tips:Role`` with multiple assigned roles
    from evaluate-all role mapping), the predicate matches if ANY value
    in the list satisfies the condition. For ``not_*`` operators this
    means ALL values must satisfy the "not" — a stricter semantic that
    matches ClearPass behavior.
    """
    if expr is None:
        return True  # absent condition matches everything

    if isinstance(expr, Predicate):
        return _evaluate_predicate(expr, context)
    if isinstance(expr, And):
        return _eval_and([evaluate(o, context) for o in expr.operands])
    if isinstance(expr, Or):
        return _eval_or([evaluate(o, context) for o in expr.operands])
    if isinstance(expr, Not):
        inner = evaluate(expr.operand, context)
        return None if inner is None else not inner
    return None


def _evaluate_predicate(predicate: Predicate, context: dict[str, str | list[str]]) -> bool | None:
    """Evaluate a single predicate. Returns None when the attribute is unknown."""
    op = predicate.op
    # Exists / not_exists are special — they only need to know presence
    if op is Op.exists:
        return _attribute_path(predicate) in context
    if op is Op.not_exists:
        return _attribute_path(predicate) not in context

    values = _values_for(predicate, context)
    if values is None:
        return None  # unknown attribute

    rhs = predicate.rhs_display or predicate.rhs_raw

    # Multi-valued semantics:
    #   For positive ops (equals, contains, regex, ...): ANY match → True
    #   For negative ops (not_equals, not_contains, ...): ALL must hold → True
    is_negative_op = op.value.startswith("not_") or op is Op.not_regex

    if not values:
        # Empty list: positive ops cannot match (no value to satisfy them);
        # negative ops trivially hold (no value contradicts them).
        return is_negative_op

    per_value = [_eval_predicate_against_value(op, v, rhs) for v in values]
    if is_negative_op:
        return all(per_value)
    return any(per_value)


def _eval_and(results: list[bool | None]) -> bool | None:
    if any(r is False for r in results):
        return False
    if any(r is None for r in results):
        return None
    return True


def _eval_or(results: list[bool | None]) -> bool | None:
    if any(r is True for r in results):
        return True
    if any(r is None for r in results):
        return None
    return False


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


_OP_SHORT = {
    Op.equals: "=",
    Op.not_equals: "≠",
    Op.contains: "⊇",
    Op.not_contains: "⊉",
    Op.starts_with: "^=",
    Op.not_starts_with: "^≠",
    Op.ends_with: "$=",
    Op.not_ends_with: "$≠",
    Op.regex: "~=",
    Op.not_regex: "~≠",
    Op.in_: "∈",
    Op.matches_all: "≡",
    Op.exists: "∃",
    Op.not_exists: "∄",
    Op.less_than: "<",
    Op.less_than_or_equals: "≤",
    Op.greater_than: ">",
    Op.greater_than_or_equals: "≥",
}


def expr_to_compact_label(expr: BooleanExpr | None, max_len: int = 80) -> str:
    """Render a compact single-line label suitable for dense diagrams.

    Trades verbosity for legibility — drops the namespace prefix, uses
    short operator glyphs, and joins multi-predicate boolean wrappers
    inline with ``&`` / ``|``. Designed for Mermaid decision-diamond
    labels in policies with many rules where the multi-line
    :func:`expr_to_node_label` output collapses into an unreadable
    column.

    Examples::

        # Single predicate
        "Device Role ID = 21"
        # Two-predicate AND
        "Role = 'IoT Device' & Status = 'Active'"
        # Long values truncated
        "memberOf = 'CN=Tier-2-Wireless-Den...'"
    """
    if expr is None:
        return "(no condition)"

    def _trim_rhs(raw: str, display: str, budget: int) -> str:
        chosen = _pick_rhs_for_display(raw, display)
        if len(chosen) > budget:
            chosen = chosen[: max(1, budget - 3)] + "..."
        return chosen

    def _pred(e: Predicate, budget: int) -> str:
        attr = e.attribute or e.namespace or "?"
        op = _OP_SHORT.get(e.op, e.op.value)
        rhs = _trim_rhs(e.rhs_raw, e.rhs_display, max(8, budget - len(attr) - len(op) - 3))
        # Quote strings that aren't bare numerics / simple tokens
        if rhs and not rhs.isdigit() and not all(c.isalnum() or c in "._-" for c in rhs):
            rhs = f"'{rhs}'"
        return f"{attr} {op} {rhs}"

    def _render(e: BooleanExpr, budget: int) -> str:
        if isinstance(e, Predicate):
            return _pred(e, budget)
        if isinstance(e, And):
            parts = [_render(o, budget // max(1, len(e.operands))) for o in e.operands]
            return " & ".join(parts)
        if isinstance(e, Or):
            parts = [_render(o, budget // max(1, len(e.operands))) for o in e.operands]
            return " | ".join(parts)
        if isinstance(e, Not):
            return f"!({_render(e.operand, max(8, budget - 3))})"
        return str(e)

    label = _render(expr, max_len)
    if len(label) > max_len:
        label = label[: max_len - 3] + "..."
    return label


def _pick_rhs_for_display(raw: str, display: str) -> str:
    """Prefer ``displayValue`` when ``value`` is a bare numeric ID or
    internal reference token (e.g. ``NadGroup:3004``) — these would
    otherwise leak opaque IDs into the label.
    """
    raw_stripped = raw.strip()
    if display.strip() and (_NUMERIC_CSV.match(raw_stripped) or _INTERNAL_REF.match(raw_stripped)):
        return display.strip()
    return raw


def expr_to_node_label(expr: BooleanExpr | None) -> str:
    """Render a multi-line label for a flowchart decision node.

    Each predicate becomes three lines (attribute / operator / value).
    Long values wrap at comma boundaries (suitable for AD DNs). AND/OR
    separators appear between predicates.

    For dense diagrams where this verbosity makes the rendered output
    unreadable, prefer :func:`expr_to_compact_label`.
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

    def _pred(e: Predicate) -> str:
        attr = f"{e.namespace}:{e.attribute}" if e.namespace else e.attribute
        op = e.raw_operator or e.op.value.upper()
        rhs = _wrap_value(_pick_rhs_for_display(e.rhs_raw, e.rhs_display))
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
