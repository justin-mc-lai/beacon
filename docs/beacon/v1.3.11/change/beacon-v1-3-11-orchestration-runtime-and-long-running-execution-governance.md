# Beacon Feature Change Document

- feature: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- feature_slug: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- version: `v1.3.11`
- status: `reopened-for-model-closure`

## Scope
- orchestration runtime delivery model closure
- version-level baseline host
- host-driven implementation ordering

## Added
- `implementation-delivery-host` 作为版本级 canonical baseline host
- blueprint 不只承载按 feature 投影，还要承载版本级 host registry projection
- implementation ordering 优先读取 host registry，而不是只依赖 technical review contract
- baseline envelope 原生支持 `depends_on_features`

## Removed / Reduced
- 降低“版本级实现顺序只能从 change payload 或 technical review contract 临时拼装”的隐式假设
- 降低“同版本多 feature 虽然分 block，但仍缺少统一宿主模型”的结构性风险

## Fixed
- 明确“同版本多个 feature 共存”不能只停留在 markdown block 不互相覆盖，还必须有版本级 baseline host 来注册这些 feature baseline。
- 明确 implementation ordering 的稳定输入面应回到 delivery baseline host，而不是继续散落在 `change payload / technical review contract / 临时排序逻辑`。
- 明确 `execution/architecture-blueprint.md` 现在承担两层投影：
  - per-feature technical delta / implementation baseline
  - version-level implementation delivery host registry
- 明确同版本多 feature 的串并行分析，要能在部分 feature 尚未完成 technical review contract 时仍给出稳定排序建议。

## Not Added
- 未新增新的一级公开主命令。
- 未把 orchestration runtime 扩张成多租户控制平面。
- 未引入脱离版本 requirement package 的独立 runtime schema registry。

## Traceability Refs
- `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `docs/beacon/v1.3.11/.machine/execution/technical-implementation-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.json`
- `docs/beacon/v1.3.11/.machine/execution/implementation-summary-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.json`
- `docs/beacon/v1.3.11/execution/implementation-brief-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `beacon/utils/delivery_baseline.py`
- `beacon/commands/release.py`
- `tests/test_v1312_feature_aware_architecture_blueprint.py`
- `tests/test_regression_workflow_release_fixes.py`
