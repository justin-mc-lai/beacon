# Research note: intent decomposition hardening (2026-07-21)

## Problem
Ocean SaaS goals were mis-classified as `plan_subintent=default`, `auto_tick` advanced plan→truth→implement without user-journey freeze, and host subagents stayed off unless exact keywords matched weakly-scored rules.

## Fix (v1.6.9 worktree → main)
- `beacon/utils/intent_decomposition.py`
- multi-signal `plan_subintent`
- `plan_artifact.journeys` + `truth_readiness.blocks_auto_tick_past_plan`
- `run_goal_facade --auto-tick` hard-stops at plan for ocean
- host gate: `并行子代理` / `子代理`

## Verification
`pytest tests/test_v169_intent_decomposition_hardening.py` (+ related) green.

## Consumer proof
open-saas-base goal `pgr-5f4af43e3087`: stage stayed `plan` with 7 journey seeds until journeys frozen, then tick → `truth`.
