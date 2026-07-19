---
slug: loom-gitscope-topology-gates
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-19 option2: freeze W1-W5 kernel closure lakes under program loom-kernel-closure-w1w5-v200"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-gitscope-topology-gates/truth.md
  tests: docs/beacon/v2.0.0/features/loom-gitscope-topology-gates/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-gitscope-topology-gates/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-gitscope-topology-gates/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json
parent_kernel: beacon-v2-rust-kernel-redesign
upstream_acs: ["AC-171", "AC-172", "AC-173"]
wave: W4b
priority: P2
ux_required: false
design_deferral: "kernel/CLI; no product marketing UI"
display_name: "Loom GitScope Topology Gates"
brand: Loom
---

# Requirement Truth: GitScope 拓扑三模式 + topology_gate (W4b)

## 人话

monorepo/多 git 不踩坑：GSG→BranchContext；三拓扑；loop/implement 强制 topology_gate_ref。

本湖是 Loom（Beacon 进化品牌）内核补齐的一部分；**不**把生产 `beacon` 默认切走。

## Overview

| Wave | Priority | Upstream AC |
|------|----------|-------------|
| W4b | P2 | AC-171, AC-172, AC-173 |

Depends on: loom-git-worktree-implement-harness

## User Intent

monorepo/多 git 不踩坑：GSG→BranchContext；三拓扑；loop/implement 强制 topology_gate_ref。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-W4B-001 | gsg_load | v1.6.7 GitScopeGraph fixture 可加载投影 |
| UD-LOOM-W4B-002 | three_topo | single_repo|monorepo|multi_git_workspace 行为 fixture |
| UD-LOOM-W4B-003 | force_ref | loop/implement/admission 强制 topology_gate_ref |
| UD-LOOM-W4B-004 | parallel_w4a | 可与 W4a 并行 implement |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-171 | gsg-parity | GSG→BranchContext 扩展字段；失败 gitscope_branch_context_parity_failed（Must） |
| AC-172 | three-topo | 三拓扑 admission 行为级 fixture（Must） |
| AC-173 | force-topology | 缺 topology_gate_ref/pass → 不得 implement：topology_gate_missing|blocked（Must） |

## Illegal

| ID | Illegal |
|----|---------|
| I-W4B-001 | 仅 single_repo 却宣称 BranchContext 完备 |
| I-W4B-002 | 无 topology_gate_ref 进入 implement |

## Non-Goals

- 默认 `BEACON_V2=1` / loom 覆盖 beacon
- 本湖单独宣称整个 v2.0.0 release 完成
- feature slug 全量路径 rename

## Alignment Surface

完成定义以上表 AC 为准；implement/QA 须 integration tier 行为证据与可执行 TC。
