# Beacon v1.3.0 Source Architecture Index

This source-architecture surface explains which code now backs the `v1.3.0` planning line.

## Command surfaces

- `beacon/commands/ask.py` — natural-language entrypoint that should recognize planning-line prompts
- `beacon/commands/prompt.py` — prompt routing, execution policy, router history, and input-audit writeback
- `beacon/commands/debug.py` — Codex `UserPromptSubmit` hook adapter plus prompt/debug audit surfaces
- `beacon/commands/implement.py` — `implement plan`, `team-plan`, `team-run`, and codex-subagents adopter surface
- `beacon/commands/qa.py` — `qa team-plan`, `qa team-run`, QA evolve, audit truth, and isolated QA execution
- `beacon/commands/review.py` — quality review and package closure checks

## Shared kernel modules

- `beacon/utils/intent_router.py` — planning prompt routing and recommended command generation
- `beacon/utils/versioning.py` — canonical version truth + version semantics resolver layer
- `beacon/utils/help_support.py` — stage-aware next-step routing, including `implement-team` / `qa-team` preference for `v1.3.0`
- `beacon/utils/implementation_plan.py` — frozen requirement package to implementation-plan compilation
- `beacon/utils/implement_native.py` — native implement execution and codex-subagents integration seam
- `beacon/utils/team_surface.py` — explicit implement/qa team contracts, isolation rules, and implement→qa handoff
- `beacon/utils/artifact_language.py` — renderer for human/machine language policy mirrors
- `beacon/utils/input_audit.py` — structured user-input audit trail for CLI and hook ingress

## Canonical contracts

- `beacon/version-truth.json` — current runtime release truth plus planning-line registry
- `beacon/version-semantics.json` — canonical version semantics contract
- `beacon/artifact-language-policy.json` — canonical human/machine artifact language policy

## Tests that currently back the line

- `tests/test_v130_implement_team_surface.py`
- `tests/test_prompt_optimize_contract.py`
- `tests/test_version_semantics_contract.py`
- `tests/test_artifact_language_policy_contract.py`
- `tests/test_v121_codex_user_prompt_submit.py`
- `tests/test_v110_debug_prompt_capture.py`

## Boundary note

Even with delegated implement-team and qa-team support, `v1.3.0` still treats Beacon as a governed stage orchestrator.
Project-private execution logic remains outside Beacon core, and release truth still depends on formal package artifacts rather than raw worker transcripts.
