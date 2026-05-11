# Beacon v1.4.3 总览

## 版本状态

- `v1.4.3` 当前主题是：`evidence-first decision surfaces and governed learning activation`
- 当前版本状态：`current runtime release line`
- 当前版本已经提升为 runtime/default docs line：`v1.4.3`
- 当前版本承接 `v1.4.0` 人类面与子 skill 对标 `gstack` 后暴露的产品缺口：Beacon 在 requirement challenge、design decision、prototype 边界、learning recall、support-surface explainability 上仍偏薄，导致 evidence-first 更强地体现在交付后段，而不是从问题定义到 UX handoff 全链路生效。

## 版本目标

`v1.4.3` 聚焦一条主线：

> 把 Beacon 从“冻结真相后强治理”的 evidence-first 内核，继续提升为“从问题定义、范围挑战、设计决策、原型交接、学习召回到 QA/release 全程都强 evidence”的产品系统，同时不扩张公开主生命周期与 truth/gate 边界。

## 当前需求包

- PRD
  - `docs/beacon/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
  - `docs/beacon/v1.4.3/prd/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md`
  - `docs/beacon/v1.4.3/prd/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`
  - `docs/beacon/v1.4.3/prd/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`
- User Story
  - `docs/beacon/v1.4.3/user-story/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
  - `docs/beacon/v1.4.3/user-story/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md`
  - `docs/beacon/v1.4.3/user-story/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`
  - `docs/beacon/v1.4.3/user-story/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`
- Test Cases
  - `docs/beacon/v1.4.3/qa/test-cases/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
  - `docs/beacon/v1.4.3/qa/test-cases/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md`
  - `docs/beacon/v1.4.3/qa/test-cases/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`
  - `docs/beacon/v1.4.3/qa/test-cases/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`
- Execution
  - `docs/beacon/v1.4.3/execution/index.md`
  - `docs/beacon/v1.4.3/execution/architecture-blueprint.md`
  - `docs/beacon/v1.4.3/execution/boundaries.md`
- Change
  - `docs/beacon/v1.4.3/change/v1.4.3.md`
  - `docs/beacon/v1.4.3/change/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
  - `docs/beacon/v1.4.3/change/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md`
  - `docs/beacon/v1.4.3/change/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`
  - `docs/beacon/v1.4.3/change/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`

## 正式子线

- `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`
- `beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface`
- `beacon-v1.4.3-design-review-surface-and-prototype-governance`
- `beacon-v1.4.3-governed-learning-recall-and-route-explainability`

## 当前冻结判断

- `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / qa-accepted umbrella aggregation`
- `beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / qa-accepted`
- `beacon-v1.4.3-design-review-surface-and-prototype-governance`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / qa-accepted`
- `beacon-v1.4.3-governed-learning-recall-and-route-explainability`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / qa-accepted`

## 当前边界判断

- `v1.4.3` 不新增公开一级主命令。
- 新增能力优先以 host-visible support/review skill 形态进入，而不是扩张主生命周期。
- `ceo-review`、`design-review`、`learn` 若进入范围，必须被定义为 support/review surface，而不是新的 truth source 或 gate source。
- `prototype` 若继续保留，必须收缩回 `requirement-driven freeze + UX handoff contract`，不得继续承担产品战略判断或设计定稿职责。
- learning 进入默认决策输入后，仍只能作为 hint / recall / warning / prior pattern，不能单独定义 pass、blocked、freeze-ready 或 release-ready。
- `help / status / ask / deep` 若增强 explainability，必须解释 route、证据缺口、learning injection 与下一步，而不是创造并行 completion truth。

## 与 v1.4.2 的关系

`v1.4.2` 聚焦：

- test contract governance
- browser-native QA admission
- skill delivery guidance

`v1.4.3` 继续把 evidence-first 往上游推：

```text
problem framing
-> CEO-grade challenge
-> requirement truth
-> design-grade challenge
-> prototype/handoff freeze
-> implement
-> qa
-> release
-> learning audit and recall
-> next skill run
```

## 当前收敛判断

- `v1.4.3` 不再只是一条总线想法，而是已经拆成 3 条可实施子线：
  - `ceo-review` 前置战略挑战
  - `design-review + prototype 去负载`
  - `learning recall + route explainability`
- 总线 feature 继续作为版本级收敛框架存在，用于约束这 3 条子线共同服务同一个 evidence-first 方向。
- 当前结论是：
  - `v1.4.3 requirement package frozen`
  - `subfeature decomposition completed`
  - `support-surface implementation completed`
  - `umbrella acceptance aggregation completed`
  - `strict gate passed`
  - `release check passed`
  - `runtime/default docs promotion completed`

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- `docs/beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- `docs/analysis/beacon-v1.4.0-human-surface-and-subskill-benchmark-vs-gstack.md`
- `docs/analysis/beacon-v1.4.0-gstack-command-matrix-and-prototype-surface-gap.md`
