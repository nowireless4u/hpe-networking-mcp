"""GreenLake tools package.

Tool modules here are auto-discovered and imported by
``platforms.greenlake.register_tools`` via ``pkgutil`` (same as Mist/EdgeConnect)
— there is no hand-maintained ``TOOLS`` registry. Modules named
``<service>__<tag>.py`` are generated from the vendored specs (see the package
docstring); ``bulk_add`` + ``_bulk_*`` are hand-written orchestration.
"""

from __future__ import annotations
