# Test Cases: Browser Fallback Deterministic Command Contract

**Feature**: `browser-fallback-deterministic-command-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-BROWSER-FALLBACK-001 | CLI | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "current_deterministic_command_option"` | Browser adapter current syntax exposes deterministic command option. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-001.json` |
| AC-002 | TC-BROWSER-FALLBACK-002 | compatibility | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "fallback_cmd_remains_compat_alias"` | `--fallback-cmd` remains callable as compatibility alias. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-002.json` |
| AC-003 | TC-BROWSER-FALLBACK-003 | evidence | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "deterministic_command_execution_mode"` | Deterministic command evidence uses `execution_mode=deterministic_command`. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-003.json` |
| AC-004 | TC-BROWSER-FALLBACK-004 | evidence | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "browser_agent_and_command_evidence_are_split"` | Evidence separates browser availability from deterministic command execution. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-004.json` |
| AC-005 | TC-BROWSER-FALLBACK-005 | evidence | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "deterministic_command_does_not_claim_browser_success"` | Deterministic command success does not claim browser-agent success. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-005.json` |
| AC-006 | TC-BROWSER-FALLBACK-006 | compatibility | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "fallback_alias_records_compatibility_evidence"` | Legacy alias usage records compatibility evidence bound to `browser-fallback-command-name`. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-006.json` |
| AC-007 | TC-BROWSER-FALLBACK-007 | generation | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "current_templates_prefer_deterministic_command"` | Current generated QA/browser templates do not promote legacy fallback syntax. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-007.json` |
| AC-008 | TC-BROWSER-FALLBACK-008 | guardrail | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "missing_browser_and_command_fail_closed"` | Missing browser agent and deterministic command fails closed with clear reason code. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-008.json` |
| AC-009 | TC-BROWSER-FALLBACK-009 | regression | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "no_unrelated_phase_behavior_changes"` | Prototype/design, QA mirror, PRD mirror, implement, memory, intent, and marker behavior remain out of scope. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-009.json` |
| AC-010 | TC-BROWSER-FALLBACK-010 | readout | `python3 -m pytest -q tests/test_v1411_browser_fallback_deterministic_command.py -k "readout_distinguishes_browser_and_command_repair"` | Readout distinguishes browser setup repair from deterministic command setup repair. | `.beacon/evidence/test-results/browser-fallback-deterministic-command-contract/TC-BROWSER-FALLBACK-010.json` |

## Explicit Non Coverage

- These tests do not cover prototype/design adapter behavior.
- These tests do not cover memory migration.
- These tests do not cover intent routing.
- These tests do not cover test marker relayering.
- These tests do not produce release pass/fail verdicts by themselves.
