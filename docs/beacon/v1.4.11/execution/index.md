# Beacon v1.4.11 执行索引

## 状态

- `v1.4.11` 已冻结低风险第一切片。
- 当前 frozen feature：`authority-vocabulary-and-baseline-inventory-contract`。
- 该 feature 已完成 implementation evidence binding 和 QA acceptance。
- QA verdict：`passed`。
- QA run id：`run-20260526T180040809108`。

## Research Inputs

- `docs/beacon/v1.4.11/research/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- `docs/beacon/v1.4.11/research/v1410-feature-carry-forward-intake.md`
- `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`

## Frozen Requirement Package

- Change: `docs/beacon/v1.4.11/change/authority-vocabulary-and-baseline-inventory-contract.md`
- PRD: `docs/beacon/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md`
- User Story: `docs/beacon/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md`
- Test Cases: `docs/beacon/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md`
- Source Architecture: `docs/beacon/v1.4.11/source-architecture/authority-vocabulary-and-baseline-inventory-contract.md`
- Requirement Clarity: `docs/beacon/v1.4.11/execution/requirement-clarity-authority-vocabulary-and-baseline-inventory-contract.md`
- Revision Delta: `docs/beacon/v1.4.11/execution/revision-delta-authority-vocabulary-and-baseline-inventory-contract.md`
- Refreeze Summary: `docs/beacon/v1.4.11/change/authority-vocabulary-and-baseline-inventory-contract.refreeze-summary.md`
- Implementation Evidence: `impl-f448e052-authority-inventory`
- QA Acceptance Brief: `docs/beacon/v1.4.11/execution/qa-acceptance-brief-authority-vocabulary-and-baseline-inventory-contract.md`
- QA Scorecard: `.beacon/qa/features/authority-vocabulary-and-baseline-inventory-contract/scorecard.json`
- AC Closure: `.beacon/qa/features/authority-vocabulary-and-baseline-inventory-contract/ac-closure.json`

## Frozen Scope Boundary

In scope:

- Phase 0 baseline inventory.
- Phase 1 authority vocabulary.
- Forbidden machine-as-truth wording tests.
- Inventory markdown and JSON artifacts.
- No behavior-retirement regression guard.

Out of scope:

- Compatibility registry.
- QA / PRD legacy mirror policy changes.
- Implement legacy loader migration.
- Prototype / browser / memory / intent behavior changes.
- Release verdict changes.

## Legacy Burden Reduction Candidate Cuts

- `authority-vocabulary-and-baseline-inventory-contract` frozen
- `authority-vocabulary-and-projection-kernel-contract` follow-up candidate
- `compatibility-registry-and-command-catalog-contract`
- `qa-prd-legacy-mirror-retirement-contract`
- `implement-package-legacy-loader-retirement-contract`
- `prototype-browser-memory-intent-compat-boundary-contract`
- `test-layering-and-compat-contract-governance`

## Carry-Forward Candidate Pool

- `qa-multi-layer-real-browser-e2e-acceptance`
- `ralph-task-loop-checkpoint-recovery-contract`
- `learn-context-to-project-skill-lifecycle-injection`
- `qa-attribution-regression-kit`
- `beacon-skill-evolution-proposal-loop`

## 下一跳

推荐正式路由：

```bash
beacon release check --project . --version v1.4.11
```

release check 只应评估已冻结并通过 QA 的 Phase 0 + Phase 1。完整 legacy 减负计划见 `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`。

如果 v1.4.11 先处理 v1.4.10 未纳入 aggregate package 的 QA carry-forward，则推荐路由：

```bash
beacon change-refreeze "qa-multi-layer-real-browser-e2e-acceptance" --project . --version v1.4.11
```

只有在选定 feature 已具备 PRD、user story、test case 和 freeze 材料后，才应进入 implementation。
