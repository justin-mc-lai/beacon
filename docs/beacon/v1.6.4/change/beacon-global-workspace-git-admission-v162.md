# Change Record: Workspace Admission Nested-Ref Coexistence R7

**version**: `v1.6.4`  
**feature**: `beacon-global-workspace-git-admission-v162`  
**revision**: `R7`  
**status**: `requirement-change-draft`  
**reason**: After doctor path repair, QA lake admits still fail because bare aggregation ref `beacon/v1.6.4` conflicts with child feature refs, and stale per-feature deterministic contracts force program-level resolution.

## Accepted Change Intent

1. Nested-ref coexistence: do not select bare `beacon/<version>` when child refs exist; default to `beacon/<version>/_agg` or governance override.
2. Per-feature deterministic contracts are not program-level authority by themselves.
3. Aggregation worktree must not target the primary checkout root.
4. Nested-ref failures emit `aggregation_branch_nested_ref_conflict`.

## Scope

- `resolve_workspace_branch_targets` / workspace admit contract
- R7 AC-028..AC-031 and UD-032..UD-035
- Preserve R6 AC-023..AC-027

## Non-Goals

- no remote feature-branch cleanup requirement
- no QA/release verdict from generator
- no SidePilot-specific hard-code

## Downstream

- implement: `beacon-gen-implement`
- qa: `beacon-eval-qa`
- release: `beacon-eval-release`
