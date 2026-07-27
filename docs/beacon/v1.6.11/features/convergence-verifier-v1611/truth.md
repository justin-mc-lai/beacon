---
slug: convergence-verifier-v1611
version: v1.6.11
status: frozen
revision_id: R2
language: zh
domain_required: true
domain_kind: gate
ux_required: false
ux_deferred: true
package_maturity: filled
materials_status: current
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
program_ref: docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/program-manifest.md
truth_map_contract: beacon-truth-map-v1
participating_services: beacon
git_canonical_branch: main
previous_revision: R1
change_reason: "D3: authenticated PAC trace and full-package fill convergence"
parent_truth: docs/beacon/v1.6.11/features/cancel-replan-next-ready-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.11/features/task-progress-ledger-v1611/truth.md; docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md; docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md; docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/convergence-verifier-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/convergence-verifier-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/convergence-verifier-v1611/tests.md
---

# Requirement Truth: L8 Convergence Verifier

## 人话

最后不能由 AI 说“差不多完成了”。系统要证明每条用户意图、路径、验收、状态、任务和证据都闭环，才允许 Goal 完成。

- 能做：六层闭环、路径一致性、stale 检查和 verifier refs
- 不能做：只看任务勾选，或 subagent 直接完成 Goal
- 怎样算完：所有 required path closed，所有 must covered，所有完成任务有有效证据

## User Intent

给“大目标真正落地”一个可计算、可审计的完成定义。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
completion_owner: GoalRun
public_lifecycle: beacon_1plus6_only
verifier_role: evaluate_only
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 汇总九湖与任务账本。2. 校验六层追溯。3. 检查 stale/blocked/cancel replacement。4. 输出 pass 或明确缺口。5. 仅 pass 后由 Goal owner 完成。

## First principles

- 完成来自 frozen truth 与 evidence，不来自 agent 自述。
- cancelled 可以关闭非必要路径；必要路径必须替代或阻断。
- verifier 只裁决，不修 Truth、不实现代码。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| ClosureMatrix | intent, path, ac, state, task, evidence | 六层闭环 |
| VerificationFinding | layer, ref, reason, route | 未闭环项 |
| GoalVerdict | status, refs, graph_revision, truth_revisions | 最终裁决 |
| GoalRun | run_id, program_slug, graph_revision, truth_revision_set, ready_set, human_decisions, admission_refs, trace_refs, verifier_refs | 完成权与全局上下文所有者 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-CNV-01 | user | must | AC-CNV-001 | covered |
| INT-CNV-02 | closure | must | AC-CNV-002 | covered |
| INT-CNV-03 | stale | must | AC-CNV-003 | covered |
| INT-CNV-04 | ownership | must | AC-CNV-004 | covered |
| INT-CNV-05 | recovery | must | AC-CNV-005 | covered |
| INT-CNV-06 | goal-context | must | AC-CNV-006 | covered |
| INT-CNV-07 | lifecycle-boundary | must | AC-CNV-007 | covered |
| INT-CNV-08 | pac-trace | must | AC-CNV-008 | covered |
| INT-CNV-09 | authenticated-program-freeze | must | AC-CNV-009 | covered |
| INT-CNV-10 | fill-chain-convergence | must | AC-CNV-010 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-CNV-001 | ClosureMatrix 覆盖 intent/path/AC/state/task/evidence 六层并可双向追溯 |
| AC-CNV-002 | Goal pass 要求 must intents covered、required paths closed、AC verified、状态合法、任务终态一致、证据有效 |
| AC-CNV-003 | 任一 Truth/graph/material/evidence stale 均阻断完成并给出重建 route |
| AC-CNV-004 | subagent/task executor 不能直接完成 GoalRun；只有 Goal owner 在 verifier pass 后转换 complete |
| AC-CNV-005 | fail verdict 必须列出最小未闭环集合及 recommended next-ready/replan/truth/qa route |
| AC-CNV-006 | GoalRun 必须持有 `run_id`、program slug、graph revision、truth revision set、current ready set、human decision refs、admission/worktree refs、`agent_trace.v1` refs 与 verifier refs；任一 required ref 缺失或 stale 均阻断 complete |
| AC-CNV-007 | L0–L8 只能映射到既有 goal→plan→truth→可选 design→implement→qa→release；不得新增 public harness，且 verifier pass 只产生裁决，最终 complete 仍由 Goal owner 执行 |
| AC-CNV-008 | Program trace matrix 必须实现 `PAC → lake slug → AC IDs → TC IDs → task/evidence refs → R2/final baseline hash` 全链；任一 PAC 只映射湖名、无 TC、无 evidence 或 hash stale 都阻断 Program freeze |
| AC-CNV-009 | Program freeze 必须逐湖重新执行并验证 package validation pass、Truth Review pass、human ack、R2 revision 与当前四文件 hash 一致、promotion receipt hash-authenticated；不得仅信任 promotion JSON 的 `status=complete` |
| AC-CNV-010 | `truth-fill-transaction.v1` 的 scaffold/request/response/schema/patch/projection/validation/review/human-ack/freeze 步骤必须全部闭合，且 L5 progress 与 L7 recovery refs 可追溯，才可把 package 与 Program 判定 frozen |

## Domain FSM GoalConvergence

| State | From | Guard |
|-------|------|-------|
| verification_ready | —, blocked, verified | lakes available or upstream refs updated |
| evaluating | verification_ready | required refs current |
| verified | evaluating | six closure layers pass |
| blocked | evaluating | minimum closure gap found |
| complete | verified | Goal owner authorized |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| verification_ready | verify | lakes_available | evaluating | build closure matrix |
| evaluating | pass | six_layers_closed | verified | emit verifier refs |
| evaluating | gap | finding_present | blocked | emit minimal gaps |
| blocked | inputs_updated | refs_current | verification_ready | schedule recheck |
| verified | owner_complete | owner_authorized | complete | close GoalRun |
| verified | upstream_stale | revision_changed | verification_ready | revoke verdict |

终态：`complete`。

## Illegal transitions

- `verification_ready → complete`
- `evaluating → verified` with blocked/stale required path
- subagent `verified → complete`
- revoked verdict remaining complete
- GoalRun complete with missing admission/trace/human-decision refs
- internal L0–L8 stage exposed as a new public harness
- PAC 只映射湖名而未落到 AC/TC/task/evidence/revision/hash
- Program freeze 仅依据 promotion status string
- fill transaction 任一步缺失、hash 漂移或 recovery 未闭环

## Non-goals

- verifier 自动修实现或改写 Truth。
- 用任务完成率阈值替代 required path closure。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] Goal owner、GoalRun refs 与 public lifecycle 边界获确认（`user-confirmation-2026-07-27`）
