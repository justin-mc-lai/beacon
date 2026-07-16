# Tests: Version Truth Archive Lineage

## Coverage Intent

Prove MD catalog authority, active/archive physical layout, projection drift verify, resolver defaults, unified feature discovery, lineage/inventory commands, generated INDEX, bootstrap relocate, skill contract docs, and global-boundaries §4.1 merge — without JSON-first catalog or archive as a lifecycle stage.

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_catalog_md_is_sole_commit_source -q` | Catalog parser round-trip; JSON projection derived only. |
| AC-002 | TC-002 | unit | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_active_window_three_versions -q` | Exactly 3 active roots under `docs/beacon/<v>/`. |
| AC-003 | TC-003 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_catalog_apply_relocates_archived_tree -q` | Move to `archive/<v>/`; bounded link rewrite; no delete. |
| AC-004 | TC-004 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_verify_strict_fails_on_catalog_drift -q` | Tampered projection or path mismatch → fail closed. |
| AC-005 | TC-005 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_resolver_uses_active_catalog_only -q` | Delivery commands ignore archived unless `--include-archived`. |
| AC-006 | TC-006 | unit | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_discover_features_uses_truth_md -q` | v1.5.2 discovery finds `features/*/truth.md`. |
| AC-007 | TC-007 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_archive_lineage_spans_active_and_archive -q` | Ordered hops with truth paths across roots. |
| AC-008 | TC-008 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_archive_inventory_active_ac_matrix -q` | Matrix from active truth AC tables only by default. |
| AC-009 | TC-009 | unit | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_archive_index_regenerated_on_apply -q` | INDEX.md matches catalog; not stale after apply. |
| AC-010 | TC-010 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_catalog_bootstrap_dry_run_and_confirm -q` | Dry-run previews moves; confirm atomic + verify strict. |
| AC-011 | TC-011 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_beacon_archive_skill_documents_examples -q` | Skill contains four verbs + examples A–F boundaries. |
| AC-012 | TC-012 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_global_boundaries_section_4_1_present -q` | §4.1 + archive/change clarification merged in global-boundaries. |

## Coverage Boundary

- Tests may fail until implementation lands; they define contracts only.
- Bootstrap integration tests use fixture temp trees; do not run destructive moves against real repo in unit tests.
- Parent governance + projection lifecycle regression suites must remain green after changes.
