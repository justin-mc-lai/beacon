---
slug: beacon-goal-implement-admission-hard-gate-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
change_reason: "User GO: Scheme A goal implement hard gate via run_workspace_admit + pool + merge-main; dual v1.6.9\\v2.0.0"
---

# Requirement Truth: Goal Implement Admission Hard Gate

## Intent

product-goal 在 **implement 写路径** 前强制 `workspace admit`（复用既有分支治理 / worktree pool / merge-main）；现存 worktree 则 switch 并 merge 主分支；失败 **fail-closed**。不 auto-release。

## UD

| ID | Value |
|----|-------|
| UD-GIA-001 | implement 前必须 `ensure_goal_implement_admission` → `run_workspace_admit`；fail → goal blocked，禁止 ralph |
| UD-GIA-002 | 复用 branch_governance contract + leaf lane；禁止第二套 branch 规则 |
| UD-GIA-003 | 现存 worktree → switched；否则 git worktree add；mkdir-only 非法 |
| UD-GIA-004 | pooled：写入/更新 workspace-pool/<version>/pool.json |
| UD-GIA-005 | admit 后 merge base→feature；conflict → merge_main_conflict 硬停 |
| UD-GIA-006 | stage_trace/execution.jsonl 记录 implement_admission |
| UD-GIA-007 | 不 auto-release；complete 仍要 verifier |
| UD-GIA-008 | 文档登记：git-worktree-execution-flow + beacon-gov-branch；交叉引用 loom W1 |
| UD-GIA-009 | 当 contract `require_workspace_admission=false` 时，goal 仍 **force** dedicated leaf worktree（关 main 直写洞） |
| UD-GIA-010 | parallel_plan satellite worktree 路径以 admit 解析为准对齐 |

## AC

| ID | Description |
|----|-------------|
| AC-GIA-001 | tick --execute @ implement 无 feature → blocked goal_implement_feature_required |
| AC-GIA-002 | require=true 路径复用 run_workspace_admit；pass 后才 ralph |
| AC-GIA-003 | require=false 时 goal_forced_worktree + created/switched |
| AC-GIA-004 | 再次 admit/force → switched + merge 非 conflict |
| AC-GIA-005 | admit/force fail → 不设置 implement_delegate=ralph |
| AC-GIA-006 | execution log 含 implement_admission |
| AC-GIA-007 | 双轨 feature 包 v169+v200 |
| AC-GIA-008 | flow.md + gov-branch 登记 goal 硬闸 |

## Non-goals

- auto-release / self-complete
- 替换 doctor branch-governance 人类面
- mkdir 冒充 worktree

## Runtime

- `beacon/utils/goal_implement_admission.py`
- `beacon/utils/product_goal_runtime.tick_goal_run`（dispatch ralph 前 + enter implement prewarm）
- `beacon/utils/workspace_admission.run_workspace_admit`
