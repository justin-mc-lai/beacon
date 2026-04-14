# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-04-09

### Added

- Added the v1.2.0 runtime release package under `docs/beacon/v1.2.0/`, including machine execution/QA artifacts, architecture blueprints, release notes, and source-architecture mapping.
- Added bounded project-skill discovery primitives:
  - `beacon skill discover`
  - `beacon profile discovery`
  - template-backed starter packs under `beacon/templates/skill_profiles/`
  - static project analysis and explainable preview/apply workflow helpers
- Added release-line regression coverage for:
  - v1.2.0 interface/help surface
  - skill discovery
  - runtime release alignment
  - spec-fingerprint path stability
  - workflow acceptance / release consistency fixes

### Changed

- Promoted Beacon runtime/package/docs default line to `v1.2.0`.
- Updated managed guidance, root/package skill docs, metadata, and examples to treat `v1.2.0` as the current runtime release line.
- Hardened the default CLI surface so the visible mainline prioritizes:
  - `think`
  - `user-story`
  - `prd`
  - `test-case`
  - `implement`
  - `qa`
  - `gate`
  - `release`
- Improved help/profile/skill-doctor linkage so missing project binding can route through discovery instead of static guidance.
- Repaired review/gate/release consistency so accepted workflow closure refreshes terminal/gate/evidence/spec-fingerprint truth and keeps release checks aligned with the latest QA execution.
- Normalized spec-fingerprint path hashing to project-relative paths for stable release-gate comparisons across different path resolutions.

### Verified

- Full regression: `python3 -m pytest -q` → `607 passed`
- Bytecode sanity: `python3 -m compileall beacon tests`
- Package build: `python3 -m build --sdist --wheel`
- Materials audit: `python3 -m beacon.main doctor verify-materials --project-root . --version v1.2.0 --strict --json`
- Release gate: `python3 -m beacon.main gate check release --project-root . --version v1.2.0 --json`
- Release readiness: `python3 -m beacon.main release check v1.2.0 --project .`

## [1.1.9] - 2026-03-28

### Added

- Added feature-aware QA closure surfaces around `beacon qa run <feature>` and `beacon qa evolve <feature>`.
- Added story-scenario-map generation across the v1.1.x requirement line, including browser-relevant scenario-family expansion.
- Added browser runner artifact normalization via shared runner helpers and richer browser evidence packs (session/task/report refs).
- Added release scorecard summarization into report/status main human surfaces.
- Added v1.1.9 release note and v1.1.10 planning docs for QA confidence / autoresearch closure.

### Changed

- Promoted Beacon runtime/package release line to `v1.1.9`.
- Updated managed AGENTS / CLAUDE guidance to target `v1.1.9`.
- Updated root/package skill docs and examples to treat `v1.1.9` as the current line and `v1.1.10` as the next planning line.
- Corrected v1.1.9 docs from exploration-only wording to implemented/verified wording where implementation has landed.

### Verified

- v1.1.9 targeted slice: `python3 -m pytest -q tests/test_v119_feature_qa_closure.py tests/test_v119_keep_discard_engine.py tests/test_v119_debug_control_plane.py tests/test_v119_release_scorecard_and_browser_compiler.py tests/test_v119_story_exhaustive_browser_qa.py tests/test_v119_requirement_materials.py` → `25 passed`
- docs/skill/version alignment slice: `python3 -m pytest -q tests/test_docs_current_contract.py::test_skill_should_prefer_beacon_subcommand_and_docs_beacon_output tests/test_skill_standard_layout.py tests/test_v119_requirement_materials.py` → `13 passed`
- broader regression slice: `python3 -m pytest -q tests/test_report_memory_metrics.py tests/test_v118_qa_primary_surface.py tests/test_v119_release_scorecard_and_browser_compiler.py tests/test_v119_story_exhaustive_browser_qa.py tests/test_v119_requirement_materials.py tests/test_beacon.py` → `99 passed`

## [1.1.8] - 2026-03-26

### Added

- Added `beacon qa` as the primary QA/testing surface while preserving `auto-test` compatibility.
- Added canonical QA runtime helpers under `.beacon/qa/`, including session manifest persistence and current-session tracking.
- Added canonical debug runtime feedback surfaces under `.beacon/debug/`, plus issue harvest and idea export flows.
- Added technical implementation archive outputs under `docs/beacon/<version>/.machine/execution/technical-implementation-*.json` and matching Markdown projections.
- Added project onboarding outputs for `init`: architecture blueprint, version evolution blueprint, implementation archive index, and project lifecycle onboarding.
- Added v1.1.8 tests for init onboarding, QA primary surface, debug runtime feedback, and implement technical archive.

### Changed

- Promoted Beacon runtime/package release line to `v1.1.8`.
- Updated managed AGENTS / CLAUDE guidance to target `v1.1.8` and include progressive disclosure order.
- Updated command catalog, CLI surface, intent routing, and skill docs to expose `qa`.
- Closed the five v1.1.8 design tracks through freeze → native-team implement → review accept → spec review closure.

### Verified

- v1.1.8 targeted/contract checks: `25 passed`
- regression slices: `56 passed`
- full regression: `python3 -m pytest -q` → `475 passed`
- formal spec review closure: `review-spec-v118-design-lines.json` → `5/5 pass`

## [1.1.5] - 2026-03-23

### Added

- Added v1.1.5 human/machine layering helpers in `beacon.utils.v115_delivery`.
- Added `beacon doctor repair-package` to migrate execution and QA machine artifacts into `.machine` and create human-primary indexes.
- Added v1.1.5 prompt first-principles contract output and clarification gate payloads.
- Added eval-lab skeleton bootstrap under `.beacon/state/eval-lab/`.
- Added v1.1.5 release evidence refresh path and machine execution terminal artifact.

### Changed

- Promoted Beacon runtime/package release line to `v1.1.5`.
- Updated current README / SKILL / CLAUDE / AGENTS guidance to point at v1.1.5 as the active release.
- Closed v1.1.5 release and strict gate checks with synchronized evidence, coverage, and spec fingerprints.

### Verified

- Full regression: `python3 -m pytest -q` → `438 passed`
- Release readiness: `python3 -m beacon.main release check v1.1.5 --project .`
- Gate closure: `python3 -m beacon.main gate check release --project-root . --version v1.1.5 --json`

## [1.1.4] - 2026-03-22

### Added

- Added `implement` command group with adapter-driven runner resolution, request/result contracts, and implementation summary outputs.
- Added `skill` command group for adapter detection, registration, preference, and environment diagnostics.
- Added v1.1.4 release materials under `docs/beacon/v1.1.4/` covering implement design, runner config, recipes, FAQ, and release notes.
- Added current-release evidence refresh flow to regenerate `.beacon` release artifacts from the v1.1.4 requirement materials and verification commands.

### Changed

- Standardized public package/install naming to `beacon` across packaging metadata and README install instructions.
- Removed `pytest` from runtime dependencies and moved build/test tooling into `dev` extras.
- Refreshed v1.1.4 QA matrices and release artifacts to reference the real verification suite and current release run metadata.

### Verified

- Full regression: `python3 -m pytest -q` → `421 passed`
- Package build: `python3 -m pip wheel . --no-deps -w /tmp/beacon-dist`
- Release readiness: `python3 -m beacon.main release check v1.1.4 --project .`
- Gate closure: `python3 -m beacon.main gate check release --project-root . --version v1.1.4 --json`

## [1.1.2] - 2026-03-16

### Added

- Added `beacon prototype` command group for static single-page UI reference prototypes.
- Added prototype lifecycle governance artifacts: `manifest.json`, `source-map.json`, `freeze.json`.
- Added optional workflow `prototype` stage with gate enforcement for UI visualization requirements.
- Added v1.1.2 requirement materials, boundaries, current-version summary, acceptance audit, and execution docs.
- Added prototype-focused contract tests and current-version docs assertions.

### Changed

- Upgraded current release line, runtime metadata, and managed guidance to **v1.1.2**.
- Default prototype stack is now formally fixed to Bootstrap 5.3.x + Bootstrap Icons + Beacon Theme CSS + Alpine.js.
- Prompt routing now recognizes prototype requests as a first-class intent.
- Workflow/gate/report/status surfaces now understand optional prototype lifecycle state.

### Verified

- Full regression: `python3 -m pytest -q` → `378 passed`

## [1.0.4] - 2026-03-09

### Added

- Added `beacon doctor setup-context` to create/refresh Beacon managed blocks in `CLAUDE.md` and `AGENTS.md`.
- Added `beacon doctor verify-context` with `--strict` mode to enforce context integrity and version alignment.
- Added `beacon/utils/context_files.py` as the shared context manager (merge, backup, version marker inspection).
- Added Doctor v2 compatibility checks:
  - `context_files_presence` (`COMP-207`)
  - `managed_block_integrity` (`COMP-208`)
  - `managed_block_version_drift` (`COMP-209`)
- Added test coverage for context setup/verify flows and diagnostics:
  - `tests/test_context_files.py`
  - `tests/test_init_context_integration.py`
  - `tests/test_doctor_context_commands.py`
  - `tests/test_doctor_v2_context_checks.py`

### Changed

- Refactored `beacon.commands.doctor` to use the shared `context_files` utilities instead of duplicated logic.
- `beacon doctor --fix` now also repairs context files and managed block guidance.
- `beacon init` now integrates context guidance by default, with explicit toggle:
  - `--with-context-guidance` / `--without-context-guidance`

### Migration (existing projects)

- Run `beacon doctor setup-context --project-root .` once in existing repositories.
- Verify with `beacon doctor verify-context --project-root . --strict`.
- If markers were edited manually or corrupted, run:
  - `beacon doctor setup-context --project-root . --force`
