---
slug: beacon-goal-hard-stage-exit-gates-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
domain_required: true
ux_required: false
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
sources:
  - .omx/specs/deep-interview-beacon-goal-harness-drift-fix.md
change_reason: "Hard stage exits + freeze-before-implement + fill-then-pass; deep-interview Decision A"
---

## 人话

Goal tick 硬门：不齐补齐，不齐不前进；freeze ack 后才 implement；main 业务写硬拦。

# Requirement Truth

## User Intent

让 `$beacon-goal` 按 1+6 harness 编排跨边界持续跑到人审 release；边界 gate 强硬；未齐工件由 LLM/worker 补齐后验再进；freeze 补齐≠自签。

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-BG-001 | tick 离开 truth 时若 package status=draft → blocked，stage 不标 done |
| AC-BG-002 | 无 freeze（revision/frontmatter frozen）→ implement admission 失败 freeze_ack_required |
| AC-BG-003 | freeze + worktree admission → implement allow |
| AC-BG-004 | 存在 design stage 且无 design evidence → 不能完成 design→implement |
| AC-BG-005 | qa 无 scorecard/ac_closure 证据时不能 tick 完成 qa |
| AC-BG-006 | main 上 business path commit check blocked |
| AC-BG-007 | plan→truth：ocean blocks_auto_tick 变 hard block |
| AC-BG-008 | release 不 auto human_confirmed |
| AC-BG-009 | block payload 含 fill_harness + resume_action |
| AC-BG-010 | 既有 GIA worktree admission 行为不回归 |
| AC-BG-011 | reason_code 稳定目录见 goal_reason_codes.REASON_CATALOG |
| AC-BG-012 | main 仅允许 docs/beacon/**；其它 docs/** → main_docs_policy_forbidden |
| AC-BG-013 | truth missing vs draft 使用不同 reason_code |

## Non-goals

- open-saas-base 业务
- 改 1+6 公共 surface
- machine freeze 无 ack
- auto-release

## Freeze readiness

- [x] AC table
- [ ] Human freeze ack
