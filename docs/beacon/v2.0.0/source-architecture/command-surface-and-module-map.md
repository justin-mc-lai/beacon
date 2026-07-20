# Beacon v2.0.0 Command Surface And Module Map

## Entry Path

The command surface is registered through:

- `beacon/main.py`
- `beacon/cli_factory.py`
- `beacon/command_catalog.py`

## Command Modules

| Command | Module |
| --- | --- |
| `adapter` | `beacon/commands/implement/adapter.py` |
| `analyze` | `beacon/commands/analyze.py` |
| `api-design` | `beacon/commands/api_design.py` |
| `archive` | `beacon/commands/archive.py` |
| `ask` | `beacon/commands/ask.py` |
| `auto-test` | `beacon/commands/auto_test.py` |
| `automation` | `beacon/commands/automation.py` |
| `board` | `beacon/commands/board.py` |
| `brainstorm` | `beacon/commands/brainstorm.py` |
| `change` | `beacon/commands/change.py` |
| `code2truth` | `beacon/commands/code2truth.py` |
| `commands` | `beacon/commands/implement/commands.py` |
| `data-dictionary` | `beacon/commands/data_dictionary.py` |
| `debug` | `beacon/commands/debug.py` |
| `deep` | `beacon/commands/deep.py` |
| `design` | `beacon/commands/design.py` |
| `doctor` | `beacon/commands/doctor.py` |
| `eval` | `beacon/commands/eval.py` |
| `evolution-summary` | `beacon/commands/evolution_summary.py` |
| `feature-package` | `beacon/commands/feature_package.py` |
| `feedback` | `beacon/commands/feedback.py` |
| `freeze` | `beacon/commands/freeze.py` |
| `friction-intake` | `beacon/commands/friction_intake.py` |
| `gate` | `beacon/commands/gate.py` |
| `git` | `beacon/commands/implement/git.py` |
| `goal` | `beacon/commands/goal.py` |
| `help` | `beacon/commands/help.py` |
| `hooks` | `beacon/commands/hooks.py` |
| `init` | `beacon/commands/init.py` |
| `jtbd` | `beacon/commands/jtbd.py` |
| `kano` | `beacon/commands/kano.py` |
| `lighthouse` | `beacon/commands/lighthouse.py` |
| `loop-goal` | `beacon/commands/loop_goal.py` |
| `manifest` | `beacon/commands/manifest.py` |
| `memory-friction-evolution` | `beacon/commands/memory_friction_evolution.py` |
| `moscow` | `beacon/commands/moscow.py` |
| `orchestrate` | `beacon/commands/orchestrate.py` |
| `persona` | `beacon/commands/persona.py` |
| `plan` | `beacon/commands/plan.py` |
| `planner-review` | `beacon/commands/planner_review.py` |
| `prd` | `beacon/commands/prd.py` |
| `prd-bootstrap` | `beacon/commands/prd_bootstrap.py` |
| `profile` | `beacon/commands/profile.py` |
| `program` | `beacon/commands/program.py` |
| `prompt` | `beacon/commands/prompt.py` |
| `prototype` | `beacon/commands/prototype.py` |
| `qa` | `beacon/commands/qa.py` |
| `ralph` | `beacon/commands/implement/ralph.py` |
| `ralph-bridge` | `beacon/commands/ralph_bridge.py` |
| `recall` | `beacon/commands/recall.py` |
| `release` | `beacon/commands/release.py` |
| `remember` | `beacon/commands/remember.py` |
| `reopen` | `beacon/commands/reopen.py` |
| `report` | `beacon/commands/report.py` |
| `resume` | `beacon/commands/resume.py` |
| `review` | `beacon/commands/review.py` |
| `roadmap` | `beacon/commands/roadmap.py` |
| `run` | `beacon/commands/run.py` |
| `save` | `beacon/commands/save.py` |
| `skill` | `beacon/commands/skill.py` |
| `status` | `beacon/commands/status.py` |
| `team` | `beacon/commands/implement/team.py` |
| `team` | `beacon/commands/team.py` |
| `test-case` | `beacon/commands/test_case.py` |
| `test-progress` | `beacon/commands/test_progress.py` |
| `think` | `beacon/commands/think.py` |
| `truth` | `beacon/commands/truth.py` |
| `truth-cutover` | `beacon/commands/truth_cutover.py` |
| `truth-map` | `beacon/commands/truth_map.py` |
| `ui-spec` | `beacon/commands/ui_spec.py` |
| `user-story` | `beacon/commands/user_story.py` |
| `verify` | `beacon/commands/verify.py` |
| `version` | `beacon/commands/version.py` |
| `workflow` | `beacon/commands/workflow.py` |
| `workspace` | `beacon/commands/workspace.py` |

## Key Point

Most complexity lives below the command functions, in state helpers, artifact helpers, project workflow helpers, and QA/release scoring helpers.

