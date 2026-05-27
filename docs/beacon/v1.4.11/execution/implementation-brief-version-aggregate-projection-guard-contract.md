# Implementation Brief: Version Aggregate Projection Guard Contract

**Feature**: `version-aggregate-projection-guard-contract`  
**Version**: `v1.4.11`  
**Run ID**: `run-20260527T024500Z-version-aggregate-projection-guard`  
**Status**: `implemented`

## Scope

本次实现把版本级 aggregate 对齐收敛为 release-facing projection/read model 守卫，不新增 `aggregate-sync` 生命周期。

实现路径：

- `release create` 继续从 feature change projection 重建 `change/<version>.md` 和 `.machine/change/<version>.json`。
- `release check` 在当前 QA accepted feature 不在版本聚合投影时 fail-closed，并输出可执行 repair 命令。
- `doctor repair-version-aggregate-projection` 作为 repair-only 入口，重建 feature change projection、version aggregate projection，并刷新/校验 test-contract-index。
- scorecard 的 change document 状态统一走 projection guard helper，保留既有 release gate 字段。

## Changed Files

- `beacon/utils/version_aggregate_projection.py`
- `beacon/utils/release_scorecard.py`
- `beacon/commands/release.py`
- `beacon/utils/doctor_orchestrator.py`
- `beacon/commands/doctor.py`
- `tests/test_v1411_version_aggregate_projection_guard.py`

## Boundary

- 不新增生命周期阶段。
- 不新增 QA 与 release 之间的强制人工命令。
- 不执行 release publish。
- 不执行 post-release install。
- 不把 `.machine` 投影提升为 requirement truth。

## Verification

```bash
rtk python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py
rtk python3 -m pytest -q tests/test_release_check_contract.py
```

结果：

- `10 passed`
- `21 passed`
