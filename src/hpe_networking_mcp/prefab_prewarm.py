"""Build-time pre-warm for the Prefab / Pyodide generative-UI sandbox.

The ``GenerativeUI`` provider (enabled by ``MCP_APP_ENABLE``) renders
dashboards by executing Prefab Python in a Deno + Pyodide subprocess. The
FIRST render in a container pays a cold start: Deno fetches ``npm:pyodide``
plus the ``deno.land/std`` modules and Pyodide initializes the WASM runtime.

Running one throwaway render at image-build time populates ``DENO_DIR``
inside the layer, so the runtime first render is ~2x faster (measured
~3.0s → ~1.5s) and needs no network at first use — which also matters for
locked-down deployments with restricted egress.

Invoked from the Dockerfile as
``uv run --no-sync python -m hpe_networking_mcp.prefab_prewarm``.

Best-effort by design: if Deno is absent or the build has no network
egress, it logs to stderr and exits 0 so the image still builds (the
runtime simply cold-starts on the first render, exactly as before).
"""

from __future__ import annotations

import asyncio
import sys

# A minimal but representative render: a container with a heading, exercising
# the import -> component-tree -> wire-protocol path a real dashboard hits.
# Uses the context-manager build form (children register onto the open
# container) — the same shape the GenerativeUI tool documents to the model.
_WARMUP_PROGRAM = (
    "from prefab_ui.app import PrefabApp\n"
    "from prefab_ui.components import Column, Heading\n"
    "with Column() as view:\n"
    "    Heading('prewarm')\n"
    "app = PrefabApp(view=view)\n"
)


async def _render_once() -> None:
    """Drive one render through the Pyodide sandbox to populate DENO_DIR."""
    from prefab_ui.sandbox import Sandbox

    async with Sandbox() as sandbox:
        await sandbox.run(_WARMUP_PROGRAM)


def main() -> int:
    """Pre-warm the sandbox; never fail the build (returns 0 on any error)."""
    try:
        asyncio.run(_render_once())
    except Exception as exc:  # noqa: BLE001 - best-effort: builds without deno/network still succeed
        print(
            f"prefab prewarm skipped ({type(exc).__name__}: {exc}); "
            "the first generative-UI render will cold-start at runtime",
            file=sys.stderr,
        )
        return 0
    print("prefab prewarm: Pyodide sandbox cache populated (DENO_DIR baked into image)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
