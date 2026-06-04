# Legacy Burden Baseline Inventory

- version: `v1.4.11`
- feature: `authority-vocabulary-and-baseline-inventory-contract`
- status: `inventory_generated`
- behavior_change_allowed: `False`
- generated_at: `2026-05-26T12:22:02.956585+00:00`

## Summary

- row_count: `11`
- high_risk_count: `4`

## Inventory

| compat_id | source_file | symbol | category | role | risk | phase | behavior | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `authority-artifact-language-policy` | `beacon/artifact-language-policy.json` | `artifact_classes.human_mirrors_of_machine_contracts` | `authority` | `evidence` | `low` | `phase-1` | Defines artifact language and mirror wording policy. | forbidden-wording-test, artifact-language-render-test |
| `authority-artifact-language-renderer` | `beacon/utils/artifact_language.py` | `render_artifact_language_policy_markdown` | `authority` | `evidence` | `low` | `phase-1` | Renders the human-readable artifact language policy mirror. | render-snapshot-test |
| `command-catalog-compat-deprecated-aliases` | `beacon/command_catalog.py` | `COMPAT_COMMANDS / DEPRECATED_COMMANDS` | `command` | `evidence` | `medium` | `phase-2` | Keeps compatibility and deprecated command names discoverable outside the default user surface. | catalog-coverage-test, help-snapshot-test |
| `cli-factory-hidden-compat-registrations` | `beacon/cli_factory.py` | `build_app` | `command` | `evidence` | `medium` | `phase-3` | Registers hidden compatibility commands and deprecated aliases while keeping the mainline compact. | cli-command-registration-test, compat-registry-coverage-test |
| `implement-legacy-cli-loader` | `beacon/commands/implement/__init__.py` | `app / run_implement_stage package exports` | `implement` | `evidence` | `high` | `phase-6` | Retains compatibility registry traceability after the implement package took ownership of the public app without the legacy dynamic loader. | implement-cli-smoke-test, legacy-loader-static-scan |
| `qa-auto-test-status-legacy-mirror` | `beacon/utils/qa_runtime.py` | `write_qa_status / load_qa_status` | `qa` | `evidence` | `high` | `phase-4` | Writes canonical QA status and legacy auto-test status mirror; reads canonical first and legacy second. | canonical-qa-status-test, legacy-only-qa-blocking-test |
| `prd-legacy-machine-mirror` | `beacon/utils/material_audit.py` | `legacy_machine_mirror_sync` | `prd` | `evidence` | `high` | `phase-5` | Audits legacy PRD mirror drift alongside Markdown-first material audit findings. | material-audit-projection-vs-compat-test |
| `prototype-legacy-wireframe-source` | `beacon/utils/prototype_utils.py` | `evaluate_prototype_status` | `prototype` | `evidence` | `high` | `phase-7` | Reports legacy single-file prototype source when current prototype bundle is missing. | prototype-status-compat-test, release-gate-boundary-test |
| `browser-fallback-command-name` | `beacon/adapters/browser_runner_common.py` | `write_runner_artifacts` | `browser` | `evidence` | `medium` | `phase-8` | Records fallback command execution mode for browser runner adapters. | browser-evidence-snapshot-test, compat-alias-test |
| `memory-legacy-projection` | `beacon/utils/memory.py` | `_migrate_legacy_to_v1_if_needed` | `memory` | `evidence` | `medium` | `phase-9` | Migrates older memory files into memory-v1 when the v1 file is absent. | memory-migration-transaction-test |
| `intent-legacy-router` | `beacon/utils/intent_router.py` | `detect_intent / route_intent` | `intent` | `evidence` | `medium` | `phase-9` | Preserves backward-compatible intent detection and routing facade for older importers. | intent-current-route-test, legacy-router-admission-test |

## Boundary

- This inventory is a pre-change audit artifact.
- It does not retire, disable, or alter runtime compatibility behavior.
- Later compatibility registry and behavior retirement work must cite this inventory.
