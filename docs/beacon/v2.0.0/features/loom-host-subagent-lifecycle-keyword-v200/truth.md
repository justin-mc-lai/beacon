---
slug: loom-host-subagent-lifecycle-keyword-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "UD-SA-004 parity mirror of v1.6.8 host subagent keyword gate"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-host-subagent-lifecycle-keyword-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-host-subagent-lifecycle-keyword-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-host-subagent-lifecycle-keyword-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-host-subagent-lifecycle-keyword-v200/evidence.md
ux_required: false
parity_of: docs/beacon/v1.6.8/features/beacon-host-subagent-lifecycle-keyword-v168/truth.md
---

# Loom / v2.0.0 mirror: Host Subagent Keyword Gate

Same AC IDs **AC-SA-KW-001..008**, **AC-SA-ST/BD/IN/VR/EX/SC** as v1.6.8.

Public entry: `$loom-goal` / `loom goal run` (dual-install; does not replace beacon).

Keyword gate + 6-role pack + default single-thread + no self-complete.

Implementation may share Python modules under `beacon.utils.host_subagent_*`.
