"""Central API connection helpers.

Tools obtain the connection from ``ctx.lifespan_context["central_conn"]``
rather than importing a global singleton.  The ``create_connection`` factory
and ``verify_connection`` health-check are used by the server lifespan handler.
"""

from hpe_networking_mcp.config import CentralSecrets

try:
    from pycentral import NewCentralBase
except ImportError:  # allow import even if pycentral is missing at lint time
    NewCentralBase = None  # type: ignore[assignment,misc]


def create_connection(secrets: CentralSecrets) -> "NewCentralBase":
    """Build a new ``NewCentralBase`` instance from config secrets."""
    if NewCentralBase is None:
        raise RuntimeError("pycentral is not installed")
    return NewCentralBase(
        token_info={
            "new_central": {
                "base_url": secrets.base_url,
                "client_id": secrets.client_id,
                "client_secret": secrets.client_secret,
            }
        },
    )


def verify_connection(conn: "NewCentralBase") -> None:
    """Verify credentials are valid by making a lightweight GET to the Central API.

    Raises ``RuntimeError`` with a clear message if the connection fails.
    """
    try:
        conn.command(
            api_method="GET",
            api_path="network-monitoring/v1/sites-health",
            api_params={"limit": 1},
        )
    except Exception as exc:
        raise RuntimeError(
            f"Central API connectivity check failed: {exc}. "
            "Check base_url, client_id, and client_secret in secrets.json"
        ) from exc
