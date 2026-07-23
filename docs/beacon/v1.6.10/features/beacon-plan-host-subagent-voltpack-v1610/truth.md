---
slug: beacon-plan-host-subagent-voltpack-v1610
version: v1.6.10
status: frozen
revision_id: R1
language: zh
domain_required: false
ux_required: false
package_maturity: filled
package_kind: platform
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.10/programs/beacon-plan-host-subagent-voltpack-v1610/program-manifest.md
change_reason: "UD lock D-VA + D-VA-CNT: plan-review pack=10; default spawn 3; count param; gate tokens; readiness 1+6; default off"
canonical_refs:
  truth: docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md
  tests: docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/tests.md
  tasks: docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/tasks.md
  evidence: docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/evidence.md
---

# Requirement Truth: Plan Host Subagent VoltPack (v1.6.10 R1)

## 人话

Beacon plan 要做全面多角度分析时，可以**按意图**拉起 Codex/Claude 子代理：架构审查、代码审查、协调、合成等。默认仍是单线程；只有说了子代理/多代理等词才开。角色从 VoltAgent 两仓**精选投影 10 个**，不是全装 150+。装包、门闩、doctor 校验、诚实 fallback 齐了才算可交付。

- 能做：plan-review 10 角色 pack；阶段词命中架构/代码审查；1+6 readiness；确定性 pln-review + intent-on host lanes 合同
- 不能做：默认自动 spawn；子代理 freeze/complete/release；全量 VoltAgent 同步；第二公共 skill
- 怎样算完：AC↔TC 绿；install/verify plan-review；示例可跟做

## User Intent（一行）

