# Change: beacon-program-next-action-admission-v164

- feature: `beacon-program-next-action-admission-v164`
- version: `v1.6.4`
- status: `requirement-change-accepted`
- scope: `program next_action admission / non-behavior implementation evidence`

## Summary

Beacon v1.6.4 must block program lake implementation when the requested target does not match `program-run-state.next_action`, must block downstream waves whose prerequisite lakes lack implementation/QA closure, and must reject non-behavior/static-source evidence as acceptance for behavior AC.

## Source Evidence

- `friction:9ac4930999fc` - SidePilot W7 UI/UX static-shell closure
- `friction:a1ec6dcfc7b1` - `beacon-gen-implement` ignored SidePilot program next_action
- `/Users/apple/Developer/Personal/products/selfmedia-sync-ai/.beacon/analysis/friction-intake-fit-20260710T024312Z.md`
- `/Users/apple/Developer/Personal/products/selfmedia-sync-ai/.beacon/analysis/friction-intake-fit-20260710T024311Z.md`

## Added

- Program next-action implement admission contract.
- Program dependency closure gate for downstream lakes.
- Anti-non-behavior implementation evidence contract.
- Contract/regression test matrix TC-PNA-001..007.

## Fixed

- Generator can no longer treat W7 static-shell UI as valid closure when W0 remains the required `next_action`.
- Static source-grep tests can no longer be sole acceptance evidence for runtime/browser/user-behavior AC.

## Downstream

- implement: `beacon-gen-implement`
- qa: `beacon-eval-qa`
- release: `beacon-eval-release`
