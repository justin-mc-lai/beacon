# Beacon Technical Implementation Archive

- feature: `beacon-v1.3.2-karpathy-boundary-defaults`
- feature_slug: `beacon-v1.3.2-karpathy-boundary-defaults`
- version: `v1.3.2`
- run_id: `beacon-v1.3.2-karpathy-boundary-defaults-impl-accepted`
- runner: `native-single`
- git_commit: `78107c4f6304971b2fee66fea2feb2eb0e42b1b2`

## Boundary Principles
- `explicit_assumptions`: 显式假设与歧义管理
- `simplicity_first`: 简单优先
- `surgical_changes`: 外科手术式改动
- `goal_driven_execution`: 目标驱动验证闭环
- `trivial_task_exception`: trivial task 可以轻量处理，但不能越界

## Scope Summary

Karpathy boundary defaults were promoted from prose guidance into machine-verifiable contracts across `implement`, `qa`, `doctor`, and technical review surfaces.

## Changed Files
- `beacon/utils/global_boundaries.py`
- `beacon/utils/doctor_diagnostics.py`
- `beacon/utils/technical_review_contract.py`
- `beacon/utils/implementation_plan.py`
- `beacon/utils/implement_adapters.py`
- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/utils/qa_feature.py`

## Verification
- `python3 -m pytest -q tests/test_v132_karpathy_boundary_defaults.py`
- `python3 -m pytest -q tests/test_v132_karpathy_boundary_execution_materials.py`
- `beacon review accept "beacon-v1.3.2-karpathy-boundary-defaults" --project . --version v1.3.2 --json`