交付 intent-on 的 plan-review host 子代理包（10 角色，VoltAgent 精选），默认关闭，支撑架构与软件工程代码审查等全面 beacon plan 分析。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
pack_size: 10
pack_id: plan-review
default: single_thread
trigger: keyword_or_flag
source: VoltAgent curated projection
authority: parent_integrates
truth_write: forbidden_for_subagents
```

## User Decisions（locked 2026-07-22）

| ID | Value |
|----|-------|
| D-VA-001 | 全量 171/164 角色同步 **defer** |
| D-VA-002 | plan-review pack **10** 角色 |
| D-VA-003 | install **投影** oss-sync/VoltAgent 正文 + Beacon HARD；缺失则 curated fallback |
| D-VA-004 | security/performance 等 **条件 lane**；默认 spawn **core 3**（architect-reviewer / code-reviewer / knowledge-synthesizer）；catalog 仍 10；`开N个子代理` / `subagent-count` / `BEACON_SUBAGENT_MAX` 可调，硬顶 10 |
| D-VA-005 | 无 host spawn 时必须 `single_process_multi_reviewer` + `fallback_reason` |
| UD-VP-001 | 继承 UD-SA-001：仅「并行」不开 host agents |
| UD-VP-002 | 继承 UD-SA-006：子代理不可 complete GoalRun / auto-release |
| UD-VP-003 | 唯一公共入口仍 `beacon-goal` / 1+6 plan；无第二公共 skill |
| UD-VP-004 | Plan→Truth Gate 仍最高权威；host review 只是 support evidence |
| D-VA-CNT | 默认 spawn_max=3；用户可传参；env BEACON_SUBAGENT_MAX 为硬顶；install 文件数与 spawn 数解耦 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-VP-01 | user | must | AC-VP-KW-001..003 | covered |
| INT-VP-02 | user | must | AC-VP-PK-001..003 | covered |
| INT-VP-03 | user | must | AC-VP-GT-001..003 | covered |
| INT-VP-04 | plan | must | AC-VP-RD-001 | covered |
| INT-VP-05 | plan | must | AC-VP-BD-001..002 | covered |
| INT-VP-06 | user | must | AC-VP-FB-001 | covered |
| INT-VP-07 | plan | should | AC-VP-EX-001 | covered |
| INT-VP-08 | user | must | AC-VP-DF-001 | covered |
| INT-VP-CNT | user | must | AC-VP-CNT-001..003 | covered |

## First principles

| ID | Constraint |
|----|------------|
| FP-VP-001 | protocol first，catalog 启发切片 |
| FP-VP-002 | default off；显式意图才 host spawn 规划 |
| FP-VP-003 | parent integrates；子代理不写 truth / 不 freeze |
| FP-VP-004 | 诚实 execution_mode；禁止假 parallel |
| FP-VP-005 | minimal(6) 保留兼容；plan-review(10) 为 plan 全面分析包 |

## 用户旅程

1. 用户只说「规划登录」→ 单线程 pln-review，不装不 spawn host agents。
2. 用户说「启用子代理做架构与代码审查全面 plan 分析」→ gate_on + pack-review catalog(10) 默认 spawn core 3；`开5个子代理` 可升到 5。
3. 操作者 `install-subagent-pack --pack plan-review` → doctor verify（含 agents + 1+6 skill root）pass。
4. 无 host runtime 时 planner-review 仍可跑，标 fallback，不宣称 parallel。
5. findings 合成后路由 truth；仅 Truth Review Gate pass 后 freeze。

## Overview

| Entity | Notes |
|--------|-------|
| KeywordGate | 全局 on/off + pack-review 扩展阶段词 |
| PlanReviewPack | 10 curated roles（VoltAgent 投影） |
| CoreLanes | coordinator, architect-reviewer, code-reviewer, knowledge-synthesizer |
| ConditionalLanes | security-auditor, performance-engineer, api-designer, qa-expert, docs-researcher, search-specialist |
| Readiness | flat 1+6 `beacon-*` skill roots + agents pack |
| PlannerRuntime | deterministic multi-reviewer always; parallel label only when host available |

## Plan-review pack (10)

| # | role | core/cond | VoltAgent category (hint) |
|---|------|-----------|---------------------------|
| 1 | multi-agent-coordinator | core | 09-meta-orchestration |
| 2 | architect-reviewer | core | 04-quality-security |
| 3 | code-reviewer | core | 04-quality-security |
| 4 | knowledge-synthesizer | core | 09-meta-orchestration |
| 5 | security-auditor | cond | 04-quality-security |
| 6 | performance-engineer | cond | 04-quality-security |
| 7 | api-designer | cond | 01-core-development |
| 8 | qa-expert | cond | 04-quality-security |
| 9 | docs-researcher | cond | 10-research-analysis |
| 10 | search-specialist | cond | 10-research-analysis |

HARD on every role: `cannot_complete_goal`; `cannot_auto_release`; `cannot_write_truth`; findings 对齐 planner finding-schema；parent 唯一 synthesis。

## Keyword contract

**Priority**: `--no-subagent` / 否定词 > `--subagent` / 全局 on > default false

**Global on**: `subagent`, `sub-agents`, `sub agents`, `with agents`, `子代理`, `多代理`, `开子代理`, `启用子代理`, `并行子代理`

**Global off**: `no subagent`, `without subagent(s)`, `不要子代理`, `禁用子代理`, `关闭子代理`

**pack-review 阶段词（扩展）**: `全面审查`, `多角度`, `oracle`, `challenge`, `pln-review`, `architect-reviewer`, `架构`, `架构设计`, `架构审查`, `代码审查`, `code review`, `软件工程`, `全面分析`, `plan review`, `需求分析`, `设计审查`

**pack-review roles**: 上表 10 角色；gate 规划至少 core 4。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-VP-KW-001 | off | 无关键词无 flag → spawn=false, reason=subagent_default_off |
| AC-VP-KW-002 | review tokens | 「启用子代理」+ 架构/代码审查/全面分析 → pack-review，含 architect-reviewer 与 code-reviewer |
| AC-VP-KW-003 | parallel alone | 仅「并行」→ host_agents=false |
| AC-VP-PK-001 | pack10 | `--pack plan-review` 安装恰好 10 角色文件到 host agents dir |
| AC-VP-PK-002 | hard | 每个角色文件含 cannot_complete_goal / cannot_write_truth（或等价 HARD） |
| AC-VP-PK-003 | minimal | `--pack minimal` 仍可装 6 角色（兼容 v1.6.8） |
| AC-VP-GT-001 | gate roles | pack-review gate 返回 roles 包含 core 4 |
| AC-VP-GT-002 | negate | 否定词覆盖正向词 |
| AC-VP-GT-003 | default pack | 全局 on 无阶段词 → pack-default（search-specialist only） |
| AC-VP-RD-001 | readiness | verify-subagent-runtime：1+6 flat skill（任一 beacon-goal 等）可过 skill_root；require-agents 校验 pack |
| AC-VP-BD-001 | bound | gate_on payload cannot_complete_goal=true |
| AC-VP-BD-002 | entry | 无第二公共 skill 入口（仍 goal/plan） |
| AC-VP-FB-001 | fallback | planner-review 无 host subagent runtime → single_process_multi_reviewer + fallback_reason |
| AC-VP-EX-001 | example | examples 含 plan-review on 路径 |
| AC-VP-DF-001 | defer full | 文档/真相声明全量 VoltAgent dump 为 non-goal |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| idle | Utterance | always | keyword_gate | evaluate_host_subagent_gate |
| keyword_gate | Evaluate | miss | single_thread | deterministic_pln_review |
| keyword_gate | Evaluate | hit_global_on | pack_select | match_stage_packs |
| pack_select | StageMatch | pack_review_tokens | plan_review_ready | select_core4_plus_cond |
| pack_select | StageMatch | no_stage | pack_default | search_only |
| plan_review_ready | HostReady | agents_ok | planned_spawn | parent_may_spawn |
| plan_review_ready | HostReady | agents_missing | fallback_single | reason_pack_not_ready |
| planned_spawn | Integrate | always | synthesis | parent_merge_findings |
| synthesis | Route | always | route_out | recommend_truth_or_change |
| single_thread | Run | always | synthesis | single_process_multi_reviewer |
| any | Negate | off_tokens_or_flag_false | single_thread | spawn_false |

### invalid / illegal

- keyword_miss → planned_spawn
- subagent_session → goal_completed
- subagent_session → truth_frozen
- pack-qa → release_confirmed
- install full VoltAgent dump as default pack

## Non-goals

- 全量 VoltAgent 171/164 角色同步
- 子代理自动 complete / release
- 用 catalog 替代 Plan→Truth Gate
- 默认开启 host agents
- 新公共 skill 入口

## done_when

- AC 合同测绿
- `install-subagent-pack --pack plan-review` + verify 可调用
- 阶段词「架构/代码审查」进 pack-review
- readiness 认 1+6 flat skills
- examples 可跟做
- release 仍人工
