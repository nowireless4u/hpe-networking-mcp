"""Read-only query layer over the baked spec-lookup index.

See ``scripts/build_spec_index.py`` for the schema. This module is the interface
the enrichment consumers use; it never mutates the index and never raises on a
missing/corrupt index — it reports ``available == False`` and returns empty
results so ``get_schema`` / error enrichment degrade to "no hint" instead of
failing.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_DEFAULT_DB = Path(__file__).resolve().parent / "spec_index.db"


def _clean_fts_query(query: str) -> str:
    """Quote each term so arbitrary user text can't break FTS5 MATCH syntax."""
    terms = [t.replace('"', "") for t in query.split() if t.strip()]
    return " ".join(f'"{t}"' for t in terms)


class SpecIndex:
    """Deterministic lookups over the vendored OpenAPI specs.

    Args:
        db_path: Override the index location (defaults to the baked
            ``spec_index.db`` beside this module). Missing file → ``available``
            is False and all queries return empty.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._path = Path(db_path) if db_path else _DEFAULT_DB
        self._con: sqlite3.Connection | None = None
        self._op_schema_cache: dict[str, dict[str, str]] = {}

    @property
    def available(self) -> bool:
        """True when the index file exists and can back queries."""
        return self._path.exists()

    def _conn(self) -> sqlite3.Connection | None:
        if not self.available:
            return None
        if self._con is None:
            self._con = sqlite3.connect(f"file:{self._path}?mode=ro", uri=True, check_same_thread=False)
            self._con.row_factory = sqlite3.Row
        return self._con

    # ----- enum resolution -----

    def _schema_enum(self, platform: str, schema_name: str | None) -> list[Any] | None:
        if not schema_name:
            return None
        con = self._conn()
        if con is None:
            return None
        row = con.execute(
            "SELECT enum_json FROM schemas WHERE platform=? AND schema_name=? AND enum_json IS NOT NULL LIMIT 1",
            (platform, schema_name),
        ).fetchone()
        return json.loads(row["enum_json"]) if row else None

    def _resolve_field_enum(self, platform: str, field: sqlite3.Row | dict) -> list[Any] | None:
        """A field's legal values: its own ``enum``, else the enum of the schema
        it ``$ref``s (Mist/ClearPass model enums as standalone named schemas)."""
        raw = field["enum_json"] if field["enum_json"] else None
        if raw:
            return json.loads(raw)
        enum = self._schema_enum(platform, field["ref_schema"])
        if enum is not None:
            return enum
        return self._schema_enum(platform, field["item_ref"])

    # ----- public API -----

    def schema_fields(self, platform: str, schema_name: str) -> list[dict[str, Any]]:
        """Every field of a schema, with enums resolved (incl. via ``$ref``).

        Returns [] when the schema is unknown or the index is unavailable.
        """
        con = self._conn()
        if con is None:
            return []
        srow = con.execute(
            "SELECT id FROM schemas WHERE platform=? AND schema_name=? LIMIT 1", (platform, schema_name)
        ).fetchone()
        if srow is None:
            return []
        out: list[dict[str, Any]] = []
        for f in con.execute("SELECT * FROM fields WHERE schema_id=? ORDER BY field_name", (srow["id"],)):
            ftype = f["type"]
            if ftype == "array" and (f["item_type"] or f["item_ref"]):
                ftype = f"array[{f['item_type'] or f['item_ref']}]"
            out.append(
                {
                    "name": f["field_name"],
                    "type": ftype,
                    "required": bool(f["required"]),
                    "format": f["format"],
                    "enum": self._resolve_field_enum(platform, f),
                    "default": json.loads(f["default"]) if f["default"] else None,
                    "ref_schema": f["ref_schema"] or f["item_ref"],
                    "variants": json.loads(f["variants"]) if f["variants"] else None,
                    "constraints": json.loads(f["constraints_json"]) if f["constraints_json"] else None,
                    "example": json.loads(f["example"]) if f["example"] else None,
                    "read_only": bool(f["read_only"]),
                    "write_only": bool(f["write_only"]),
                    "deprecated": bool(f["deprecated"]),
                    "deprecated_note": f["deprecated_note"],
                    "device_types": json.loads(f["device_types"]) if f["device_types"] else None,
                    "description": f["description"],
                }
            )
        return out

    def field_enum(self, platform: str, schema_name: str, field_name: str) -> list[Any] | None:
        """Legal values for one field, or None if it has no enum / is unknown."""
        con = self._conn()
        if con is None:
            return None
        row = con.execute(
            "SELECT f.* FROM fields f JOIN schemas s ON f.schema_id=s.id "
            "WHERE s.platform=? AND s.schema_name=? AND f.field_name=? LIMIT 1",
            (platform, schema_name, field_name),
        ).fetchone()
        return self._resolve_field_enum(platform, row) if row else None

    def endpoint(
        self,
        platform: str,
        *,
        path: str | None = None,
        operation_id: str | None = None,
        method: str | None = None,
    ) -> dict[str, Any] | None:
        """Resolve one endpoint (by path and/or operationId) with its parameters."""
        con = self._conn()
        if con is None:
            return None
        clauses = ["platform=?"]
        args: list[Any] = [platform]
        if path:
            clauses.append("path=?")
            args.append(path)
        if operation_id:
            clauses.append("operation_id=?")
            args.append(operation_id)
        if method:
            clauses.append("method=?")
            args.append(method.upper())
        row = con.execute(
            f"SELECT * FROM endpoints WHERE {' AND '.join(clauses)} LIMIT 1",  # nosec B608 — clauses are literals, values parameterized
            args,  # noqa: S608 — clauses are literals
        ).fetchone()
        if row is None:
            return None
        params = [
            {
                "name": p["name"],
                "in": p["location"],
                "required": bool(p["required"]),
                "type": p["type"],
                "format": p["format"],
                "enum": json.loads(p["enum_json"]) if p["enum_json"] else None,
                "example": json.loads(p["example"]) if p["example"] else None,
                "deprecated": bool(p["deprecated"]),
                "description": p["description"],
            }
            for p in con.execute("SELECT * FROM parameters WHERE endpoint_id=? ORDER BY name", (row["id"],))
        ]
        responses = [
            {"status": r["status_code"], "description": r["description"], "schema": r["schema_name"]}
            for r in con.execute("SELECT * FROM responses WHERE endpoint_id=? ORDER BY status_code", (row["id"],))
        ]
        return {
            "platform": row["platform"],
            "path": row["path"],
            "method": row["method"],
            "operation_id": row["operation_id"],
            "summary": row["summary"],
            "request_schema": row["request_schema"],
            "request_example": json.loads(row["request_example"]) if row["request_example"] else None,
            "responses": responses,
            "deprecated": bool(row["deprecated"]),
            "deprecated_note": row["deprecated_note"],
            "trust": row["trust"],
            "parameters": params,
        }

    def response_description(self, platform: str, status_code: str, *, min_share: float = 0.6) -> str | None:
        """The API's documented meaning of a status code for a platform.

        Returns the most-common response description for ``(platform, code)`` —
        but only when it dominates (``>= min_share`` of that code's responses),
        so uniform codes (429/401/403 on most platforms) enrich safely while
        endpoint-specific ones (EdgeConnect's per-path 400s) return ``None``
        rather than a misleading generic.
        """
        con = self._conn()
        if con is None:
            return None
        rows = con.execute(
            "SELECT r.description, COUNT(*) c FROM responses r JOIN endpoints e ON r.endpoint_id=e.id "
            "WHERE e.platform=? AND r.status_code=? AND r.description IS NOT NULL "
            "GROUP BY r.description ORDER BY c DESC",
            (platform, str(status_code)),
        ).fetchall()
        if not rows:
            return None
        total = sum(r["c"] for r in rows)
        top = rows[0]
        return top["description"] if total and top["c"] / total >= min_share else None

    def operation_schemas(self, platform: str) -> dict[str, str]:
        """``{operation_id: request_schema}`` for a platform's body-bearing endpoints.

        Cached per instance (the index is immutable). Used to map a generated
        tool back to its request body schema by operationId (e.g. Mist tools are
        ``mist_<snake(operationId)>``).
        """
        cached = self._op_schema_cache.get(platform)
        if cached is not None:
            return cached
        con = self._conn()
        result: dict[str, str] = {}
        if con is not None:
            for r in con.execute(
                "SELECT operation_id, request_schema FROM endpoints "
                "WHERE platform=? AND operation_id IS NOT NULL AND request_schema IS NOT NULL",
                (platform,),
            ):
                result[r["operation_id"]] = r["request_schema"]
        self._op_schema_cache[platform] = result
        return result

    def schema_body(self, platform: str, schema_name: str) -> dict[str, Any] | None:
        """A body descriptor for a schema: ``fields`` (object), else ``root``
        (array/scalar), else ``variants`` (oneOf/anyOf). ``None`` if unknown."""
        fields = self.schema_fields(platform, schema_name)
        if fields:
            return {"fields": fields}
        con = self._conn()
        if con is None:
            return None
        row = con.execute(
            "SELECT root, variants FROM schemas WHERE platform=? AND schema_name=? LIMIT 1",
            (platform, schema_name),
        ).fetchone()
        if row is None:
            return None
        if row["variants"]:
            return {"variants": json.loads(row["variants"])}
        if row["root"]:
            return {"root": row["root"]}
        return None

    def config_body(self, platform: str, resource: str) -> dict[str, Any] | None:
        """Resolve a config-object's writable body schema by its path segment.

        Maps a resource segment (e.g. ``"system-info"``) to its write endpoint
        (``.../network-config/.../system-info/{name}``), returning the body
        field set plus the scope query params a caller must supply. This is what
        powers ``get_schema`` enrichment for the opaque ``payload: dict`` config
        tools — the model no longer authors the body blind. Returns ``None`` when
        no matching writable endpoint is found.
        """
        con = self._conn()
        if con is None:
            return None
        row = con.execute(
            "SELECT * FROM endpoints WHERE platform=? AND request_schema IS NOT NULL "
            "AND (path LIKE ? OR path LIKE ?) "
            "ORDER BY CASE method WHEN 'PATCH' THEN 0 WHEN 'PUT' THEN 1 WHEN 'POST' THEN 2 ELSE 3 END LIMIT 1",
            (platform, f"%/{resource}", f"%/{resource}/%"),
        ).fetchone()
        if row is None:
            return None
        body = self.schema_body(platform, row["request_schema"])
        if body is None:
            return None
        scope_params = [
            {"name": p["name"], "in": p["location"], "required": bool(p["required"]), "description": p["description"]}
            for p in con.execute(
                "SELECT * FROM parameters WHERE endpoint_id=? AND location='query' ORDER BY name", (row["id"],)
            )
        ]
        return {
            "object": resource,
            "path": row["path"],
            "method": row["method"],
            **body,
            "scope_parameters": scope_params,
        }

    def search(
        self, query: str, *, kind: str = "field", platform: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Free-text FTS over one facet.

        Args:
            query: Free text (quoted internally so it can't break MATCH syntax).
            kind: ``"field"``, ``"endpoint"``, ``"schema"``, or ``"parameter"``.
            platform: Optional platform filter.
            limit: Max rows.
        """
        con = self._conn()
        if con is None or not query.strip():
            return []
        match = _clean_fts_query(query)
        if not match:
            return []
        specs = {
            "field": (
                "SELECT s.platform, s.schema_name, f.field_name AS name, f.type FROM fields_fts x "
                "JOIN fields f ON f.id=x.rowid JOIN schemas s ON f.schema_id=s.id WHERE fields_fts MATCH ?"
            ),
            "endpoint": (
                "SELECT e.platform, e.method, e.path, e.operation_id AS name FROM endpoints_fts x "
                "JOIN endpoints e ON e.id=x.rowid WHERE endpoints_fts MATCH ?"
            ),
            "schema": (
                "SELECT s.platform, s.schema_name AS name, s.description FROM schemas_fts x "
                "JOIN schemas s ON s.id=x.rowid WHERE schemas_fts MATCH ?"
            ),
            "parameter": (
                "SELECT e.platform, e.path, p.name, p.location FROM parameters_fts x "
                "JOIN parameters p ON p.id=x.rowid JOIN endpoints e ON p.endpoint_id=e.id WHERE parameters_fts MATCH ?"
            ),
            "response": (
                "SELECT e.platform, e.path, rs.status_code, rs.description FROM responses_fts x "
                "JOIN responses rs ON rs.id=x.rowid JOIN endpoints e ON rs.endpoint_id=e.id WHERE responses_fts MATCH ?"
            ),
        }
        sql = specs.get(kind)
        if sql is None:
            raise ValueError(f"kind must be one of {sorted(specs)}, got {kind!r}")
        args: list[Any] = [match]
        plat_col = "e.platform" if kind in ("endpoint", "parameter", "response") else "s.platform"
        if platform:
            sql += f" AND {plat_col}=?"  # noqa: S608  # nosec B608 — plat_col is a literal, value parameterized
            args.append(platform)
        sql += " LIMIT ?"
        args.append(limit)
        return [dict(r) for r in con.execute(sql, args)]


_SINGLETON: SpecIndex | None = None


def get_spec_index() -> SpecIndex:
    """Return a process-wide :class:`SpecIndex` over the baked index."""
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = SpecIndex()
    return _SINGLETON
