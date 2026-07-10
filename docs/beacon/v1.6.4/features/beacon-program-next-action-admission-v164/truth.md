---
slug: beacon-program-next-action-admission-v164
version: v1.6.4
status: frozen
revision_id: R1
language: zh
change_reason: R1 - program next_action admission and non-behavior implementation evidence; SidePilot v0.0.12 W7 false-closure friction friction:9ac4930999fc / friction:a1ec6dcfc7b1
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.4/features/beacon-program-next-action-admission-v164/truth.md
  user_story: docs/beacon/v1.6.4/features/beacon-program-next-action-admission-v164/truth.md
  test_case: docs/beacon/v1.6.4/features/beacon-program-next-action-admission-v164/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Program Next-Action Admission and Non-Behavior Evidence R1

## Overview

R1 repairs a Beacon harness gap exposed by SidePilot v0.0.12. The frozen `sidepilot-pi-host` program state said the next implementation action was W0 `content-hub-foundation`, but implementation was still able to land W7 `pi-host-ui-ux` shell work first. The W7 surface then used static navigation, `coming_soon` readiness, source-grep tests, and static recovery controls to appear structurally complete without closing the behavior promised by the program truth.

Beacon must treat frozen program run state as implementation admission truth. `beacon-gen-implement` must refuse to write implementation artifacts or implementation evidence for a program lake when `program-run-state.next_action` points at another lake, and it must also refuse downstream waves whose declared dependencies have not closed implementation and QA evidence. QA/release must not count static shell UI, static source-grep assertions, dry-run evidence, or zero-behavior evidence as acceptance closure.

## User Intent

Ensure Beacon harness follows program/lake topology before implementation and prevents non-behavior implementation evidence from creating false delivery closure.

## Source Evidence

| Ref | Role |
|-----|------|
| `friction:9ac4930999fc` | P1 SidePilot W7 UI/UX closure gap: static shell, static-shell readiness, recovery buttons without behavior |
| `friction:a1ec6dcfc7b1` | P2 Beacon harness implement-order violation: generator ignored `program-run-state.next_action` |
| `/Users/apple/Developer/Personal/products/selfmedia-sync-ai/.beacon/analysis/friction-intake-fit-20260710T024312Z.md` | UI/UX closure friction intake |
| `/Users/apple/Developer/Personal/products/selfmedia-sync-ai/.beacon/analysis/friction-intake-fit-20260710T024311Z.md` | implement-order friction intake |
| `/Users/apple/Developer/Personal/products/selfmedia-sync-ai/.beacon/debug/friction-captures/8af3a58f4005.json` | W7 static-shell closure capture |
| `/Users/apple/Developer/Personal/products/selfmedia-sync-ai/.beacon/debug/friction-captures/292369e23884.json` | next_action admission violation capture |
| `docs/beacon/v1.6.4/features/beacon-global-workspace-git-admission-v162/truth.md` | R6 shared program/lake branch resolver precedent |
| `docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/truth.md` | v1.6.4 anti-fake-delivery and adversarial review contract |

## User Decisions

| ID | Decision | Value |
|----|----------|-------|
| UD-032 | program next_action is implement admission truth | When a frozen program topology has `program-run-state.next_action`, `beacon-gen-implement` must align the target feature with that action before writes. |
| UD-033 | dependency closure is required before downstream waves | A lake with `depends_on` cannot be implemented as closure when prerequisite lakes lack implementation and QA acceptance evidence. |
| UD-034 | blocked implementation writes no delivery evidence | On next-action or dependency mismatch, the generator may write diagnostics only; it must not write implementation summary, acceptance evidence, or done tasks. |
| UD-035 | non-behavior evidence is non-acceptance | Static shells, `coming_soon`/preview static-shells for required surfaces, disabled/no-op recovery controls, source-grep-only tests, dry-run evidence, and no-assertion evidence cannot satisfy behavior AC. |
| UD-036 | per-feature compatibility remains unchanged | Features without program/lake topology continue through normal per-feature implementation admission. |

## Program Admission Contract

Normative inputs:

