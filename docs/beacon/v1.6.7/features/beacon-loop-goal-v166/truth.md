---
slug: beacon-loop-goal-v166
version: v1.6.7
status: frozen
revision_id: R7
language: zh
change_reason: R7 - Intent-aware loop continuation + topology_gate consumption + dual runtime CLI/host parity; promotion_ref friction:2e306f7acea7
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-loop-goal-v166/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-loop-goal-v166/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-loop-goal-v166/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-loop-goal-v166/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-loop-meta-remediation-v166/feature-graph.json
---

# Requirement Truth: Loop Goal Orchestrator v1.6.6

## Overview

Beacon v1.6 公开 host-visible skill surface 冻结为 38 个 skill：planner(7) / generator(11) / evaluator(5) / governor(15)。每个 skill 在单次调用内有 hard gate 互斥边界——planner 不能 implement，generator 不能自证完成，evaluator 不能改 truth。但用户缺少一个 **跨 harness 编排入口**，能用一个提示词驱动 truth → implement → QA → release 全流程自动运行。

本 feature 定义 `beacon-loop-goal` **公开 host-visible governor 编排 skill**——它不执行任何 harness 职责，只做路由、状态追踪和阶段决策。它通过顺序加载其他 37 个公开 skill（不嵌套、不自我编排），在文件状态上判断阶段转换，支持 auto-decide 模式（release 门永远需要人工确认）。

## User Intent（一行）

一个 governor 编排 skill，用提示词驱动 Beacon 全流程（truth → implement → QA → release）自动闭环，每个阶段顺序加载对应 skill，编排器自身不执行任何 harness 职责。

## User Intent Snapshot

- user_prompt: "跨 harness 全职责 loop goal skill，提示词驱动自动闭环"
- lake_or_ocean: 海（跨 4 harness 编排，已拆分为 Alignment Surface）
- scope_mode: full_parity
- program_ref: docs/beacon/v1.6.7/programs/beacon-loop-meta-remediation-v166/feature-graph.json
- silent_scope_change_allowed: false

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LG-001 | Harness 类型 | **governor**——编排 = 路由 + 状态追踪，不执行 truth/implement/QA/release |
| UD-LG-002 | 调用模式 | **顺序加载**（agent 加载完一个 skill 后编排器才做下一步决策），不嵌套调用 |
| UD-LG-003 | 状态传递 | **文件系统状态**（`.beacon/state/loop-goal/`），不依赖 agent 内存 |
| UD-LG-004 | Auto-decide 白名单 | truth freeze / implement start / QA start 可 auto-decide；**release 永远人工确认** |
| UD-LG-005 | Error 路由 | 任何阶段失败 → `beacon-gov-debug` → 修复后回到对应阶段 |
| UD-LG-006 | 发布形态 | `beacon-loop-goal` 是公开 host-visible governor skill；v1.6 taxonomy、agent surface expected list、skill inventory/count、release governance 必须接受它 |
| UD-LG-007 | Truth-on-main 物理闭环 | 需求真相 **只能** 在 governance `truth_canonical`（默认 `main`/`master`）上编写、reopen、freeze/refreeze；feature worktree 不得成为 requirement authority |
| UD-LG-008 | Precheck 证据主权 | `standard_execution_precheck` 的 verification bundle **必须由 CLI 产出**；禁止 agent 口头/手工拼装 pass 结果进入 implement |
| UD-LG-009 | GIT_ADMISSION 双轨 | truth 编写 skill（`beacon-gen-truth` / `beacon-gen-change` / `beacon-gen-refreeze`）走 `truth_canonical` preamble；delivery skill（implement/qa/release/branch）走 feature worktree admit |

## Problem Statement

