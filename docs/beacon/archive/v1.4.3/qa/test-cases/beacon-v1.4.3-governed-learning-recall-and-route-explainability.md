# Test Cases: beacon-v1.4.3-governed-learning-recall-and-route-explainability

## Overview

**Feature**: `beacon-v1.4.3-governed-learning-recall-and-route-explainability`  
**Version**: `v1.4.3`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-LEARN-001 | contract | `python3 -m pytest -q tests/test_v143_learn_surface.py -k "learn_surface_exists_and_is_visible"` | `beacon-learn` exists as visible learning governance surface |
| AC-002 | TC-LEARN-002 | integration | `python3 -m pytest -q tests/test_v143_learning_injection.py -k "progressive_disclosure_injection"` | relevant learning can be injected by default into core decision surfaces |
| AC-003 | TC-LEARN-003 | integration | `python3 -m pytest -q tests/test_v143_learning_injection.py -k "prior_learning_applied_visibility"` | applied learning is visible with confidence/staleness context |
| AC-004 | TC-LEARN-004 | regression | `python3 -m pytest -q tests/test_v143_learn_surface.py -k "stale_and_conflicting_learning_downgraded"` | stale/conflicting learning is downgraded, flagged, or pruned |
| AC-005 | TC-LEARN-005 | integration | `python3 -m pytest -q tests/test_v143_route_explainability.py -k "support_surfaces_explain_route_and_learning"` | `help / status / ask / deep` explain route, evidence gaps, and learning influence |
