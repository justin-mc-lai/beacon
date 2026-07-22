---
slug: truth-core-authority-v1610
version: v1.6.10
revision_id: R3
---

# Evidence R3

| Kind | Path |
|------|------|
| change | docs/beacon/v1.6.10/change/beacon-truth-authority-humanizer-v1610-r3.md |
| package | docs/beacon/v1.6.10/features/truth-core-authority-v1610/ |
| prior | R2 superseded for gate semantics |

## Implement R3 runtime

| surface | path |
|---------|------|
| gate | beacon/utils/truth_review_gate.py |
| humanizer | beacon/utils/humanizer_config.py |
| CLI | beacon truth review |
| freeze precheck | beacon/commands/freeze.py |
| reopen stale | beacon/commands/reopen.py |
| doctor materials | beacon/utils/material_audit.py |
| skill mode | skills/beacon/beacon-truth/references/modes/truth-review.md |
| tests | tests/test_v1610_truth_review_gate.py |
| config example | docs/beacon/v1.6.10/config/beacon.config.humanizer.example.yaml |

Manual:
```text
beacon truth review truth-gold-order-pay-v1610 -v v1.6.10 --json
```
