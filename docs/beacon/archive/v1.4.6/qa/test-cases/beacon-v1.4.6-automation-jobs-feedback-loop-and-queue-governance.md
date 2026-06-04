# Test Cases: beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance

## Overview

**Feature**: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`  
**Version**: `v1.4.6`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-AUTO46-001 | contract | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "qa_feedback_ledger_contract_is_frozen"` | Beacon freezes a project-local QA feedback ledger contract |
| AC-002 | TC-AUTO46-002 | integration | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "automation_cli_exposes_summarize_qa"` | Beacon exposes `beacon automation summarize-qa` as a public automation surface |
| AC-003 | TC-AUTO46-003 | integration | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "automation_cli_exposes_update_queue"` | Beacon exposes `beacon automation update-queue` as a public automation surface |
| AC-004 | TC-AUTO46-004 | regression | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "queue_update_is_explicit_and_governed"` | queue update uses explicit pass/repair rules and does not create opportunistic work |
| AC-005 | TC-AUTO46-005 | contract | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "nightly_qa_wrapper_refreshes_feedback_loop"` | nightly QA wrapper refreshes feedback ledger and queue after QA execution |
| AC-006 | TC-AUTO46-006 | contract | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "gated_implement_wrapper_refreshes_queue"` | gated implement wrapper refreshes queue after implement execution |
| AC-007 | TC-AUTO46-007 | contract | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "automation_capabilities_report_feedback_loop_surface"` | automation capability reporting exposes feedback loop surfaces |
| AC-008 | TC-AUTO46-008 | boundary | `python3 -m pytest -q tests/test_v146_automation_jobs_feedback_loop.py -k "automation_jobs_feedback_loop_preserves_core_lifecycle_boundary"` | the automation/jobs supplement preserves Beacon core lifecycle boundaries |
| AC-009 | TC-AUTO46-009 | integration | `python3 -m pytest -q tests/test_automation_scaffold.py -k "automation_init_cli_should_support_json_output"` | Beacon exposes `beacon automation init --project-root .` as a public scaffold bootstrap surface |
| AC-010 | TC-AUTO46-010 | regression | `python3 -m pytest -q tests/test_automation_scaffold.py -k "automation_init_scaffold_should_generate_project_local_assets"` | scaffold output is project-local and rewrites paths/labels for the target repo |
| AC-011 | TC-AUTO46-011 | regression | `python3 -m pytest -q tests/test_automation_scaffold.py -k "automation_init_should_not_overwrite_existing_files_without_force or automation_init_should_refresh_existing_files_with_force"` | scaffold generation is conservative by default and refreshes only with explicit force |
| AC-012 | TC-AUTO46-012 | contract | `python3 -m pytest -q tests/test_automation_executors.py -k "executor_capability_matrix_should_reflect_tiered_support"` | Beacon freezes a tiered executor capability matrix instead of claiming uniform native automation across all agents |
| AC-013 | TC-AUTO46-013 | integration | `python3 -m pytest -q tests/test_automation_scaffold.py -k "automation_init_should_support_non_codex_executor_profiles"` | scaffold generation supports executor profiles and reflects them in queue/spec outputs |
| AC-014 | TC-AUTO46-014 | boundary | `python3 -m pytest -q tests/test_automation_capabilities.py -k "automation_capabilities_cli_should_support_json_and_human_output"` | unsupported executors are not represented as current Beacon-native implement/qa runtimes |
| AC-015 | TC-AUTO46-015 | contract | `python3 -m pytest -q tests/test_automation_capabilities.py -k "automation_build_summary_cli_should_emit_shared_schema"` | Beacon freezes a shared automation summary schema that multiple QA layers and notification adapters can consume |
| AC-016 | TC-AUTO46-016 | integration | `python3 -m pytest -q tests/test_automation_capabilities.py -k "automation_build_summary_cli_should_emit_shared_schema"` | Beacon exposes `beacon automation build-summary` as a public automation surface |
| AC-017 | TC-AUTO46-017 | regression | `python3 -m pytest -q tests/test_automation_scaffold.py tests/test_v146_automation_jobs_feedback_loop.py -k "automation_init_scaffold_should_generate_project_local_assets or nightly_qa_wrapper_refreshes_feedback_loop"` | scaffolded wrappers and notification helpers consume the same summary schema instead of project-specific summary formats |
| AC-018 | TC-AUTO46-018 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_surface.py -k "alongside_existing_toolkits"` | Beacon exposes a human-facing `beacon-toolkit-automation` support surface for project-local scheduled automation bootstrap and maintenance |
