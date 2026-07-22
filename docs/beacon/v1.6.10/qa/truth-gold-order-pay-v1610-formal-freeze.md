# Formal CLI freeze — truth-gold-order-pay-v1610

## Workspace admit

| item | value |
|------|-------|
| feature worktree | `.beacon/worktrees/v1.6.10/truth-gold-order-pay-v1610` |
| feature branch | `beacon/v1.6.10/truth-gold-order-pay-v1610` @ `d9bb2d1d` |
| admission artifact | `.beacon/state/workspace-admission/v1.6.10/truth-gold-order-pay-v1610.json` |
| `beacon workspace admit` | pass (contract soft-skip `require_workspace_admission=false`) |
| validate @ feature worktree | **valid=true** |

## Formal freeze (truth_canonical = main)

```bash
# cwd = .beacon/worktrees/v1.6.10/main-truth-freeze  (branch main)
python3 -m beacon freeze truth-gold-order-pay-v1610 -v v1.6.10 --json
```

| field | value |
|-------|-------|
| status | `frozen` |
| revision_id | `R1` |
| baseline_hash | `sha256:b47a0d3186acba7844375a84179212c557db62c9c5ebe48f7f27fdfb57cc65de` |
| review_gate_pass | `True` |
| branch | `main` (truth_canonical) |

## Evidence

- formal JSON: `docs/beacon/v1.6.10/qa/truth-gold-order-pay-v1610-formal-freeze.json`
- TRG report: `docs/beacon/v1.6.10/.machine/execution/truth-gold-order-pay-v1610.truth-review-gate.json`
- revision state: `docs/beacon/v1.6.10/.machine/execution/truth-gold-order-pay-v1610.revision.json`
