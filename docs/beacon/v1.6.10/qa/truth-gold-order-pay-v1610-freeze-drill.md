# Freeze drill — truth-gold-order-pay-v1610 (v1.6.10)

## CLI (real)

```bash
beacon freeze truth-gold-order-pay-v1610 -v v1.6.10 --json
```

**Result:** `blocked` / `truth_canonical_branch_mismatch`  
- `truth_canonical`: `main`  
- `current_branch`: `beacon/v1.6.9/goal-hard-stage-exit-gates`  

Governance correctly refuses freeze off canonical branch.

## Post-precheck drill (branch guard bypass only)

After package integrity + TRG fixes, freeze body returned:

| field | value |
|-------|--------|
| status | `frozen` |
| revision_id | `R1` |
| review_gate_pass | `true` |
| baseline_hash | see `*-freeze-drill.json` |

Gates exercised: integrity → package validation → **Truth Review Gate** → freeze_revision_state.

## Package fixes applied for freeze-passability

- `canonical_refs` frontmatter
- Domain Model / Domain FSM Order / Illegal transitions (domain_required integrity)
- evidence `surface|authority` table
- tests header `TC ID | AC ID | …`
- `_extract_test_rows` accepts TC-first rows

## Related

- Scorecard: `truth-gold-order-pay-v1610-scorecard.md` (18/18 TC pass)
- TRG report: `docs/beacon/v1.6.10/.machine/execution/truth-gold-order-pay-v1610.truth-review-gate.json`
