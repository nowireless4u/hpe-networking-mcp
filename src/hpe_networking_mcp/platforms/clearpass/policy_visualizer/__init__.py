"""Engine for compiling ClearPass policy decisions into a renderable flow graph.

Internal sub-package used by ``tools/policy_visualizer.py``. Not exposed
directly to AI clients.

Pipeline:

    REST JSON
      → api_adapter.adapt()      raw dict in policy_model's expected shape
      → policy_model.build()     typed PolicyModel (services + cross-refs)
      → flow_graph.compile_service()    FlowGraph (nodes + edges +
                                                    optional simulation)

ClearPass-only. The upstream project this was lifted from also supported
Cisco ISE; those code paths were stripped during the port and the
engine has no ISE-specific operators, parsers, or data models.
"""
