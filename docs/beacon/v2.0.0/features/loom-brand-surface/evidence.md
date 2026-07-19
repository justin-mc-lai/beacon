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

## Phase-2 public prefix mirror (2026-07-19)

- Generated `skills/loom/loom-*` for public progressive skills (see `skills/loom/mirror-manifest.json`)
- Content single-source remains `skills/beacon/*` via CONTENT_SOURCE
- skill_load_plan defaults brand=loom
- Isolated worktree path: `.loom/worktrees/<run_id>`
- Public CLI brand name: **`loom`** (Rust + Python); not `loom-v2` / `beacon-v2` as product name

## Brand correction (2026-07-19)

User intent: **Loom = Beacon 升级品牌（v2 产品线）**，不是 `loom-v2` 旁支命名。

- Public CLI name: **`loom`** (Rust bin + Python facade)
- Removed product naming: `loom-v2` / `beacon-v2` as user-facing brand
- Version remains `v2.0.0` as release line under Loom brand
