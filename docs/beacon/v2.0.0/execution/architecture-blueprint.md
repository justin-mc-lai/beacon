# Beacon v2.0.0 Architecture Blueprint

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v2.0.0`
- feature_count: `1`
- transaction_id: `tx-5ee3cba9d9e9121bf`
- source_hash: `sha256:c608d2c6be724fe3b72f9d805c130dd41f4104344af720579802d3f317e6cb88`

### Registered Feature Baselines
- `beacon-v2-rust-kernel-redesign` | revision=`R20` | branch=`beacon/v2.0.0/beacon-v2-rust-kernel-redesign` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v2.0.0/.machine/execution/implementation-delivery-baseline-beacon-v2-rust-kernel-redesign.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v2-rust-kernel-redesign:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`

### Source Refs
- none

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v2-rust-kernel-redesign:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v2-rust-kernel-redesign:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v2.0.0-beacon-v2-rust-kernel-redesign-R20`
- transaction_id: `tx-d612d9627b7a5d232`
- source_hash: `sha256:8cd15fef4541a2946864e1eda5bec4a4c551dffa085f7c1677e64dc890dbb63b`
- projection_seq: `1`
- version: `v2.0.0`
- feature: `beacon-v2-rust-kernel-redesign`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v2.0.0/beacon-v2-rust-kernel-redesign`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `/Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v2.0.0/beacon-v2-rust-kernel-redesign`
- workspace_root: `/Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v2.0.0/beacon-v2-rust-kernel-redesign`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs
- depends_on_features: -

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v2-rust-kernel-redesign:END -->
