# Beacon v1.6.7 Architecture Blueprint

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-loop-goal-v166:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-loop-goal-v166`
- version: `v1.6.7`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-loop-goal-v166:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-loop-goal-v166:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.7-beacon-loop-goal-v166-R7`
- transaction_id: `tx-5bf1e7f5a28b4504a`
- source_hash: `sha256:c99f0bb5796e23b309a950b4e0d6f112bfeb0e68113455866686a3ea159a714d`
- projection_seq: `1`
- version: `v1.6.7`
- feature: `beacon-loop-goal-v166`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.7/beacon-loop-goal-v166`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `/Users/apple/Developer/Personal/products/beacon`
- workspace_root: `/Users/apple/Developer/Personal/products/beacon`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs
- depends_on_features: -

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-loop-goal-v166:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.6.7`
- feature_count: `2`
- transaction_id: `tx-eb881b43106b54ca4`
- source_hash: `sha256:f76e792c4ffbeed58a71fe081834b5638e9816133eb0d0585129b3cdf11a8079`

### Registered Feature Baselines
- `beacon-git-scope-graph-v167` | revision=`R1` | branch=`beacon/v1.6.7/beacon-git-scope-graph-v167` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.7/.machine/execution/implementation-delivery-baseline-beacon-git-scope-graph-v167.json`
- `beacon-loop-goal-v166` | revision=`R7` | branch=`beacon/v1.6.7/beacon-loop-goal-v166` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.7/.machine/execution/implementation-delivery-baseline-beacon-loop-goal-v166.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-git-scope-graph-v167:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-git-scope-graph-v167`
- version: `v1.6.7`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-git-scope-graph-v167:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-git-scope-graph-v167:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.7-beacon-git-scope-graph-v167-R1`
- transaction_id: `tx-2b3634dc73f90fd06`
- source_hash: `sha256:c915487ff30472ac7b3e3991714df7499ec5d5e8be7cfc0b5deffdcdd9d36526`
- projection_seq: `1`
- version: `v1.6.7`
- feature: `beacon-git-scope-graph-v167`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.7/beacon-git-scope-graph-v167`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `/Users/apple/Developer/Personal/products/beacon`
- workspace_root: `/Users/apple/Developer/Personal/products/beacon`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs
- depends_on_features: -

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-git-scope-graph-v167:END -->
