---
artifact_type: planner_review
skill: beacon-pln-review
status: support_advisory
canonical_review: docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md
---

# Loom / v2.0.0 — Ops philosophy parity pointer (v1.6.8 program)

Full analysis and lake plan live in:

`docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md`

## v2 / Loom obligations (summary)

When `beacon-prod-ops-hardening-v168` freezes:

1. Mirror lakes on `beacon-v2-product-goal-parallel-v200` (or successor program):
   - hotfix-lane parity
   - release-profile + evidence self-heal parity
   - longrun default policy (upgrade `beacon-v2-goal-durable-longrun`)
   - version-fleet ops parity
2. Regenerate `goalrun-main-axis.md` for v2.
3. Loom skill docs: same ops philosophy; no second entry; no default replace of beacon.
4. Implement may remain Python-backed until Rust Wave; **contracts must not diverge**.

## Route

Same as canonical review: `beacon-gen-change` for v1.6.8 program first; v2 truth mirror in same milestone.
