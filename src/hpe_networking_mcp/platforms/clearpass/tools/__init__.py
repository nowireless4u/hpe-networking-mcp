"""Tool modules for the Aruba ClearPass platform.

Tools are classified with the ``capability=`` kwarg on the ``@tool`` decorator
(see ``platforms/_common/annotations.py`` and ``docs/tool-annotation-rubric.md``).
That single classification derives the MCP annotations, the
``clearpass_write_delete`` enable tag, and the ``requires_confirmation`` gate
tag — there are no hand-written ``ToolAnnotations`` constants.
"""
