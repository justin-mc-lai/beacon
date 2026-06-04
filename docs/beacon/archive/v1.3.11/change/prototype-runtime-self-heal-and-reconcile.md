# Beacon Feature Change Document

- feature: `prototype runtime self-heal and reconcile`
- feature_slug: `prototype-runtime-self-heal-and-reconcile`
- version: `v1.3.11`
- status: `reopened`

## Change Intent

- 将当前 prototype bundle 在 `create -> review -> freeze` 之间暴露出来的人工修补摩擦，正式收口为 Beacon requirement change。
- 明确 prototype runtime 不能继续要求 host LLM 通过分析话术承担 bundle 修复、truth 判断、transaction 修补与 freeze 收口。
- 将 `review truth source 分裂`、`freeze source drift 无 repair path`、`create 覆盖 human narrowing` 三类问题升级为正式模型线，而不是继续保留为人工经验。

## Scope Delta

- 新增 `prototype runtime self-heal` requirement line
- 新增 `prototype reconcile` requirement line
- 补充 `create / review / freeze / status` 四个 surface 的职责边界
- 补充 `metadata-only drift / sink drift / source drift / stale plan truth` 的 reason-code 与 repair-path 语义
- 将本次变更定位为 `post-freeze requirement change`，不是一次性 runtime hotfix

## Added

- requirement delta:
  - prototype 必须存在正式 `reconcile` surface，把 authoritative source 单向重投影到 `plan / manifest / canonical-envelope / freeze metadata`
  - prototype review 必须只认单一 canonical truth，不允许 host 通过人工判断补齐“真正读取的结构化字段”
  - prototype freeze 必须区分 `destructive recreate` 与 `metadata-only repair`
  - prototype status / gate 必须给出明确 `reason_code / diagnosis / next_action / repair_path`
  - prototype runtime 必须提供 `non-destructive refresh`，不得默认覆盖已收窄的人类页面与可见语义

## Removed / Reduced

- 不再接受“review 失败后由 host LLM 自行解释先补哪几个 JSON 字段”的隐式运行机制
- 降低对 `create` 作为唯一 bundle 修复入口的依赖
- 降低对手工 patch `manifest / prototype-plan / canonical-envelope / transaction headers` 的依赖

## Fixed / Clarified

- 明确 `prototype create` 是 create-time bundle projection，不等于后续所有修订都必须重新 destructive create
- 明确 `prototype review` 的 canonical truth source 必须固定，禁止 `plan / manifest / canonical-envelope` 语义分裂
- 明确 `prototype freeze` 发现 drift 时，必须先判断 drift 类型，再决定 `reconcile / repair / recreate`
- 明确 `brainstorm` 只负责只读诊断，不承担 prototype bundle repair 责任
- 明确本次 change 的目标是补齐 prototype runtime self-heal 与 reconcile 闭环，后续再进入 PRD / user-story / test-case / implement

## Not Added

- 未新增新的一级公开生命周期 stage
- 未在本次 change 中直接承诺完整视觉重构或独立设计后台
- 未把 `doctor repair` 直接等同于正常 prototype reconcile path
- 未跳过 requirement refresh 直接进入源码实现

## Readiness

- requirement clarity：已收口
- main-chain refresh：待继续
- freeze readiness：未完成，需先完成 PRD / user-story / test-case 刷新
- 当前状态：已正式 reopen 为 change item，可继续进入版本级 PRD 收敛

## Traceability Refs

- `docs/beacon/archive/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md`
- `docs/beacon/archive/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- `docs/beacon/archive/v1.3.11/change/beacon-operator-workbench-and-board-launcher.md`
- `docs/beacon/archive/v1.3.11/change/beacon-execution-runtime-kernel.md`
- `docs/beacon/archive/v1.3.11/prototype/prototype-design-intelligence-and-governed-rendering-separation/`
- `beacon/utils/prototype_utils.py`
- `beacon/commands/prototype.py`
- `beacon/commands/gate.py`