1. 37 个既有公开 skill 各自有 hard gate 互斥边界，用户需要手动判断"下一步该调哪个 skill"。
2. v1.6.0 的 `beacon-loop goal`（Node.js）已有编排能力，但与 Python CLI 生态脱节，且 v1.6.5+ 新能力未集成。
3. 跨 harness 上下文传递依赖 agent 内存，长会话中容易丢失阶段状态。
4. 没有统一的 stop-when / error-recovery 机制贯穿全流程。
5. R2 truth 和 `loop_goal_state.py` 已出现 `review_routing`，但 public SKILL.md 决策树和 state outputs 未把 `beacon-pln-review` 的 decision packet 正式纳入 loop-goal 生命周期决策，导致 review artifact 只能人工转译。
6. R3 已能消费 planner-review decision packet，但仍缺少 canonical truth branch commit、feature-local stale refreeze quarantine、merge-main verification bundle 和 workspace admission 这组标准执行流硬门；因此 review 通过后仍可能从未提交/未合入/本地漂移的 truth baseline 直接进入 implement。
7. R4 消费端已能拦未提交/未合入 baseline，且 CLI 已对 freeze/reopen/refreeze-chain 做 `truth_canonical` 分支硬拦；但仍未煮干第一性原理闭环：**(a)** 直接改 feature package Markdown 仍可能在 feature 分支发生，且当前 workspace admission hook 反而把 truth 写操作赶进 feature worktree；**(b)** `record_standard_execution_precheck` 仍可消费 agent 自报的 verification bundle，而非 CLI 自跑证据；**(c)** skill GIT_ADMISSION 曾把 change 指向 worktree，与 truth-on-main 冲突（部分已修，需合同化）。

## Non-Goals

- 替代现有 37 个被编排 skill 的任何一个（编排器只做路由，不做执行）。
- 嵌套调用子 skill（违反 hard gate 互斥原则）。
- 跨项目编排（v2 scope）。
- Subagent 级多 agent 协作（v2 scope）。
- 概率模型决策（保持 deterministic）。
- 替代 v1.6.0 Node.js `beacon-loop` CLI（保留兼容，不废弃）。
- 让 governor `beacon-loop-goal` 自己执行 git/verify（仍只路由；CLI 负责跑 precheck，governor 只记录 CLI artifact）。

## Alignment Surface（本 revision 必煮干）

| 能力 | 描述 |
|------|------|
| 状态机驱动 | 6 阶段状态机：precheck → truth → implement → qa → release_gate → done |
| 顺序 skill 加载 | 每个阶段加载对应 skill，skill 完成后编排器读状态文件做下一步决策 |
| 文件状态传递 | `.beacon/state/loop-goal/<run_id>.json` 记录阶段、产出、时间戳 |
| Auto-decide 模式 | truth freeze / implement start / QA start / **P1-only review continue** 可 auto-decide（opt-out `--human-gate`） |
| Release human gate | release 阶段永远需要人工确认，不可 auto-decide |
| Review blocking human gate | 仅 `P0` / `user_decision_required` / drift routes（truth|change|refreeze）阻断；单独 P1 不阻断 |
| Same-session continue + resume | 输出 route 后同会话加载下一 skill；`beacon status loop-goal --resume` 按 state 续跑 |
| Observability metrics | `human_stops_per_run` / stop_reason 分布 / `p1_continue_count` / pseudo_stall（可判定时） |
| Error recovery | 任何阶段 blocked → 路由 `beacon-gov-debug`，修复后回到对应阶段 |
| Stop-when 检查 | 每个阶段转换前检查 stop 条件 |
| Governance precheck | 启动前验证版本在 governance 中注册（消费 v1.6.6 governance_precheck） |
| Planner review decision packet | truth freeze 后、implement 前可进入 `review_routing`；读取 `beacon-pln-review` artifact 的 `review_id`、`recommended_route`、`user_decision_required`、highest severity、finding count、artifact ref，并写入 `.beacon/state/loop-goal/<run_id>.json` |
| Standard Execution Flow admission | review 允许进入 implement 前，必须验证 canonical truth/refreeze 已提交、feature worktree 已合入 baseline、stale feature-local refreeze 已 quarantine、verification bundle 完整、workspace admission pass |
| Truth-on-main CLI write gate | `freeze` / `reopen` / `change --refreeze-chain` 在非 `truth_canonical` 分支 fail-closed（`reason_code=truth_canonical_branch_mismatch`） |
| Truth-on-main file write gate | 已知 version+feature 时，写 `docs/beacon/<version>/features/<slug>/{truth,tests,tasks,evidence}.md`（及等价 requirement 路径）若不在 `truth_canonical` → 文件级/hook 级 blocked；在 `truth_canonical` 上写 **不得** 被强制赶入 feature worktree |
| CLI-owned precheck runner | 提供 CLI 入口自跑 standard execution verification bundle，写入可引用 artifact；loop-goal 只消费该 artifact，拒绝无 CLI 证据的 agent 自报 pass |
| GIT_ADMISSION 双轨合同 | truth 编写 skill 注入 `truth_canonical` preamble；delivery skill 保留 worktree `workspace admit` |

