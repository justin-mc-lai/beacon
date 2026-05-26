# Beacon v1.4.11 总览

## 状态

- Version line: `v1.4.11`
- Current status: `qa_passed_ready_for_release_check`
- 初始调研主题：Markdown-first 投影权威清理与旧版兼容退场。
- Carry-forward 调研主题：承接 v1.4.10 中已形成 feature 候选但未纳入当前 aggregate package，或仍停留在 research/backlog 的方向。
- 减负重构主题：保留 Beacon 全功能能力，将固定流程下沉为工具 / gate / schema / test，并将 legacy / fallback / compat 历史包袱显式登记和逐步退场。
- 已冻结低风险第一切片：`authority-vocabulary-and-baseline-inventory-contract`。

## 调研输入

- `docs/beacon/v1.4.11/research/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/research/friction-cd1809c3220a-ui-ux-design-truth-writeback-incident.md`
- `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- `docs/beacon/v1.4.11/research/v1410-feature-carry-forward-intake.md`
- `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`

## Frozen Feature

```text
authority-vocabulary-and-baseline-inventory-contract
```

冻结证据：

- Change: `docs/beacon/v1.4.11/change/authority-vocabulary-and-baseline-inventory-contract.md`
- PRD: `docs/beacon/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md`
- User Story: `docs/beacon/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md`
- Test Cases: `docs/beacon/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md`
- Requirement clarity: `docs/beacon/v1.4.11/execution/requirement-clarity-authority-vocabulary-and-baseline-inventory-contract.md`
- Refreeze summary: `docs/beacon/v1.4.11/change/authority-vocabulary-and-baseline-inventory-contract.refreeze-summary.md`
- Implementation evidence: `impl-f448e052-authority-inventory`
- QA acceptance: `docs/beacon/v1.4.11/execution/qa-acceptance-brief-authority-vocabulary-and-baseline-inventory-contract.md`
- QA scorecard: `.beacon/qa/features/authority-vocabulary-and-baseline-inventory-contract/scorecard.json`

冻结边界：

- 只覆盖 Phase 0 baseline inventory 和 Phase 1 authority vocabulary。
- 不包含 compatibility registry。
- 不改变 QA legacy mirror、PRD legacy mirror、implement legacy loader、prototype legacy source、browser fallback、memory migration、intent router 的运行行为。

## 初始方向

`v1.4.11` 应把 Markdown-first authority cleanup 视为治理硬化线，而不是删除 `.machine`。

推荐收敛方向：

- Markdown requirement package 仍是需求真相。
- `.machine`、`.beacon/state`、runtime ledger、QA matrices、acceptance contracts、release scorecards 仍是 projection / evidence / read model。
- 任何把 machine artifacts 称为 source of truth 的源码文案或运行输出都需要修正。
- legacy / compat / fallback path 必须被清点、版本有界，并且要么退场，要么以 fail-closed 方式显式 admission。
- 固定流程不应长期依赖 Skill 反复解释执行；应下沉为 deterministic tools、gate registry、schema 和回归测试。
- P0 friction `friction:cd1809c3220a` 已纳入 v1.4.11 调研：accepted `ui-ux-dev` UI/UX facts 未写回 `PRODUCT.md` / `DESIGN.md` / PRD / user-story / test-cases 时，implement / QA / release 应 fail closed，而不是按旧 frozen truth 回滚已验收前端事实。候选 gate：`accepted_ui_ux_truth_gap_gate`。

## 候选 Feature

已冻结首个低风险候选：

```text
authority-vocabulary-and-baseline-inventory-contract
```

该候选是 `markdown-first-projection-authority-and-legacy-retirement-contract` 的低风险第一切片，优先解决 authority vocabulary、machine-as-truth 文案和 baseline inventory。Projection kernel 深化留给后续切片。

后续减负重构候选切片：

```text
compatibility-registry-and-command-catalog-contract
qa-prd-legacy-mirror-retirement-contract
implement-package-legacy-loader-retirement-contract
prototype-browser-memory-intent-compat-boundary-contract
test-layering-and-compat-contract-governance
```

Carry-forward 候选池：

```text
qa-multi-layer-real-browser-e2e-acceptance
ralph-task-loop-checkpoint-recovery-contract
learn-context-to-project-skill-lifecycle-injection
qa-attribution-regression-kit
beacon-skill-evolution-proposal-loop
```

其中 `qa-multi-layer-real-browser-e2e-acceptance` 在 v1.4.10 已有 refreeze / QA acceptance 材料，但未纳入当前 8-feature aggregate change package；v1.4.11 必须显式决定是否接收、缩窄或拆分。

本版本当前首个 frozen requirement package 已完成 implementation evidence binding 和 QA acceptance。下一步应进入 release check；后续减负重构候选仍必须单独 refreeze，不得从本切片直接扩大 scope。
