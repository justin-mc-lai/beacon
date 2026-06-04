# Beacon v1.4.6 Architecture Blueprint

## Architecture Intent

`v1.4.6` extends the `v1.4.5` lightweight governance line by tightening host-visible skill behavior before downstream runtime gates need to intervene.

The architecture goal is:

> Beacon should express stronger public-surface contracts, connect challenge outputs back to evidence/state/gate semantics, and preserve philosophy-first skill design without collapsing into rigid operation scripts.

## Layer Placement

The existing architecture remains authoritative:

```text
Truth Layer
-> Contract Layer
-> Kernel Services Layer
-> Surface Layer
-> Plugin / Projection Layer
```

`v1.4.6` does not add a new layer.
It tightens contracts inside the surface and projection bands:

```text
public skill contract anatomy
-> anti-rationalization
-> support-surface constitution
-> challenge binding
-> machine-checkable anti-drift checks
-> existing truth/evidence/gate governance
```

## New Contract Focus

### Skill Anatomy v2

Purpose:

- freeze a uniform contract skeleton for key host-visible skills
- expose boundary, workflow, rationalization, verification, evidence, state, and gate semantics
- make misuse harder before execution begins

Boundary:

- cannot become a verbose how-to script template
- cannot replace feature truth or release gate semantics

### Support-Surface Constitution

Purpose:

- unify `brainstorm`, `deep`, `ceo-review`, `design-review`, `help`, `status`, and `doctor`
- preserve their role as challenge/explain/route surfaces
- make overreach auditable

Boundary:

- cannot become truth source
- cannot become gate source
- cannot become a new lifecycle stage

### High-Risk Challenge Binding

Purpose:

- allow adversarial challenge for public promises, release decisions, acceptance closure, and cross-surface consistency
- require challenge output to bind back to route, evidence, state, or gate semantics

Boundary:

- no free-form verdicts without traceable consequence
- no bypass of frozen requirement truth

### Machine-Checkable Anti-Drift Enforcement

Purpose:

- detect missing required sections
- detect support-surface overreach
- detect challenge outputs that are not bound back to Beacon governance surfaces

Boundary:

- checks remain a projection of frozen contract truth
- linting cannot replace human requirement decisions by itself

### Automation Jobs Feedback Loop

Purpose:

- formalize project-local scheduled QA as a reusable automation feedback loop
- persist machine-readable QA feedback that the next QA or gated implement window can consume
- emit one shared automation summary schema for wrappers, operators, and notification adapters
- keep queue updates explicit and governed instead of wrapper-invented

Boundary:

- feedback ledger is automation intent support, not requirement truth
- queue update cannot reopen frozen truth automatically
- scheduler runtime remains outside Beacon core lifecycle
- transport adapters consume Beacon summary schema instead of defining truth themselves

## Minimal Implementation Slices

### Slice 1: Public Skill Contract Upgrade

Files likely to change:

- `skills/beacon/SKILL.md`
- key skill entry surfaces under `skills/beacon/*/SKILL.md`
- contract-aware validation helpers if present

Outcome:

- key public skills expose one stronger anti-drift anatomy

### Slice 2: Support-Surface Constitution Binding

Files likely to change:

- support-surface skill docs
- route/explainability helpers
- review/challenge projection helpers

Outcome:

- support surfaces share one bounded constitution and clearer handoff semantics

### Slice 3: Anti-Drift Check Projection

Files likely to change:

- docs/skill lint helpers
- projection or doctor checks that validate contract anatomy

Outcome:

- missing or overreaching contracts become machine-detectable

### Slice 4: Automation Jobs Feedback Loop

Files likely to change:

- `beacon/commands/automation.py`
- `beacon/utils/automation_feedback.py`
- `beacon/utils/automation_capabilities.py`
- `automation/jobs/*.sh`
- `tests/test_v146_automation_jobs_feedback_loop.py`

Outcome:

- one QA run can feed the next QA or gated implement window through project-local queue-governed machine state

## Non-Goals

- no new public lifecycle stage
- no runtime dependency on external skill packs
- no regression into long procedural step scripts
- no broad rewrite of historical skill lines in one pass

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- version: `v1.4.6`

### Source Refs
- prd: `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- user_story: `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- test_case: `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.6-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces-R1`
- transaction_id: `tx-7ffa3435b4ea79cc6`
- source_hash: `sha256:e33ff59e0ed6ca40796f0a2feb2c5e9164738fafb584975b8899fc7ae2f5c64f`
- projection_seq: `1`
- version: `v1.4.6`
- feature: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.6`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:END -->

dback-loop-and-queue-governance:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-implementation-first-reconciliation-governance:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.6-implementation-first-reconciliation-governance`
- version: `v1.4.6`

### Source Refs
- prd: `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- user_story: `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- test_case: `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-implementation-first-reconciliation-governance.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-implementation-first-reconciliation-governance:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-implementation-first-reconciliation-governance:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.6-beacon-v1.4.6-implementation-first-reconciliation-governance-R1`
- transaction_id: `tx-f5d460a9460199081`
- source_hash: `sha256:df9ea8e093c41b533bdcc06401f65b07ff5330ff38c558452b61e1c94e102bf1`
- projection_seq: `1`
- version: `v1.4.6`
- feature: `beacon-v1.4.6-implementation-first-reconciliation-governance`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.6`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-implementation-first-reconciliation-governance:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.4.6`
- feature_count: `3`
- transaction_id: `tx-18e68bcdeb67ba338`
- source_hash: `sha256:5689ea1fe1bcced5235cb526e215aae7b4d13de39150922a33a355891508b842`

### Registered Feature Baselines
- `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces` | revision=`R1` | branch=`beacon/v1.4.6` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/archive/v1.4.6/.machine/execution/implementation-delivery-baseline-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.json`
- `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance` | revision=`R1` | branch=`beacon/v1.4.6` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/archive/v1.4.6/.machine/execution/implementation-delivery-baseline-beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.json`
- `beacon-v1.4.6-implementation-first-reconciliation-governance` | revision=`R1` | branch=`beacon/v1.4.6` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/archive/v1.4.6/.machine/execution/implementation-delivery-baseline-beacon-v1.4.6-implementation-first-reconciliation-governance.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`
- version: `v1.4.6`

### Source Refs
- prd: `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- user_story: `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- test_case: `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.6-beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance-R1`
- transaction_id: `tx-a72944e7232376a2e`
- source_hash: `sha256:febfb253b7b66c4493add208d38eea8684307309fc3444a09e14f2d5870da6e8`
- projection_seq: `1`
- version: `v1.4.6`
- feature: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.6`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance:END -->
