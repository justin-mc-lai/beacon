# Beacon v1.3.11 Architecture Blueprint

## 主题

把 Beacon 从“只会冻结 requirement truth”推进到“既能冻结 truth，也能稳定编排长任务，并且能阻断 PRD human/machine 漂移”。

## 核心结构

1. Requirement Truth Layer
2. Orchestration Runtime Layer
3. Delivery Closure Layer
4. PRD reconcile / audit / transaction pointer safety layer
5. doctor fallback / repair boundary

## 执行边界

- orchestration runtime 只能消费 truth，不能反向改写 truth
- `PRD markdown` 可以被人类正式修订，但 machine mirror 必须可确定性重投影
- `doctor` repair surface 只作为 fallback，不替代正常 change-loop 主路径
- `implement / qa / release` 必须以最新 audit-pass truth 为唯一入口

## 关键门禁

- `prd validate`
- `prd audit` 扩展后的 full mirror drift 检测
- `doctor verify-materials --strict`
- `freeze / implement / qa / release` 对 stale mirror 的 fail-closed

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation`
- version: `v1.3.11`

### Source Refs
- prd: `docs/beacon/v1.3.11/prd/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- user_story: `docs/beacon/v1.3.11/user-story/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- test_case: `docs/beacon/v1.3.11/qa/test-cases/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`

### Delivery Change Surface
- none
### Available Entry Surfaces
- none
### Current Service Facts
- none

### Must Change
- none

### Can Reuse
- none

### No-Expand Guardrails
- none

### Compatibility Rules
- none

### Delivery Constraints
- none

### Implement Handoff
- none
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.3.11-beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation-R1`
- transaction_id: `tx-9cc1d572b20926f41`
- source_hash: `sha256:f49e85f06cd897749e84088083b6c272a721e65a6674196c92303d31083149a1`
- projection_seq: `1`
- version: `v1.3.11`
- feature: `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.3.11`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `.`
- workspace_root: `.`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:END -->
