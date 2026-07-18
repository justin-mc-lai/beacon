---
slug: beacon-v2-goal-durable-longrun
version: v2.0.0
status: frozen
revision_id: R1
---

# Evidence Index

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md | frozen | truth |
| beacon-gen-truth | test_truth | docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tests.md | frozen | truth |
| upstream | requirement_truth | docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md | frozen | parity |
| program | support_advisory | docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json | indexed | program |
| research | support_advisory | docs/beacon/v2.0.0/research/beacon-v2-goal-durable-longrun.md | indexed | change |
| parent | requirement_truth | docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/truth.md | frozen | dependency |

## Boundary

`evidence.md` is an index/read model only.

## Implement + contract QA (2026-07-18)

- Product Goal run: `pgr-51a763f2a691`
- Suite: `python3 -m pytest tests/test_v200_*.py` → **90 passed**
- Scorecard: `.beacon/qa/features/v2-0-0-full-delivery/scorecard.json`
- Release: **human gate** (not auto-confirmed)
- Open: full Rust kernel P1/P2/carrier (track_v2); W4 default BEACON_V2 still forbidden
