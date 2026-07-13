---
slug: beacon-loop-goal-v166
version: v1.6.6
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Cross-harness loop goal orchestrator skill (governor sequencing all Beacon lifecycle)
canonical_refs:
  truth: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/truth.md
  tests: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/tests.md
  tasks: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/tasks.md
  evidence: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
---

# Requirement Truth: Loop Goal Orchestrator v1.6.6

## Overview

Beacon 现有 36 个 skill，分为 planner(7) / generator(11) / evaluator(5) / governor(13) 四个 harness。每个 skill 在单次调用内有 hard gate 互斥边界——planner 不能 implement，generator 不能自证完成，evaluator 不能改 truth。但用户缺少一个 **跨 harness 编排入口**，能用一个提示词驱动 truth → implement → QA → release 全流程自动运行。

本 feature 定义 `beacon-loop-goal` **governor 编排 skill**——它不执行任何 harness 职责，只做路由、状态追踪和阶段决策。它通过顺序加载现有 skill（不嵌套），在文件状态上判断阶段转换，支持 auto-decide 模式（release 门永远需要人工确认）。

## User Intent（一行）

一个 governor 编排 skill，用提示词驱动 Beacon 全流程（truth → implement → QA → release）自动闭环，每个阶段顺序加载对应 skill，编排器自身不执行任何 harness 职责。

## User Intent Snapshot

- user_prompt: "跨 harness 全职责 loop goal skill，提示词驱动自动闭环"
- lake_or_ocean: 海（跨 4 harness 编排，已拆分为 Alignment Surface）
- scope_mode: full_parity
- program_ref: docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/feature-graph.json
- silent_scope_change_allowed: false

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LG-001 | Harness 类型 | **governor**——编排 = 路由 + 状态追踪，不执行 truth/implement/QA/release |
| UD-LG-002 | 调用模式 | **顺序加载**（agent 加载完一个 skill 后编排器才做下一步决策），不嵌套调用 |
| UD-LG-003 | 状态传递 | **文件系统状态**（`.beacon/state/loop-goal/`），不依赖 agent 内存 |
| UD-LG-004 | Auto-decide 白名单 | truth freeze / implement start / QA start 可 auto-decide；**release 永远人工确认** |
| UD-LG-005 | Error 路由 | 任何阶段失败 → `beacon-gov-debug` → 修复后回到对应阶段 |

## Problem Statement

1. 36 个 skill 各自有 hard gate 互斥边界，用户需要手动判断"下一步该调哪个 skill"。
2. v1.6.0 的 `beacon-loop goal`（Node.js）已有编排能力，但与 Python CLI 生态脱节，且 v1.6.5+ 新能力未集成。
3. 跨 harness 上下文传递依赖 agent 内存，长会话中容易丢失阶段状态。
4. 没有统一的 stop-when / error-recovery 机制贯穿全流程。

## Non-Goals

- 替代现有 36 个 skill 的任何一个（编排器只做路由，不做执行）。
- 嵌套调用子 skill（违反 hard gate 互斥原则）。
- 跨项目编排（v2 scope）。
- Subagent 级多 agent 协作（v2 scope）。
- 概率模型决策（保持 deterministic）。
- 替代 v1.6.0 Node.js `beacon-loop` CLI（保留兼容，不废弃）。

## Alignment Surface（本 revision 必煮干）

| 能力 | 描述 |
|------|------|
| 状态机驱动 | 6 阶段状态机：precheck → truth → implement → qa → release_gate → done |
| 顺序 skill 加载 | 每个阶段加载对应 skill，skill 完成后编排器读状态文件做下一步决策 |
| 文件状态传递 | `.beacon/state/loop-goal/<run_id>.json` 记录阶段、产出、时间戳 |
| Auto-decide 模式 | truth freeze / implement start / QA start 可 auto-decide（opt-out `--human-gate`） |
| Release human gate | release 阶段永远需要人工确认，不可 auto-decide |
| Error recovery | 任何阶段 blocked → 路由 `beacon-gov-debug`，修复后回到对应阶段 |
| Stop-when 检查 | 每个阶段转换前检查 stop 条件 |
| Governance precheck | 启动前验证版本在 governance 中注册（消费 v1.6.6 governance_precheck） |

