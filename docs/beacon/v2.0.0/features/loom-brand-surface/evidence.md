---
slug: loom-brand-surface
version: v2.0.0
status: frozen
revision_id: R1
---

# Evidence Index: loom-brand-surface

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/v2.0.0/features/loom-brand-surface/truth.md | frozen | truth |
| analysis | support_advisory | docs/beacon/v2.0.0/research/beacon-v2-rename-loom-subagent-trace-pln-review.md | indexed | change |
| user_go | support_advisory | User GO 2026-07-18 Loom brand + dual-install | indexed | change |

## Boundary

`evidence.md` is an index/read model only.

## Implement + contract QA (2026-07-18)

- Product Goal run: `pgr-51a763f2a691`
- Suite: `python3 -m pytest tests/test_v200_*.py` → **90 passed**
- Scorecard: `.beacon/qa/features/v2-0-0-full-delivery/scorecard.json`
- Release: **human gate** (not auto-confirmed)
- Open: full Rust kernel P1/P2/carrier (track_v2); W4 default BEACON_V2 still forbidden
