---
name: beacon-real-project-validation
description: Validate Beacon's current-version human-facing CLI surfaces against a real project root and a `docs/beacon/VERSION` line. Use when you need to prove current-version release proof on an actual repository, distinguish CLI defects from project-state blockers, or run specialized multi-project board acceptance when the feature itself is a board/projection capability.
---

# Beacon Real Project Validation

Use this skill to validate Beacon on a live project before rollout, after runtime upgrades, or when a user reports that Beacon works in-repo but not on a real repository.

Default to `current-version real-project release proof`.

Preferred public shortcut:

- `beacon real-project-validation --project-root <root> --version <version> --feature "<feature>" --json`

Only switch to specialized board acceptance when the capability itself is a cross-project board or projection surface.

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
- Do not treat internal `.beacon/` artifacts as the primary operator surface.

Distinguish clearly:

- current-feature closure readiness
- version-line package closure / change-doc closure
- single-project release proof
- specialized board acceptance

## Validation protocol

Validate Beacon from the public human-facing surface inward.

- Resolve project root, docs line, and one primary feature.
- Preflight with `doctor` and current context health.
- Prefer the read-only public surface before any write-path validation.
- Treat version-aware blocked/not-ready results as meaningful outcomes until proven to be CLI defects.
- Use isolated worktrees for write-path or browser/session-heavy validation.

## Failure classification

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

## Repair rule

When a real CLI defect is found:

1. Reproduce it against the real project.
2. Trace the Beacon source command responsible.
3. Make the smallest correct fix in the Beacon repo.
4. Add a regression test.
5. Run the targeted Beacon tests.
6. Re-run the failing command against the same real project and version.

Do not claim success until the same real-project command returns the corrected result.

## Optional write-path validation

Only if the user explicitly wants full write-path validation:

- create an isolated copy or worktree of the target project
- validate the minimal write path there
- confirm generated artifacts land under the intended `docs/beacon/<version>/` line

When browser QA/session/profile validation is required:

- prefer isolated worktree execution
- verify that browser-capable QA layers actually have a usable session or runner admission path

## Report results

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
- `references/board-acceptance-record-template.md`
- `scripts/run_real_project_board_validation.sh`

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

## Examples

- 适用例：
  - “Beacon 在自己仓里能跑，但我想证明它在真实项目里也成立。”
  - “我需要区分这是 CLI 缺陷，还是目标项目状态本来就没 ready。”
- 不适用例：
  - “我现在只是想推进单条 feature 的正常主链工作。” -> 应优先回对应主链或 support surface