## Phased Backlog（显式不在本包 closure 的范围）

| ID | 项目 | 决断 |
|----|------|------|
| D-LG-001 | 跨项目编排（多 feature 并行） | defer to v2 |
| D-LG-002 | subagent 级编排（多 agent 协作） | defer to v2 |
| D-LG-003 | 概率模型决策 | rejected（保持 deterministic） |
| D-LG-004 | Node.js beacon-loop 迁移/废弃 | defer（保留兼容） |

## Affected Surfaces

- `.agents/skills/beacon-loop-goal/SKILL.md` (new/R3): skill 定义 + 决策树 + 状态机 + `review_routing` decision packet gate
- `skills/beacon/beacon-loop-goal/SKILL.md` (new/R3): packaged public skill source + `review_routing` decision packet gate
- `.agents/skills/beacon-loop-goal/SKILL.md` (R4): `review_verify -> standard_execution_precheck -> implement_routing` 前置门、reason_code 与 state outputs
- `skills/beacon/beacon-loop-goal/SKILL.md` (R4): packaged public skill source 同步 Standard Execution Flow admission contract
- `beacon/utils/agent_surface.py`: v1.6 taxonomy / agent surface expected list accepts `beacon-loop-goal` as a governor skill
- `beacon/utils/agent_eval_kit.py`: release/eval inventory counts `beacon-loop-goal` as governor host-visible skill
- `beacon/utils/loop_goal_state.py` (new/R3, R4 extended): 状态文件读写、阶段转换、stop-when 检查、planner-review decision packet 写入、standard execution flow admission outputs
- `beacon/commands/status.py`: 新增 `loop-goal` 状态视图
- `tests/test_v166_loop_goal.py` (new)
- `tests/test_doctor_agent_surface.py`, `tests/test_v160_skill_harness_taxonomy.py`, `tests/test_v161_agent_eval.py`: public skill packaging and release governance regression coverage
- `beacon/utils/git_alignment.py` (R5): `check_truth_authoring_branch` / `resolve_truth_canonical_branch`
- `beacon/utils/change_refreeze.py`, `beacon/commands/freeze.py`, `beacon/commands/reopen.py` (R5): truth_canonical CLI write gate
- `beacon/utils/workspace_admission.py` / hooks (R5): truth package path write gate; main checkout must not be forced to feature worktree for truth authoring
- `beacon/utils/loop_goal_state.py` + new CLI precheck runner (R5): CLI-owned verification bundle for standard_execution_precheck
- `tests/test_v166_truth_canonical_branch.py` (R5): truth_canonical branch + GIT_ADMISSION split coverage


## Orchestration Model

### 状态机

```text
idle → governance_precheck
  → pass: truth_routing | blocked: governance_repair → idle
truth_routing → invoke beacon-gen-truth → truth_verify
  → frozen: review_routing | not_frozen: truth_routing (retry) | blocked: error_recovery
review_routing → invoke beacon-pln-review → review_verify
  → blocking (P0 | user_decision_required | drift route): drift_routing | error_recovery
  → non_blocking (incl. P1-only advisory): standard_execution_precheck (record severity + continue audit)
  → blocked: error_recovery
standard_execution_precheck → verify canonical baseline + branch governance + workspace admission
  → pass: implement_routing
  → blocked: error_recovery
implement_routing → invoke beacon-gen-implement → implement_verify
  → tests_pass: qa_routing | tests_fail: implement_routing (retry) | blocked: error_recovery
qa_routing → invoke beacon-eval-qa → qa_verify
  → pass: release_gate | fail: implement_routing (repair loop) | blocked: error_recovery
release_gate → human_confirmed: invoke beacon-eval-release → done
  → human_rejected: idle
error_recovery → invoke beacon-gov-debug → 修复后回到对应阶段
```

