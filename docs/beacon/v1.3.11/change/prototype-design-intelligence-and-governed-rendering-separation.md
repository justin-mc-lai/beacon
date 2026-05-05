# Beacon Feature Change Document

- feature: `prototype-design-intelligence-and-governed-rendering-separation`
- feature_slug: `prototype-design-intelligence-and-governed-rendering-separation`
- version: `v1.3.11`
- status: `reopened-for-artifact-topology-and-consumption-closure`

## Change Intent

- 将 `prototype -> implement` 持续漂移正式收口为 requirement change，而不是继续视为 design prompt 质量问题。
- 补齐 prototype bundle 的正式 artifact topology，避免 internal reasoning、review copy、production copy、implementation handoff 在同一默认执行面混读。
- 把 implement 的唯一允许读取入口收紧到 machine-view / design-artifacts / projection contract，不再默认暴露 explanation materials。

## Scope Delta

- 新增 prototype 四层 artifact topology
- 新增 implement 唯一默认读取入口合同
- 新增 human-readable explanation materials 的 review-only 降级边界
- 新增 projection gate / compile gate 相对 prototype review gate 的前置约束

## Added

- `artifact-topology-contract`
  - prototype bundle 正式区分：
    1. `authoring artifacts`
    2. `review artifacts`
    3. `projection artifacts`
    4. `implementation artifacts`
- `implementation-consumption-entry-contract`
  - implement 默认且唯一允许读取 `machine-view / design-artifacts / implementation-map / projection contracts`
- `review-only-human-materials-boundary`
  - `ux-prd.md`、`DESIGN.md`、`prototype-review.md`、页面解释型 markdown 不再属于默认执行输入面
- `projection-gate-before-render`
  - 在 prototype review 之前增加一层投影闭锁要求：未经投影合同批准的材料不得进入 production render surface

## Removed / Reduced

- 降低 human-readable explanation materials 作为“事实上的正式 handoff 输入”地位
- 降低 implement 对 bundle 同级人类文档的默认可见性
- 降低 gate 只在输出后做词面审查的单点依赖

## Fixed / Clarified

- 明确当前漂移主因不是“提示词不够强”，而是 `artifact topology` 与 `command consumption surface` 未真正 fail-closed
- 明确 `design skill role contract` 不只约束“不能直接 render”，还要约束“不能默认进入 implement 读取面”
- 明确 `pages/*.md / page-specs/*.json / preview.html` 属于 production/review surface，不等于 implement 默认输入 truth
- 明确 review materials 可以保留，但必须从默认执行面降级为 secondary review surface

## Not Added

- 未要求本次 change 直接重写全部 prototype bundle 文件树
- 未把 Beacon 改造成通用设计系统平台
- 未在本次 change 中直接承诺实现层代码完成

## Refresh Route

- `prd revise`: `docs/beacon/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md`
- `user-story refresh`: `docs/beacon/v1.3.11/user-story/prototype-design-intelligence-and-governed-rendering-separation.md`
- `test-case refresh`: `docs/beacon/v1.3.11/qa/test-cases/prototype-design-intelligence-and-governed-rendering-separation.md`
- `prototype refresh`: `docs/beacon/v1.3.11/prototype/prototype-design-intelligence-and-governed-rendering-separation/`
- `implement delta`: `beacon/utils/prototype_utils.py`, `beacon/commands/workflow.py`, `beacon/commands/gate.py`

## Traceability Refs

- `docs/brainstorms/2026-05-04-beacon-brainstorm-分析-beacon-项目中-prototype-子skill-为何在借鉴开源设计-skill-后-仍无法正确描述原型与实现边界-导致-prototype-与-i.md`
- `docs/beacon/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md`
- `docs/beacon/v1.3.11/user-story/prototype-design-intelligence-and-governed-rendering-separation.md`
- `docs/beacon/v1.3.11/qa/test-cases/prototype-design-intelligence-and-governed-rendering-separation.md`
- `docs/beacon/v1.3.11/prototype/prototype-design-intelligence-and-governed-rendering-separation/`
- `beacon/utils/prototype_utils.py`
- `beacon/commands/workflow.py`
- `beacon/commands/gate.py`
