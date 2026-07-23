---
slug: version-contract-auto-register-v1610
version: v1.6.10
revision_id: R1
materials_status: current
---

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-VCA-001 | AC-VCA-001 | `PYTHONPATH=. python3 -m pytest tests/test_version_contract_auto_register.py::test_ensure_version_contract_from_feature_package_registers_feature_branch -q` | pass and branch=feature/v9.9.1 |
| TC-VCA-002 | AC-VCA-002 | `rg -n "ensure_version_contract_from_feature_package|version_contract_sync" beacon/commands/freeze.py` | freeze hooks ensure + payload |
| TC-VCA-003 | AC-VCA-003 | `rg -n "truth_canonical" beacon/utils/project_metadata.py beacon/commands/doctor.py` | upsert + CLI flag present |
| TC-VCA-004 | AC-VCA-004 | `PYTHONPATH=. python3 -m pytest tests/test_version_contract_auto_register.py::test_implement_preflight_blocks_unregistered_version_with_clear_reason -q` | reason_code=governance_version_not_registered |
| TC-VCA-005 | AC-VCA-005 | `PYTHONPATH=. python3 -m pytest tests/test_version_contract_auto_register.py::test_governance_precheck_defaults_truth_canonical_when_contract_exists -q` | pass + defaulted |
| TC-VCA-006 | AC-VCA-006 | `PYTHONPATH=. python3 -m pytest tests/test_version_contract_auto_register.py tests/test_v166_governance_precheck_sync_catalog.py -q` | all pass |
| TC-VCA-007 | AC-VCA-001 | `rg -n "def _normalize_service_dev_branch|feature/" beacon/utils/project_metadata.py` | monorepo normalize helper |
| TC-VCA-008 | AC-VCA-004 | `rg -n "governance_version_not_registered" beacon/utils/truth_map.py beacon/commands/implement/commands.py` | fail-closed surfaces |
| TC-VCA-009 | AC-VCA-006 | `PYTHONPATH=. python3 -m pytest tests/test_project_governance_projection_lifecycle.py -q` | governance projection suite green |
| TC-VCA-010 | AC-VCA-002 | `rg -n "version_contract_sync" beacon/commands/freeze.py` | payload key present |
| TC-VCA-011 | AC-VCA-004 | `rg -n "Illegal transitions|VersionContractRegister.implement_start" docs/beacon/v1.6.10/features/version-contract-auto-register-v1610/truth.md` | illegal transition slots present |
| TC-VCA-012 | AC-VCA-002 | `rg -n "VersionContractRegister.freeze_ok|ensure_version_contract" docs/beacon/v1.6.10/features/version-contract-auto-register-v1610/truth.md` | freeze illegal path documented |
