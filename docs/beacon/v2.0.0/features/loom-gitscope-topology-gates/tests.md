---
slug: loom-gitscope-topology-gates
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-gitscope-topology-gates/truth.md
---

# Tests: loom-gitscope-topology-gates

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-171 | TC-W4B-001 | integration | `cargo test tc171_gsg_parity` | fields present |
| AC-172 | TC-W4B-002 | integration | `cargo test tc172_three_topo` | all three |
| AC-173 | TC-W4B-003 | negative | `cargo test tc173_missing_topology` | blocked |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-W4b-LEGAL-01 | legal walk | happy path satisfies AC |
| TC-W4b-ILLEGAL-01 | illegal | fail-closed reason_code |
