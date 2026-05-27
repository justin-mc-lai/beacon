# Beacon v1.4.11 Architecture Blueprint

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.4.11`
- feature_count: `1`
- transaction_id: `tx-dee34874dcbb84161`
- source_hash: `sha256:4606fdbedf391cb7a38dbe7b60f965d6a5ab11ef215529f6c4df045c901669ee`

### Registered Feature Baselines
- `test-directory-marker-relayering-contract` | revision=`R2` | branch=`beacon/v1.4.11` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.4.11/.machine/execution/implementation-delivery-baseline-test-directory-marker-relayering-contract.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:test-directory-marker-relayering-contract:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `test-directory-marker-relayering-contract`
- version: `v1.4.11`

### Source Refs
- prd: `docs/beacon/v1.4.11/prd/test-directory-marker-relayering-contract.md`
- user_story: `docs/beacon/v1.4.11/user-story/test-directory-marker-relayering-contract.md`
- test_case: `docs/beacon/v1.4.11/qa/test-cases/test-directory-marker-relayering-contract.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:test-directory-marker-relayering-contract:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:test-directory-marker-relayering-contract:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.11-test-directory-marker-relayering-contract-R2`
- transaction_id: `tx-ba53c00ae8c6745c9`
- source_hash: `sha256:b19c8ddf1da6524ea6a06f25a134c5e7d8bb6b1df66f797c7884f518830bdf9a`
- projection_seq: `1`
- version: `v1.4.11`
- feature: `test-directory-marker-relayering-contract`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.11`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:test-directory-marker-relayering-contract:END -->
