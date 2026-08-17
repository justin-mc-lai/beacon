---
slug: beacon-v2-loom-ops-philosophy-sync
version: v1.6.8
status: frozen
revision_id: R1
---

# Tests: beacon-v2-loom-ops-philosophy-sync

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V168-001 | TC-PHY-SYNC-001 | contract | `python3 -m pytest tests/test_v168_prod_ops_hardening.py -q -k loom_parity` | contract |
| AC-V168-002 | TC-PHY-SYNC-002 | unit | `python3 -m pytest tests/test_v168_prod_ops_hardening.py -q` | fsm/illegal |
| AC-V168-003 | TC-PHY-SYNC-003 | contract | `python3 -m pytest tests/test_v168_prod_ops_hardening.py -q` | cli |
| AC-V168-004 | TC-PHY-SYNC-004 | unit | `python3 -m pytest tests/test_v168_prod_ops_hardening.py -q` | positive/negative |
| AC-V168-005 | TC-PHY-SYNC-005 | contract | `beacon goal axis validate -v v1.6.8 --program beacon-prod-ops-hardening-v168` | axis |
| AC-V168-006 | TC-PHY-SYNC-006 | contract | `python3 -c "from pathlib import Path; assert Path('skills/beacon/examples').exists()"` | examples dir |
| AC-V168-007 | TC-PHY-SYNC-007 | negative | `python3 -m pytest tests/test_v168_prod_ops_hardening.py -q -k no_fake` | no fake |
| AC-V168-008 | TC-PHY-SYNC-008 | contract | `python3 -m pytest tests/test_v168_prod_ops_hardening.py -q -k loom` | loom parity |
