# Beacon v1.4.7 Real-Project Proof: shopxo_canada

## Scope

- validated_at: `2026-05-16`
- runtime_line: `v1.4.7`
- target_project: `shopxo_canada`
- target_docs_version: `v1.0.0`
- target_feature: `admin-merchandising-analytics`
- validation_mode: `read-write project repair + final read-only release proof`

## What Was Repaired

This validation round first repaired real blockers inside `shopxo_canada`:

1. admin login/session bootstrap for Playwright acceptance
2. admin auth/provider concurrency behavior around Supabase session reads
3. acceptance selectors that were too wide and caused Playwright strict-mode false failures

The final QA/release proof was then rerun on the repaired project state.

## Executed Commands

```bash
python3 -m beacon.main qa run admin-merchandising-analytics \
  --project-root /Users/apple/Developer/Personal/products/shopxo_canada \
  --version v1.0.0 \
  --mode feature-aware \
  --runtime file \
  --json

python3 -m beacon.main release check v1.0.0 \
  --project-root /Users/apple/Developer/Personal/products/shopxo_canada \
  --json

python3 -m beacon.main gate check release \
  --project-root /Users/apple/Developer/Personal/products/shopxo_canada \
  --version v1.0.0 \
  --json
```

## Final Verdict

- QA run id: `run-20260516T004007963577`
- QA status: `passed`
- acceptance closure: `8/8 accepted`
- scenario pass: `8/8`
- feature scorecard `release_ready`: `true`
- `release check`: `pass`
- `gate check release`: `Pass`
- blocked_count: `0`

## Key Evidence

- project QA scorecard:
  - `/Users/apple/Developer/Personal/products/shopxo_canada/.beacon/qa/features/admin-merchandising-analytics/scorecard.json`
- project gate report:
  - `/Users/apple/Developer/Personal/products/shopxo_canada/.beacon/gate-report.json`
- project release proof:
  - `/Users/apple/Developer/Personal/products/shopxo_canada/.beacon/auto-test-status.json`

## Interpretation

This proof demonstrates that the promoted `v1.4.7` Beacon runtime can:

1. drive real-project QA against a nontrivial repository
2. distinguish project-state blockers from Beacon runtime defects
3. recover from validation-script false negatives without truth drift
4. produce a structured `qa -> release -> gate` closure on the target feature

It does not claim that every feature in `shopxo_canada` is release-ready.
It proves that Beacon `v1.4.7` remains operational and release-grade on this real project for the validated feature path.
