"""Code-mode sandbox provider that grants ``execute()`` a read-only clock.

fastmcp's stock ``MontySandboxProvider`` never passes an ``os=`` handler to
``monty.run_async``, so every clock call inside an ``execute()`` block fails:

    datetime.now()        -> NotImplementedError: OS function 'datetime.now' not implemented
    datetime.utcnow()     -> AttributeError: 'datetime.datetime' object has no attribute 'utcnow'

Network operators routinely need "now" to build time-window queries
(last-24h reports, audit-log windows), and small models reach for
``datetime.utcnow()`` by reflex (issue: Haiku 4.5 morning-report transcript).
Steering them via INSTRUCTIONS.md is unreliable — MCP-server content is
treated as advisory — so the fix is structural.

Passing ``os=OSAccess()`` enables monty's clock callbacks, so
``datetime.now()``, ``datetime.now(tz)`` and ``datetime.date.today()`` return
the real host clock. A bare ``OSAccess`` is otherwise inert: it exposes an
empty in-memory virtual filesystem and an empty environ, and ``open`` is not
even bound in the sandbox — verified live, host env vars and host files do not
leak (only the clock is added). A fresh instance per run keeps any in-memory
state from bleeding between ``execute()`` calls.

Monty implements only ``datetime.now`` — not ``datetime.utcnow`` — and has no
``time`` module, so ``datetime.utcnow()`` and ``time.time()`` still fail.
``SandboxErrorCatchMiddleware`` turns those residual dead-ends into a
self-correcting error pointing at ``datetime.now(datetime.timezone.utc)``.
"""

from __future__ import annotations

from typing import Any

from fastmcp.experimental.transforms.code_mode import MontySandboxProvider
from pydantic_monty import OSAccess


class ClockEnabledMontySandboxProvider(MontySandboxProvider):
    """``MontySandboxProvider`` that grants sandbox code a read-only clock.

    Overrides the private ``_run_monty`` launch seam (the isolated point the
    base class exposes so cancellation handling in ``run()`` stays testable)
    to pass a fresh ``OSAccess`` as the monty ``os=`` handler. This is the
    only mechanism monty offers to enable ``datetime.now`` — there is no
    public knob on ``MontySandboxProvider`` for it.
    """

    def _run_monty(
        self,
        monty: Any,
        *,
        inputs: dict[str, Any] | None,
        external_functions: dict[str, Any] | None,
    ) -> Any:
        return monty.run_async(
            inputs=inputs,
            external_functions=external_functions,
            limits=self.limits,
            os=OSAccess(),
        )
