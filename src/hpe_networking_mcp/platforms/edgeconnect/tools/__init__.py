"""Tool modules for the template platform.

Tools are classified with the ``capability=`` kwarg on the ``@tool`` decorator
(see ``platforms/_template/tools/example_read.py``). That single classification
derives the MCP annotations, the ``<platform>_write[_delete]`` enable tag, and
the ``requires_confirmation`` gate tag — there are no hand-written
``ToolAnnotations`` constants. See ``docs/tool-annotation-rubric.md``.
"""
