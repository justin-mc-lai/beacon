# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

