---
slug: loom-cross-track-adversarial-release
version: v2.0.0
status: frozen
revision_id: R1
---

# Evidence Index: loom-cross-track-adversarial-release

| Surface | Authority | Canonical Artifact | Status |
|---------|-----------|--------------------|--------|
| requirement_truth | requirement_truth | docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/truth.md | frozen |
| acceptance | acceptance_truth | docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/truth.md | frozen |
| test_case | test_truth | docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/tests.md | frozen |
| planner | support_advisory | .beacon/state/planner-review/beacon-v2-rust-kernel-redesign/pln-review-20260719t110159z.json | accepted |
| program | support_advisory | docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json | frozen |
| parent-kernel | support_advisory | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md | indexed |
| change | support_advisory | docs/beacon/v2.0.0/change/loom-kernel-closure-w1w5-v200.md | indexed |

## Boundary

Index only — formal implement/QA verdicts appended after wave implementation.

## Implement evidence (W4a)
- `beacon-gate/src/release_adversarial.rs` AC-166/167
- CLI: `beacon-v2 release check --claim-track v2 --with-adversarial`
- Tests: w3_w4a_gates tc166/tc167
- Timestamp: 2026-07-19T11:55:39Z
