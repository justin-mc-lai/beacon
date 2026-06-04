# Beacon v1.3.11 Boundaries

## In Scope

- orchestration runtime 的最小 requirement contract
- `work item / run / scheduler / runtime board`
- PRD freeze anti-drift 闭环
- machine mirror reconciliation
- change-loop stale mirror detection
- doctor fallback boundary clarification

## Out of Scope

- 多租户 orchestration SaaS control plane
- 任意远程 worker 集群
- 让 `doctor sync-materials` 重新成为正常 PRD revise 主路径
- 让 runtime board 反向改写 requirement truth

## Explicit Constraints

- no new public top-level Beacon command
- no hidden manual JSON patch as normal operator path
- no machine sink can silently outrank current human truth after formal reconcile
- no release/qa/implement pass when stale mirror is already detected
