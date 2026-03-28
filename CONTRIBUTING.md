# Contributing to HPE Networking MCP Server

Thank you for your interest in contributing! This guide covers how to set up your development environment and submit changes.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)
- A GitHub account

## Development Setup

This is a **Docker-only** project. All building, testing, and running happens inside containers.

### 1. Fork and Clone

```bash
gh repo fork nowireless4u/hpe-networking-mcp --clone
cd hpe-networking-mcp
```

### 2. Create Secret Files

Copy the example templates and fill in your credentials for the platforms you have access to:

```bash
cp secrets/mist_api_token.example secrets/mist_api_token
cp secrets/mist_host.example secrets/mist_host
# Edit each file with real credentials
```

### 3. Build and Run

```bash
docker compose up -d --build
docker compose logs          # Verify all platforms initialize
```

### 4. Run Tests

```bash
docker compose run --rm hpe-networking-mcp uv run pytest
docker compose run --rm hpe-networking-mcp uv run pytest -m unit        # Unit tests only
docker compose run --rm hpe-networking-mcp uv run pytest -m integration # Integration tests only
```

### 5. Lint and Type Check

```bash
docker compose run --rm hpe-networking-mcp uv run ruff check .
docker compose run --rm hpe-networking-mcp uv run ruff format --check .
docker compose run --rm hpe-networking-mcp uv run mypy src/
```

## Making Changes

### Branching

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Rebuild and test:
   ```bash
   docker compose up -d --build
   docker compose logs
   ```

### Adding a New Tool

Tools are organized by platform in `src/hpe_networking_mcp/platforms/<platform>/tools/`.

1. Create a new file in the appropriate `tools/` directory
2. Import `mcp` from the platform's `_registry` module
3. Use the `@mcp.tool()` decorator with proper annotations
4. Follow the platform's naming convention (`mist_*`, `central_*`, `greenlake_*`)
5. For Mist tools, add the tool name to the `TOOLS` dict in `platforms/mist/__init__.py`

### Adding a New Platform

1. Create a new directory under `src/hpe_networking_mcp/platforms/<name>/`
2. Implement `__init__.py` with a `register_tools(mcp, config)` function
3. Create `_registry.py` for the module-level FastMCP holder
4. Create `client.py` for API authentication and communication
5. Add credential loading to `config.py`
6. Add platform initialization to the lifespan handler in `server.py`
7. Add secret file templates in `secrets/`

## Code Standards

- **Python 3.12+**
- **Formatting**: `ruff format`
- **Linting**: `ruff check`
- **Type hints**: Use them for function signatures
- **Tool prefixes**: Always prefix tool names by platform (`mist_*`, `central_*`, `greenlake_*`)
- **Logging**: Use `from loguru import logger` — all output to stderr
- **Secrets**: Never log credentials; use `mask_secret()` from `utils/logging.py`

## Pull Request Process

1. Ensure your branch is up to date with `main`
2. Verify the Docker build succeeds: `docker compose up -d --build`
3. Verify all tests pass
4. Verify linting passes
5. Write a clear PR description explaining what changed and why
6. Link related issues (e.g., "Closes #5")

## Reporting Issues

- Use [GitHub Issues](https://github.com/nowireless4u/hpe-networking-mcp/issues)
- Include Docker logs (`docker compose logs`) for bug reports
- Specify which platform(s) are affected

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