### Skill 串联矩阵

| 阶段 | 串联的 Skill | Skill 返回后编排器检查 |
|------|-------------|---------------------|
| S0: Precheck | CLI: `beacon plan start` governance precheck | `status=pass` or `blocked` |
| S1: Truth | `beacon-gen-truth` (含 truth-init, brainstorm) | `truth.md status=frozen`? |
| S1.5: Review | `beacon-pln-review`（条件触发） | findings severity? |
| S1.6: Standard execution precheck | `beacon-gov-branch` + CLI preflight (`truth-map verify`, `verify-materials`, `git diff --check`, `implement check-branch`) | canonical baseline committed/merged? workspace admission pass? |
| S2: Implement | `beacon-gen-implement` | tests pass? |
| S3: QA | `beacon-eval-qa` | verdict=pass? |
| S3.5: Deep QA | `beacon-eval-qa-deep`（条件触发） | findings 可修复? |
| S4: Release | `beacon-eval-release` | go/no-go |
| Error | `beacon-gov-debug` | 恢复路由 |
| Drift | `beacon-gen-change` | 回到 S1 refreeze |

### 状态文件格式

```json
{
  "schema_version": "loop-goal-state.v1",
  "run_id": "<run_id>",
  "version": "<version>",
  "feature": "<feature_slug>",
  "utterance": "<user_prompt>",
  "current_stage": "truth_routing|implement_routing|qa_routing|release_gate|done|error_recovery",
  "auto_decide": true,
  "human_gate_overrides": [],
  "stage_history": [
    {"stage": "precheck", "status": "pass", "at": "<iso-8601>"},
    {"stage": "truth_routing", "status": "invoke", "skill": "beacon-gen-truth", "at": "<iso-8601>"}
  ],
  "outputs": {
    "truth_frozen": true,
    "planner_review_id": "<review_id|null>",
    "planner_review_artifact_ref": ".beacon/state/planner-review/<feature>/<review_id>.json",
    "planner_review_recommended_route": "beacon-gen-implement|beacon-gen-change|beacon-gen-refreeze|beacon-eval-qa|continue_delivery",
    "planner_review_user_decision_required": false,
    "planner_review_highest_severity": "P0|P1|P2|P3|",
    "planner_review_finding_count": 0,
    "planner_review_continue_audit": {
      "continued_with_advisory": false,
      "continued_severity": "P1|P2|P3|",
      "blocking_reason_code": ""
    },
    "human_stop_metrics": {
      "human_stops_per_run": 0,
      "stop_reason_counts": {},
      "p1_continue_count": 0,
      "pseudo_stall_count": 0
    },
    "standard_execution_flow_status": "not_checked|pass|blocked",
    "truth_baseline_commit": "<git-sha|null>",
    "canonical_refreeze_committed": false,
    "feature_worktree_reconciled": false,
    "stale_feature_refreeze_quarantine_ref": "<stash-or-artifact-ref|null>",
    "verification_bundle_ref": ".beacon/state/loop-goal/<run_id>.verification-bundle.json",
    "workspace_admission_ref": ".beacon/state/workspace-admission/<version>/<feature>.json",
    "tests_pass": false,
    "qa_verdict": null,
    "release_verdict": null
  }
}
```

### Auto-Decide 规则

