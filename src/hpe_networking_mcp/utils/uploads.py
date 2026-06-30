# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Server-side reads of operator-uploaded files (MCP-Apps ``FileUpload``).

The single, shared way for a tool to consume a file the operator uploaded via
the ``file_manager`` widget. The file is read INSIDE the server from the
session-scoped upload store (the ``FileUpload`` provider's ``on_read``) so its
contents — device serials/MACs, AOS 8 configs with PSKs and RADIUS/TACACS
secrets, etc. — **never enter the model context**.

This is why the ``read_file`` tool is NOT exposed to the model (it would return
raw content to the LLM, defeating the guarantee). Tools that need uploaded data
call :func:`read_uploaded_text` and process it server-side, returning only
counts / tokenized / parsed results.
"""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError


def read_uploaded_text(ctx: Context, name: str) -> str:
    """Read an operator-uploaded text file server-side, by name.

    Reads from the ``FileUpload`` provider's session-scoped store via its
    ``on_read`` (the same backend the removed ``read_file`` tool used) so the
    content is fetched INSIDE the server and never reaches the model. The
    provider handle is placed on ``lifespan_context`` (``file_upload_provider``)
    by ``server.create_server`` only when ``MCP_APP_ENABLE=true``.

    Args:
        ctx: FastMCP request context (carries ``lifespan_context`` + session).
        name: The uploaded file's name, as shown by ``list_files``.

    Returns:
        The decoded text content of the uploaded file.

    Raises:
        ToolError: 400 if file upload is unavailable or the file is empty / not
            text-readable; 404 if no upload by that name exists; 502 on an
            unexpected read failure.
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
                    "client has no MCP-Apps support). Provide the data another way (paste / local path / live API)."
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
        raise ToolError({"status_code": 400, "message": f"uploaded file {name!r} is empty or not readable as text"})
    return content
