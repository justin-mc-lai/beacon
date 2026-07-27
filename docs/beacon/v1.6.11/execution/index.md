# Execution Index (v1.6.11)

## Human Primary Surface

- `architecture-blueprint.md`
- `boundaries.md`
- Feature-level markdown notes under `execution/`
  - `requirement-clarity-*-v1611.md`
  - `deterministic-implementation-contract-*-v1611.md`
  - `git-workflow-*-v1611.md`
  - `qa-acceptance-brief-*-v1611.md`
  - `implementation-summary-*-v1611.md`
  - `tasks-*-v1611.md`

## Machine Secondary Surface

- `docs/beacon/v1.6.11/.machine/execution/`
  - implementation plans / progress
  - delivery baseline + host
  - git workflow contracts
  - acceptance kits / QA acceptance projections
  - revision + truth-review gate payloads

## Program Scope

- Program: `beacon-plan-goal-task-closure-v1611`
- Lakes (L0–L8):
  - `atomic-task-graph-compiler-v1611`
  - `brownfield-context-resolver-v1611`
  - `cancel-replan-next-ready-v1611`
  - `change-impact-state-diff-v1611`
  - `contract-baseline-convergence-v1611`
  - `convergence-verifier-v1611`
  - `drift-padding-review-gate-v1611`
  - `intent-completeness-engine-v1611`
  - `task-progress-ledger-v1611`

## Notes

- `execution/` stays Markdown-first for humans.
- `.beacon/` remains runtime internal state only.
- Truth freezes only on `main`; implement/QA run in admitted worktrees.
- Host Agent (skill-authored fill) is the primary package fill path; local semantic compile is fallback only.
