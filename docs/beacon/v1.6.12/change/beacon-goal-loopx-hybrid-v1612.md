# Beacon Feature Change Projection

- feature: `beacon-goal-loopx-hybrid-v1612`
- feature_slug: `beacon-goal-loopx-hybrid-v1612`
- version: `v1.6.12`
- artifact_role: `release-facing projection/read model`
- truth_source: `false`

## Scope
- Maintains release-facing version aggregate projection guards so QA accepted features are included in version change scope before release check.

## Change Record

- 2026-08-17 · TC-007 command fix (recovery reconciliation)
  - 原命令引用 `pgr-0dd73fcf5c9f.verification-bundle.json`，该 run-id 文件从未入库，fresh clone 无法复现（仅 worktree 运行时状态存在过）。
  - 修正为读取 main 中真实跟踪的旧状态 bundle `pgr-35ca10598c49.verification-bundle.json`（schema=`standard-execution-precheck.v1`），语义不变：旧状态文件可读。
  - 验证：`python3 -m pytest -q tests/test_...` + TC-007 命令行实测 `ok`，evidence 见 `.beacon/evidence/`。
