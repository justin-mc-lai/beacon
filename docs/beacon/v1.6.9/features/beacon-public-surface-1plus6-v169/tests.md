---
slug: beacon-public-surface-1plus6-v169
version: v1.6.9
---

# Tests

| AC | TC | Assertion |
|----|-----|-----------|
| AC-PS-001 | TC-001 | public-surface-1plus6.md exists; 6 harness rows |
| AC-PS-002 | TC-002 | harness.rs PUBLIC_ABILITIES == 6; map matches table |
| AC-PS-003 | TC-003 | goal not in PUBLIC_ABILITIES |
| AC-PS-004 | TC-004 | v169 and v200 truth both reference shared table |
| AC-PS-005 | TC-005 | denylist names not public |
| AC-PS-006 | TC-006 | whitelist goal+6 documented |
| AC-PS-007 | TC-007 | seventh ability forbidden by code contract |
| AC-PS-008 | TC-008 | install-loom-cli / governance doc mention dual runtime |

Primary: `tests/test_v169_public_surface_1plus6.py`
