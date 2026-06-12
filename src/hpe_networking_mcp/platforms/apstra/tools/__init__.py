"""Tool modules for the Juniper Apstra platform.

Tools are classified with the ``capability=`` kwarg on the ``@tool`` decorator
(see ``platforms/_common/annotations.py`` and ``docs/tool-annotation-rubric.md``).
That single classification derives the MCP annotations, the
``apstra_write[_delete]`` enable tag, and the ``requires_confirmation`` gate
tag — there are no hand-written ``ToolAnnotations`` constants.
"""
