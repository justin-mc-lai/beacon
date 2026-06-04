# Beacon v1.4.3 Source Architecture Index

## Status

- version: `v1.4.3`
- status: `implementation-in-progress`
- theme: `evidence-first decision surfaces and governed learning activation`

## Architecture Intent

`v1.4.3` adds support-surface projections that sit above frozen requirement truth and below execution routing.

The intent is to strengthen upstream evidence discipline without creating a second lifecycle or a second truth root.

## Expected Source Touchpoints

### Review Surfaces

- `beacon/commands/review.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/design_review_surface.py`

Responsibilities:

- render support-surface decisions;
- evaluate requirement/design challenge before implementation;
- route accepted changes back to canonical truth surfaces.

### Learning Surface

- `beacon/commands/recall.py`
- `beacon/utils/learn_surface.py`
- `beacon/utils/learning_loop.py`

Responsibilities:

- recall relevant learning by default;
- expose stale/conflicting/suppressed learning;
- keep learning advisory and auditable.

### Support-Surface Transaction Layer

- `beacon/utils/support_surface_transactions.py`
- `beacon/utils/support_surface_reason_codes.py`

Responsibilities:

- write machine and human receipts;
- update latest state sinks;
- provide route-explainable summaries for `help` and `status`.

### Help / Status Read Model

- `beacon/commands/help.py`
- `beacon/commands/status.py`
- `beacon/utils/help_support.py`

Responsibilities:

- explain route choice;
- show evidence gaps and requirement-package blockers;
- show learning influence and support-surface next routes.

## Non-Touchpoints

`v1.4.3` must not:

- add a public top-level lifecycle command;
- change release-line version truth from `v1.4.0`;
- allow support surfaces to override gate verdicts.
