# Beacon Feature Change Document

- feature: `Beacon v1.3.11 PRD freeze anti-drift and machine-mirror reconciliation`
- feature_slug: `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation`
- version: `v1.3.11`
- status: `reopened`

## Change Intent

- 将本次 `v1.3.11` PRD 从“手工增强 markdown 后 machine 侧静默滞后”的状态，正式收口为 requirement truth 变更项。
- 明确 `PRD freeze` 的闭环不应只要求 markdown contract valid，还必须要求 human truth 与 machine mirror 保持可重投影、可审计、可恢复的一致性。
- 将当前一次性脚本修复暴露出来的流程缺口，升级为 Beacon 正式 requirement scope，而不是保留为人工补洞经验。

## Scope Delta

- 新增 `PRD freeze anti-drift` requirement line
- 新增 `machine mirror reconciliation` requirement line
- 补充 `validate / audit / reconcile` 三者职责边界
- 补充 transaction latest/supersedes 语义需求
- 将这次变更定位为 change-loop requirement refresh，而不是实现层临时修补

## Added

- requirement delta:
  - `prd markdown` 允许成为 authoritative editable truth
  - `machine mirror` 必须支持从当前 markdown 确定性重投影
  - `audit` 必须覆盖 `.beacon/prd` 与 `docs/beacon/<version>/.machine/prd`
  - `change loop` 必须能表达 `human changed / machine stale / reconcile required`

## Removed / Reduced

- 不再接受“validate 通过即可视为 freeze truth 完整”的隐含假设
- 降低对一次性脚本手工修复 machine sink 的依赖

## Fixed / Clarified

- 明确 `prd create` 只是创建时双写，不等于后续编辑自动同步。
- 明确 `prd validate` 只校验 markdown contract，不承担 machine write-back。
- 明确 `prd audit` 不能只比对 `.beacon/prd/*.json`，后续必须扩展到 canonical/compile mirror。
- 明确 transaction 历史需要表达最新冻结结果，避免多个 transaction 并存但没有 latest 指针。
- 明确本次 change 的目标是补齐 freeze anti-drift requirement 闭环，后续再进入 user-story / test-case / implement。

## Not Added

- 未直接在本次 change 文档中引入新的一级公开命令。
- 未在本次 change 文档中直接承诺 remote store、数据库或多租户控制平面。
- 未跳过 requirement refresh 直接进入实现。

## Readiness

- requirement clarity：已收口
- main-chain refresh：待继续
- freeze readiness：未完成，需先完成 user-story / test-case refresh
- 当前状态：已正式 reopen 为 change item，可继续进入 requirement refresh

## Traceability Refs

- `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `docs/beacon/v1.3.11/.machine/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.canonical.json`
- `docs/beacon/v1.3.11/.machine/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.compile.json`
- `.beacon/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.json`
- `.beacon/state/prd-transactions/tx-prd-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance-prd-38c952ca4330dd7a.json`
