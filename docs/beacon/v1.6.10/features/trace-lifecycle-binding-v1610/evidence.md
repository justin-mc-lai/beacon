---
slug: trace-lifecycle-binding-v1610
version: v1.6.10
revision_id: R1
---

# Evidence — Lifecycle agent_trace binding

| surface | authority | path |
|---------|-----------|------|
| package | requirement_truth | docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md |
| tests | test_truth | docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/tests.md |
| parent | requirement_truth | docs/beacon/v1.6.6/features/beacon-agent-structured-trace-v166/truth.md |
| util | implementation | beacon/utils/agent_trace.py |
| hooks | implementation | beacon/commands/{truth,freeze,qa}.py + goal_agent_driver |
| unit | qa_verdict | tests/test_v1610_trace_lifecycle_binding.py |
