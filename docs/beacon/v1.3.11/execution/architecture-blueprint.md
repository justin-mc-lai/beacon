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

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.3.11`
- feature_count: `2`
- transaction_id: `tx-b96e6e6859ff76203`
- source_hash: `sha256:3a62e046701daae936a03f130f61175d45b00586c889f7b3bd6bdaeea8b15012`

### Registered Feature Baselines
- `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance` | revision=`R3` | branch=`beacon/v1.3.11` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.3.11/.machine/execution/implementation-delivery-baseline-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.json`
- `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation` | revision=`R1` | branch=`beacon/v1.3.11` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.3.11/.machine/execution/implementation-delivery-baseline-beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- version: `v1.3.11`

### Source Refs
- prd: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- user_story: `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- test_case: `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.3.11-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance-R3`
- transaction_id: `tx-0c852b16d531bb8f3`
- source_hash: `sha256:c710b62629a70578e181456a6b56654fa0f6f3cf9e0ccc775811db68608e9819`
- projection_seq: `1`
- version: `v1.3.11`
- feature: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
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
- depends_on_features: -

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance:END -->
