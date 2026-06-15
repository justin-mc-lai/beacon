# Beacon v1.6.1 Architecture Blueprint

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-harness-program-plan-v161:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-harness-program-plan-v161`
- version: `v1.6.1`

### Source Refs
- test_case: `docs/beacon/v1.6.1/qa/test-cases/beacon-harness-program-plan-v161.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-harness-program-plan-v161:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-harness-program-plan-v161:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.1-beacon-harness-program-plan-v161-R2`
- transaction_id: `tx-9a484dc01ed07510c`
- source_hash: `sha256:bf743b997217a643c175b59053322241f752812a2de753f538d11b7216ebffe3`
- projection_seq: `1`
- version: `v1.6.1`
- feature: `beacon-harness-program-plan-v161`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `pre-main`
- default_target_branch: `pre-main`
- branch_prefix: `pre-main/`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-harness-program-plan-v161:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.6.1`
- feature_count: `2`
- transaction_id: `tx-ec3f38900109d1748`
- source_hash: `sha256:199fa5c34dbc83697fc01cfeecd3ccc13b1b8824741de1bdf0fb4e997316e8c8`

### Registered Feature Baselines
- `beacon-agent-eval-v161` | revision=`R2` | branch=`pre-main` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.1/.machine/execution/implementation-delivery-baseline-beacon-agent-eval-v161.json`
- `beacon-harness-program-plan-v161` | revision=`R2` | branch=`pre-main` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.1/.machine/execution/implementation-delivery-baseline-beacon-harness-program-plan-v161.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-agent-eval-v161:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-agent-eval-v161`
- version: `v1.6.1`

### Source Refs
- prd: `docs/beacon/v1.6.1/prd/beacon-agent-eval-v161.md`
- user_story: `docs/beacon/v1.6.1/user-story/beacon-agent-eval-v161.md`
- test_case: `docs/beacon/v1.6.1/qa/test-cases/beacon-agent-eval-v161.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-agent-eval-v161:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-agent-eval-v161:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.1-beacon-agent-eval-v161-R2`
- transaction_id: `tx-877c26850500a6429`
- source_hash: `sha256:7a732e6b4bb174b584039534030d5ccf4d4dee6562ecbd7b072ad0b77382b886`
- projection_seq: `1`
- version: `v1.6.1`
- feature: `beacon-agent-eval-v161`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `pre-main`
- default_target_branch: `pre-main`
- branch_prefix: `pre-main/`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-agent-eval-v161:END -->
