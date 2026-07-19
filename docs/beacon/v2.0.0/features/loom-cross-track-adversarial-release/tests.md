---
slug: loom-cross-track-adversarial-release
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/truth.md
---

# Tests: loom-cross-track-adversarial-release

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-166 | TC-W4A-001 | negative | `pytest or cargo tc166_contamination` | blocked |
| AC-167 | TC-W4A-002 | negative | `pytest or cargo tc167_missing_adversarial` | blocked |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-W4a-LEGAL-01 | legal walk | happy path satisfies AC |
| TC-W4a-ILLEGAL-01 | illegal | fail-closed reason_code |
