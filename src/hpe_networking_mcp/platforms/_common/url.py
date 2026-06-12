"""URL path-segment escaping for interpolated selector values (#476).

Operator-supplied selectors (usernames, MACs, attribute names, template
names) are interpolated into URL paths via f-strings throughout the
platform tools. httpx percent-encodes spaces and unicode when normalizing
the URL, but a value containing ``/`` restructures the route, ``?`` starts
the query string, and ``#`` truncates everything after it — producing
silently wrong requests (wrong resource targeted, no error) for
legal-but-unusual names. Every interpolated path segment must go through
:func:`path_seg`.
"""

from urllib.parse import quote


def path_seg(value: object) -> str:
    """Encode one URL path segment so it cannot restructure the route.

    Args:
        value: Selector value destined for a single path segment. Coerced
            with ``str()`` first (numeric IDs are common).

    Returns:
        The percent-encoded segment with no characters exempt
        (``safe=""``), so ``/``, ``?``, ``#``, and ``%`` are all escaped.
        The value is treated as raw text — pre-encoded input is encoded
        again rather than trusted.

    Example:
        >>> path_seg("Policy #2/v1")
        'Policy%20%232%2Fv1'
    """
    return quote(str(value), safe="")
