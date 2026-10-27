# Every base image is pinned by version tag AND multi-arch index digest so a
# build is reproducible and the scanned image is the shipped image. Dependabot's
# docker ecosystem bumps tag+digest together — merge those PRs to pick up base
# fixes. uv and deno are FROM-stages (not inline COPY --from=image:tag) so
# Dependabot can see and update them.
FROM ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff AS uv
FROM denoland/deno:bin-2.9.8@sha256:b507583d3c68ba69f3ed2ce5969ae5b8b70f43421c781279c7aea06435263543 AS deno

FROM python:3.13-slim-trixie@sha256:d3449c0493345868b09708d7056dce5edda3a75233ea86008fc80c934d355a10 AS deps

# Install uv
COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev deps, no project itself yet) exactly as locked.
# --locked fails the build if uv.lock is missing or out of date with
# pyproject.toml — never silently re-resolve, or the image ships versions that
# pip-audit (which audits uv.lock) never saw.
RUN uv sync --locked --no-dev --no-install-project

# --- Spec-index build stage ---
# Bakes the deterministic OpenAPI lookup index (SQLite/FTS5) from the vendored
# specs. Stdlib-only (json + sqlite3), so it needs no project deps — just the
# builder script and vendor/. Only the resulting .db ships to the runtime image;
# the 90 vendored specs stay out of it.
FROM python:3.13-slim-trixie@sha256:d3449c0493345868b09708d7056dce5edda3a75233ea86008fc80c934d355a10 AS specindex
WORKDIR /app
COPY scripts/build_spec_index.py ./scripts/build_spec_index.py
COPY vendor/ ./vendor/
RUN python scripts/build_spec_index.py /tmp/spec_index.db

# --- Runtime stage ---
FROM python:3.13-slim-trixie@sha256:d3449c0493345868b09708d7056dce5edda3a75233ea86008fc80c934d355a10

# Install uv in runtime
COPY --from=uv /uv /usr/local/bin/uv

# Deno binary — required ONLY by the optional Generative UI provider (enabled via
# MCP_APP_ENABLE), which runs Prefab/Pyodide in a Deno subprocess for server-side
# validation. prefab_ui does shutil.which("deno") and raises if it's absent (it
# does NOT auto-install). Harmless dead weight when the MCP-Apps providers are off.
COPY --from=deno /deno /usr/local/bin/deno

# Remove the base image's system pip. The app runs from a uv-managed venv that
# never uses it, and pip vendors its own (often stale) copies of urllib3,
# msgpack and setuptools that image scanners flag as HIGH. ensurepip's bundled
# wheel goes too so pip can't be re-bootstrapped inside the container.
RUN python -m pip uninstall -y pip \
    && rm -rf /usr/local/lib/python3.13/ensurepip/_bundled

# Create non-root user
RUN groupadd -g 1000 mcpuser && useradd -u 1000 -g mcpuser -m mcpuser

WORKDIR /app

# Copy venv from deps stage
COPY --from=deps /app/.venv /app/.venv

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Bake the spec-lookup index beside its query module (before the project install
# so it ships whether the project installs editable or as a built wheel).
COPY --from=specindex /tmp/spec_index.db ./src/hpe_networking_mcp/spec_index/spec_index.db

# Install the project itself (as root so it can write to .venv/bin). --no-cache
# keeps root's uv download cache out of the shipped layer.
RUN uv sync --locked --no-dev --no-cache

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
