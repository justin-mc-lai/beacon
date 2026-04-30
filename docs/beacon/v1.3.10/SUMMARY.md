# Beacon v1.3.10 总览

## 版本状态

- `v1.3.10` 是围绕真实项目 `rolo` 暴露出的 monorepo / repo-binding / branch-governance 漂移问题收口的一条单主题版本线。
- 当前版本主题是：`project topology metadata + requirement package dual-write gate + deterministic remediation support surface`。
- 当前版本材料状态：`curated and verify-materials pass`。

## 版本目标

`v1.3.10` 聚焦解决三类确定性治理缺口：

1. 缺少 `project_root -> service repo roots -> version-scoped allowed working branch` 的固定元信息模型
2. `beacon-change / reopen / freeze` 之后 requirement package 仍可能出现 human / machine 单面更新
3. help / status / real-project-validation 对 requirement package 漂移的 remediation 指引还不够显式

## 当前需求包

- PRD
  - `docs/beacon/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- User Story
  - `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- Test Cases
  - `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`

## 正式子线

- `beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance`

## 冻结状态

- `Beacon v1.3.10 project topology and version-branch metadata transaction governance`: `material-curated`

## 当前收口结论

- 项目元信息命令面已固定收口到 `beacon doctor metadata ...`
- 核心 metadata 边界已收敛为：
  - topology
  - repo binding
  - participating services
  - per-service allowed working branch
- requirement package dual-write contract 已固定为 `v1.3.10+` 的强门禁
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

## 版本主题图

```text
rolo monorepo friction
-> metadata governance
-> doctor metadata surface
-> deterministic repo / branch guard
-> change-loop requirement package dual-write
-> help / status / proof remediation convergence
```
