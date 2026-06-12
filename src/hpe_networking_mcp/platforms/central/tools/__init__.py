"""Tool modules for the Aruba Central platform.

Tools are classified with the ``capability=`` kwarg on the ``@tool`` decorator
(see ``platforms/_common/annotations.py`` and ``docs/tool-annotation-rubric.md``).
That single classification derives the MCP annotations, the
``central_write[_delete]`` enable tag, and the ``requires_confirmation`` gate
tag — there are no hand-written ``ToolAnnotations`` constants.

NOTE: scope-membership writes carry an explicit ``central_write_delete``
functional tag on top of ``Capability.WRITE`` because Central's visibility
transform only hides ``central_write_delete`` (the bare ``central_write``
tag gates nothing — see the gating footgun note in the rubric rollout).
"""
