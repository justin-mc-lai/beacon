# Tests: Project Governance Projection Lifecycle

## Coverage Intent

Prove governance MD stays the sole commit authority while truth-map, sqlite, and verify align with global-boundaries §4, and version contracts support archive lifecycle without copying global topology per version.

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | contract | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_truth_map_single_governance_truth_surface -q` | Only `project_governance` maps live MD with `is_truth=True`. |
| AC-002 | TC-002 | contract | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_truth_map_no_dual_role_on_governance_md -q` | No generated surface points at governance MD path. |
| AC-003 | TC-003 | contract | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_truth_map_resolver_documents_projection_roles -q` | Resolver/inventory payload includes truth vs projection roles. |
| AC-004 | TC-004 | unit | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_sqlite_stores_source_hash_from_md -q` | After commit, sqlite `source_hash` matches MD frontmatter. |
| AC-005 | TC-005 | integration | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_verify_fails_on_projection_drift -q` | Tampered sqlite or stale hash → `governance_projection_drift`. |
| AC-006 | TC-006 | unit | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_sqlite_payload_not_commit_authority -q` | No function writes MD from sqlite payload alone. |
| AC-007 | TC-007 | unit | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_parser_accepts_archived_validation_state -q` | Parse round-trip `active` / `archived`. |
| AC-008 | TC-008 | integration | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_resolver_skips_archived_contract -q` | Archived version not used for branch preflight. |
| AC-009 | TC-009 | integration | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_doctor_archive_version_marks_archived -q` | `archive-version` sets `validation_state: archived` in MD. |
| AC-010 | TC-010 | integration | `python3 -m pytest tests/test_project_governance_projection_lifecycle.py::test_doctor_prune_archived_dry_run_and_apply -q` | Prune dry-run vs apply removes archived blocks only. |

## Coverage Boundary

- Tests may fail until implementation lands; they define contracts only.
- No test may reintroduce `.beacon/metadata/project-version-metadata.json` as authority.
- Parent feature regression suite (`test_markdown_only_project_version_governance.py`) must remain green after changes.
