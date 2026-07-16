---
slug: markdown-only-project-version-governance
version: v1.5.2
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/archive/v1.5.2/features/markdown-only-project-version-governance/truth.md
  user_story: docs/beacon/archive/v1.5.2/features/markdown-only-project-version-governance/truth.md
  test_case: docs/beacon/archive/v1.5.2/features/markdown-only-project-version-governance/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
governance_parser_contract: beacon-project-governance-v1
---

# Feature Truth: Markdown-Only Project Version Governance

## Summary

Align version / topology / Git branch governance with v1.5.2 feature-package philosophy: **one Markdown authority**, **no governance JSON records**, **read and write through the same truth-map resolver**. Retire execution `branch-governance-*` / `git-workflow-*` / `deterministic-implementation-contract-*` as branch authority when governance truth exists.

## Canonical Governance Document

| Field | Value |
|---|---|
| Path | `docs/beacon/governance/project-version-governance.md` |
| Parser | `beacon-project-governance-v1` |
| Resolver | `resolve_project_governance(project_root, version=...)` |

Sections (machine contract):

- `global_topology` (topology_kind, default_execution_service)
- `service_bindings[]` (service_key, repo_root, role)
- `version_contracts/<version>` (participating_services, per_service_canonical_branch, branch_guard_mode, branch_governance)

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | md-only-authority | `docs/beacon/governance/project-version-governance.md` is the sole authority for topology, version contracts, and per-service canonical branches. |
| AC-002 | zero-governance-json | No governance JSON records under `.beacon/metadata/` (including `project-version-metadata.json`); strict verify fails closed if any remain after migration. |
| AC-003 | resolver-required | `beacon-toolkit-metadata`, `beacon-toolkit-branch-governance`, implement preflight, material gate, and doctor metadata verify consume `resolve_project_governance` only. |
| AC-004 | read-from-md | `load_project_metadata` (or successor) parses governance MD; it must not treat JSON as authority. |
| AC-005 | write-to-md-only | Metadata/branch-governance write transactions update governance MD only; they must not create or update governance JSON as authority. |
| AC-006 | no-execution-triple-authority | When governance MD exists for the active version, `load_execution_branch_contract` must not merge branch fields into implement contract (fail-closed or hard ignore with diagnostic). |
| AC-007 | unified-toolkit-transaction | Metadata and branch-governance toolkit surfaces share one governance MD transaction path (no split JSON vs execution sinks). |
| AC-008 | branch-guard-resolver-only | `_branch_guard_inputs` derives `expected_branch`, `git_roots`, `participating_services`, `service_branch_map`, and `branch_governance` from the resolver view without execution-contract residue. |
| AC-009 | monorepo-md-contract | Monorepo topology with multiple `service_bindings` and `per_service_canonical_branch` entries round-trips through governance MD parse and implement preflight. |
| AC-010 | migrate-and-delete-json | `beacon doctor metadata migrate-to-governance-md` (or equivalent) imports existing JSON envelope into governance MD and removes governance JSON files after successful verify. |
| AC-011 | material-gate-md-path | Material gate / release supplements reference governance MD via resolver, not hard-coded `.beacon/metadata/*.json` paths. |
| AC-012 | truth-map-surface | truth-map registers `project_governance` (or equivalent) as version governance truth for Git/topology, distinct from `SUMMARY.md` product boundary surfaces. |
| AC-013 | explicit-version-preflight | Explicit-version implement preflight resolves canonical branch/worktree from governance MD for the requested version; `origin/master` ancestry alone cannot pass preflight when canonical branch mismatches. |

## Authority

Feature package Markdown is requirement authority. Governance MD is operational truth for version/topology/Git branch contracts. Research documents under `docs/beacon/archive/v1.5.2/research/` are support evidence only.

## Research Provenance

| Research | Role |
|---|---|
| `version-governance-git-branch-closure.md` | Closure assessment, implement merge order, monorepo notes |
| `version-governance-md-only-convergence.md` | Parser contract, gap list, toolkit unification |
| `explicit-version-canonical-branch-worktree-preflight-gate.md` | Per-service canonical branch preflight intent (supersedes execution-triple branch authority) |
