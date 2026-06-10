# 证据：Beacon Loop Native Runner and Automation Retirement

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| planner-research | support_advisory | docs/beacon/v1.6.0/research/beacon-loop-native-runner-and-automation-retirement.md | accepted-for-change | truth.define |
| feature-package | requirement_truth | docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/evidence.md | evidence-indexed | evaluate |
| gnhf-analysis | support_advisory | /Users/apple/Developer/Personal/oss-sync/index/analysis/kunchenguid-gnhf.md | indexed | source-study |
| gnhf-learning-note | support_advisory | /Users/apple/Developer/Personal/personal-brain/sources/oss-sync-notes/kunchenguid-gnhf/2026-06-09-104020.md | indexed | source-study |
| beacon-project-note | support_advisory | /Users/apple/Developer/Personal/personal-brain/projects/notes/beacon/2026-06-09-104021.md | indexed | source-study |
| compound-engineering-article | support_advisory | /Users/apple/Developer/Personal/personal-brain/sources/web/mp-weixin-qq-com-superpowers-ai-51-agent-35.md | indexed | source-study |
| implementation-python-retirement | support_advisory | beacon/cli_factory.py; beacon/command_catalog.py; beacon/commands/automation.py; beacon/commands/implement/commands.py | implemented | generate |
| implementation-loop-package | support_advisory | packages/beacon-loop/ | implemented | generate |
| implementation-automation-tombstone | support_advisory | automation/README.md | implemented | generate |
| implementation-tests-python | support_advisory | tests/test_v160_beacon_loop_automation_retirement.py | passing | qa |
| implementation-tests-node | support_advisory | packages/beacon-loop/tests/beacon-loop.test.mjs | passing | qa |

## 决策记录

- 已接受：旧 `automation` 业务面不继续承载长 loop agent 保活，应退役或仅保留 blocking stub。
- 已接受：Beacon 仓库采用同仓库双 CLI 目标形态：`beacon` 负责 truth/gate，`beacon-loop` 负责 long loop runner。
- 已接受：`beacon-loop` 正式入口为 `beacon-loop goal "<goal>"`。
- 已接受：不保留 `beacon-loop lfg "<goal>"` alias、deprecated alias、compatibility route 或 help hint。
- 已接受：`beacon-loop` 必须先读取 Beacon resolver-selected truth，resolver blocked 或 feature package 缺失时 fail closed 并路由 `beacon-gen-change`。
- 已接受：`beacon-loop` runtime artifacts 是 process records，不是 requirement truth。
- 已接受：implementation candidate 必须通过 Beacon evidence import、QA 和 release gate 回到主链；`beacon-loop` 不给 QA/release verdict。

## Implementation Candidate Evidence

- `beacon automation` 已从 `beacon/cli_factory.py` active registration 和 `beacon/command_catalog.py` default/support surfaces 移除。
- `beacon/commands/automation.py` 仅保留 blocking stub：`automation retired; use beacon-loop goal`。
- 旧 scheduler queue/job 业务 utils 和 `automation/jobs/`、`automation/launchd/`、`automation/beacon-automation-queue.json` 已退役。
- `packages/beacon-loop` 提供独立 Node 20-compatible CLI package，bin 为 `beacon-loop`。
- `beacon-loop goal` 写入 `.beacon/loop/runs/<run-id>/` runtime process records，并通过 `beacon truth-map resolve ... --json` fail-closed 读取 truth。
- `beacon-loop import-evidence` 调用 `beacon implement import-evidence`，只导入 implementation evidence candidate。
- Runtime evidence 标记 `runtime_process_record_not_requirement_truth`，并显式声明不提供 QA/release closure verdict。

## Verification Commands

```bash
npm --prefix packages/beacon-loop run build
npm --prefix packages/beacon-loop test
pytest -q tests/test_v160_beacon_loop_automation_retirement.py tests/test_v113_command_layering.py tests/test_skill_command_alignment.py
beacon --help
rg "beacon-automation-queue|beacon-hourly-qa|repair-window" beacon automation
```

## 边界

`evidence.md` 是证据索引/read model，不是 final verdict。它不得包含 release readiness、QA pass、implementation completion 或 source-of-truth override。
