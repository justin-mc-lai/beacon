# Implementation Brief: Browser Fallback Deterministic Command Contract

**Feature**: `browser-fallback-deterministic-command-contract`  
**Version**: `v1.4.11`  
**Status**: `implemented`

## What Changed

- Added current browser adapter options `--deterministic-command` and `--explicit-project-command`.
- Kept `--fallback-cmd` callable as a compatibility alias and bound alias evidence to `browser-fallback-command-name`.
- Changed deterministic project command evidence from `execution_mode=fallback` to `execution_mode=deterministic_command`.
- Split browser-agent evidence from deterministic-command evidence in runner report/meta/result and browser evidence packs.
- Updated generated QA browser command templates to prefer `--deterministic-command`.
- Preserved old explicit CLI `--fallback-cmd` behavior while preventing env-injected current commands from recursively executing the adapter itself.
- Kept this slice out of prototype/design, QA/PRD mirror, implement package, memory, intent, and test marker relayering behavior.

## Evidence

- `rtk python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py`
  - Result: `11 passed`
- `rtk python3 -m pytest -q tests/test_v119_release_scorecard_and_browser_compiler.py tests/test_v132_implement_three_modes_compatibility.py tests/test_v132_implement_three_modes_functional.py tests/test_v119_story_exhaustive_browser_qa.py tests/test_v142_test_contract_governance.py tests/test_v1411_compatibility_registry_and_command_catalog.py`
  - Result: `67 passed`

## Notes

- `fallback_cmd` remains in the shared writer signature for compatibility audit and existing test coverage.
- New evidence fields include `browser_agent_requested`, `browser_agent_available`, `browser_agent_executed`, `deterministic_command_configured`, `deterministic_command_executed`, `compat_alias_used`, `compat_id`, `reason_code`, and repair routes.
- Explicit CLI arguments now take precedence over browser command environment variables. This avoids recursive adapter execution when old `--fallback-cmd` commands run under current auto-test env injection.

## Next Route

Run Beacon QA for this feature:

```bash
rtk python3 -m beacon.main qa run "browser-fallback-deterministic-command-contract" --project . --version v1.4.11
```
