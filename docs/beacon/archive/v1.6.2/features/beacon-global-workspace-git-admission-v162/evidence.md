# 证据：Global Workspace Git Admission v1.6.2

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|-------------------|--------|-------|
| planner-review | support_advisory | .beacon/state/planner-review/beacon-global-git-governance-admission/pln-review-20260622t093832z.json | indexed | change R2 |
| change-intent | support_advisory | user utterance：方案 A slash/skill Step 0 + 无 TTL | accepted R2 | beacon-gen-change |
| feature-package | requirement_truth | docs/beacon/archive/v1.6.2/features/beacon-global-workspace-git-admission-v162/truth.md | **frozen R2** | implement |
| package-tests | test_truth | docs/beacon/archive/v1.6.2/features/beacon-global-workspace-git-admission-v162/tests.md | draft R2 | truth.coverage |
| upstream-governance | requirement_truth | docs/beacon/v1.5.2/features/markdown-only-project-version-governance/truth.md | frozen | dependency |
| upstream-branch-gate | requirement_truth | docs/beacon/archive/v1.1.12/ implement branch gate | archived | dependency |

## 决策记录

- R1：workspace admit + 三层 defense + 4h TTL（planner draft）。
- **R2 change（用户确认方案 A）**：**Must** = skill Step 0 + CLI + dirty-only；**无 TTL**；hook **Should**。

## Gate 证据

| gate | status | artifact |
|------|--------|----------|
| TIG block | pass | 0 findings (2026-06-23) |
| feature-package-validation | pass | ac=11 tests=18 |
| freeze R2 | frozen | `beacon freeze` revision_id=R2 baseline `sha256:7c232f82…cdc65` |
| governance v1.6.2 | metadata | tx-project-governance-d165b22ba61349d3 |

## Boundary

本表不承载 formal QA/release verdict；authority 仅 `support_advisory` / `requirement_truth` / `test_truth`。

## Implementation handoff (2026-06-23)

| check | result | notes |
|-------|--------|-------|
| pytest `tests/test_v162_*.py` | **26 passed** | includes branch-preflight + governance waiver integration |
| `beacon workspace admit` | pass | feature worktree `beacon/v1.6.2/beacon-global-workspace-git-admission-v162` |
| `beacon implement plan` | **planned** | metadata branch mismatch waived when admission valid |
| `beacon implement run --dry-run` | **dry_run** | `workspace_admission_branch_guard=true` |
| `beacon doctor verify-materials --strict` | pass | post upgrade-package |
| `beacon qa run` | blocked | `evidence_binding_missing` — route formal verdict to `beacon-eval-qa` |

## R5 release proof (v1.6.4 line, 2026-07-06)

| check | result | notes |
|-------|--------|-------|
| `pytest tests/test_v162_delivery_program_branch_r5.py` | **7 passed** | AC-019–AC-022 unit coverage |
| v1.6.4 auto-test unit bundle | **28 passed** | `run-20260706T171931359390` |
| `beacon release check v1.6.4` | **pass** | `release_ready=true` after R5 on `main` |
| SidePilot admit v0.0.9 / v0.0.10 | **pass** | program-level worktree resolve |
| Friction queue | **resolved** | `73c1790d551e`, `025cd2a6322f`, `cd5f8a72940b` |

Release-facing doc: `docs/beacon/v1.6.4/release/v1.6.4.md` (R5 patch section).

### Code delta (implement continuation)

- `build_workspace_admission_branch_preflight()` — branch guard satisfied by valid admission artifact
- `_run_branch_preflight()` — short-circuit legacy canonical-branch check when admission valid
- `evaluate_implement_version_governance_preflight()` — waive metadata `branch_contract:*` failures when admission valid