| 决策点 | 默认行为 | 可覆盖？ | 依据 |
|--------|----------|----------|------|
| truth scope（海拆湖） | auto-decide | `--human-gate` | feature-graph.json |
| truth freeze | auto-decide（verify pass 即 freeze） | `--human-gate` | `beacon truth verify` |
| planner-review P1-only | auto-continue → `standard_execution_precheck`（记 severity + continue audit） | `--human-gate` 可强制停 | AC-014 R6 |
| planner-review blocking | 停：`P0` 或 `user_decision_required=true` 或 route∈{truth,change,refreeze} | 不可用 auto-decide 绕过 | AC-014 R6 |
| implement 启动 | auto-decide（review non-blocking + precheck pass） | `--human-gate` | 状态文件 |
| QA 启动 | auto-decide（tests pass 即进入） | `--human-gate` | pytest exit code |
| **release 启动** | **必须人工确认** | **不可覆盖** | global-boundaries §1 / AC-007 |

### Human-gate 集合（R6 唯一默认人门）

默认人类急停集合：

1. `release_gate`（永远）
2. review blocking：`highest_severity=P0` **或** `user_decision_required=true` **或** `recommended_route ∈ {beacon-gen-truth, beacon-gen-change, beacon-gen-refreeze}`

**不**在默认急停集合：单独的 `P1` / `P2` / `P3` findings（记 advisory continue audit 后进入 precheck）。

### Same-session continue + resume（R6 Phase B）

- public SKILL.md 决策树必须写死：每次输出 next route 后，**同一会话立即加载**对应 skill；禁止以「只打印下一步」结束回合（假性卡死）。
- 必须提供 `beacon status loop-goal --resume`（或等价 CLI）：读取 `.beacon/state/loop-goal/<run_id>.json`，输出当前 stage + 下一步 skill + 禁止 no-op 打印；agent 据此续跑。

### Observability（R6 Phase C）

loop-goal state / status 视图必须可观测：

- `human_stops_per_run`
- `stop_reason` 分布（release / p0 / user_decision_required / drift_route / human_gate_override / …）
- `p1_continue_count`（P1 advisory 续跑次数）
- `pseudo_stall_count`（检测到只打印 next-route 未加载 skill 的次数，若可判定）



## R7 Alignment Surface（intent continuation + dual runtime）

| 能力 | 描述 |
|------|------|
| IntentContext.v1 | state 输出含 `seed_utterance`、`latest_utterance`、`intent_forks[]`、`decision_cache[]` |
| Intent fork record | 每个路由分叉调用 `record_intent_fork()`，写入 utterance slice + decision + reason_code |
| Decision cache | `user_decision_required` 回答一次后写入 `decision_cache`；同 run_id 不重复 AskQuestion |
| Interrupt semantics | 区分 `host_turn_interrupted` 与 `stage_blocked`；resume 回到 `last_substep` |
| Resume utterance map | deterministic 短词表：`继续|continue|resume|go` + 有效 run → `resume_action=load_next_skill` |
| Resilient stop contract | 每次停必须输出 `reason_code` + `resume_action`；禁止无状态 no-op 成功 |
| topology_gate consume | `standard_execution_precheck` 必须消费 `GitScopeGraph` / `topology_gate_status`（依赖 `beacon-git-scope-graph-v167`） |
| Dual runtime parity | `beacon loop-goal run`（CLI+agent）与 host `beacon-loop-goal` skill 写同一 state 文件 |
| v2 schema parity | v1 JSON schema fixtures 与 v2 `BranchContext.v1` / `TraceContext.v1` / `intent_snapshot` 对齐 |

### 「不能随便停」合同（用户确认 UD-TOPO-002）

合法停止集合不变：`release_gate`、review blocking（P0 / user_decision_required / drift routes）、topology_gate fail、stage_blocked。

**新增**：上述停止必须附带 `resume_action`；已缓存决策不得重复 human wait；host interrupt 不得等同 stage failure。

### LoopExecutionMode.v1

| mode | 入口 | 合同 |
|------|------|------|
| `host_skill` | `/beacon-loop-goal` | AC-028 same-session continue |
| `cli_agent` | `beacon loop-goal run` | 同一 `loop-goal-state.v1`；step executor 可为 agent |

### 扩展状态 outputs（R7）

