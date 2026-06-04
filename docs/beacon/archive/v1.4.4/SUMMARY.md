# Beacon v1.4.4 总览

## 版本状态

- `v1.4.4` 当前主题是：`pragmatic design baseline and restrained template governance`
- 当前版本状态：`planning_only`
- 当前版本不是 runtime release line；当前 runtime/default docs 仍保持 `v1.4.3`
- 当前版本承接 `v1.4.3` 已建立的 `design-review + prototype` 分层，但继续补齐一个务实缺口：Beacon 需要在不新增一组 design 子 skill 的前提下，把基础反 AI UI/UX 质量、默认设计模板与 agent-friendly 设计资产收敛进现有人类面。

## 版本目标

`v1.4.4` 聚焦一条主线：

> 把 Beacon 的基础审美、交互一致性与反 AI UI/UX 约束吸收到既有 `design-review / prototype / implement / qa` 闭环中，并提供 3 个固定、克制、可直接使用的默认模板；模板基线借鉴 `VoltAgent/awesome-design-md` 的 `apple` 与 `vercel` 设计资产，但不把外部仓库升级为 Beacon 默认依赖。

## 当前需求包

- PRD
  - `docs/beacon/archive/v1.4.4/prd/beacon-v1.4.4-pragmatic-design-baseline-and-template-governance.md`
- User Story
  - `docs/beacon/archive/v1.4.4/user-story/beacon-v1.4.4-pragmatic-design-baseline-and-template-governance.md`
- Test Cases
  - `docs/beacon/archive/v1.4.4/qa/test-cases/beacon-v1.4.4-pragmatic-design-baseline-and-template-governance.md`
- Execution
  - `docs/beacon/archive/v1.4.4/execution/index.md`
  - `docs/beacon/archive/v1.4.4/execution/architecture-blueprint.md`
- Change
  - `docs/beacon/archive/v1.4.4/change/v1.4.4.md`
  - `docs/beacon/archive/v1.4.4/change/beacon-v1.4.4-pragmatic-design-baseline-and-template-governance.md`

## 正式子线

- `beacon-v1.4.4-pragmatic-design-baseline-and-template-governance`

## 当前边界判断

- `v1.4.4` 不新增公开一级主命令。
- `v1.4.4` 不新增一组面向人类的 design 子 skill 家族。
- 设计质量能力优先挂载到 `beacon-design-review`、`beacon-prototype`、`implement`、`qa` 与对应 machine projection。
- 模板目录固定为 3 个，不提供开放式风格市场。
- `VoltAgent/awesome-design-md` 的 `apple` / `vercel` 只能作为研究与归一化输入，不能成为 Beacon 运行时默认依赖。
- 反 AI UI/UX 约束必须作为默认基线进入 review / prototype / QA，而不是只作为可选审美建议。
- `prototype` 仍然只承担 requirement-driven freeze 与设计资产投影，不升级为 final visual approval。

## 与 v1.4.3 的关系

`v1.4.3` 已经建立：

- `design-review` 是独立的 support/review surface
- `prototype` 被收缩回 conditional freeze / handoff contract
- 设计判断与原型冻结不再混层

`v1.4.4` 继续在这个边界上补齐默认产品化能力：

```text
design-review boundary exists
-> Beacon still lacks a small default taste baseline
-> anti-AI UI/UX rules are not yet normalized into one contract
-> design assets still need a small fixed template catalog
-> existing human surface should absorb the improvement without skill sprawl
```

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.3/SUMMARY.md`
- `docs/beacon/v1.4.3/prd/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`
- `docs/beacon/v1.3.10/prd/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- `skills/beacon/beacon-design-review/SKILL.md`
- `skills/beacon/beacon-prototype/SKILL.md`
