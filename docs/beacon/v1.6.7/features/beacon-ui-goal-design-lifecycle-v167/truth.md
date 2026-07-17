---
slug: beacon-ui-goal-design-lifecycle-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
ux_required: false
domain_required: false
change_reason: "P0+P1 goal design stage + google design.md lint ship + company templates auto-select"
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-ui-goal-design-lifecycle-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-ui-goal-design-lifecycle-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-ui-goal-design-lifecycle-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-ui-goal-design-lifecycle-v167/evidence.md
  research: docs/beacon/v1.6.7/research/beacon-ui-lifecycle-goal-design-baseline-v167-planner-review.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: UI Goal Design Lifecycle v1.6.7

## Overview

把 **DESIGN baseline / 公司模板自动选择 / google design.md lint** 挂进 **beacon goal** 全生命周期，使 `ux_required`（或等价视觉交付信号）时：

```text
plan → truth → design → implement → qa → release
```

原则：**先对齐商业大公司视觉（可千篇一律），再 fine-tune**；awesome-design-md 仅 seed/参考，不是 ship 权威。

## User Intent（一行）

有视觉交付的目标，必须先自动冻结 DESIGN，再严格实现与验收。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-UIG-001 | Goal stage | **ux_required 时强制插入 design stage** |
| UD-UIG-002 | Baseline | **design stage 自动 baseline（surface+company auto）** |
| UD-UIG-003 | Existing DESIGN | **不覆盖；写 fine-tune-proposal** |
| UD-UIG-004 | Lint | **google design.md lint 为 ship/QA 证据** |
| UD-UIG-005 | Company templates | **curated 商业模板自动选择；先对齐再调** |
| UD-UIG-006 | Implement | **无 DESIGN 且 UX → fail-closed 指向 baseline** |
| UD-UIG-007 | awesome-md | **reference-only，永不 ship authority** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-UIG-G01 | goal-stage | ux_required 时 stages 含 `design` 且 progressive skills 含 design（**Must**） |
| AC-UIG-G02 | auto-baseline | design stage/tick 可自动 synthesize baseline 并记录 artifact 路径（**Must**） |
| AC-UIG-G03 | fine-tune | 已有 DESIGN 时不覆盖，产出 fine-tune-proposal（**Must**） |
| AC-UIG-L01 | lint-cli | `beacon design lint` 调用 google design.md lint 并落 JSON 证据（**Must**） |
| AC-UIG-L02 | lint-ship | ux_required 且 lint error/missing → ui_design_ship blocked（**Must**） |
| AC-UIG-T01 | company-catalog | ≥8 公司模板可被 catalog 选择且可解释 reason（**Must**） |
| AC-UIG-T02 | company-auto | auto 选择与 surface/关键词一致（**Must**） |
| AC-UIG-I01 | implement | UX 且无 DESIGN 时 implement prompt/precheck fail-closed（**Must**） |
| AC-UIG-Q01 | qa-scorecard | scorecard 暴露 design_baseline / design_md_lint / ui_state_matrix（**Must**） |
| AC-UIG-R01 | release | design ship blocked 时 release_ready 不允许（**Should**） |

## Non-Goals

- 不把 70+ 品牌全量导入为默认
- 不替代 ui-ux-dev 探索执行面
- 不把 support checklist 当已强制门禁

## Dependencies

- beacon-product-goal-runtime-v167
- beacon-ui-design-ship-gate-v167
- design_baseline / design_surfaces
