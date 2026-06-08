# Beacon Revision Delta

- feature: `beacon-skill-harness-taxonomy-v160`
- version: `v1.6.0`
- revision_id: `R7`
- source_revision_id: `R6`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `5`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-019` Benchmark 必须覆盖 TC-006 到 TC-011、TC-017，把 planner/generator/evaluator/governor 边界、rough routing、no-fake-delivery 和 hard-gate injection 从静态或 replay-only 证明升级为行为证据。
- `AC-022` Analysis artifact 必须产出跨 case failure patterns、covered AC/TC、static-only AC/TC、recommended route，并说明 benchmark evidence 不能替代 formal evaluator/release verdict。
- `AC-020` Benchmark 每个关键 case 必须同时记录 `with_skill` 与 `baseline` 配置，并聚合 pass rate、boundary violation、fake delivery block 和 delta；baseline 只能作为对照证据，不能替代 gate。
- `AC-021` Grading artifact 必须包含 assertion evidence、reason codes、fake-delivery critique 和 weak-assertion critique；弱断言或假证据不能被记为 release-ready。
- `AC-018` `beacon skill eval-kit benchmark --version v1.6.0` 必须输出 `eval_metadata/`、`grading/`、`benchmark/`、`analysis/` 四类 runtime evidence artifact，并标记 `runtime_evidence_only=true`、`requirement_truth=false`。
