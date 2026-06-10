# Architecture Blueprint v1.6.0

- status: planning
- project_mode: greenfield
- feature: `beacon-skill-harness-taxonomy-v160`

## Scope

- host-visible skill taxonomy
- shared skill preamble generation
- planner/generator/evaluator/governor hard gates
- old-to-new skill migration
- package-authoritative truth preservation

## Service Map

- `skills/beacon/`: packaged host-visible skills.
- `.agents/skills/`: project-local Codex agent skill surface.
- `beacon/command_catalog.py`: CLI command layer catalog.
- `beacon/cli_factory.py`: CLI registration surface.
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/`: authoritative requirement package.

## No-Expand Guardrails

- Do not reintroduce `prd`, `user-story`, or `test-case` as v1.6.0 primary skill categories.
- Do not keep old host-visible skill aliases in the v1.6.0 package.
- Do not allow support/planner surfaces to write implementation, frozen truth, QA verdicts, or release verdicts.
- Do not allow generator surfaces to claim completion without evaluator evidence.

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.6.0`
- feature_count: `1`
- transaction_id: `tx-d822529fb5852aaf2`
- source_hash: `sha256:bdb774b86743fb579fa9b1e4aa476512938e2cc1b298e98f02702fdc9835031a`

### Registered Feature Baselines
- `beacon-loop-native-runner-and-automation-retirement` | revision=`R2` | branch=`beacon/v1.6.0` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.6.0/.machine/execution/implementation-delivery-baseline-beacon-loop-native-runner-and-automation-retirement.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-loop-native-runner-and-automation-retirement:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-loop-native-runner-and-automation-retirement`
- version: `v1.6.0`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-loop-native-runner-and-automation-retirement:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-loop-native-runner-and-automation-retirement:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.6.0-beacon-loop-native-runner-and-automation-retirement-R2`
- transaction_id: `tx-cea3d94dfc4fd060c`
- source_hash: `sha256:c5521eb66fea66d19f46b15256259661e68e562d68a727960cfa8c5ff547b3a8`
- projection_seq: `1`
- version: `v1.6.0`
- feature: `beacon-loop-native-runner-and-automation-retirement`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.6.0`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-loop-native-runner-and-automation-retirement:END -->
