# Program Plan Contract v1.6.1

## Program directory layout

```text
docs/beacon/<version>/programs/<program-slug>/
  program-manifest.md       # 目录：User Intent 一行、scope_mode、source refs
  module-map.md             # 大纲：源模块 → Beacon 映射
  feature-graph.json        # 海→湖：slug、depends_on、parity_subset、lake_or_ocean=湖
  program-parity-matrix.md  # 全书 capability 对照
  change-intent-log.jsonl   # change 审计链（append-only）
```

Authority: `support_advisory` until promoted via feature truth or governed change. Not package truth.

## Program Plan Loop (planner harness)

| Round | Name | Output |
|-------|------|--------|
| P0 | source_scan | source_capability_inventory |
| P1 | module_map | module-map.md |
| P2 | program_review | review-artifact (intent + parity + deferral) |
| P3 | feature_graph | feature-graph.json |
| P4 | user_ack | program-ack.json |
| P5..P5+N | per_lake_truth | frozen features/<slug>/ packages + per-lake `truth-promotion.json` |
| P6 | program_freeze | program-truth-freeze.json |

## Per-lake truth promotion (P5)

Each lake **must** record machine-readable seven-round closure **before** program P5 promotes that lake to frozen package truth.

Artifact path (normative):

```text
docs/beacon/<version>/programs/<program-slug>/lakes/<lake-slug>/truth-promotion.json
```

Required fields:

| Field | Meaning |
|-------|---------|
| `program_slug` | Program identifier |
| `lake_slug` | Lake feature slug |
| `truth_freeze_loop_round` | Last completed Round 0–7 (or block at round) |
| `status` | `complete` \| `blocked` |
| `commands` | CLI commands executed (e.g. `beacon freeze`, TIG block) |
| `block_reason` | Required when `status=blocked` |

Program P6 **must not** pass unless every lake in `feature-graph.json` has `truth-promotion.json` with `status=complete` or an **accepted** deferral row in `program-parity-matrix.md`.

## Plan mode (R2)

`plan_mode` is selected **after** `program_intent_captured` and **before** P0 execution profile diverges.

| `plan_mode` | Skill delegate | P0–P4 profile |
|-------------|----------------|---------------|
| `auto` | `beacon-pln-program-auto` | machine inventory + sectional P4 ack |
| `interactive` | `beacon-pln-program-interactive` | BR rounds + brainstorm + sectional P4 ack |
| `auto-detect` | umbrella classifies then delegates | — |

**Classifier (deterministic):**

1. CLI `--mode auto|interactive` wins
2. else source URL + full-parity signals → `auto`
3. else brainstorm/探讨/对齐 signals → `interactive`
4. else low confidence → umbrella asks **one** multiple-choice question; record `plan_mode` + `reason` in `program-manifest.md` frontmatter

**Operator cognitive load:** one public entry — `beacon plan start` or `beacon-pln-program`; artifacts only under `programs/<slug>/`.

## CLI (normative, Phase E)

```bash
beacon plan start "<utterance>" --program <slug> --version <v> \
  --mode auto|interactive|auto-detect --source <url> --json
```

## Change closure

```text
change utterance → change-intent-log.jsonl
  → beacon-gen-change (affected slugs)
  → beacon-pln-review (promotion_diff vs frozen + change intent)
  → user ack
  → update module-map / feature-graph and/or lake truth packages
  → gen-truth rounds + TIG block + beacon-gen-refreeze
  → program_freeze_gate re-run if graph structure changed
```

## Governance

- Planner (`beacon-pln-*`) writes program artifacts only.
- Generator (`beacon-gen-truth`) writes per-lake package truth only via resolver + 7-round loop.
- Evaluator issues QA/release; loop runner does not self-certify.
- TIG `mode=block` mandatory before any lake or program-level freeze recommendation.
