# Test Cases: markdown-first-freeze-truth-and-minimal-machine-state-contract

## Overview

**Feature**: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
**Version**: `v1.4.8`
**Status**: `frozen`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-MDFIRST-001 | contract | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "markdown_documents_are_canonical_freeze_truth"` | Markdown requirement documents are the canonical freeze truth |
| AC-002 | TC-MDFIRST-002 | contract | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "fulltext_machine_mirrors_are_not_truth_sources"` | Fulltext machine mirrors are not treated as canonical truth |
| AC-003 | TC-MDFIRST-003 | contract | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "freeze_stage_json_contains_only_minimal_state"` | Freeze-stage JSON contains only minimal state fields |
| AC-004 | TC-MDFIRST-004 | runtime | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "runtime_evidence_json_is_preserved"` | Implement, QA, and release runtime evidence JSON remains supported |
| AC-005 | TC-MDFIRST-005 | parser | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "gate_parses_ac_and_coverage_from_markdown_first"` | Gate parses AC and test coverage from Markdown before cache |
| AC-006 | TC-MDFIRST-006 | gate | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "markdown_parser_failure_blocks"` | Markdown parser failure blocks freeze/gate |
| AC-007 | TC-MDFIRST-007 | gate | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "baseline_hash_mismatch_blocks"` | Markdown baseline hash mismatch blocks and routes to change |
| AC-008 | TC-MDFIRST-008 | gate | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "ambiguous_refreeze_status_blocks"` | Missing or ambiguous refreeze status blocks |
| AC-009 | TC-MDFIRST-009 | diagnostics | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "diagnostics_include_path_line_hash_reason_and_route"` | Diagnostics include path, line or section, hash, reason_code, and repair route |
| AC-010 | TC-MDFIRST-010 | compatibility | `python3 -m pytest -q tests/test_v148_markdown_first_freeze_truth.py -k "historical_fulltext_json_is_readable_but_not_generated_for_new_freezes"` | Historical fulltext JSON remains readable while new freeze artifacts avoid fulltext duplication |

## QA Execution Snapshot

- QA date: `pending`
- Verified command: `pending`
- Result: `pending`
- QA verdict: `pending_implementation`

## Findings

- Requirement package is frozen for implementation planning.
- Runtime tests are not implemented yet.
- Implementation must add `tests/test_v148_markdown_first_freeze_truth.py`.
