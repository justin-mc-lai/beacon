# Loop Failure Modes - v1.6.5

## S1 Annoying

### stale-evidence-manifest

- id: stale-evidence-manifest
- severity: S1
- symptom: Evidence manifest does not reflect the latest generated artifacts.
- cause: A runtime artifact changed without refreshing the manifest projection.
- mitigation: Rebuild or refresh evidence manifest before QA or release.
- route: beacon-gov-doctor
- evidence_expectation: Manifest diff or refreshed manifest path.

## S2 Harmful

### truth-drift

- id: truth-drift
- severity: S2
- symptom: Implementation or generated projections disagree with frozen feature truth.
- cause: Post-freeze edits bypassed change/refreeze or legacy truth was treated as authority.
- mitigation: Route through change/refreeze or repair projections back to feature-package truth.
- route: beacon-gen-change
- evidence_expectation: Truth-map resolve output and repaired package references.

### git-alignment-blocked

- id: git-alignment-blocked
- severity: S2
- symptom: Implementation, QA, or release cannot enter the governed branch/worktree.
- cause: Dirty worktree, wrong branch, missing admission artifact, or invalid worktree lane.
- mitigation: Run workspace admission and repair the branch/worktree state before writes.
- route: beacon-gov-branch
- evidence_expectation: Passing workspace admission JSON.

### infinite-fix-loop

- id: infinite-fix-loop
- severity: S2
- symptom: The loop repeats repairs without new evidence or failing test movement.
- cause: No attempt cap, no failure classification, or no route escalation.
- mitigation: Stop after capped attempts and route to planner/evaluator finding review.
- route: beacon-eval-qa
- evidence_expectation: Attempt ledger with unchanged failure signature.

### protected-path-attempt

- id: protected-path-attempt
- severity: S2
- symptom: Automatic write surface attempts to edit secrets, auth, payment, migration, or environment files.
- cause: Broad implementation scope touched a protected path without explicit human handling.
- mitigation: Fail closed and ask for a scoped human decision or manual edit route.
- route: human-override
- evidence_expectation: Block payload with protected_path_denylist reason code.

## S3 Critical

### unattended-release-without-qa

- id: unattended-release-without-qa
- severity: S3
- symptom: Release is attempted without layered QA evidence.
- cause: Dashboard or status projection was mistaken for release proof.
- mitigation: Block release and complete QA evidence chain first.
- route: beacon-eval-qa
- evidence_expectation: QA verdict artifacts and release scorecard inputs.
