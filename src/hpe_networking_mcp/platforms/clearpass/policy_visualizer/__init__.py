"""Engine for compiling ClearPass policy decisions into a renderable flow graph.

Internal sub-package used by ``tools/policy_visualizer.py``. Not exposed
directly to AI clients.

Pipeline:

    REST JSON
      → api_adapter.adapt()      raw dict in policy_model's expected shape
      → policy_model.build()     typed PolicyModel (services + cross-refs)
      → flow_graph.compile_service()    FlowGraph (nodes + edges)

Lifted (and adapted) from the policy-visualizer project. Cisco ISE
support, the FastAPI HTTP layer, and the XML parser are intentionally
omitted — we pull live data via the existing ``clearpass_get_*`` tools.
"""