```json
{
  "intent_context_ref": ".beacon/state/loop-goal/<run_id>.intent-context.json",
  "intent_forks": [],
  "decision_cache": [],
  "last_substep": "",
  "topology_gate_status": "not_checked|pass|blocked",
  "topology_gate_ref": ".beacon/state/git-scope-graph/<version>/<feature>.json",
  "loop_execution_mode": "host_skill|cli_agent",
  "resume_action": "none|load_next_skill|await_human_confirmation|replay_substep"
}
```

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | state-init | `loop_goal_state.init()` 创建状态文件，schema 为 `loop-goal-state.v1`，包含 run_id/version/feature/utterance/current_stage |
| AC-002 | stage-transition | `loop_goal_state.transition()` 更新 `current_stage` 并追加 `stage_history`，每次转换写入 `at` 时间戳 |
| AC-003 | precheck-gate | 编排器启动前调用 governance precheck；`blocked` 时停止并输出 `reason_code=governance_version_not_registered` |
| AC-004 | truth-gate | Truth 阶段完成后，编排器读 `truth.md` frontmatter；`status != frozen` 时停留在 `truth_routing`，不进入 implement |
| AC-005 | implement-gate | Implement 阶段完成后，编排器检查 pytest exit code；失败时回到 `implement_routing`（repair loop），最多 3 次 |
| AC-006 | qa-gate | QA 阶段完成后，编排器读 qa verdict；`fail` 时回到 `implement_routing`（repair loop），最多 3 次 |
| AC-007 | release-human-gate | Release 阶段永远需要人工确认；即使 `auto_decide=true`，`current_stage=release_gate` 时编排器停在人工输入门 |
| AC-008 | error-recovery | 任何阶段 `blocked` 时，`current_stage` 转为 `error_recovery`，输出推荐路由 `beacon-gov-debug` |
| AC-009 | stop-when | 每个阶段转换前检查 `stop_when` 条件；满足时停止并输出 `reason_code=stop_when_satisfied` |
| AC-010 | skill-routing | 编排器的 SKILL.md 包含完整决策树，agent 可按决策树顺序加载对应 skill |
| AC-011 | public-skill-release-shape | `beacon-loop-goal` 作为公开 host-visible governor skill 被 v1.6 taxonomy、agent surface expected list、skill inventory/count 和 release governance 接受；公开 skill 总数为 38 |
| AC-012 | review-routing-public-skill | public SKILL.md 的 State Machine、Decision Tree、Skill Routing Matrix 必须显式包含 `review_routing -> beacon-pln-review`，并声明 review 后才能自动进入 implement 的条件 |
| AC-013 | review-decision-packet-state | `loop_goal_state` 必须提供 deterministic review decision packet 写入函数，把 planner-review artifact 的 review id、artifact ref、recommended route、user decision flag、highest severity、finding count 写入 state outputs |
| AC-014 | review-gate-fail-closed | **R6**：blocking 仅当 `highest_severity=P0` **或** `user_decision_required=true` **或** `recommended_route ∈ {beacon-gen-truth, beacon-gen-change, beacon-gen-refreeze}` → 不得自动进入 `implement_routing`，必须停在 drift_routing / error_recovery。**单独的 P1（及更低）不得阻断**；必须进入 `standard_execution_precheck`，并写入 continue audit（severity + `continued_with_advisory=true`）（**Must**） |
| AC-015 | standard-flow-public-skill | public SKILL.md 的 State Machine、Decision Tree、Skill Routing Matrix 必须显式包含 `standard_execution_precheck`，位于 `review_verify` 和 `implement_routing` 之间 |
| AC-016 | canonical-commit-boundary | canonical truth/refreeze 只有在 main/master 提交后才可成为 loop-goal baseline；未提交 refreeze artifact 不得进入 implement |
| AC-017 | stale-feature-refreeze-quarantine | feature/dev worktree 中发现本地 `.machine` revision/projection dirty 或 feature-local refreeze 时，必须 scoped stash/archive 并记录 quarantine ref；不得采信为 requirement authority |
| AC-018 | baseline-merged-gate | loop-goal 进入 implement 前必须验证 feature branch 包含 `truth_baseline_commit`；未合入时 fail-closed |
| AC-019 | verification-bundle | standard execution precheck 必须产出 verification bundle，至少包含 truth-map verify、verify-materials strict、git diff check、branch-governance verify、workspace admission 五类结果 |
| AC-020 | workspace-admission-gate | `implement check-branch` / workspace admission 必须 pass，并把 artifact ref 写入 loop-goal state outputs；缺失或 blocked 不得进入 implement |
| AC-021 | idempotent-resume | standard execution flow 重复执行已完成步骤时必须返回 pass/up_to_date，不得再次 bump requirement revision 或产生 reason-only refreeze |
| AC-022 | truth-canonical-cli-gate | `beacon freeze` / `beacon reopen` / `beacon change --refreeze-chain` 在非 governance `truth_canonical` 分支必须 blocked，`reason_code=truth_canonical_branch_mismatch`（**Must**） |
| AC-023 | truth-file-write-gate | 写 feature package requirement Markdown（`features/<slug>/{truth,tests,tasks,evidence}.md`）时：不在 `truth_canonical` → blocked；在 `truth_canonical` → **允许**，且不得因 `require_workspace_admission` 强制要求 feature worktree cwd（**Must**） |
| AC-024 | git-admission-dual-track | `beacon-gen-truth` / `beacon-gen-change` / `beacon-gen-refreeze` 物化 skill 必须含 truth_canonical GIT_ADMISSION；`beacon-gen-implement` / qa / release / gov-branch 必须保留 worktree `workspace admit` preamble（**Must**） |
| AC-025 | cli-owned-precheck-bundle | 必须提供 CLI 命令自跑 standard execution verification bundle（至少五类检查）并写 artifact；`record_standard_execution_precheck` 只接受带 CLI artifact ref 的结果，拒绝无 ref 的 agent 自报 pass（**Must**） |
| AC-026 | truth-routing-branch-check | public `beacon-loop-goal` SKILL.md Step 2 必须在进入 `beacon-gen-truth` 前校验当前分支为 `truth_canonical`，否则 route `beacon-gov-debug` + `truth_canonical_branch_mismatch`（**Must**） |
| AC-027 | auto-decide-human-gate-alignment | Auto-decide 表必须与 AC-007/AC-014 对齐：默认人类急停仅 release + review blocking 集合；P1-only 默认续跑；`--human-gate` 可把 P1 升为停；release 永远不可 auto 覆盖（**Must**） |
| AC-028 | same-session-skill-continue | public SKILL.md 决策树必须声明：输出 next route 后**同会话立即加载**下一 skill；禁止以「仅打印下一步」结束编排回合（**Must**） |
| AC-029 | loop-goal-resume-cli | 必须提供 `beacon status loop-goal --resume`（或等价），按 state 文件返回 `current_stage` + next skill + reason_code；禁止无状态变更的 no-op 打印充当 resume（**Must**） |

