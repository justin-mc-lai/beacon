---
name: beacon-real-project-validation
description: Validate Beacon's current-version human-facing CLI surfaces against a real project root and a `docs/beacon/VERSION` line. Use when you need to prove current-version release proof on an actual repository, distinguish CLI defects from project-state blockers, or run specialized multi-project board acceptance when the feature itself is a board/projection capability.
---

# Beacon Real Project Validation

Use this skill to validate Beacon on a live project before rollout, after runtime upgrades, or when a user reports that Beacon works in-repo but not on a real repository.

Default to:

- `current-version real-project release proof`

Preferred public shortcut:

- `beacon real-project-validation --project-root <root> --version <version> --feature "<feature>" --json`

Only switch to:

- `specialized multi-project board acceptance`

when the target capability itself is a cross-project board / projection feature.

## Required Inputs

- real project root
- docs version to validate
- one primary feature with existing PRD, user-story, and test-case materials

If the user only gives a versioned docs path such as `docs/beacon/v1.0.0`, infer the project root from that path and use the last path segment as the docs version.

## Safety Rules

- Treat the project worktree as user-owned and potentially dirty.
- Prefer read-only commands first.
- Do not run `prd create`, `user-story create`, `test-case create`, `implement plan`, or `implement run` on the live repo unless the user explicitly asks for write-path validation.
- If write-path validation is required, use an isolated copy or worktree instead of the user's main working tree.
- Treat `blocked`, `release_ready=false`, or failed release checks as valid command execution results until you confirm the CLI itself is wrong.
- For latest Beacon lines, validate the public human surface first:
  - `help`
  - `status`
  - `doctor`
  - `prd`
  - `user-story`
  - `test-case`
  - `prototype`
  - `implement`
  - `qa`
  - `release`
  - `archive`
  - `gate`
- Do not treat internal `.beacon/` artifacts as the primary operator surface.
- Distinguish clearly:
  - current-feature closure readiness
  - version-line package closure / change-doc closure
  These can diverge without indicating a CLI defect.
- Distinguish clearly:
  - default single-project current-version release proof
  - specialized multi-project board acceptance
  The board path cannot replace current-version release proof.

## Workflow

### 1. Resolve Project Context

- Confirm the project root exists.
- Confirm `docs/beacon/<version>/` exists.
- Read:
  - `AGENTS.md`
  - `docs/beacon/<version>/SUMMARY.md`
  - `docs/beacon/<version>/execution/index.md`
  - `docs/beacon/<version>/release/<version>.md` when present
  - `skills/beacon/SKILL.md`
- Pick a primary feature from the existing PRD / user-story / QA set.

Before running commands, derive a version-specific acceptance overlay from those sources. Do not assume an older fixed command matrix fully proves the current Beacon line.

### 2. Preflight The Real Repo

- Check whether the real project worktree is dirty.
- Run `beacon doctor --json --project-root <root>` first.
- Record whether Beacon sees:
  - the intended docs version
  - the active runtime version
  - healthy context files

Use the exact command matrix in `references/command-matrix.md`.

### 3. Run The Read-Only Minimal Surface

Run the public minimal commands against the real project:

- `help`
- `doctor`
- `status`
- `prd list`
- `user-story list`
- `test-case list`
- `test-case gate`
- `prototype list`
- `prototype status`
- `implement status`
- `qa status`
- `qa evolve --no-write-matrix`
- `release check`
- `release scorecard`
- `archive status`
- `archive explain`
- `archive plan`
- `gate check prototype`
- `gate check release`

Prefer JSON output when the surface supports it.

For Beacon versions with team / Ralph support, also validate:

- `implement run FEATURE --mode team --dry-run --json`
- `implement run FEATURE --mode ralph --dry-run --json`
- `implement ralph-status FEATURE --json`
- `doctor verify-subagent-runtime --host-runtime codex|claude --json`
- `doctor verify-subagent-delegation FEATURE --version VERSION --json`

For Beacon versions with browser QA/session support, also validate:

- `qa session list --json`
- `qa run FEATURE --json`
- `qa team-run FEATURE --host-runtime codex|claude --json`

If browser QA is in scope, verify whether the target feature's formal QA bundle actually declares browser-capable layers rather than assuming browser automation should run.

For Beacon `v1.3.8`, the version overlay must also explicitly classify whether real-project proof exists for:

- diagram truth admission
- post-freeze host prompt trace
- prompt-boundary gate / release convergence
- archive governance support surface
- canonical delivery baseline convergence

### 4. Classify What Failed

Treat the result as a **project-state blocker**, not a Beacon defect, when:

- the command exits cleanly
- the payload is structured and version-aware
- the command reports real project issues such as QA blocked, release not ready, or missing evidence
- the feature is release-ready but the version line still lacks change docs / package closure
- browser QA is formally configured but the project lacks local runtime, runner configuration, or session/profile prerequisites
- `prototype`, `archive`, or `gate` returns a structured not-ready / warn / blocked verdict tied to real project truth

