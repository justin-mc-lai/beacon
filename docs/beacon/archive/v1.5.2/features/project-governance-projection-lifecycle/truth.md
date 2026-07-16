---
slug: project-governance-projection-lifecycle
version: v1.5.2
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/archive/v1.5.2/features/project-governance-projection-lifecycle/truth.md
  user_story: docs/beacon/archive/v1.5.2/features/project-governance-projection-lifecycle/truth.md
  test_case: docs/beacon/archive/v1.5.2/features/project-governance-projection-lifecycle/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parent_feature: markdown-only-project-version-governance
governance_parser_contract: beacon-project-governance-v1
---

# Feature Truth: Project Governance Projection Lifecycle

## Summary

Minimal follow-on to `markdown-only-project-version-governance`: align **truth-map**, **sqlite projection**, and **version contract lifecycle** with `docs/beacon/global-boundaries.md` §4 (single canonical, projections hash-bound, fail-closed on drift).

Cross-version facts (`topology_kind`, `service_bindings`) remain **global once** in `docs/beacon/governance/project-version-governance.md`. This feature does **not** relocate docs-version, runtime version, skill profiles, or feature-package truth into that file.

## Non-Goals

| Item | Rationale |
|------|-----------|
| Per-version copies of topology/bindings | Already versionless; out of scope |
| New governance JSON authority | Parent feature AC-002 |
| “All project meta” in one MD | Violates layered canonical model; use separate surfaces |

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | truth-map-single-truth | `VERSION_GOVERNANCE_SURFACES.project_governance` remains the only truth surface (`version_governance_truth`, `is_truth=True`) for `docs/beacon/governance/project-version-governance.md`. |
| AC-002 | truth-map-no-dual-role | `GENERATED_GOVERNANCE_SURFACES` must not register the same governance MD path with `generated_governance_state_not_truth`. Legacy alias `project_version_metadata` may remain only if it points to a **deprecated** path (e.g. removed `.beacon/metadata/project-version-metadata.json`) or is removed; never dual-classify the live MD. |
| AC-003 | truth-map-resolver-docs | `resolve_truth_map` / entrypoint inventory documents governance truth vs sqlite projection roles for operators and skills. |
| AC-004 | sqlite-hash-projection | `project_metadata_current` / events store `source_hash` from governance MD frontmatter; full `payload_json` is optional diagnostic cache, not a competing write authority. |
| AC-005 | verify-projection-drift | `doctor metadata verify` (and governance verify helper) fails closed when MD `source_hash` ≠ sqlite `source_hash` or sqlite row missing while MD authoritative (`reason_code`: `governance_projection_drift`). |
| AC-006 | sqlite-not-write-authority | No commit path may load sqlite `payload_json` to mutate governance MD; commits flow MD → sqlite projection only. |
| AC-007 | version-contract-validation-state | `beacon-project-governance-v1` accepts `validation_state: active \| archived` on each `### <version>` contract block (default `active`). |
| AC-008 | resolver-active-contract | `resolve_project_governance(version=…)` uses **active** contract for branch preflight; **archived** contracts are ignored unless `--include-archived` (doctor/inspect only). |
| AC-009 | doctor-archive-version | `beacon doctor metadata archive-version --version <v>` sets contract `validation_state: archived` via the same MD transaction as upsert (no JSON sink). |
| AC-010 | doctor-prune-archived | `beacon doctor metadata prune-archived` removes archived `###` blocks from governance MD with `--dry-run` default; strict verify passes after prune. |

## Authority

Feature package Markdown is requirement authority. Governance MD remains operational truth for Git/topology/version-branch contracts (parent feature). Research and brainstorm outputs are support-only.

## Research Provenance

| Artifact | Role |
|---|---|
| `version-governance-md-only-convergence.md` §4.2 | §4 projection principles; Phase 2 hash |
| `markdown-only-project-version-governance/truth.md` | Parent delivery baseline |
| `global-boundaries.md` §4 | Normative anti-drift rules |
