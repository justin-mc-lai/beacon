# Beacon v1.3.8 Architecture Blueprint

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `Beacon v1.3.8 archive governance and historical requirement isolation`
- version: `v1.3.8`

### Source Refs
- prd: `docs/beacon/archive/v1.3.8/prd/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- user_story: `docs/beacon/archive/v1.3.8/user-story/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- test_case: `docs/beacon/archive/v1.3.8/qa/test-cases/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`

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

- baseline_id: `impl-delivery-baseline-v1.3.8-beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-R2`
- transaction_id: `tx-1e02d533175ae9da7`
- source_hash: `sha256:0b8a34ebe5cb782ed9d75d5101735452cd3b51b10c1642b678e50bda2d79538a`
- projection_seq: `1`
- version: `v1.3.8`
- feature: `Beacon v1.3.8 archive governance and historical requirement isolation`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.3.8`
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
