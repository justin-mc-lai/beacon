---
slug: atomic-task-graph-compiler-v1611
version: v1.6.11
status: frozen
revision_id: R2
language: zh
domain_required: true
domain_kind: platform
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
change_reason: "D3: deterministic tests/tasks/evidence projection from accepted full-package truth"
parent_truth: docs/beacon/v1.6.11/features/change-impact-state-diff-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md; docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/atomic-task-graph-compiler-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/atomic-task-graph-compiler-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/atomic-task-graph-compiler-v1611/tests.md
---

# Requirement Truth: L4 Atomic Task Graph Compiler

## 人话

把确认后的 Journey、AC 和状态差异编译成真正可执行的小任务，并明确谁依赖谁、怎么验证、证据放哪里。

- 能做：生成可承载 100+ 节点的原子任务 DAG 与 ready set
- 不能做：为了“上百个”而拆碎注水，或产生无需求落点的孤儿任务
- 怎样算完：每任务都有 intent/journey/AC/code/dependency/verification/evidence 绑定

## User Intent

让详细任务清单既足够细，又始终能追溯回用户目标。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
task_capacity: 100_plus_without_count_kpi
subagent_mode: intent_on_with_honest_fallback
implementation_admission: shared_real_git_worktree
completion_owner: parent_goal_owner
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 读取 approved Change。2. 按最小可验证单元编译任务。3. 建依赖与并行边。4. 校验孤儿、环和不可验证任务。

## First principles

- 原子性指单一可验证结果，不指最少代码行。
- 任务数量是容量，不是 KPI。
- 无 intent/AC 映射的任务默认是 orphan/padding。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| TaskNode | id, intent_ref, journey_ref, ac_ref, code_scope, verify, evidence, execution_mode, required_role, delegation_reason, service, worktree_ref, admission_ref, cwd_ref, head_ref | 原子任务 |
| DependencyEdge | from, to, required, replacement_policy | DAG 边 |
| ReadySet | graph_revision, task_ids | 当前可调度任务 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-DAG-01 | user | must | AC-DAG-001 | covered |
| INT-DAG-02 | trace | must | AC-DAG-002 | covered |
| INT-DAG-03 | dependency | must | AC-DAG-003 | covered |
| INT-DAG-04 | anti-padding | must | AC-DAG-004 | covered |
| INT-DAG-05 | scale | must | AC-DAG-005 | covered |
| INT-DAG-06 | delegation | must | AC-DAG-006 | covered |
| INT-DAG-07 | honest-runtime | must | AC-DAG-007 | covered |
| INT-DAG-08 | worktree | must | AC-DAG-008 | covered |
| INT-DAG-09 | deterministic-projection | must | AC-DAG-009 | covered |
| INT-DAG-10 | semantic-compile-migration | must | AC-DAG-010 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-DAG-001 | Journey/AC/FSM diff 编译为最小可独立验证的 TaskNode |
| AC-DAG-002 | 每 TaskNode 绑定 intent、journey、AC、code scope、verification command、evidence path |
| AC-DAG-003 | 图必须无环；依赖未满足时任务不能进入 ready |
| AC-DAG-004 | 无需求落点、重复语义或只为增加数量的任务标记 orphan/padding 并阻断 |
| AC-DAG-005 | 图与查询/聚合接口可承载 100+ 节点，不设最低任务数 |
| AC-DAG-006 | 每个可委派 TaskNode 声明 `execution_mode`、`required_role`、`delegation_reason`、输入合同和输出 evidence contract；子代理只能返回 finding/patch/evidence，不能转换 Goal、Truth、QA 或 release 终态 |
| AC-DAG-007 | 仅显式 intent-on 才规划 host subagent；host runtime 不可用时必须记录 `single_process_multi_reviewer` 与 `fallback_reason`，不得宣称 parallel |
| AC-DAG-008 | 每个 implementation TaskNode 必须在 dispatch 前绑定 service、shared admission ref、真实 git worktree、cwd 与 HEAD；branch-only、soft skip、mkdir-only、empty gitlink、hook-installed 均不能进入 running |
| AC-DAG-009 | CLI 必须从已校验的 canonical truth 结构确定性再生成 `tests.md`、`tasks.md`、`evidence.md`；每个 AC 至少映射一个 Command+Assertion TC，每个 task 包含 `ac=` 与 `evidence=`，每个 evidence ref 可回到 transaction/revision/source hash |
| AC-DAG-010 | 旧 PRD/User Story semantic compile 的角色、故事、验收与测试语义必须迁移为当前 package 的 Intent/Journey/AC/TC/Task/Evidence 图，不得生成或依赖平行旧 shape 作为执行输入 |

## Domain FSM AtomicTaskGraph

| State | From | Guard |
|-------|------|-------|
| input_ready | — | approved Change current |
| compiling | input_ready, blocked, stale | compile or rebuild requested |
| validating | compiling | nodes emitted |
| ready | validating | DAG, bindings and admission requirements valid |
| blocked | validating | cycle, orphan, padding or unbound execution contract |
| stale | ready | upstream revision changed |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| input_ready | compile | change_approved | compiling | emit nodes |
| compiling | validate | nodes_emitted | validating | check bindings and DAG |
| validating | pass | no_cycle_no_orphan | ready | compute ready set |
| validating | fail | findings_present | blocked | publish findings |
| blocked | revise | change_or_rules_updated | compiling | rebuild graph |
| ready | upstream_refreeze | revision_changed | stale | invalidate graph |
| stale | recompile | inputs_current | compiling | rebuild graph |

终态：`ready`。

## Illegal transitions

- `input_ready → ready`
- `validating → ready` with cycle/orphan/unbound task
- stale graph dispatching tasks
- implementation TaskNode dispatched without real-worktree admission
- unavailable host runtime reported as parallel subagent execution
- child executor closing GoalRun or freezing Truth
- 手工独立编辑 tests/tasks/evidence 造成 canonical truth 反向漂移
- semantic compiler 只生成旧 PRD/User Story 文件而未进入当前 task graph

## Non-goals

- 强制每个目标拆成至少 100 个任务。
- 在编译器内执行任务。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] 原子性、delegation 与 worktree admission 规则获人工确认（`user-confirmation-2026-07-27`）
