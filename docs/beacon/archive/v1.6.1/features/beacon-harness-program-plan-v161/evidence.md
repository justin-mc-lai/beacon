# 证据：Beacon Harness Program Plan v1.6.1

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| planner-research | support_advisory | docs/beacon/archive/v1.6.1/research/beacon-harness-program-plan-v161.md | promoted | truth.define |
| change-record | support_advisory | docs/beacon/archive/v1.6.1/change/beacon-harness-program-plan-v161.md | accepted-for-change | refreeze |
| feature-package | requirement_truth | docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md | frozen R4 | implement |
| operator-guide | support_advisory | docs/beacon/archive/v1.6.1/execution/long-task-operator-guide.md | present | operator |
| package-tests | test_truth | docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/tests.md | authoritative | truth.coverage |
| program-contract | support_advisory | docs/beacon/archive/v1.6.1/execution/program-plan-contract.md | normative | implement |
| upstream-harness-taxonomy | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | frozen | dependency |
| upstream-pln-review | requirement_truth | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md | frozen | dependency |
| upstream-tig | requirement_truth | docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md | frozen | dependency |
| upstream-loop-orchestrator | requirement_truth | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md | frozen R10 | dependency |
| upstream-loop-v161 | requirement_truth | docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md | frozen R1 | dependency |

## 决策记录

- 用户确认：v1.6.1 冻结 program harness，覆盖书籍目录章节、海湖、治理、change 闭环。
- **R4（2026-06-16）**：implementation-first-reconciliation refreeze + operator guide + v1.6.1 release line GO。
- **R3（2026-06-15）**：真实 `--mode program` FSM + `beacon-loop goal` 主入口 + loop v161 handoff（路线 A：pre-main）。
- 版本线：`beacon/version-truth.json` 升级 `v1.6.1` 为 current_runtime_release。

## Gate 证据（R3 freeze — 2026-06-15）

| gate | command | status | notes |
|------|---------|--------|-------|
| TIG | `beacon doctor verify-truth-integrity … --mode block` | pass (0 findings) | cross-package AC-068/072 delegated |
| refreeze-chain | `beacon change … --refreeze-chain` | blocked:legacy_cutover_required | 与 R2 同路径 |
| freeze R3 | `beacon freeze … --version v1.6.1` | frozen | AC-PBP-016/027/029/030 truth 闭合 |

## Gate 证据（R2 hygiene refreeze — 2026-06-15）

| gate | command | status | artifact |
|------|---------|--------|----------|
| TIG hygiene | `beacon doctor verify-truth-integrity … --mode block` | pass (0 findings) | embedded in freeze `truth_integrity_gate` |
| requirement-clarity | `beacon doctor sync-requirement-clarity …` | PASS | `docs/beacon/archive/v1.6.1/.machine/execution/requirement-clarity-beacon-harness-program-plan-v161.json` |
| truth-map rebuild | `beacon truth-map rebuild-machine …` | written | `.machine/requirement/*.truth-map.json` |
| refreeze-chain | `beacon change … --refreeze-chain` | blocked:legacy_cutover_required | agent_surface + governance（见 change refreeze-summary） |
| freeze hygiene | `beacon freeze … --version v1.6.1` | frozen | baseline `sha256:8552009a017ea6e0cb02388e945a164b9a4c8a383004ca603a4cf05e3de5708b` |
| skill triad | `skills/beacon/beacon-pln-program{,-auto,-interactive}/` | present | TASK-PBP-E02/E04 pass |

## Gate 证据（implement — 2026-06-15）

| gate | command | status | artifact |
|------|---------|--------|----------|
| program CLI | `beacon program validate-graph/guard-sea-single-lake/freeze --help` | pass | `beacon/commands/program.py` |
| plan CLI | `beacon plan start --mode auto --json` | pass | `beacon/commands/plan.py` |
| state tests | `pytest tests/test_program_plan_state_contract.py tests/test_program_plan_cli.py` | 24 passed | Phase B–F unit coverage |
| agent surface | `beacon doctor verify-agent-surface --version v1.6.1 --strict` | pass | program skills preamble/gate aligned |
| materials | `beacon doctor verify-materials --version v1.6.1 --strict` | pass | governance stubs present |
| TIG | `beacon doctor verify-truth-integrity … --mode block` | pass (0 findings) | AC-PBP-008 |
| change intent | `beacon change --program <slug>` append + promotion_diff gate | implemented | `beacon/utils/program_change_intent.py` |
| ralph implement | `beacon implement run … --mode ralph` | blocked:legacy_cutover_required | route: `beacon truth-cutover run … --apply` |
| verify-closure | `beacon skill package verify-closure --version v1.6.1` | pass (closure_allowed=true) | AC-PBP-009 |

## Context traceability

- 对话：OSS 全功能复刻、海→湖、书籍真相、双模式 program plan、LLM 治理、change 闭环 → AC-PBP-001..028
