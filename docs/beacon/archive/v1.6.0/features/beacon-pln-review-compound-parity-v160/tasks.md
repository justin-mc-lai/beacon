# 任务：Beacon Planner Review Compound Parity v1.6.0

## 任务台账

- [x] TASK-001 创建 package-authoritative feature package，并冻结 `full_parity` scope。
- [x] TASK-002 更新 `beacon-pln-review` references，新增 Compound parity review contract。
- [x] TASK-003 扩展 reviewer catalog，覆盖 Compound reviewer、Beacon intent/source parity reviewer 和 release/QA evidence reviewer。
- [x] TASK-004 实现 source parity delivery artifact schema。
- [x] TASK-005 实现 finding synthesis schema、dedup、conflict 和 route selection。
- [x] TASK-006 实现 autofix classification routing，确保 planner 不执行修复。
- [x] TASK-007 实现 diff/PR/worktree scope review artifact。
- [x] TASK-008 实现 release ops closure review artifact。
- [x] TASK-009 实现 QA evidence hygiene review artifact。
- [x] TASK-010 扩展 planner review runtime/state-machine contract。
- [x] TASK-011 扩展 `beacon skill eval-kit benchmark --version v1.6.0` 覆盖新 cases。
- [x] TASK-012 增加 `tests/test_v160_pln_review_compound_parity.py`。
- [x] TASK-013 重新 materialize skill package、generated projection 和 agent surface。
- [x] TASK-014 导入 implementation evidence。
- [x] TASK-015 路由到 `beacon-eval-qa` 做 formal QA。（superseded-by-qa：`qa-acceptance-beacon-pln-review-compound-parity-v160.json`，2026-06-09 passed）
- [x] TASK-016 路由到 `beacon-eval-release` 做 release readiness。（superseded-by-qa：feature QA accepted；版本级 release 仍待 v1.6.0 promotion）

## 边界

Checkboxes 是任务 ledger，不代表 implementation、QA 或 release 完成。完成判断必须来自 implementation evidence、formal QA 和 release gate。