| AC-031 | intent-context-state | state outputs 必须含 `IntentContext.v1` 字段（seed/latest utterance、intent_forks、decision_cache）并可引用 artifact（**Must**） |
| AC-032 | intent-fork-record | 每个路由分叉必须 `record_intent_fork()` 追加 fork 记录（stage、utterance_slice、decision、reason_code）（**Must**） |
| AC-033 | decision-cache | `user_decision_required` 的用户回答写入 `decision_cache`；同 run 不得重复触发同一 decision key（**Must**） |
| AC-034 | interrupt-semantics | `host_turn_interrupted` 与 `stage_blocked` 必须区分；resume 回 `last_substep` 而非默认 error_recovery 重头（**Must**） |
| AC-035 | resume-utterance-map | `beacon status loop-goal --resume --utterance` 支持短续跑词 deterministic 映射到 `load_next_skill`（**Must**） |
| AC-036 | loop-goal-run-cli | 必须提供 `beacon loop-goal run` 公共 CLI；与 host skill 共享 state 文件与 resume 语义（**Must**） |
| AC-037 | topology-gate-consume | `standard_execution_precheck` / `record_standard_execution_precheck` 必须消费 `topology_gate_status`；blocked 不得进入 implement（**Must**） |
| AC-038 | dual-runtime-parity | 同一 run_id 在 `host_skill` 与 `cli_agent` 模式下 `build_resume` 输出一致（**Must**） |
| AC-039 | resilient-stop-contract | 所有 stop 路径输出 `reason_code` + `resume_action`；禁止 no-op pass（**Must**） |
| AC-040 | v2-schema-parity | 提供 v1.6.7 schema fixtures；v2 program parity test 可加载 `IntentContext`/`GitScopeGraph` 对齐 `TraceContext`/`BranchContext`（**Must**） |

