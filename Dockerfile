FROM python:3.13-slim-trixie AS deps

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml ./

# Install dependencies (no dev deps, no project itself yet)
RUN uv sync --frozen --no-dev --no-install-project 2>/dev/null || uv sync --no-dev --no-install-project

# --- Spec-index build stage ---
# Bakes the deterministic OpenAPI lookup index (SQLite/FTS5) from the vendored
# specs. Stdlib-only (json + sqlite3), so it needs no project deps — just the
# builder script and vendor/. Only the resulting .db ships to the runtime image;
# the 90 vendored specs stay out of it.
FROM python:3.13-slim-trixie AS specindex
WORKDIR /app
COPY scripts/build_spec_index.py ./scripts/build_spec_index.py
COPY vendor/ ./vendor/
RUN python scripts/build_spec_index.py /tmp/spec_index.db

# --- Runtime stage ---
FROM python:3.13-slim-trixie

# Install uv in runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Deno binary — required ONLY by the optional Generative UI provider (enabled via
# MCP_APP_ENABLE), which runs Prefab/Pyodide in a Deno subprocess for server-side
# validation. prefab_ui does shutil.which("deno") and raises if it's absent (it
# does NOT auto-install). Harmless dead weight when the MCP-Apps providers are off.
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

# Create non-root user
RUN groupadd -g 1000 mcpuser && useradd -u 1000 -g mcpuser -m mcpuser

WORKDIR /app

# Copy venv from deps stage
COPY --from=deps /app/.venv /app/.venv

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Bake the spec-lookup index beside its query module (before the project install
# so it ships whether the project installs editable or as a built wheel).
COPY --from=specindex /tmp/spec_index.db ./src/hpe_networking_mcp/spec_index/spec_index.db

# Install the project itself (as root so it can write to .venv/bin)
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

# Set ownership (Docker secrets mounted read-only at /run/secrets/ by compose)
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Environment defaults
ENV MCP_PORT=8000
ENV MCP_HOST=0.0.0.0
ENV LOG_LEVEL=info
ENV SECRETS_DIR=/run/secrets
# Deno download cache (Generative UI / Prefab sandbox) — under the writable HOME.
ENV DENO_DIR=/home/mcpuser/.cache/deno
ENV ENABLE_MIST_WRITE_TOOLS=false
ENV ENABLE_CENTRAL_WRITE_TOOLS=false
ENV DISABLE_ELICITATION=false

# Pre-warm the Prefab/Pyodide generative-UI sandbox (see prefab_prewarm.py):
# bakes the Deno module graph + Pyodide runtime into this layer's DENO_DIR so
# the first generate_prefab_ui render is ~2x faster (measured ~3.0s -> ~1.5s)
# and needs no network at first use. Runs as mcpuser with DENO_DIR already set,
# so the cache lands at the exact runtime path. Best-effort: the module exits 0
# even without build-time network egress (the image just cold-starts at runtime).
RUN uv run --no-sync python -m hpe_networking_mcp.prefab_prewarm

EXPOSE 8000

# Health check — hits the plain /livez probe (200 when the process is alive).
# Liveness is intentionally decoupled from upstream platform reachability, so a
# transient Mist/Central/GreenLake outage never marks the container unhealthy.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD uv run --no-sync python -c "import httpx; r = httpx.get('http://localhost:8000/livez', timeout=5); assert r.status_code == 200" || exit 1

CMD ["uv", "run", "--no-sync", "python", "-m", "hpe_networking_mcp"]
