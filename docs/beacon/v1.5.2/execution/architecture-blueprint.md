# Beacon v1.5.2 Architecture Blueprint

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-truth-map-center-and-package-cutover:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-truth-map-center-and-package-cutover`
- version: `v1.5.2`

### Source Refs
- prd: `docs/beacon/v1.5.2/prd/beacon-truth-map-center-and-package-cutover.md`
- user_story: `docs/beacon/v1.5.2/user-story/beacon-truth-map-center-and-package-cutover.md`
- test_case: `docs/beacon/v1.5.2/qa/test-cases/beacon-truth-map-center-and-package-cutover.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-truth-map-center-and-package-cutover:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-truth-map-center-and-package-cutover:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.5.2-beacon-truth-map-center-and-package-cutover-R1`
- transaction_id: `tx-b90e0dbf85e1d9023`
- source_hash: `sha256:0e0609e2d0c483de7e9f1c4e48df63c97f22b000ae2b8e7f7bcb376d480962de`
- projection_seq: `1`
- version: `v1.5.2`
- feature: `beacon-truth-map-center-and-package-cutover`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.5.2`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-truth-map-center-and-package-cutover:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.5.2`
- feature_count: `2`
- transaction_id: `tx-ac4f00c694343e1ad`
- source_hash: `sha256:74461e3659ccfd20eb8505b8de3bf99bda85dfd901ff81ee0eecff778a869f95`

### Registered Feature Baselines
- `beacon-truth-map-center-and-package-cutover` | revision=`R1` | branch=`beacon/v1.5.2` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.5.2/.machine/execution/implementation-delivery-baseline-beacon-truth-map-center-and-package-cutover.json`
- `beacon-truth-skill-lifecycle-rename` | revision=`R3` | branch=`beacon/v1.5.2` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.5.2/.machine/execution/implementation-delivery-baseline-beacon-truth-skill-lifecycle-rename.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-truth-skill-lifecycle-rename:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-truth-skill-lifecycle-rename`
- version: `v1.5.2`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-truth-skill-lifecycle-rename:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-truth-skill-lifecycle-rename:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.5.2-beacon-truth-skill-lifecycle-rename-R3`
- transaction_id: `tx-6cb84bcab7d559b21`
- source_hash: `sha256:baea00c080fda17f6104b7fc1d8d049e2aede594a78a7d42d879abddd4c6c785`
- projection_seq: `1`
- version: `v1.5.2`
- feature: `beacon-truth-skill-lifecycle-rename`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.5.2`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-truth-skill-lifecycle-rename:END -->