Treat the result as a **Beacon CLI defect** when:

- the command crashes
- the command ignores the requested version
- the command selects the wrong feature run
- the command requires undocumented arguments to function
- a read-only validation command unexpectedly mutates tracked docs or implementation files
- the public human surface contradicts newer authoritative feature scorecard state, for example:
  - `help` still points to repair after current-feature QA is release-ready
  - `status` / `release scorecard` aggregate older fields and miss the authoritative feature scorecard outcome
- browser QA formal layers are selected, but Beacon silently falls back to unrelated default layers instead of executing the declared browser-capable matrix
- the current version's published release note / summary / skill surface says a feature shipped, but the real-project validation path has no way to prove it on the public surface
- specialized board acceptance is presented as if it were sufficient proof of current-version release readiness

### 5. Fix Beacon If The CLI Is Wrong

When a real CLI defect is found:

1. Reproduce it against the real project.
2. Trace the Beacon source command responsible.
3. Make the smallest correct fix in the Beacon repo.
4. Add a regression test.
5. Run the targeted Beacon tests.
6. Re-run the failing command against the same real project and version.

Do not claim success until the same real-project command returns the corrected result.

### 6. Optional Write-Path Validation

Only if the user explicitly wants full write-path validation:

- create an isolated copy or worktree of the target project
- run the write-heavy minimal chain there:
  - `beacon prd create`
  - `beacon user-story create`
  - `beacon test-case create`
  - `beacon implement plan`
- confirm the generated artifacts land under the intended `docs/beacon/<version>/` line

For modern Beacon lines, this write-path validation may also include:

- `beacon doctor setup-context --project-root <isolated-root>`
- `beacon freeze FEATURE --project-root <isolated-root> --version VERSION`
- `beacon doctor sync-technical-review-contract FEATURE --project-root <isolated-root> --version VERSION ...`
- `beacon implement run FEATURE --mode team|ralph --dry-run --json`
- `beacon qa session save/use ...`
- `beacon qa team-run FEATURE --json`
- `beacon release scorecard VERSION --json`

When browser QA/session/profile validation is required:

- prefer isolated worktree execution
- start the target app locally in that isolated worktree
- save a canonical QA session
- bind a minimal project profile if needed
- verify that browser-capable QA layers really produce browser-task / evidence-pack artifacts

### 7. Report Results

Always report:

- which commands were executed
- which surfaces were operational
- which failures were real project-state blockers
- which failures were Beacon defects
- what Beacon source changes and regression tests were added, if any
- whether the validation touched the real project worktree or only read from it

## Multi-Project Board Acceptance

When the target feature is a cross-project board / projection capability, extend the validation path from “single real repo command proof” to “multi-project board acceptance”.

This is a specialized path.

It is:

- valid for board / projection acceptance
- useful for compatibility / portfolio views

It is not:

- the default current-version release proof path
- sufficient by itself to claim the latest Beacon line is fully validated on a real project

Use the assets under this skill directory:

- `references/command-matrix.md`
  - base command matrix for preflight and read-only CLI validation
- `references/board-acceptance-record-template.md`
  - markdown record template for multi-project board acceptance
- `scripts/run_real_project_board_validation.sh`
  - read-only capture script for specialized multi-project board validation packs

For Beacon `v1.3.4` board acceptance, prefer this sequence:

1. Freeze the acceptance checklist in version docs.
2. Run the multi-project validation capture script against the intended project set.
3. Use the generated `portfolio-board.txt` / `portfolio-board.json` as the canonical homepage evidence.
4. Use the generated `acceptance-record.md` as the prefilled review record, then complete the remaining verdict sections.
5. For deterministic projection checks, review each target folder `projection-determinism.json`.
6. For degradation / rebuild checks, compare per-project `status.json` truth snapshots against the isolated ledger outputs under the capture pack.
7. Fill the record template with:
   - homepage summary result
   - project detail result
   - deterministic projection result
   - debug tri-state result
   - degradation / rebuild result
8. Classify outcomes into:
   - Beacon defect
   - project-state blocker
   - not-yet-implemented acceptance gap

The default `v1.3.4` target set should include:

- `/Users/apple/Developer/Company/rolo`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop`
- `/Users/apple/Developer/Personal/products/shopxo_canada`
- `/Users/apple/Developer/Personal/products/beacon`

This board-acceptance path is still read-only unless the user explicitly asks for write-path validation in an isolated worktree.

## Output Standard

Conclude with a compact validation summary:

- validated project root
- validated docs version
- command surfaces that passed
- command surfaces that returned meaningful blocked/not-ready states
- command surfaces that exposed real Beacon defects
- whether current-feature closure is ready
- whether version-line package/change-doc closure is still open
- whether the run covered:
  - current-version release proof
  - specialized board acceptance
- follow-up recommendation:
  - `safe to use on this project`
  - `safe for read-only use only`
  - `blocked until Beacon defect is fixed`
