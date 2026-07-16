---
program_slug: beacon-unified-topology-loop-goal-v167
version: v1.6.7
plan_mode: interactive
scope_mode: full_parity
lake_or_ocean: 海拆湖
program_phase: P1
p4_ack: true
delegated_sub_skill: beacon-pln-review
upstream_program: beacon-loop-meta-remediation-v166
upstream_version: v1.6.6
promotion_ref: friction:2e306f7acea7
user_decisions:
  UD-TOPO-001: GitScopeGraph_unified_main_plus_satellite_scopes
  UD-TOPO-002: resilient_stop_requires_reason_code_and_resume_action
  UD-TOPO-003: deterministic_intent_re_resolution_not_probabilistic
  UD-TOPO-004: dual_runtime_cli_agent_and_host_skill_share_state
  UD-TOPO-005: v2_schema_parity_with_BranchContext_TraceContext
  UD-PROGRAM-002: v1.6.7_new_program_after_v1.6.6_loop_goal_R6
---

# Program Manifest — Unified Topology + Intent-Aware Loop Goal v1.6.7

## User Intent (one line)

Beacon 统一治理 **单仓 / monorepo / 多 git 卫星仓**，并让 **loop-goal 可持续续跑**（每次停有 reason + resume 路径）；v1 Python 与 v2 Rust **同一 schema**；支持 **CLI+agent** 与 **host skill** 双通道。

## Utterance (stable paraphrase)

1. 采用 `GitScopeGraph`：主仓 + 卫星仓一张图，统一 admission / topology_gate。
2. loop-goal R7：意图分叉记录、决策缓存、interrupt 语义、resume 短词映射、`beacon loop-goal run` CLI。
3. 「不能随便停」= 合法硬停 + 可恢复续跑；release 仍人工门。
4. v2 `BranchContext` / `TraceContext` / `intent_snapshot` 与 v1 JSON schema 钉死 parity。

## Scope Mode

`full_parity` — 两湖 feature（B→A 拓扑序），v2 parity 为 cross-version contract，不交付 Rust 实现。

## Non-Negotiable Boundaries (user-confirmed)

| UD | Decision |
|----|----------|
| UD-TOPO-001 | **GitScopeGraph** 统一 single_repo / monorepo / multi_git_workspace |
| UD-TOPO-002 | 每次停必须 `reason_code` + `resume_action`；禁止无状态 no-op |
| UD-TOPO-003 | **deterministic** intent re-resolution；拒绝概率路由（D-LG-003） |
| UD-TOPO-004 | CLI `beacon loop-goal run` ≡ host `beacon-loop-goal` skill（同一 state 文件） |
| UD-TOPO-005 | v1.6.7 schema fixtures 必须被 v2 program parity AC 引用 |
| UD-PROGRAM-002 | 独立 v1.6.7 program；不 reopen v1.6.6 frozen closure |

## Topology Order

1. `beacon-git-scope-graph-v167` (Slice B)
2. `beacon-loop-goal-v166` R7 (Slice A; depends on topology_gate)

## Route Recommendation

After truth freeze per feature → `beacon-gen-implement v1.6.7` → `beacon-eval-qa` → `beacon-eval-release`.
