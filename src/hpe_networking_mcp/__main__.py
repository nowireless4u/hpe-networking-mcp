"""CLI entry point for HPE Networking MCP Server."""

import argparse
import sys

from hpe_networking_mcp.config import load_config
from hpe_networking_mcp.utils.logging import flush_logs, setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HPE Networking MCP Server — Unified Mist, Central, and GreenLake",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--port", type=int, help="HTTP port (default: 8000, env: MCP_PORT)")
    parser.add_argument("--host", help="HTTP bind address (default: 0.0.0.0, env: MCP_HOST)")
    parser.add_argument(
        "--secrets-dir",
        help="Directory containing secret files (default: /run/secrets, env: SECRETS_DIR)",
    )
    parser.add_argument("--log-level", help="Log level (default: INFO, env: LOG_LEVEL)")
    parser.add_argument(
        "--disable-elicitation",
        action="store_true",
        help="DANGER: Skip user confirmation for write tools",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Apply CLI overrides to environment before config loading
    import os

    if args.secrets_dir:
        os.environ["SECRETS_DIR"] = args.secrets_dir
    if args.port:
        os.environ["MCP_PORT"] = str(args.port)
    if args.host:
        os.environ["MCP_HOST"] = args.host
    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level
    if args.disable_elicitation:
        os.environ["DISABLE_ELICITATION"] = "true"
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["DEBUG"] = "true"

    # Initialize logging BEFORE load_config() so its "Loading secrets from ...",
    # per-platform "credentials loaded", "Enabled platforms: ...", and
    # "Tool mode: ..." info lines reach stderr. The module-level
    # ``logger.remove()`` in utils/logging.py fires at import time and leaves
    # loguru with zero handlers; without this early setup_logging call,
    # anything load_config emits is silently dropped. Env-var fallbacks match
    # load_config()'s own reads so the level/file stays consistent.
    setup_logging(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        log_file=os.environ.get("LOG_FILE") or None,
    )

    from loguru import logger

    # Load config (reads Docker secrets + env vars). Logs from here now reach stderr.
    config = load_config()

    logger.info(
        "Starting HPE Networking MCP Server — platforms: {} — port: {}",
        ", ".join(config.enabled_platforms),
        config.port,
    )

    try:
        from hpe_networking_mcp.server import create_server

        mcp = create_server(config)
        mcp.run(transport="streamable-http", host=config.host, port=config.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error: {}", e)
        sys.exit(1)
    finally:
        flush_logs()


if __name__ == "__main__":
    main()
