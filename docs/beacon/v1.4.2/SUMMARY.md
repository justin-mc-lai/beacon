# Beacon v1.4.2 总览

## 版本状态

- `v1.4.2` 当前主题是：`contract-aligned test evolution and skill delivery governance`
- 当前版本状态：`planning_only`
- 当前版本不是 runtime release line；当前 runtime/default docs 仍保持 `v1.4.0`
- 当前版本承接 `v1.4.1` deep support surface 之后暴露的测试演进治理缺口：新功能、旧测试、generated surface、skill delivery surface 必须能按契约 lane 增量对齐，而不是把 full-suite 失败混成单一 release 判断。

## 版本目标

`v1.4.2` 聚焦一条主线：

> 把 Beacon 自迭代过程中的测试增量、契约 lane、AC/TC/pytest/evidence 映射、generated surface 同步、legacy snapshot 分类、browser-native QA admission 与 skill delivery 指引收敛为可审计的产品能力，确保 Beacon 在持续演进时仍能保持强交付闭环。

## 当前需求包

- PRD
  - `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- User Story
  - `docs/beacon/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- Test Cases
  - `docs/beacon/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- Execution
  - `docs/beacon/v1.4.2/execution/index.md`
  - `docs/beacon/v1.4.2/execution/architecture-blueprint.md`

## 正式子线

- `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`

## 当前边界判断

- `v1.4.2` 不新增公开一级主命令。
- 测试契约治理能力优先挂载到 `doctor / test-case / qa / release / deep` 现有表面。
- `Test Contract Index` 是 machine-readable delivery governance projection，不是第二 requirement truth。
- `legacy_snapshot` lane 不默认阻断当前 feature release，除非该测试被显式声明为 active compatibility contract。
- generated skill/context/version surfaces 漂移必须被归类为阻断型交付风险。
- skill delivery 文案必须指导 agent 按契约 lane 验证，而不是把 full-suite 失败作为无分类 release 判断。
- browser-capable QA 不能停留在 placeholder runner 或 transcript-only evidence；受保护 live surface 必须显式执行 attached-session / CDP admission judgment。
- `web-access -> attached agent-browser -> playwright attach/CDP -> bare Playwright` 是 protected surface 的优先级方向；如果没有 session bridge，结果必须是 `skip/blocked`，不是假失败。

## 与 v1.4.1 的关系

`v1.4.1` 建立 `deep` 支持面，用于发现复杂业务隐藏风险并生成 test delta。

`v1.4.2` 继续收敛 test delta 被采用后的产品治理问题：

```text
feature evolves
-> affected contract layer is identified
-> AC / TC / pytest / evidence mapping is indexed
-> protected browser surfaces are admitted by session/runner truth
-> tests are classified into lanes
-> release-facing lanes gate current delivery
-> generated surface drift blocks release
-> historical drift routes to explicit test evolution backlog
```

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- `docs/beacon/v1.4.1/deep/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure/deep-test-delta.md`
- `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