## Phased Backlog（显式不在本包 closure 的范围）

| ID | 项目 | 决断 |
|----|------|------|
| D-LG-001 | 跨项目编排（多 feature 并行） | defer to v2 |
| D-LG-002 | subagent 级编排（多 agent 协作） | defer to v2 |
| D-LG-003 | 概率模型决策 | rejected（保持 deterministic） |
| D-LG-004 | Node.js beacon-loop 迁移/废弃 | defer（保留兼容） |

## Affected Surfaces

- `.agents/skills/beacon-loop-goal/SKILL.md` (new): skill 定义 + 决策树 + 状态机
- `beacon/utils/loop_goal_state.py` (new): 状态文件读写、阶段转换、stop-when 检查
- `beacon/commands/status.py`: 新增 `loop-goal` 状态视图
- `tests/test_v166_loop_goal.py` (new)

## Orchestration Model

### 状态机

```text
idle → governance_precheck
  → pass: truth_routing | blocked: governance_repair → idle
truth_routing → invoke beacon-gen-truth → truth_verify
  → frozen: implement_routing | not_frozen: truth_routing (retry) | blocked: error_recovery
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
| implement 启动 | auto-decide（truth frozen 即进入） | `--human-gate` | 状态文件 |
| QA 启动 | auto-decide（tests pass 即进入） | `--human-gate` | pytest exit code |
| **release 启动** | **必须人工确认** | **不可覆盖** | global-boundaries §1 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | state-init | `loop_goal_state.init()` 创建状态文件，schema 为 `loop-goal-state.v1`，包含 run_id/version/feature/utterance/current_stage |
| AC-002 | stage-transition | `loop_goal_state.transition()` 更新 `current_stage` 并追加 `stage_history`，每次转换写入 `at` 时间戳 |
| AC-003 | precheck-gate | 编排器启动前调用 governance precheck；`blocked` 时停止并输出 `reason_code=governance_version_not_registered` |
| AC-004 | truth-gate | Truth 阶段完成后，编排器读 `truth.md` frontmatter；`status != frozen` 时停留在 `truth_routing`，不进入 implement |
| AC-005 | implement-gate | Implement 阶段完成后，编排器检查 pytest exit code；失败时回到 `implement_routing`（repair loop），最多 3 次 |
| AC-006 | qa-gate | QA 阶段完成后，编排器读 qa verdict；`fail` 时回到 `implement_routing`（repair loop），最多 3 次 |
| AC-007 | release-human-gate | Release 阶段永远需要人工确认；即使 `auto_decide=true`，`current_stage=release_gate` 时编排器停止等待人工输入 |
| AC-008 | error-recovery | 任何阶段 `blocked` 时，`current_stage` 转为 `error_recovery`，输出推荐路由 `beacon-gov-debug` |
| AC-009 | stop-when | 每个阶段转换前检查 `stop_when` 条件；满足时停止并输出 `reason_code=stop_when_satisfied` |
| AC-010 | skill-routing | 编排器的 SKILL.md 包含完整决策树，agent 可按决策树顺序加载对应 skill |

## State Model

```text
idle -> governance_precheck -> truth_routing -> implement_routing -> qa_routing -> release_gate -> done
                                                         |               |              |
                                                         +-- repair loop (max 3) --+     |
                                                         |                          |     |
                                                    error_recovery <--- blocked ---+-----+
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
| D-LG-001 | Cross-project orchestration | accepted defer (v2) |
| D-LG-002 | Subagent orchestration | accepted defer (v2) |
| D-LG-003 | Probabilistic decisions | rejected |
| D-LG-004 | Node.js beacon-loop migration | accepted defer |

## Downstream Routes

- `beacon-gen-implement`: SKILL.md + state utility + status view + tests.
- `beacon-eval-qa`: behavioral TC-LG-* matrix.
- `beacon-eval-release`: human review gate before release verdict.
