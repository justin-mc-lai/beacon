---
slug: loop-goal-dynamic-intent-routing-friction-2e306f7a
version: v1.6.7
status: support_advisory
authority: beacon-pln-review
promotion_ref: friction:2e306f7acea7
promoted_to: docs/beacon/v1.6.7/programs/beacon-unified-topology-loop-goal-v167/
user_confirmed_at: 2026-07-16
---

# Research: Loop Goal Dynamic Intent Routing (friction:2e306f7acea7)

Planner review artifact promoted to v1.6.7 program per user confirmation.

## Summary

- **Problem**: loop-goal stops due to host interrupt, uncached user_decision_required, missing multi-git topology_gate, and AC-028 host non-enforcement.
- **Lake**: IntentContext, decision_cache, resume semantics, dual runtime, GitScopeGraph.
- **Ocean**: per-project DeliveryStageGraph (git-uat) — not in v1.6.7 global state machine.
- **Route taken**: `beacon-gen-change` v1.6.7 program `beacon-unified-topology-loop-goal-v167` slices A+B.

## User decisions locked

1. Resilient stop contract (UD-TOPO-002)
2. GitScopeGraph main + satellite (UD-TOPO-001)
3. v1.6.7 program A+B + v2 schema parity (UD-TOPO-004/005)
