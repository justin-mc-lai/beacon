# Beacon v1.3.8 Command Surface And Module Map

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
| `brainstorm` | `beacon/commands/brainstorm.py` |
| `data-dictionary` | `beacon/commands/data_dictionary.py` |
| `debug` | `beacon/commands/debug.py` |
| `design` | `beacon/commands/design.py` |
| `doctor` | `beacon/commands/doctor.py` |
| `evolution-summary` | `beacon/commands/evolution_summary.py` |
| `feedback` | `beacon/commands/feedback.py` |
| `freeze` | `beacon/commands/freeze.py` |
| `gate` | `beacon/commands/gate.py` |
| `git` | `beacon/commands/implement/git.py` |
| `help` | `beacon/commands/help.py` |
| `implement` | `beacon/commands/implement.py` |
| `init` | `beacon/commands/init.py` |
| `jtbd` | `beacon/commands/jtbd.py` |
| `kano` | `beacon/commands/kano.py` |
| `lighthouse` | `beacon/commands/lighthouse.py` |
| `memory-friction-evolution` | `beacon/commands/memory_friction_evolution.py` |
| `moscow` | `beacon/commands/moscow.py` |
| `orchestrate` | `beacon/commands/orchestrate.py` |
| `persona` | `beacon/commands/persona.py` |
| `prd` | `beacon/commands/prd.py` |
| `prd-bootstrap` | `beacon/commands/prd_bootstrap.py` |
| `profile` | `beacon/commands/profile.py` |
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
| `ui-spec` | `beacon/commands/ui_spec.py` |
| `user-story` | `beacon/commands/user_story.py` |
| `verify` | `beacon/commands/verify.py` |
| `version` | `beacon/commands/version.py` |
| `workflow` | `beacon/commands/workflow.py` |

## Key Point

Most complexity lives below the command functions, in state helpers, artifact helpers, project workflow helpers, and QA/release scoring helpers.

