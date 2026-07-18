---
slug: loom-brand-surface
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-18: v2 evolution brand=Loom; dual-install with beacon; no default replace"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-brand-surface/truth.md
  tests: docs/beacon/v2.0.0/features/loom-brand-surface/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-brand-surface/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-brand-surface/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
ux_required: false
design_deferral: "CLI/skill branding; no product marketing UI"
---

# Requirement Truth: Loom Brand Surface (R1)

## Overview

将 v2 进化线对外品牌定为 **Loom**（织多条交付能力线），与生产轨 **Beacon (v1.6.7)** **并行安装、互不默认覆盖**。

| 面 | 生产轨 Beacon | 进化/验收轨 Loom |
|----|---------------|------------------|
| 品牌 | Beacon | **Loom** |
| pip | `beacon` | **`loom`**（冲突时可 `loom-ai`） |
| CLI | `beacon` | **`loom`** |
| 公共 skill | `$beacon-goal` | **`$loom-goal`** |
| support skill | `$beacon-loop-goal` | **`$loom-loop-goal`**（support only） |
| 状态根 | `.beacon/` 既有 | **`.loom/` 或 `~/.loom/`**（隔离） |

## User Intent

v2 不再叫「又一个 beacon」，叫 **Loom**；本机可同时装 beacon 生产与 loom 验收，互不盖掉。

## User Decisions（locked — GO 2026-07-18）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-001 | Brand | **Loom** |
| UD-LOOM-002 | CLI | **`loom`** |
| UD-LOOM-003 | Public skill | **`$loom-goal`** |
| UD-LOOM-004 | Dual install | **并行** `beacon` + `loom` |
| UD-LOOM-005 | Default replace | **禁止** Day-1 用 loom 覆盖/alias `beacon` |
| UD-LOOM-006 | Semantic entry | 每轨仍唯一 goal facade；loop 仅 support |
| UD-LOOM-007 | Sub-skills Phase-1 | **共享** `skills/beacon/*` 内容路由；Phase-2 可选 `loom-*` 镜像 |
| UD-LOOM-008 | Docs path | 过渡期可保留 `docs/beacon/v2.0.0`；对外称 Loom |
| UD-LOOM-009 | W4 | 仍禁止默认 `BEACON_V2=1` / 默认 `loom` 接管 `beacon` 直至人工 GO |
| UD-LOOM-010 | Relation to beacon2 research | 取代 `beacon2`/`beacon-v2` 命名建议，统一 **loom** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-LOOM-BR-001 | names | 合同固定 pip=`loom`、CLI=`loom`、skill=`loom-goal`（**Must**） |
| AC-LOOM-BR-002 | dual-install | 同机可装 beacon 与 loom，二进制名不冲突（**Must**） |
| AC-LOOM-BR-003 | no-replace | 安装 loom **不得**改写 `beacon` launcher（**Must**） |
| AC-LOOM-BR-004 | facade | `$loom-goal` 为 loom 轨唯一公共入口；loop 为 support（**Must**） |
| AC-LOOM-BR-005 | beacon-preserved | `$beacon-goal` / `beacon goal` 行为不被 loom 安装破坏（**Must**） |
| AC-LOOM-BR-006 | state-isolation | loom 默认状态根与 `.beacon` 隔离（**Must**） |
| AC-LOOM-BR-007 | matrix | 双装验收矩阵（which/version/goal/release）有测试或 checklist（**Must**） |
| AC-LOOM-BR-008 | docs | 30s 用法示例 loom + beacon 并列（**Must**） |
| AC-LOOM-BR-009 | no-early-default | 发布材料不宣称 loom 为默认替代 beacon（**Must**） |
| AC-LOOM-BR-010 | legal-illegal | tests 含合法双装 walk + 非法覆盖路径（**Must**） |

## Illegal

| ID | Illegal |
|----|---------|
| I-LOOM-BR-001 | pip install loom 覆盖 `~/.local/bin/beacon` |
| I-LOOM-BR-002 | 第三公共入口 skill 与 loom-goal 并列主编排 |
| I-LOOM-BR-003 | W4 前默认 alias beacon→loom |
| I-LOOM-BR-004 | 两轨静默写同一未标注权威状态库 |

## Non-Goals

- 立刻重命名整个 monorepo 目录为 loom
- 立刻 fork 33 个 skill 为 loom-*
- 废弃 beacon 生产包

## Dependencies

- research: docs/beacon/v2.0.0/research/beacon-v2-rename-loom-subagent-trace-pln-review.md
- research: docs/beacon/v2.0.0/research/beacon-v2-parallel-cli-skill-naming-pln-review.md
- peer: loom-goal-optional-subagent, loom-goal-trace-bundle

## Planner promotion

User GO 2026-07-18 confirmed brand Loom + dual-install + three capability lakes.
