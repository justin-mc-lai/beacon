---
slug: beacon-host-subagent-lifecycle-keyword-v168
version: v1.6.8
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO UD-SA-001..004 accepted; pln-review host subagent keyword gate"
canonical_refs:
  truth: docs/beacon/v1.6.8/features/beacon-host-subagent-lifecycle-keyword-v168/truth.md
  tests: docs/beacon/v1.6.8/features/beacon-host-subagent-lifecycle-keyword-v168/tests.md
  tasks: docs/beacon/v1.6.8/features/beacon-host-subagent-lifecycle-keyword-v168/tasks.md
  evidence: docs/beacon/v1.6.8/features/beacon-host-subagent-lifecycle-keyword-v168/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.8/programs/beacon-host-subagent-lifecycle-v168/feature-graph.json
ux_required: false
design_deferral: "CLI/skill/host agents; no product marketing UI"
promotion_ref: docs/beacon/v1.6.8/research/beacon-host-subagent-lifecycle-keyword-pln-review.md
---

# Requirement Truth: Host Subagent Lifecycle Keyword Gate (v1.6.8 R1)

## 人话

Codex/Claude 子代理是**增强**：默认单线程；只有关键词或 `--subagent` 才调用；「并行」只开 satellite worktree，不开 host agents。

- 能做：关键词门闩、6 角色 curated pack 安装到 `.codex/agents` / `.claude/agents`、四阶段 pack、doctor 校验、L1 测例、skill/示例
- 不能做：无词自动 spawn；子代理 complete/release；第二公共入口；全量 150+ 角色
- 怎样算完：AC 测绿；示例可跟做；v2/Loom 镜像合同一致

## User Intent（一行）

v1.6.8 交付可验收的 host 子代理关键词门闩与最小 pack，并镜像到 v2.0.0/Loom。

## User Decisions（locked 2026-07-20）

| ID | Value |
|----|-------|
| UD-SA-001 | 「并行」仅 satellite；host agents 必须全局子代理词或 `--subagent` |
| UD-SA-002 | 最小角色包 **6** |
| UD-SA-003 | vendoring 到项目 `.codex/agents` + `.claude/agents` |
| UD-SA-004 | v1.6.8 与 v2.0.0/Loom **同 AC 镜像** |
| UD-SA-005 | 唯一公共入口仍 `beacon-goal` / `loom-goal` |
| UD-SA-006 | 子代理/session **不可** complete GoalRun 或 auto-release |

## Overview

| Entity | Notes |
|--------|-------|
| KeywordGate | 全局开关 + 阶段词 + 否定词优先级 |
| SubagentPack | curated 6 roles |
| HostAdapter | codex \| claude |
| SubagentSession | audit matched_tokens; cannot complete goal |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-SA-KW-001 | off | 无关键词无 flag → spawn=false, reason=subagent_default_off |
| AC-SA-KW-002 | gate | 全局词开启 gate；无阶段词 → pack_default read-only only |
| AC-SA-KW-003 | research | 子代理+调研/搜索 → pack-research |
| AC-SA-KW-004 | review | 子代理+全面审查/oracle → pack-review |
| AC-SA-KW-005 | qa | 子代理+并行验收/reviewer → pack-qa |
| AC-SA-KW-006 | implement | 子代理+并行实现/worker → pack-implement |
| AC-SA-KW-007 | negate | 「不要子代理」或 `--no-subagent` 覆盖正向词 |
| AC-SA-KW-008 | parallel | 仅「并行」→ host_agents=false；satellite 语义不变 |
| AC-SA-ST-001 | single | 默认路径无 host agent 调用计划 |
| AC-SA-BD-001 | bound | session 标记 cannot_complete_goal=true |
| AC-SA-BD-002 | entry | 无第二公共 skill 入口 |
| AC-SA-IN-001 | install | install-subagent-pack 写入 6 角色到 host dirs |
| AC-SA-VR-001 | verify | verify-subagent-runtime --require-agents 校验 pack |
| AC-SA-EX-001 | example | examples 含 off/on 路径 |
| AC-SA-LM-001 | loom | v2 mirror package 声明同 AC |
| AC-SA-SC-001 | score | L1 suite 可跑；评分层注释 runtime_evidence_only for overlay |

## Keyword contract

**Priority**: `--no-subagent` / 否定词 > `--subagent` / 正向全局词 > default false

**Global on** (any): `subagent`, `sub-agents`, `sub agents`, `with agents`, `子代理`, `多代理`, `开子代理`, `启用子代理`

**Global off** (any): `no subagent`, `without subagents`, `不要子代理`, `禁用子代理`, `单线程 only`（见实现表）

**Stage packs** (after global on):

| pack | tokens |
|------|--------|
| pack-research | 调研, 搜索, search, 竞品, 先搜 |
| pack-review | 全面审查, 多角度, oracle, pln-review subagent, challenge |
| pack-implement | 并行实现, worker, team implement |
| pack-qa | 并行验收, reviewer, qa subagent, correctness |
| pack-default | global on only → scout/search-specialist read-only |

**Six roles**: search-specialist, docs-researcher, multi-agent-coordinator, code-reviewer, backend-developer, qa-expert

## State model

```text
idle → keyword_gate
  miss → single_thread
  hit → pack_select → host_ready
         not_ready → fallback_single + reason
         ready → planned_spawn (parent integrates)
```

Illegal: keyword_miss→spawn; session→goal_completed; pack-qa→release_confirmed

## Non-Goals

- 全量 VoltAgent 同步
- Skill_MAS 自动 rewrite skill
- Pi runtime 内嵌
- 云端 agent OS

## done_when

- AC 合同测绿
- doctor install + verify 可调用
- examples 可跟做
- release 仍人工
