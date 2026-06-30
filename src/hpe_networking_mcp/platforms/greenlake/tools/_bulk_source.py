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

from hpe_networking_mcp.utils.uploads import read_uploaded_text


def _read_uploaded_csv(ctx: Context, name: str) -> str:
    """Read an operator-uploaded CSV server-side from the FileUpload session store.

    Thin wrapper over the shared :func:`read_uploaded_text` — the CSV (up to 10k
    rows) is fetched INSIDE the server and never enters the model context.
    Raises ToolError (400/404/502) on missing capability / file / read failure.
    """
    return read_uploaded_text(ctx, name)


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
