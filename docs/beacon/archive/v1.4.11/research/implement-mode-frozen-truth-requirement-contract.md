# Research: Implement Mode Frozen Truth Requirement Contract

- version: `v1.4.11`
- feature: `implement-mode-frozen-truth-requirement-contract`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: mode_selection, truth_injection, ac_verification, design_alignment
- status: `source-driven-converged`
- date: `2026-05-29`

## Source Anchors

Every claim below is anchored to actual source code. Unsupported inferences are explicitly marked as assumptions.

| Source | Lines | Role |
|--------|-------|------|
| `beacon/utils/implement_adapters.py` | 354-467 | `build_default_task_prompt` — injects frozen truth into agent prompt |
| `beacon/commands/implement/commands.py` | 1442-1480 | `_implementation_design_truth` — design truth gate (prototype adapter only) |
| `beacon/commands/implement/commands.py` | 2630-2737 | `dev_run` — main implement entry, assembles context, passes to task prompt |
| `beacon/utils/implement_prompt_boundary.py` | 1-156 | Prompt boundary enforcement — truth conflict pattern detection |
| `beacon/utils/implement_mode_playbooks.py` | 1-172 | Mode playbooks — admission conditions per mode |
| `beacon/utils/global_boundaries.py` | 148-156 | `global_boundary_prompt_lines` — generic boundary principles |
| `beacon/utils/implement_native.py` | 1-713 | Native implement runner — zero DESIGN.md/PRODUCT.md references |
| `skills/beacon/beacon-implement/SKILL.md` | — | Skill surface — post-fix: DESIGN.md/PRODUCT.md in inputs contract |

## Finding 1: DESIGN.md/PRODUCT.md exist only in skill surface, zero code enforcement

**Claim**: The Python implementation layer has no mechanism to read, verify, or inject DESIGN.md or PRODUCT.md into the implement workflow.

**Source evidence**:

1. `build_default_task_prompt` (`implement_adapters.py:354-467`) — The generated task prompt includes PRD/user-story/test-case paths but DESIGN.md and PRODUCT.md are **never mentioned**. There is no code path that adds them.

2. `_implementation_design_truth` (`commands.py:1442-1480`) — The "design truth" gate only checks for **prototype adapter binding**. It does NOT check for DESIGN.md or PRODUCT.md file existence at the project root.

3. `implement_prompt_boundary.py` — Truth conflict patterns only match PRD/user-story/test-case. DESIGN.md/PRODUCT.md are not in detection scope.

4. `implement_native.py` — Zero occurrences of "DESIGN" or "PRODUCT" in 713 lines.

5. `global_boundary_prompt_lines` (`global_boundaries.py:148-156`) — Five generic principles. No design truth mandate.

**Conclusion**: The skill surface fix (SKILL.md Inputs Contract) is the **only** mechanism enforcing design truth reading. Zero code-level fallback.

## Finding 2: AC verification is a soft hint, not a structured contract

**Claim**: The task prompt says "Include acceptance/test mapping" but there is no mechanism to enforce a per-AC pass/partial/blocked matrix.

**Source evidence**:

1. `build_default_task_prompt` (`implement_adapters.py:446-449`):
   ```
   "Structured result should include: assumptions, simplicity_notes, scope_guard, verification."
   ```
   Free-form text instruction. Agent can write "verification: all passed" without listing individual ACs.

2. No handoff gate checks whether an AC coverage matrix exists before routing to QA.

**Friction evidence confirmed by source**:
- `friction:7f8df1217a82` (P1): 21 ACs, 5 misaligned. Code provides no AC-level verification mechanism.
- `friction:implement-ignores-design-system` (P2): DESIGN.md existed but code never told agent to read it.

## Finding 3: Three modes share identical truth injection

**Claim**: Single, team, and ralph modes all go through the same `build_default_task_prompt` with identical truth injection. No mode-specific tailoring.

**Source evidence**:

1. `implement_mode_playbooks.py` — All three modes' admission conditions say "frozen requirement truth is stable" with no DESIGN.md mention.
2. `recommend_implement_mode` selects mode based on prompt keywords, never based on truth state.
3. No mechanism exists to inject truth into team-mode sub-agent workers.

**Unsupported claim warning**: The brainstorm hypothesis about "per-worker truth injection for team mode" is **not supported** by source — no injection mechanism exists in code.

## Finding 4: Truth gate is preflight file existence only

The dev-run preflight chain (`branch_preflight → git_workflow_contract → implementation_plan → requirement_clarity`) only checks **file existence and format**, never content alignment with implementation output.

## Truth Enforcement Matrix (source-anchored)

```
Layer                      | DESIGN.md | PRODUCT.md | AC-by-AC | Per-mode truth
---------------------------|-----------|------------|----------|---------------
SKILL.md (fixed)           | ✅        | ✅         | ❌       | ❌
build_default_task_prompt  | ❌        | ❌         | ❌ hint  | ❌
_implementation_design_truth| ❌        | ❌         | ❌       | ❌
implement_prompt_boundary  | ❌        | ❌         | ❌       | ❌
implement_mode_playbooks   | ❌        | ❌         | ❌       | ❌
global_boundary_lines      | ❌        | ❌         | ❌       | ❌
dev_run preflight gates    | ❌        | ❌         | ❌       | ❌
```

