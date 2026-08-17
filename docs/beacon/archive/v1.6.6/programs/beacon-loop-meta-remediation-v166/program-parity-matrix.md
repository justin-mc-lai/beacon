---
program_slug: beacon-loop-meta-remediation-v166
version: v1.6.6
scope_mode: full_parity
---

# Program Parity Matrix

| User capability | Target lake | Status | Deferral |
|-----------------|-------------|--------|----------|
| Structured agent trace | beacon-agent-structured-trace-v166 | missing | none |
| Stagnation detection | beacon-loop-stagnation-detector-v166 | missing | none |
| Remediation sandbox + rollback | beacon-harness-remediation-sandbox-v166 | missing | D-002 canonical skill |
| Cross-project meta learning | — | defer | D-004 v2 |

## Deferral Ledger

| ID | user_decision |
|----|---------------|
| D-002 auto canonical skill | rejected |
| D-003 auto feature truth | rejected |
| D-004 cross-project learning | accepted defer |
| D-005 replace human feedback | accepted parallel |
