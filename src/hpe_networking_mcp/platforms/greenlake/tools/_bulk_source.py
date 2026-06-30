# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Input + redaction helpers for greenlake bulk_add.

Holds the pieces kept out of ``bulk_add.py`` (which already owns batching, polling,
resume and orchestration) to respect the 500-line module limit: CSV source
resolution (upload / local path / paste), uniform batch-assignment defaults, the
serial redactor factory, and the AI-facing tool description constant.
"""

from __future__ import annotations

from collections.abc import Callable

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.redaction.rules import TokenKind
from hpe_networking_mcp.redaction.token_store import KeymapFullError
from hpe_networking_mcp.redaction.tokenizer import Tokenizer
from hpe_networking_mcp.utils.uploads import read_uploaded_text

# AI-facing description for greenlake_bulk_add_devices (kept here to keep bulk_add.py
# under the module-size limit). For full guided onboarding (add → subscribe → assign
# service → verify) prefer the ``greenlake-device-onboarding`` skill over a bare call.
BULK_ADD_DESCRIPTION = (
    "Bulk-add HPE GreenLake devices from a CSV. For a full guided onboarding flow "
    "(choose upload vs paste with the paste-visibility warning, then subscribe + "
    "assign to a service), load the `greenlake-device-onboarding` skill instead of "
    "calling this bare.\n\n"
    "HOW TO PROVIDE THE LIST — ASK THE OPERATOR which they prefer before calling:\n"
    "  • FILE UPLOAD (best for large lists, up to 10k rows): have the operator upload "
    'the CSV via the `file_manager` widget, then call with `csv_filename="<uploaded name>"`. '
    "The tool reads it SERVER-SIDE — the CSV never enters the model context. Requires the "
    "server's MCP-Apps capability (MCP_APP_ENABLE) + an MCP-Apps-capable client.\n"
    "  • COPY / PASTE: pass the CSV as `csv_text`. The AI WILL see the pasted content — fine "
    "for small lists, but do NOT paste thousands of rows; use file upload for those.\n"
    '  • LOCAL PATH (CLI / same-host only): `csv_path="/abs/path.csv"`.\n'
    "Provide EXACTLY ONE of csv_filename / csv_text / csv_path.\n\n"
    "Mandatory CSV columns: serialNumber (aliases: serial, sn, serial_number) "
    "and macAddress (aliases: mac, mac_address). Optional per-row columns: "
    "subscriptionKey, serviceId, location, tags. The subscription_key / service_id / "
    "location / tags PARAMETERS apply uniformly to every device lacking that column "
    "(per-row column wins) — use them to subscribe + assign an uploaded list in one call.\n\n"
    "Rate limit: 5 POST/min (device-add), 20 PATCH/min (enrichment); batch size: 5 devices/request. "
    "A 10,000-device run takes ~400 min at ceiling; enrichment adds up to 4 PATCH/device. "
    "Resume-on-failure: a .cache.json file is written beside the input CSV "
    "and deleted after a fully successful run."
)


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


def apply_uniform_assignment(
    rows: list[dict],
    *,
    subscription_key: str | None,
    service_id: str | None,
    location: str | None,
    tags: str | None,
) -> None:
    """Fill enrichment fields on rows that don't already carry one (in place).

    Per-row CSV columns take precedence: a uniform value is applied only where the
    row has no non-empty value for that field. This lets the device-onboarding
    runbook subscribe + service-assign an *uploaded* serial/MAC list — which the AI
    cannot edit (it's read server-side) — by passing one subscription / service /
    location / tags for the whole batch. Field keys match the CSV parser's canonical
    names consumed by the assignment/enrichment phases.
    """
    uniform = {
        "subscriptionKey": subscription_key,
        "serviceId": service_id,
        "location": location,
        "tags": tags,
    }
    for row in rows:
        for field, value in uniform.items():
            if value and not str(row.get(field) or "").strip():
                row[field] = value


def make_safe_serial(ctx: Context) -> Callable[[str], str]:
    """Build a serial redactor bound to the session token store.

    Returns a callable that turns a device serial into a ``[[SERIAL:uuid]]`` token
    (round-trippable when ``ENABLE_PII_TOKENIZATION=true``) so raw serials never enter
    the model context via the result. Falls back to the non-leaking ``[serial]``
    placeholder when no token store is present OR the session keymap is full — a write
    tool must never crash mid-run over a redaction failure (the manual tokenize path
    is not behind the walker's KeymapFullError catch).
    """
    token_store = ctx.lifespan_context.get("token_store")
    tokenizer: Tokenizer | None = None
    if token_store is not None:
        tokenizer = Tokenizer(
            token_store.get_or_create(ctx.session_id),
            session_id=ctx.session_id,
            max_entries=token_store.max_entries_per_session,
        )

    def _safe_serial(value: str) -> str:
        if tokenizer is not None:
            try:
                return tokenizer.tokenize(TokenKind.SERIAL, value)
            except KeymapFullError:
                return "[serial]"
        return "[serial]"

    return _safe_serial
