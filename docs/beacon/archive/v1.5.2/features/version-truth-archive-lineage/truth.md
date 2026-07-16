---
slug: version-truth-archive-lineage
version: v1.5.2
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/truth.md
  user_story: docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/truth.md
  test_case: docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parent_feature: project-governance-projection-lifecycle
catalog_parser_contract: beacon-version-truth-catalog-v1
---

# Feature Truth: Version Truth Archive Lineage

## Summary

Extend **`beacon-archive`** with an MD-only **version truth catalog** orthogonal to **`project-version-governance.md`**. Active delivery truth stays under `docs/beacon/<version>/` (default window: **3**). Archived truth relocates to `docs/beacon/archive/<version>/` (not deleted). Operators get four daily verbs — **status**, **history**, **map**, **cutover** — backed by catalog commit, projection drift verify, `lineage`, and `inventory`.

## Non-Goals

| Item | Rationale |
|------|-----------|
| New lifecycle stage or release gate | Archive remains support-only (global-boundaries) |
| JSON/sqlite as catalog commit source | v1.5.2+ MD evolution line |
| Governance MD holding feature requirements | Separate planes; feature truth stays in `features/<slug>/truth.md` |
| Standing per-slug lineage MD forest | Command-first; optional `--emit-md` only |
| Slug alias catalog section (C5) | YAGNI until rename pain appears |

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | md-catalog-canonical | `docs/beacon/governance/version-truth-catalog.md` is the sole commit source for version-level truth placement; `parser_contract: beacon-version-truth-catalog-v1`; frontmatter carries `transaction_id`, `source_hash`, `active_delivery_window`. |
| AC-002 | active-window-three | Catalog lists exactly **3** `validation_state: active` versions; their `truth_root` values are `docs/beacon/<version>/` only. |
| AC-003 | physical-archive-relocate | Archived versions have `truth_root` under `docs/beacon/archive/<version>/`; `catalog apply` / `bootstrap --confirm` **moves** trees (relocate, not delete); bounded internal link rewrite per closure C3. |
| AC-004 | drift-verify-strict | `beacon doctor verify-version-truth-catalog --strict` fails closed on MD ↔ `.machine/version-truth-catalog.json` mismatch, missing sqlite `source_hash` row (when shared store used), or on-disk path ≠ catalog `truth_root`. |
| AC-005 | resolver-active-default | Default delivery commands (`implement`, `qa`, `release`, truth-map bulk scans) resolve roots from catalog **active** set only; explicit `--version` may target archived roots for inspect-only surfaces; non-active delivery without `--include-archived` fails closed. |
| AC-006 | feature-discovery-truth | Unified `discover_features(version)` lists `features/*/truth.md` on v1.5.2+ (not `prd/` only); used by archive plan/status and truth-map inventory. |
| AC-007 | archive-lineage | `beacon archive lineage <slug> [--from v] [--to v]` returns ordered hops with `truth_path`, optional `change_path`, freeze revision / source_hash across active + archive roots. |
| AC-008 | archive-inventory | `beacon archive inventory [--version auto]` builds feature × AC matrix from active versions' `truth.md` AC tables; archived omitted unless `--include-archived`. |
| AC-009 | archive-index-generated | `docs/beacon/archive/INDEX.md` is regenerated on every `catalog apply` / `bootstrap --confirm`; not hand-edited; lists active set, archived count, feature counts, quick commands. |
| AC-010 | catalog-bootstrap-once | `beacon archive catalog bootstrap --active v1.5.0,v1.5.1,v1.5.2 --dry-run` previews ~46 relocations; `--confirm` performs one atomic transaction: write catalog MD + mv trees + INDEX + projections + strict verify. |
| AC-011 | skill-surface-examples | `beacon-archive` skill documents decision boundary, four operator verbs, and scenario examples A–F (cutover, historical audit, cross-version evolution, capability map, feature retire, learnable archive). |
| AC-012 | global-boundaries-section | Merge global-boundaries **§4.1 MD-only catalog and archive plane** and §1 support-surface clarification for archive vs change; drift on active plane blocks freeze/qa/release per §4. |

## Authority

Feature package Markdown is requirement authority. `version-truth-catalog.md` is operational truth for version-tree placement only. Research and brainstorm outputs are support-only until refrozen here.

## Research Provenance

| Artifact | Role |
|---|---|
| `research/version-truth-archive-lineage.md` | Brainstorm + locked decisions |
| `governance/project-version-governance.md` | Sibling plane (branch contracts) |
| `global-boundaries.md` §4 | Normative anti-drift; §4.1 to be merged by this feature |