✅ enforced  ❌ not enforced  ❌ hint = soft text only

## Recommended Code Fixes (source-anchored)

### Fix A: Inject DESIGN.md/PRODUCT.md into task prompt

In `build_default_task_prompt` (`implement_adapters.py:354`), add after frozen truth lines:

```python
design_md = project_root / "DESIGN.md"
product_md = project_root / "PRODUCT.md"
if design_md.exists():
    lines.append(f"- DESIGN.md (project design truth)")
if product_md.exists():
    lines.append(f"- PRODUCT.md (project product truth)")
```

Low risk, mirrors skill surface fix at code level.

### Fix B: Structured AC coverage matrix

In `build_default_task_prompt`, replace free-form "include acceptance/test mapping" with:

```
"For each AC in the frozen test-case document, produce pass/partial/blocked.
 Write matrix to .beacon/implement/<run_id>/ac-coverage.json"
```

Medium risk — requires structured output validation.

## Route Recommendation

Enter `beacon-change` for `implement-mode-frozen-truth-requirement-contract` with scope narrowed to Fix A + Fix B. Exclude team-mode worker injection and ralph baseline hash — unsupported by current code architecture.

## Architecture

The implement truth path should stay inside the existing implement prompt architecture.

```text
beacon implement
  -> dev_run
  -> build_default_task_prompt
  -> implementation agent
  -> AC coverage matrix in handoff text
  -> beacon qa
```

Source boundary:

- `build_default_task_prompt` is the correct low-risk injection point because all modes share the default task prompt.
- `PRODUCT.md` and `DESIGN.md` are project-level truth inputs when present.
- PRD, user-story, and test-case files remain frozen requirement truth.
- `.machine` outputs remain projections/evidence, not requirement truth.

## Business Flow

```text
operator requests beacon-implement
  -> Beacon resolves feature/version requirement truth
  -> prompt includes frozen PRD/user-story/test-case refs
  -> prompt additionally includes existing PRODUCT.md/DESIGN.md refs
  -> agent implements smallest correct change
  -> agent reports AC coverage matrix before QA handoff
  -> QA verifies against frozen test cases and implementation evidence
```

Recovery flow:

```text
PRODUCT.md or DESIGN.md missing
  -> prompt generation continues
  -> project truth section records no existing project-level truth files
  -> implementation remains governed by PRD/user-story/test-case
```

Conflict flow:

```text
implementation would violate project truth or frozen requirement truth
  -> stop implementation
  -> route to beacon-change/refreeze
```

## State Machine

```text
truth_injection:
  requirement_truth_only
    -> project_truth_present when PRODUCT.md or DESIGN.md exists
    -> project_truth_absent when neither file exists

ac_verification:
  not_reported
    -> pass when every AC is satisfied with evidence
    -> partial when any AC is incomplete but not blocked
    -> blocked when implementation cannot satisfy an AC without requirement change

design_alignment:
  not_applicable
    -> aligned when DESIGN.md exists and implementation follows it
    -> partial when alignment is incomplete and documented
    -> blocked when alignment requires requirement/design truth change
```

## Decision Priority

When inputs conflict, implementation must use this priority order:

1. Global Beacon boundaries.
2. Frozen PRD/user-story/test-case requirement truth.
3. Existing project-level `PRODUCT.md` and `DESIGN.md`.
4. Version design contracts and architecture projections.
5. Local implementation convenience.

Requirement truth conflicts must route to `beacon-change/refreeze`; implementation must not silently reinterpret or code around them.

## Truth Binding

prd_refs:

- `docs/beacon/archive/v1.4.11/prd/implement-mode-frozen-truth-requirement-contract.md`

user_story_refs:

- `docs/beacon/archive/v1.4.11/user-story/implement-mode-frozen-truth-requirement-contract.md`

test_case_refs:

- `docs/beacon/archive/v1.4.11/qa/test-cases/implement-mode-frozen-truth-requirement-contract.md`

coverage_notes:

- AC-001 through AC-004 are covered by prompt truth injection and truth-section separation tests.
- AC-005 through AC-007 are covered by AC coverage matrix wording tests.
- AC-008 through AC-010 are covered by boundary and source-scope tests.

out_of_scope_notes:

- Team-mode per-worker truth injection is excluded because current source architecture has no worker injection mechanism.
- Ralph baseline hash enforcement is excluded because current source architecture does not expose a clean baseline hash gate for this change.
- This research does not add a lifecycle stage, public implement subskill, release behavior, or mandatory project-truth file creation.

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-05-29T13:17:06.847938+00:00`
- deep_artifact_root: `docs/beacon/archive/v1.4.11/deep/implement-mode-frozen-truth-requirement-contract`
- machine_artifact_root: `docs/beacon/archive/v1.4.11/.machine/deep/implement-mode-frozen-truth-requirement-contract`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/archive/v1.4.11/.machine/deep/implement-mode-frozen-truth-requirement-contract/release-supplement.json`
- adoption_status: `route_only`
