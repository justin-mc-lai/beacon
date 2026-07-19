---
slug: loom-run-agent-stop-when-external
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-run-agent-stop-when-external/truth.md
---

# Tests: loom-run-agent-stop-when-external

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-105 | TC-W2-001 | integration | `cargo test -p beacon-cli tc105_run_agent` | loop runs |
| AC-106 | TC-W2-002 | negative | `cargo test -p beacon-orchestrator tc106_self_stop_unverified` | continues |
| AC-106 | TC-W2-003 | integration | `cargo test -p beacon-orchestrator tc106_external_stop` | stops |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-W2-LEGAL-01 | legal walk | happy path satisfies AC |
| TC-W2-ILLEGAL-01 | illegal | fail-closed reason_code |