1. `docs/beacon/<version>/programs/<program>/program-run-state.json`
2. `docs/beacon/<version>/programs/<program>/feature-graph.json`
3. `docs/beacon/<version>/programs/<program>/program-manifest.md`
4. `docs/beacon/<version>/programs/<program>/program-truth-freeze.json`
5. existing implementation and QA acceptance evidence for prerequisite lakes

Normative output:

| Condition | Result |
|-----------|--------|
| target lake equals `program-run-state.next_action` | implementation admission may continue |
| target lake differs from `program-run-state.next_action` | block with `program_next_action_mismatch` |
| target lake has unclosed dependencies | block with `program_dependency_unclosed` |
| no program/lake topology owns the target | preserve per-feature default behavior |
| admission is blocked | write diagnostic only; no delivery/evidence closure |

## Non-Behavior Evidence Contract

Acceptance evidence for behavior AC must prove the promised behavior, not only the existence of labels, files, routes, components, or exported constants.

Non-acceptance evidence kinds:

- `coming_soon`, `preview`, static-shell, unready marker, disabled, no-op, or static shell state for a required full-parity surface
- source-grep-only tests such as `readFileSync(...).toContain(...)` when the AC promises runtime behavior
- dry-run, simulated runner, skipped, no-assertion, or no-artifact evidence
- recovery controls that merely navigate elsewhere without exercising the declared recovery action
- UI/UX visual smoke with no screenshot, browser trace, DOM interaction, state transition, or canvas/pixel evidence when visual/browser proof is promised

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-028 | program-next-action-admission | `beacon-gen-implement` resolves the owning program/lake topology and blocks target lake `pi-host-ui-ux` when `program-run-state.next_action=beacon-gen-implement:content-hub-foundation`; reason_code `program_next_action_mismatch`; no implementation evidence is written. |
| AC-029 | next-action-allowed-current-lake | When the target feature matches `program-run-state.next_action`, admission continues and records the resolved program slug, lake slug, material path, and next_action source. |
| AC-030 | dependency-closure-gate | A downstream lake with `depends_on` entries is blocked when prerequisite lakes lack implementation closure or QA acceptance evidence; reason_code `program_dependency_unclosed`. |
| AC-031 | per-feature-default-preserved | Repos/features without owning program topology keep normal per-feature implement admission behavior and are not blocked by program next_action checks. |
| AC-032 | static-shell-ui-evidence-rejected | QA/implementation evidence rejects required full-parity UI surfaces that are still `coming_soon`, preview-only, static shell, or no-op recovery controls; reason_code `static_shell_implementation_evidence`. |
| AC-033 | source-grep-only-not-acceptance | Tests that only grep source strings, route names, labels, or exported constants cannot satisfy runtime/browser/user-behavior AC; reason_code `static_source_assertion_only`. |
| AC-034 | blocked-generator-diagnostic-only | When implement admission is blocked by AC-028 or AC-030, generated state is diagnostic-only and cannot mark tasks done, write implementation summary, or update acceptance/release evidence. |

## Non-Goals

- Do not rewrite SidePilot history or repair SidePilot implementation in this change.
- Do not add a manual bypass that lets later waves ignore `program-run-state.next_action`.
- Do not force program gating onto standalone per-feature work that has no program topology.
- Do not classify every source-string assertion as invalid; source assertions may support contract checks, but they cannot be the only proof for behavior AC.
- Do not make planner or evaluator responsible for implementation writes.

## State Model

```text
program_truth_frozen
  -> next_action_resolved
  -> implement_admission_passed | program_next_action_mismatch | program_dependency_unclosed

implement_admission_passed
  -> implementation_write_allowed
  -> implementation_evidence_candidate
  -> behavior_evidence_valid | static_shell_implementation_evidence | static_source_assertion_only

program_next_action_mismatch
  -> diagnostic_written
  -> route_to_required_next_action

program_dependency_unclosed
  -> diagnostic_written
  -> route_to_prerequisite_lake
```

Invalid transitions:

- `program_next_action_mismatch -> implementation_summary_written`
- `program_dependency_unclosed -> qa_acceptance_written`
- `static_shell_implementation_evidence -> behavior_evidence_valid`
- `static_source_assertion_only -> browser_behavior_pass`

## Downstream Routes

| Stage | Route |
|-------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |
