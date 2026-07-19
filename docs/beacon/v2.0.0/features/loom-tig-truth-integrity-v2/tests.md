---
slug: loom-tig-truth-integrity-v2
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-tig-truth-integrity-v2/truth.md
---

# Tests: loom-tig-truth-integrity-v2

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-101 | TC-W3-001 | negative | `cargo test -p beacon-gate tc101_tig_blocks_empty_ac` | blocked |
| AC-103 | TC-W3-002 | integration | `beacon doctor verify-truth-integrity --mode block` | exit code |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-W3-LEGAL-01 | legal walk | happy path satisfies AC |
| TC-W3-ILLEGAL-01 | illegal | fail-closed reason_code |
