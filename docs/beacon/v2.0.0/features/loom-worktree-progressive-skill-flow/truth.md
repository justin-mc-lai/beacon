---
slug: loom-worktree-progressive-skill-flow
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-19: pln-review accepted — shared git worktree norms + progressive skill load mount for goal/all stages; dual v2.0.0+v1.6.8"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-worktree-progressive-skill-flow/truth.md
  tests: docs/beacon/v2.0.0/features/loom-worktree-progressive-skill-flow/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-worktree-progressive-skill-flow/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-worktree-progressive-skill-flow/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
display_name: "Loom Worktree Progressive Skill Flow"
brand: Loom
ux_required: false
design_deferral: "skill/docs surface; no product marketing UI"
---

# Requirement Truth: git worktree 规范 + 渐进 skill 挂载 (v2.0.0)

## 人话

把「真源 main + 真 git worktree 实现 + merge 对齐」写进共享规范，并由 goal/implement 等渐进加载强制挂上，避免 main 直写再 cherry-pick。

## User Intent

pln-review 接受：共享 reference + progressive always-on 挂载；双版本 v2.0.0 与 v1.6.8 完整补齐。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-WT-SKILL-001 | shared_ref | `skills/beacon/references/git-worktree-execution-flow.md` 为权威规范 |
| UD-WT-SKILL-002 | progressive | goal/implement/qa/release 渐进加载必须带该 ref（或等价 path） |
| UD-WT-SKILL-003 | example | `skills/beacon/examples/git-worktree-process-correct-30s.md` |
| UD-WT-SKILL-004 | no_cherry_pick_align | 禁止用 cherry-pick 作主干对齐主路径 |
| UD-WT-SKILL-005 | no_full_paste | 禁止每个 SKILL 全文粘贴；共享 ref |
| UD-WT-SKILL-006 | dual_version | v1.6.8 同语义包同步落地 |
| UD-WT-SKILL-007 | loom_mirror | loom skill 经 CONTENT_SOURCE 继承，不手改分叉正文 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-WT-SKILL-001 | shared-ref | 仓库存在 `skills/beacon/references/git-worktree-execution-flow.md` 且含 standard sequence + illegal table（Must） |
| AC-WT-SKILL-002 | example | 存在 process-correct 30s 示例（Must） |
| AC-WT-SKILL-003 | goal-surface | `beacon-goal` SKILL 引用共享规范且写明 implement 前 admit/worktree（Must） |
| AC-WT-SKILL-004 | progressive-py | `progressive_skills` / stage plan 对 goal 入口相关 stage 暴露 worktree ref 路径（Must） |
| AC-WT-SKILL-005 | progressive-rs | `skill_load_plan.v1` 在 implement（及 goal/loop 若映射）附带 references 含 git-worktree-execution-flow（Must） |
| AC-WT-SKILL-006 | no-bulk | progressive plan 仍 `bulk_history_forbidden` 且 loaded_count 有界（Must） |
| AC-WT-SKILL-007 | tests | 可执行 TC 验证 ref 文件 + progressive 挂载（Must） |

## Illegal

| ID | Illegal |
|----|---------|
| I-WT-001 | 仅 docs 口号无 progressive 挂载 |
| I-WT-002 | 只改 loom 不改 beacon 权威 skill |
| I-WT-003 | 宣称规范完成却无 example 路径 |

## Non-Goals

- 默认切换生产 beacon
- satellite pool 全自动 OS
- 本湖单独宣称整个 v2 release 完成

## Alignment Surface

完成以 AC 表为准；implement 须改 skill 树 + progressive loader + 测试。
