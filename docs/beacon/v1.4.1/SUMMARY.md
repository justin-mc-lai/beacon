# Beacon v1.4.1 总览

## 版本状态

- `v1.4.1` 当前主题是：`deep analysis support surface and risk closure`
- 当前版本状态：`planning_only`
- 当前版本不是 runtime release line；当前 runtime/default docs 仍保持 `v1.4.0`
- 当前版本目标是承接真实项目 `slow_uni_bmtop / friend-match` 验收复盘中暴露的深度能力缺口，并把它收敛成 Beacon 下一版本主线需求

## 版本目标

`v1.4.1` 聚焦一条主线：

> 在不扩张 Beacon 人类主生命周期、不新增默认必经阶段、不让分析面改写 frozen truth 的前提下，建立 loop-capable `deep analysis` 支持面，用于复杂业务功能的状态机建模、跨模块闭环分析、事实源一致性审查、测试用例增量生成与 release 风险收敛。

## 当前需求包

- PRD
  - `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- Research
  - `docs/beacon/v1.4.1/research/beacon-deep-capability-upgrade-research-supplement.md`
- Execution
  - `docs/beacon/v1.4.1/execution/index.md`

## 正式子线

- `beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure`

## 当前边界判断

- `deep` 不是新的主生命周期阶段
- `deep` 不替代 `prd / user-story / test-case / qa / release`
- `deep` 是支持面、分析面、gate supplement surface
- `deep` 应以 `beacon-deep` 人类面支持 skill / toolkit surface 暴露，而不是主生命周期阶段
- `deep` 应支持 loop：scan truth、model business、challenge gaps、derive delta、route repairs、verify closure
- `deep` 默认应在同一用户意图的一次 run 内尽量闭环；只有新提示词引入新 feature、角色、状态机、业务流程或 release-blocking evidence 时才开启新 loop
- `deep` 输出建议、delta、risk、closure brief；不得直接改写 frozen truth
- 高风险功能可被要求补齐 deep 产物或 skip reason
- 低风险功能允许显式跳过 deep，并记录原因

## 与 v1.4.0 的关系

`v1.4.0` 已经收敛了 lightweight kernel、core surface、prototype 条件触发、LLM decision surface、agent surface 等能力边界。

`v1.4.1` 不推翻这些边界，而是在其上补齐一个新缺口：

```text
known requirement acceptance is pass
-> complex business model may still be under-specified
-> beacon-deep loop discovers state / invariant / consistency gaps
-> test-case delta and risk register converge the gap before QA
-> accepted gaps route to change/refreeze, implement repair, or supplemental QA
-> release consumes deep closure, waiver, backlog decision, or explicit skip reason
```

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.0/SUMMARY.md`
- `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- `docs/beacon/v1.4.1/research/beacon-deep-capability-upgrade-research-supplement.md`

## 版本主题图

```text
MVP QA can validate known requirements
-> complex features still hide state-machine and data-consistency gaps
-> Beacon adds beacon-deep as loop-capable optional/support governance
-> high-risk features get state/invariant/test-delta/risk/loop closure
-> main lifecycle stays small and truth discipline stays unchanged
```
