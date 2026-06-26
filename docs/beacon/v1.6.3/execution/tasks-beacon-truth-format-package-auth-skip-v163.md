# Beacon Implementation Tasks Ledger

- feature: `beacon-truth-format-package-auth-skip-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-truth-format-package-auth-skip-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-truth-format-package-auth-skip-v163.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-truth-format-package-auth-skip-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `compute_feature_paths` 对 ≥v1.5.2 返回 `features/<slug>/{truth,tests}.m...
  - tests=TEST-001,TC-TF-001
[x] `ITASK-002` AC-002 package-auth 包 manifest status 取自 truth.md frontmatter `status`（froze...
  - tests=TEST-002,TC-TF-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 `build_requirement_package_gate` 对 ≥v1.5.2 包不报 `truth_format_non_comp...
  - tests=TEST-003,TC-TF-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 <v1.5.2 版本 truth_format 校验行为不变（**Must**）
  - tests=TEST-004,TC-TF-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 v1.6.3 frozen 包 `implement run`/`qa run` 不再因 `truth_format_non_compli...
  - tests=TEST-005,TC-TF-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 v1.6.2 包修复后 `build_requirement_package_gate` 仍 pass（不因路径修复而 break）（**...
  - tests=TEST-006,TC-TF-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 package-auth 包仍经 `feature_package.validate_feature_package` 校验（未绕过真校验...
  - tests=TEST-007,TC-TF-007 | depends_on=ITASK-006
