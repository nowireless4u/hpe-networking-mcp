FROM python:3.12-slim-bookworm AS deps

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml ./

# Install dependencies (no dev deps, no project itself yet)
RUN uv sync --frozen --no-dev --no-install-project 2>/dev/null || uv sync --no-dev --no-install-project

# --- Runtime stage ---
FROM python:3.12-slim-bookworm

# Install uv in runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user
RUN groupadd -g 1000 mcpuser && useradd -u 1000 -g mcpuser -m mcpuser

WORKDIR /app

# Copy venv from deps stage
COPY --from=deps /app/.venv /app/.venv

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

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
ENV ENABLE_MIST_WRITE_TOOLS=false
ENV ENABLE_CENTRAL_WRITE_TOOLS=false
ENV DISABLE_ELICITATION=false

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD uv run --no-sync python -c "import httpx; r = httpx.get('http://localhost:8000/mcp', timeout=5); assert r.status_code < 500" || exit 1

CMD ["uv", "run", "--no-sync", "python", "-m", "hpe_networking_mcp"]
