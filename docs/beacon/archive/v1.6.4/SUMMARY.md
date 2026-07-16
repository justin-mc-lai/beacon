# Beacon v1.6.4 — QA Capability Hardening

## Scope

v1.6.4 delivers QA capability hardening across five frozen features:

- Chrome extension e2e acceptance (`playwright-extension` runner)
- QA coverage confidence chain (single-case → e2e layered proof)
- Business state machine boundary QA (truth → FSM extract, unreachable coverage)
- Defect repair loop (classification, repair route, regression closure)
- Methodology contract (first-principles + mandatory adversarial review)

Program: `programs/beacon-qa-capability-hardening-v164/`

## Status

- **delivery**: `accepted` — implement + QA + release check passed (2026-07-02)
- **runtime line**: `current_runtime_release` (v1.6.3 demoted to `historical_release`)
- **contract tests**: 29 passed (`tests/test_v164_qa_*.py`)

## Features

| Phase | Feature slug | QA | Release |
|-------|--------------|-----|---------|
| 1 | `beacon-qa-chrome-extension-e2e-v164` | passed | ready |
| 2 | `beacon-qa-coverage-confidence-chain-v164` | passed | ready |
| 3 | `beacon-qa-business-state-machine-v164` | passed | ready |
| 4 | `beacon-qa-defect-repair-loop-v164` | passed | ready |
| 5 | `beacon-qa-methodology-contract-v164` | passed | ready |

## Release artifacts

- Version change projection: `change/v1.6.4.md`
- Release checklist: `release/checklist-v1.6.4.md`
- Test contract index: `.machine/testing/test-contract-index.json`
