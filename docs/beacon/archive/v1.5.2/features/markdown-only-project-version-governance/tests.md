# Tests: Markdown-Only Project Version Governance

## Coverage Intent

Prove governance topology and Git branch contracts use a single Markdown authority with **no governance JSON**, unified resolver consumption, and fail-closed rejection of execution triple branch overrides and JSON authority remnants.

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | contract | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_governance_md_is_sole_authority_path -q` | Resolver points to `docs/beacon/governance/project-version-governance.md`. |
| AC-002 | TC-002 | integration | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_governance_json_absence_fail_closed -q` | Strict verify fails if `.beacon/metadata/project-version-metadata.json` exists post-migrate. |
| AC-003 | TC-003 | integration | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_consumers_use_resolve_project_governance -q` | Implement preflight and metadata toolkit routes use resolver, not direct JSON read. |
| AC-004 | TC-004 | unit | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_load_project_metadata_reads_md_only -q` | Load path parses governance MD; JSON path not used as authority. |
| AC-005 | TC-005 | unit | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_commit_writes_md_not_governance_json -q` | Write transaction updates MD only. |
| AC-006 | TC-006 | integration | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_execution_triple_branch_merge_fail_closed -q` | With governance MD present, execution triple cannot override branch map. |
| AC-007 | TC-007 | contract | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_toolkit_shared_md_transaction -q` | Metadata and branch-governance commands target same MD file. |
| AC-008 | TC-008 | integration | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_branch_guard_inputs_from_resolver_only -q` | `_branch_guard_inputs` has no execution `service_branch_map` residue. |
| AC-009 | TC-009 | integration | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_monorepo_version_contract_from_md -q` | Multiple services and branches parse and preflight correctly. |
| AC-010 | TC-010 | integration | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_migrate_removes_governance_json -q` | Migrate imports JSON envelope then deletes governance JSON. |
| AC-011 | TC-011 | contract | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_material_gate_uses_governance_md_resolver -q` | Material gate does not hard-code metadata JSON path. |
| AC-012 | TC-012 | contract | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_truth_map_registers_project_governance_surface -q` | truth-map lists governance MD as truth role. |
| AC-013 | TC-013 | integration | `python3 -m pytest tests/test_markdown_only_project_version_governance.py::test_explicit_version_canonical_branch_from_governance_md -q` | Wrong per-service branch blocks before edit; master ancestry alone insufficient. |

## Coverage Boundary

- Tests define requirement contracts; many TCs are expected to fail until implementation lands.
- No test may require `.beacon/metadata/project-version-metadata.json` as authority.
- Package truth validation (`validate_feature_package`) must pass for this feature before freeze/refreeze.
