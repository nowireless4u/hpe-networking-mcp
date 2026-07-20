"""Progress-reporting capability of the code-mode ``execute`` sandbox.

``_HpeCodeMode`` (built by ``server._hpe_code_mode_class``) overrides the stock
``CodeMode._make_execute_tool`` to inject a ``report_progress`` external function
alongside ``call_tool``, bound to the live per-call ``ctx``. This lets long-running
skill code blocks stream status to the client via
``await report_progress(done, total, "message")``.

These tests drive the REAL production class end-to-end through an in-memory
``fastmcp.Client`` whose ``progress_handler`` records the notifications. They also
serve as the pin on the fastmcp internals the override copies
(``get_tool_catalog`` / ``_find_tool`` / ``sandbox_provider`` / ``max_tool_calls`` /
``_unwrap_tool_result`` / ``ctx.report_progress``): if a fastmcp upgrade changes
any of them, either ``call_tool`` or ``report_progress`` stops working and a test
here fails loudly rather than the capability silently regressing.
"""

from __future__ import annotations

import pytest
from fastmcp import Client, FastMCP

pytestmark = pytest.mark.unit

pytest.importorskip("pydantic_monty", reason="code-mode extra not installed")


def _build_code_mode_server() -> FastMCP:
    """A minimal FastMCP server with one tool and the real ``_HpeCodeMode`` transform.

    Uses the production class from ``server._hpe_code_mode_class`` with the real
    ``ClockEnabledMontySandboxProvider`` — the same wiring ``_register_code_mode``
    uses, minus the discovery-tool/skills plumbing which is orthogonal to progress.
    """
    from pydantic_monty import ResourceLimits

    from hpe_networking_mcp.code_sandbox import ClockEnabledMontySandboxProvider
    from hpe_networking_mcp.server import _hpe_code_mode_class

    mcp = FastMCP("progress-test")

    @mcp.tool
    async def central_get_sites() -> dict:
        return {"sites": ["HQ", "BRANCH-1", "BRANCH-2"]}

    limits = ResourceLimits(
        max_duration_secs=30,
        max_memory=128 * 1024 * 1024,
        max_recursion_depth=50,
    )
    cls = _hpe_code_mode_class()
    mcp.add_transform(cls(sandbox_provider=ClockEnabledMontySandboxProvider(limits=limits)))
    return mcp


async def _run(code: str) -> tuple[object, list[tuple]]:
    """Execute ``code`` in the sandbox, returning (result, progress_events)."""
    mcp = _build_code_mode_server()
    seen: list[tuple] = []

    async def progress_handler(progress, total, message):
        seen.append((progress, total, message))

    async with Client(mcp, progress_handler=progress_handler) as client:
        result = await client.call_tool("execute", {"code": code})
    return result.data, seen


@pytest.mark.asyncio
async def test_report_progress_reaches_client_handler():
    """A sandbox block calling report_progress streams every update to the client."""
    code = (
        "await report_progress(0, 3, 'start')\n"
        "await report_progress(1, 3, 'middle')\n"
        "await report_progress(3, 3, 'done')\n"
        "return {'status': 'ok'}\n"
    )
    result, seen = await _run(code)
    assert result == {"status": "ok"}
    assert seen == [
        (0.0, 3.0, "start"),
        (1.0, 3.0, "middle"),
        (3.0, 3.0, "done"),
    ]


@pytest.mark.asyncio
async def test_report_progress_and_call_tool_coexist():
    """report_progress does not displace call_tool — a realistic sweep uses both."""
    code = (
        "sites = await call_tool('central_get_sites', {})\n"
        "names = sites['sites']\n"
        "total = len(names)\n"
        "for i, n in enumerate(names):\n"
        "    await report_progress(i + 1, total, 'classifying ' + n)\n"
        "return {'count': total}\n"
    )
    result, seen = await _run(code)
    assert result == {"count": 3}
    assert len(seen) == 3
    assert seen[0] == (1.0, 3.0, "classifying HQ")
    assert seen[-1] == (3.0, 3.0, "classifying BRANCH-2")


@pytest.mark.asyncio
async def test_report_progress_optional_args():
    """total and message are optional (matches the FastMCP report_progress contract)."""
    code = "await report_progress(5)\nreturn None\n"
    _result, seen = await _run(code)
    assert seen == [(5.0, None, None)]


@pytest.mark.asyncio
async def test_execute_still_works_without_progress_calls():
    """A block that never calls report_progress behaves exactly as before (no events)."""
    code = "x = await call_tool('central_get_sites', {})\nreturn {'count': len(x['sites'])}\n"
    result, seen = await _run(code)
    assert result == {"count": 3}
    assert seen == []


def test_hpe_code_mode_subclasses_code_mode():
    """The factory returns a genuine CodeMode subclass (not a stand-in)."""
    from fastmcp.experimental.transforms.code_mode import CodeMode

    from hpe_networking_mcp.server import _hpe_code_mode_class

    cls = _hpe_code_mode_class()
    assert issubclass(cls, CodeMode)
    assert cls is not CodeMode
    assert "_make_execute_tool" in cls.__dict__  # override is present locally
