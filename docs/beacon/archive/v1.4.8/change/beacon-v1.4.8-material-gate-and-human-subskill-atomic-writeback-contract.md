# Change: beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract

**Version**: `v1.4.8`
**Status**: `accepted_for_implementation`
**Generated**: `2026-05-21`

## Why This Change Exists

`v1.4.8` 的调研已经确认两个系统性缺口：

1. execution host contract 可以退化成碎片化 side dossiers，导致 `architecture-blueprint.md`、`execution/index.md`、service / branch / worktree 事实不再有稳定住所。
2. 人类面 support / toolkit skill 可以产出建议，但如果没有显式材料更新、材料义务或 route-back，后续 `implement / QA / release` 仍可能继续推进。

这条 change 的目的，是把这两个缺口正式冻结成 requirement package：

- 恢复 Beacon 物料强 gate 门禁
- 让每个被调用的人类面 skill 都按职责产生可验证的 material effect
- 阻断默认 seed 和静默缺文档

## Delta

- add execution host required surface contract
- add branch / service / worktree explicit-fact gate
- add per-subskill material effect registry requirement
- add support finding adoption contract
- add canonical branch governance writeback target set
- add open artifact update obligation blocking rule
- add no silent default seed rule
- add implement / QA / release fail-closed gate consumption requirement

## Freeze Intent

本次冻结只冻结 requirement truth。

本次不直接执行：

- implementation
- QA
- release
- runtime promotion

## Re-freeze Result

官方 `beacon change --refreeze-chain` 已完成：

- refreeze status: `complete`
- revision before: `R2`
- revision after: `R3`
- transaction:
  - `docs/beacon/archive/v1.4.8/.machine/change/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.refreeze-transaction.json`

该 requirement package 当前冻结范围包括：

- `change`
- `prd`
- `user-story`
- `test-case`
- `research`
- `source-architecture`

当前下游 route：

- next formal stage: `implement`
- follow-up verification stage: `qa`

## Traceability

- `docs/beacon/archive/v1.4.8/research/beacon-v1.4.8-execution-material-rigor-and-version-governance-analysis.md`
- `docs/beacon/archive/v1.4.8/research/beacon-v1.4.8-human-subskill-material-closure-and-gate-contract.md`
- `docs/beacon/archive/v1.4.8/research/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- `docs/beacon/archive/v1.4.8/prd/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- `docs/beacon/archive/v1.4.8/user-story/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- `docs/beacon/archive/v1.4.8/qa/test-cases/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