| AC-030 | loop-goal-observability-metrics | state/status 必须暴露 `human_stops_per_run`、`stop_reason` 分布、`p1_continue_count`；假性卡死（pseudo_stall）在可判定时计数（**Should**） |

## State Model

```text
idle -> governance_precheck -> truth_routing -> review_routing -> standard_execution_precheck -> implement_routing -> qa_routing -> release_gate -> done
                                                                            |               |              |
                                                                            +-- repair loop (max 3) --+     |
                                                                            |                          |     |
drift_routing <--- review route requires truth/change/refreeze          error_recovery <--- blocked ---+-----+
                                                                            |
                                                                       beacon-gov-debug -> 修复后回到对应阶段
```

## Deferral Ledger

| ID | Item | user_decision |
|----|------|---------------|
| UD-LG-001 | Governor harness type | accepted |
| UD-LG-002 | Sequential loading | accepted |
| UD-LG-003 | File-system state | accepted |
| UD-LG-004 | Auto-decide whitelist | accepted |
| UD-LG-005 | Error recovery via gov-debug | accepted |
| UD-LG-006 | Public host-visible governor skill release shape | accepted |
| UD-LG-007 | Truth-on-main physical closure | accepted |
| UD-LG-008 | CLI-owned precheck evidence | accepted |
| UD-LG-009 | GIT_ADMISSION dual-track | accepted |
| UD-LG-010 | Human-gate set = release + review blocking only (P1 advisory continue) | accepted |
| UD-LG-011 | Same-session skill continue + resume CLI | accepted |
| UD-LG-012 | Loop-goal observability metrics (Phase C) | accepted |
| D-LG-001 | Cross-project orchestration | accepted defer (v2) |
| D-LG-002 | Subagent orchestration | accepted defer (v2) |
| D-LG-003 | Probabilistic decisions | rejected |
| D-LG-004 | Node.js beacon-loop migration | accepted defer |

## Downstream Routes

- `beacon-gen-implement`: public SKILL.md packaging + state utility + taxonomy/release governance + tests.
- `beacon-eval-qa`: behavioral TC-LG-* matrix.
- `beacon-eval-release`: human review gate before release verdict.

## Revision Notes

- R3 froze planner-review decision packet routing.
- R4 adds Standard Execution Flow admission before implement routing. This is a v1.6.6 loop-goal governance contract only; it does not create a new public skill, does not execute implementation, and does not provide QA/release verdict authority.
- R5 closes truth-on-main first principles: CLI + file write gates on `truth_canonical`, dual-track GIT_ADMISSION, and CLI-owned standard_execution_precheck evidence. Governor still only routes; it does not self-run git checks.
- R6 redefines the default human-gate set to match first principles: only `release_gate` plus review **blocking** (`P0` | `user_decision_required` | drift routes) stop the loop. Standalone P1 is advisory continue with audit. Adds same-session skill continue, `loop-goal --resume` CLI, and observability metrics (AC-027..030). Does not weaken AC-007.


## R7 Revision Notes

- Reopened from v1.6.6 R6 frozen closure per user-confirmed planner review.
- Depends on `beacon-git-scope-graph-v167` for topology_gate.
- Promotion ref: friction `friction:2e306f7acea7`.
