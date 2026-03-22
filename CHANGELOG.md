# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
