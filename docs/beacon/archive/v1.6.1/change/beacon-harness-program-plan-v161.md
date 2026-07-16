# Change Record: beacon-harness-program-plan-v161

- feature: `beacon-harness-program-plan-v161`
- version: `v1.6.1`
- revision_id: `R2`
- change_reason: `dual-mode-program-plan-skill-triad-cli-governance`
- artifact_role: `change_record_not_requirement_truth`
- truth_source: `false`
- user_decision: `accepted`

## Rationale

Planner review 确认双模式方案：umbrella `beacon-pln-program` + `auto`/`interactive` 子 skill，对齐 CLI `beacon plan start`，降低操作认知负担并稳定 host 触发。

## Scope (R2 delta)

- truth R2：AC-PBP-023..028、plan_mode FSM、Integration G 重写
- 新增 skills：`beacon-pln-program`、`beacon-pln-program-auto`、`beacon-pln-program-interactive`
- `program-plan-contract.md` plan_mode + CLI 节
- `agent_surface` + `metadata.json` skill 登记

## Relationship

扩展 R1 frozen harness；不修改 v1.6.0 frozen truth 正文。

## R2-hygiene（planner review 后）

- evidence.md：去除 TIG 占位触发词；索引对齐 frozen R2；traceability 扩至 AC-PBP-028
- `program-plan-contract.md`：补 per-lake `truth-promotion.json` 规范（AC-PBP-006）
- truth User Intent 一行与 research test_gap 对齐 R2
- 重跑 TIG block + `--refreeze-chain`
