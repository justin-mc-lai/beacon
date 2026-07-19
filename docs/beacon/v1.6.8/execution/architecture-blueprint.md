# Beacon v1.6.8 Architecture Blueprint

## Program

`beacon-prod-ops-hardening-v168` — production ops hardening on top of v1.6.7 product-goal spine.

## Technical delta (summary)

| Area | Change surface |
|------|----------------|
| CLI | `beacon goal --mode hotfix`, `hotfix-plan`; doctor `repair-evidence-manifest`, `align-run-id`, dual-version; version fleet |
| Runtime | `beacon/utils/prod_ops_v168.py`; product_goal_runtime longrun_default |
| Contracts | 6 feature packages under `docs/beacon/v1.6.8/features/` |
| Tests | `tests/test_v168_prod_ops_hardening.py` |
| Examples | `skills/beacon/examples/{hotfix,goal-longrun-default,version-fleet}-30s.md` |

## Must change

- Formal version package closure (boundaries, source-architecture, release)
- Lake QA evidence envelopes before human release
- SUMMARY status after QA pass

## Can reuse

- v1.6.7 GoalRun / durable supervisor / agent driver
- Existing release gate dual_read + fail_closed
- doctor upgrade-package cumulative registry

## No-expand guardrails

- No second public entry skill
- No cloud CD engine
- No auto prod rollback execution
- No default BEACON_V2=1

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-version-fleet-ops-v168:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-version-fleet-ops-v168`
- version: `v1.6.8`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-version-fleet-ops-v168:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-version-fleet-ops-v168:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.8-beacon-version-fleet-ops-v168-R1`
- transaction_id: `tx-6a8bfeda6d4cf3cc1`
- source_hash: `sha256:9c9646552127424c43d18fa4bfa64411e1c40764b2eed1c8389ab7daec22c083`
- projection_seq: `1`
- version: `v1.6.8`
- feature: `beacon-version-fleet-ops-v168`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.8`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-version-fleet-ops-v168:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-release-profile-selfheal-v168:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-release-profile-selfheal-v168`
- version: `v1.6.8`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-release-profile-selfheal-v168:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-release-profile-selfheal-v168:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.8-beacon-release-profile-selfheal-v168-R1`
- transaction_id: `tx-ea5d2a572d73ce012`
- source_hash: `sha256:5fb5ab3861903d442e99accb53bad49705037d7652ed0c41a31628e96e376532`
- projection_seq: `1`
- version: `v1.6.8`
- feature: `beacon-release-profile-selfheal-v168`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.8`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-release-profile-selfheal-v168:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-hotfix-lane-v168:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-hotfix-lane-v168`
- version: `v1.6.8`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-hotfix-lane-v168:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-hotfix-lane-v168:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.8-beacon-hotfix-lane-v168-R1`
- transaction_id: `tx-2291af56faf3eb3a0`
- source_hash: `sha256:fb843b5bfc9321e54a2ca145c248d78f0fb1bdbabc7952f650d2a9e0ed0148bf`
- projection_seq: `1`
- version: `v1.6.8`
- feature: `beacon-hotfix-lane-v168`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.8`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-hotfix-lane-v168:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-goal-longrun-default-v168:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-goal-longrun-default-v168`
- version: `v1.6.8`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-goal-longrun-default-v168:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-goal-longrun-default-v168:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.8-beacon-goal-longrun-default-v168-R1`
- transaction_id: `tx-08cdde4ea4a287928`
- source_hash: `sha256:80d47f97e29d450cf1630ca3eb8b339ba7b602f732e8a7e17d20883cd75e4290`
- projection_seq: `1`
- version: `v1.6.8`
- feature: `beacon-goal-longrun-default-v168`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.8`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-goal-longrun-default-v168:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v168-goalrun-axis-mount:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v168-goalrun-axis-mount`
- version: `v1.6.8`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v168-goalrun-axis-mount:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v168-goalrun-axis-mount:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.8-beacon-v168-goalrun-axis-mount-R1`
- transaction_id: `tx-1a4df21b4ce99c936`
- source_hash: `sha256:85d32f2597bc46be774849b32315679237c4159124fda707381708ccc55202e4`
- projection_seq: `1`
- version: `v1.6.8`
- feature: `beacon-v168-goalrun-axis-mount`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.8`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v168-goalrun-axis-mount:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.6.8`
- feature_count: `6`
- transaction_id: `tx-b84873b5a6c8a1a84`
- source_hash: `sha256:193ef6e0f3c2841648f4716163dab6e78dd4d12e825c77be6219fc250ec4d0a1`

### Registered Feature Baselines
- `beacon-goal-longrun-default-v168` | revision=`R1` | branch=`beacon/v1.6.8` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.8/.machine/execution/implementation-delivery-baseline-beacon-goal-longrun-default-v168.json`
- `beacon-hotfix-lane-v168` | revision=`R1` | branch=`beacon/v1.6.8` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.8/.machine/execution/implementation-delivery-baseline-beacon-hotfix-lane-v168.json`
- `beacon-release-profile-selfheal-v168` | revision=`R1` | branch=`beacon/v1.6.8` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.8/.machine/execution/implementation-delivery-baseline-beacon-release-profile-selfheal-v168.json`
- `beacon-v168-goalrun-axis-mount` | revision=`R1` | branch=`beacon/v1.6.8` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.8/.machine/execution/implementation-delivery-baseline-beacon-v168-goalrun-axis-mount.json`
- `beacon-v2-loom-ops-philosophy-sync` | revision=`R1` | branch=`beacon/v1.6.8` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.8/.machine/execution/implementation-delivery-baseline-beacon-v2-loom-ops-philosophy-sync.json`
- `beacon-version-fleet-ops-v168` | revision=`R1` | branch=`beacon/v1.6.8` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.8/.machine/execution/implementation-delivery-baseline-beacon-version-fleet-ops-v168.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v2-loom-ops-philosophy-sync:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v2-loom-ops-philosophy-sync`
- version: `v1.6.8`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v2-loom-ops-philosophy-sync:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v2-loom-ops-philosophy-sync:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.8-beacon-v2-loom-ops-philosophy-sync-R1`
- transaction_id: `tx-85ff6464c1a31afd1`
- source_hash: `sha256:0b7cb5bfe0566ca1d93bca44776fca1830241e89c2da288f0139249c1efd2a3a`
- projection_seq: `1`
- version: `v1.6.8`
- feature: `beacon-v2-loom-ops-philosophy-sync`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.8`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v2-loom-ops-philosophy-sync:END -->
