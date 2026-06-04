# Change: QA Evidence Attribution Layer

**Feature**: `qa-evidence-attribution-layer`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## 1. Change Reason

The research file `docs/beacon/archive/v1.4.10/research/embodiskill-skillevolver-qa-attribution-foundation.md` identifies a remaining gap in Beacon QA determinism: after QA finds a problem, Beacon needs a stable attribution layer that classifies where the evidence chain broke before routing repair or release readiness.

The accepted change promotes the EmbodiSkill-inspired attribution foundation into frozen requirement truth for `v1.4.10`. Beacon should first absorb EmbodiSkill-style failure attribution, not SkillEvolver-style automatic skill mutation.

## 2. Accepted Change

Freeze a new QA requirement that introduces a formal pre-verdict attribution layer for QA evidence:

1. QA must classify failed or incomplete evidence into a finite failure family before route recommendation.
2. Supported failure families are `implementation_gap`, `truth_drift`, `coverage_gap`, `execution_lapse`, `skill_defect`, `runner_admission_blocker`, and `evidence_insufficient`.
3. Each attribution must bind to affected AC IDs and current evidence refs, except runner admission blockers where AC binding may be unavailable.
4. Each attribution must produce a route recommendation to `beacon-implement`, `beacon-change`, `beacon-test-case`, `beacon-qa`, or `blocked`.
5. Attribution output may inform formal QA, but it must not claim PRD, user-story, test-case, QA verdict, release verdict, gate verdict, or freeze authority by itself.
6. SkillEvolver-like behavior is limited to later patch proposals and must not automatically modify Beacon skills or requirement truth.

## 3. Scope

### In Scope

- QA evidence attribution schema and reason codes.
- Route-back matrix for truth, implementation, coverage, execution, skill, runner, and evidence gaps.
- AC and evidence binding requirements for attribution output.
- Fail-closed handling when attribution cannot distinguish product failure from runner, coverage, truth, or QA execution issues.
- Regression coverage for common attribution families and authority boundaries.

### Out Of Scope

- Automatic Beacon skill patching.
- Automatic requirement truth mutation.
- New lifecycle stages.
- Replacing `beacon qa run`.
- Changing release verdict rules directly.
- Hidden hook execution or any side-effect automation.
- Ralph checkpoint recovery or project skill lifecycle injection.

## 4. Source Evidence

- Research input: `docs/beacon/archive/v1.4.10/research/embodiskill-skillevolver-qa-attribution-foundation.md`
- Existing QA evo-deep closure: `docs/beacon/archive/v1.4.10/change/qa-evo-deep-evidence-bound-ac-aware-closure.md`
- Existing Skill Eval Kit feature: `docs/beacon/archive/v1.4.10/change/qa-evo-deep-and-skill-eval-kit-v1410.md`
- Global boundary: `docs/beacon/global-boundaries.md`

## 5. Route Decision

This change accepts the research as requirement input for QA attribution only. It does not accept automatic skill evolution as implementation scope.

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and refreeze complete.

## 6. Freeze Deliverables

- `docs/beacon/archive/v1.4.10/change/qa-evidence-attribution-layer.md`
- `docs/beacon/archive/v1.4.10/prd/qa-evidence-attribution-layer.md`
- `docs/beacon/archive/v1.4.10/user-story/qa-evidence-attribution-layer.md`
- `docs/beacon/archive/v1.4.10/qa/test-cases/qa-evidence-attribution-layer.md`

## 7. Boundary

The attribution layer improves QA routing determinism. It is not a support surface verdict, not a release pass signal, and not a route for silently changing Beacon skills.
