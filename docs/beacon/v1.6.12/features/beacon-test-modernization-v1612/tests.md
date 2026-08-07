| TC ID | AC ID | Command | Assertion |
|----|----|----|----|
| TC-001 | AC-001 | `python3 -m pytest -q tests/test_v130_material_sync.py tests/test_v140_prd_bootstrap_unified_closure.py -k 'fix_upstream' --tb=no` | exit 0 |
| TC-002 | AC-002 | `python3 -m pytest -q tests --ignore=tests/legacy -m 'not legacy' --tb=no -x` | exit 0 |
| TC-003 | AC-003 | `python3 -m pytest -q tests --ignore=tests/legacy -m 'not legacy' --tb=no -x` | exit 0 |
| TC-004 | AC-004 | `python3 -m pytest --co -q tests -p no:cacheprovider \| rg 'tests/legacy'` | 无输出（legacy 不在默认收集） |
| TC-005 | AC-005 | `python3 -m pytest -q tests --ignore=tests/legacy -m 'not legacy' --tb=no` | 0 failed |
| TC-006 | AC-006 | `python3 -c "import json; d=json.load(open('docs/beacon/research/beacon-test-drift-classification-2026-08-06.json')); assert all(r['disposition']!='defer_or_recheck_planning' or r['status'] for r in d if r['band']=='v2.x')"` | exit 0 |
| TC-007 | AC-005 | `beacon freeze beacon-test-modernization-v1612 -v v1.6.12 -p . --json` | 未过 review/verify 的 illegal transition 被拒绝（blocked） |
