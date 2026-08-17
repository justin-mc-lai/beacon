# Truth: goal-main-bypass-admit-gate

## Promise
Goal + hooks close the path where implement/delivery work lands on main without workspace admission.

## Acceptance
| AC | Statement |
|----|-----------|
| AC-GIA-HOOK-01 | setup-git-hooks installs script that imports beacon package even when repo has no beacon/ sources |
| AC-GIA-DEF-01 | load_admission_contract for product v0.0.x without explicit false → require_workspace_admission true |
| AC-GIA-PRE-01 | create_goal_run with implement/交付 utterance + feature → implement_admission_preflight present |
| AC-GIA-PRE-02 | create_goal_run with implement intent but no feature → admission_preflight_warning feature_required |

## Non-goals
- Change truth_canonical authoring rules
