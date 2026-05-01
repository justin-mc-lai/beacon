# Beacon v1.3.10 总览

## 版本状态

- `v1.3.10` 起初围绕真实项目 `rolo` 暴露出的 monorepo / repo-binding / branch-governance 漂移问题收口。
- 当前版本已扩展为两条并行收口子线：
  - `project topology metadata + requirement package dual-write gate + deterministic remediation support surface`
  - `prototype UX PRD closure + design-asset projection`
- 当前版本材料状态：`requirement-freeze-ready`

## 版本目标

`v1.3.10` 当前聚焦解决两组互补缺口：

1. 项目与版本执行面治理缺口：
   - 缺少 `project_root -> service repo roots -> version-scoped allowed working branch` 的固定元信息模型
   - `beacon-change / reopen / freeze` 之后 requirement package 仍可能出现 human / machine 单面更新
   - help / status / real-project-validation 对 requirement package 漂移的 remediation 指引还不够显式
2. prototype requirement closure 缺口：
   - `prototype` 仍更接近结构 freeze，而不是真正的 UI/UX 类 PRD 编译
   - design context / design reasoning / design assets 还没有正式进入 requirement package
   - implement / qa 还不能稳定消费同一套 UX closure truth

## 当前需求包

- PRD
  - `docs/beacon/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
  - `docs/beacon/v1.3.10/prd/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- User Story
  - `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
  - `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- Test Cases
  - `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
  - `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`

## 正式子线

- `beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance`
- `beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection`

## 冻结状态

- `Beacon v1.3.10 project topology and version-branch metadata transaction governance`: `material-curated`
- `Beacon v1.3.10 prototype UX PRD closure and design-asset projection`: `freeze_ready`

## 当前收口结论

- 项目元信息命令面已固定收口到 `beacon doctor metadata ...`
- 核心 metadata 边界已收敛为：
  - topology
  - repo binding
  - participating services
  - per-service allowed working branch
- requirement package dual-write contract 已固定为 `v1.3.10+` 的强门禁
- prototype 重构方向已固定为：
  - `prototype` 仍属于 requirement-driven wireframe freeze
  - 但必须新增 `design_context / design_reasoning / ux_contract / DESIGN.md / previews`
  - 目标是把 `prototype` 升级成 UI/UX 类 PRD 编译器
  - 本轮 reopen 已把 `state-aware component contract / cross-page business transition / automation priority matrix` 补进 requirement truth
- `help / status / real-project-validation` 已能显式暴露 remediation 动作：
  - `beacon-change`
  - `beacon doctor sync-materials`
  - `beacon doctor verify-materials --strict`

## 关键验收锚点

- `docs/beacon/v1.3.10/change/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/v1.3.10/change/v1.3.10.md`
- `docs/beacon/v1.3.10/release/v1.3.10.md`
- `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.ac-test-matrix.json`
- `docs/beacon/v1.3.10/prd/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.ac-test-matrix.json`

## 版本主题图

```text
rolo monorepo friction
-> metadata governance
-> doctor metadata surface
-> deterministic repo / branch guard
-> change-loop requirement package dual-write
-> help / status / proof remediation convergence
-> prototype UX PRD closure
-> design context + design reasoning
-> DESIGN.md + preview asset projection
-> implement / qa consume same UX truth
```
