# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""CSV source resolution for greenlake bulk_add.

Resolves the operator's chosen data source — uploaded file / local path / pasted
text — to the ``(csv_path, csv_text)`` pair the parser consumes. Kept separate
from ``bulk_add.py`` (which already owns batching, polling, resume, tokenization
and orchestration) to respect the 500-line module limit.
"""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError


def _read_uploaded_csv(ctx: Context, name: str) -> str:
    """Read an operator-uploaded CSV server-side from the FileUpload session store.

    Uses the ``FileUpload`` provider's ``on_read`` (the same path the ``read_file``
    tool uses) so the CSV — up to 10k rows — is fetched INSIDE the server and never
    enters the model context. The provider handle is placed on ``lifespan_context``
    by ``server.create_server`` only when ``MCP_APP_ENABLE=true``.

    Raises ToolError (400/404/502) on missing capability / file / read failure.
    """
    try:
        provider = ctx.lifespan_context.get("file_upload_provider")
    except Exception:  # pragma: no cover - defensive
        provider = None
    if provider is None:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "File upload is not available on this server (MCP_APP_ENABLE is not set, or the "
                    "client has no MCP-Apps support). Paste the CSV via csv_text, or use csv_path."
                ),
            }
        )
    try:
        entry = provider.on_read(name, ctx)
    except ValueError as exc:  # provider raises ValueError for not-found (lists available)
        raise ToolError({"status_code": 404, "message": f"uploaded file {name!r} not found: {exc}"}) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise ToolError({"status_code": 502, "message": f"failed to read uploaded file {name!r}: {exc}"}) from exc
    content = entry.get("content") if isinstance(entry, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ToolError({"status_code": 400, "message": f"uploaded file {name!r} is empty or not readable as text CSV"})
    return content


def resolve_csv_source(
    ctx: Context,
    csv_filename: str | None,
    csv_path: str | None,
    csv_text: str | None,
) -> tuple[str | None, str | None]:
    """Validate exactly-one-source and resolve uploads to text.

    Returns the ``(csv_path, csv_text)`` pair for ``parse_csv``: an upload
    (``csv_filename``) is read server-side and returned as ``csv_text`` with
    ``csv_path=None``; otherwise the caller's path/text pass through unchanged.

    Raises ToolError(400) when zero or more-than-one source is provided.
    """
    provided = [s for s in (csv_filename, csv_path, csv_text) if s is not None]
    if not provided:
        raise ToolError(
            {
                "status_code": 400,
                "message": "provide exactly one of csv_filename (upload), csv_path, or csv_text (paste)",
            }
        )
    if len(provided) > 1:
        raise ToolError(
            {
                "status_code": 400,
                "message": "provide exactly ONE of csv_filename / csv_path / csv_text, not several",
            }
        )
    # File-upload path: read the CSV server-side from the session upload store so the
    # (possibly 10k-row) content never enters the model context.
    if csv_filename is not None:
        return None, _read_uploaded_csv(ctx, csv_filename)
    return csv_path, csv_text
