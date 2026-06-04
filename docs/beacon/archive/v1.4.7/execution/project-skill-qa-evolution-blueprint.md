# Project Skill QA Evolution Blueprint (v1.4.7)

## Intent

This blueprint explains how Beacon should validate host-visible skill evolution after promoting `v1.4.7` to the active runtime/docs line.

## What Must Stay Stable

- skill routing still follows decision surface first
- support surfaces still cannot overreach into truth or gate authority
- versioned docs remain the canonical human truth source
- machine evidence remains the stronger substrate for runtime state

## What v1.4.7 Adds

- clearer host-level routing through the main `beacon` skill
- dedicated horizontal engineering support surfaces
- stronger human-readable reference surfaces
- bounded automation state and promotion-proof routing semantics

## QA Expectations

At minimum, QA for the active line should keep checking:

- skill contract consistency
- route explainability
- version-surface alignment
- bounded automation fail-closed behavior
- release-scorecard integration
- real-project validation behavior on nontrivial repos

## Promotion-Grade Proof

`v1.4.7` runtime promotion is only credible when:

- the active line has aligned docs/runtime/version surfaces
- the skill pack points at the active docs line
- required execution docs exist
- targeted tests pass
- real-project validation returns structured, version-aware results instead of drift or crashes
