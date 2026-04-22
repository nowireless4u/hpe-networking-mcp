"""Pydantic models and input-normalization helpers for Apstra write tools.

The source apstra_core.py relied on four string/JSON coercion helpers
(normalize_boolean, normalize_to_string_list, normalize_to_int_list,
normalize_to_nested_list) to accept flexible input shapes from MCP clients.
These survive here as internal utilities, invoked from Pydantic validators
so the tool-level API remains permissive while the rest of the codebase
works with canonical typed values.
"""

from __future__ import annotations

import json
from typing import Any, Literal


def parse_bool(value: Any) -> bool | None:
    """Coerce MCP-client values (including ``"true"``/``"false"``) to ``bool``."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    if isinstance(value, int):
        return bool(value)
    raise ValueError(f"Cannot coerce {value!r} to bool")


def normalize_to_string_list(value: Any) -> list[str] | None:
    """Accept a string, JSON-array string, or list; return a list[str] or None."""
    if value is None or value == "":
        return None
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON array: {value}") from e
            if not isinstance(parsed, list):
                raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")
            return [str(v) for v in parsed]
        return [stripped]
    raise ValueError(f"Unsupported type for string list: {type(value).__name__}")


def normalize_to_int_list(value: Any, target_length: int) -> list[int] | None:
    """Accept int, string, JSON-array string, or list; return list[int] of length ``target_length``."""
    if value is None or value == "":
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return [value] * target_length
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON integer array: {value}") from e
            return [int(v) for v in parsed]
        try:
            return [int(stripped)] * target_length
        except ValueError as e:
            raise ValueError(f"Invalid integer: {value}") from e
    if isinstance(value, list):
        return [int(v) for v in value]
    raise ValueError(f"Unsupported type for int list: {type(value).__name__}")


def normalize_to_nested_list(value: Any, target_length: int) -> list[list[str]]:
    """Accept None, string, JSON-array string, flat list, or nested list; return list[list[str]]."""
    if value is None or value == "":
        return [[] for _ in range(target_length)]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON for nested list: {value}") from e
            if isinstance(parsed, list) and all(isinstance(item, list) for item in parsed):
                return [[str(x) for x in inner] for inner in parsed]
            if isinstance(parsed, list):
                return [[str(x) for x in parsed] for _ in range(target_length)]
            raise ValueError(f"Expected JSON list for nested normalization, got {type(parsed).__name__}")
        return [[stripped] for _ in range(target_length)]
    if isinstance(value, list):
        if value and isinstance(value[0], list):
            return [[str(x) for x in inner] for inner in value]
        return [[str(x) for x in value] for _ in range(target_length)]
    raise ValueError(f"Unsupported type for nested list: {type(value).__name__}")


def normalize_application_points(value: Any) -> list[dict[str, Any]]:
    """Normalize ``apply_ct_policies`` input (string|dict|list) into a validated list of dicts.

    Validates each entry has ``id`` and ``policies: list[{policy, used}]``.
    """
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError("application_points string must be valid JSON") from e
    elif isinstance(value, dict):
        parsed = [value]
    elif isinstance(value, list):
        parsed = value
    else:
        raise ValueError("application_points must be a string, dict, or list")

    if not isinstance(parsed, list):
        raise ValueError("application_points must be a list after normalization")

    for i, point in enumerate(parsed):
        if not isinstance(point, dict):
            raise ValueError(f"application_points[{i}] must be a dictionary")
        if "id" not in point:
            raise ValueError(f"application_points[{i}] missing 'id'")
        policies = point.get("policies")
        if not isinstance(policies, list):
            raise ValueError(f"application_points[{i}] 'policies' must be a list")
        for j, policy in enumerate(policies):
            if not isinstance(policy, dict):
                raise ValueError(f"application_points[{i}].policies[{j}] must be a dict")
            if "policy" not in policy or "used" not in policy:
                raise ValueError(f"application_points[{i}].policies[{j}] must contain 'policy' and 'used' fields")
            if not isinstance(policy["used"], bool):
                raise ValueError(f"application_points[{i}].policies[{j}]['used'] must be a boolean")

    return parsed


VnType = Literal["vxlan", "vlan"]
