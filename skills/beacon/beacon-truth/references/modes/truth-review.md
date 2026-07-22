# Mode: truth-review

> Progressive disclosure for `beacon-truth` (Scheme A 1+6). Implements Plan→Truth **Mandatory Review Gate** (v1.6.10+).

## Purpose

Force intent / FSM / testability review **before** freeze. Wrong truth cascades into tasks, implement, and tests.

## CLI

```text
beacon truth review <feature> --project-root . --version <ver> [--json]
```

- pass ⇒ `review_gate_pass=true` (report under `docs/beacon/<ver>/.machine/execution/<slug>.truth-review-gate.json`)
- fail ⇒ reason_code `truth_review_gate_failed` — **blocks** `beacon freeze`

## Three-step pipeline

```text
1. Plan / Draft Truth
2. Truth Review Gate
   A Intent Coverage Matrix (must ≠ missing)
   B FSM State|Event|Guard|To|Action + hang + illegal (domain_required)
   C every AC ≥ 1 TC (Command + Assertion)
   then Humanizer fulltext (after A/B/C pass only)
3. Freeze
```

## Boundaries

- `beacon-plan` / pln-review: draft + advisory only — **cannot** authorize freeze alone.
- Humanizer: polish L0/narrative only; `preserve_machine_fields=true`.
- refreeze: re-run Gate A/B/C; reopen marks tests/tasks `materials_status: stale`.

## Output contract

- `mode_id`: `truth-review`
- `public_id`: `truth`
- `review_gate_pass`: bool
- `reason_code`: empty | `truth_review_gate_failed` | …
- `recommended_next_harness`: `truth` (freeze) if pass else stay on `truth` (fix)

## Gold reference

- Feature package: `docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/`
- Skill example: `skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`
