# 证据：Beacon Loop Native Runner and Automation Retirement

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| planner-review-r2 | support_advisory | conversation: beacon-pln-review full parity | accepted-for-change | change |
| change-record-r2 | support_advisory | docs/beacon/archive/v1.6.0/change/beacon-loop-native-runner-and-automation-retirement.md | accepted-for-change | refreeze |
| planner-research | support_advisory | docs/beacon/archive/v1.6.0/research/beacon-loop-native-runner-and-automation-retirement.md | promoted | truth.define |
| feature-package | requirement_truth | docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/evidence.md | evidence-indexed | evaluate |
| gnhf-source | support_advisory | /Users/apple/Developer/Personal/oss-sync/agents/agent-systems/gnhf | indexed | source-study |
| gnhf-analysis | support_advisory | /Users/apple/Developer/Personal/oss-sync/index/analysis/kunchenguid-gnhf.md | indexed | source-study |
| manage-oss-sync-harness | support_advisory | ~/.codex/skills/manage-oss-sync/SKILL.md | indexed | source-study |
| implementation-mvp-skeleton | support_advisory | packages/beacon-loop/ | partial | generate |
| implementation-phase-a-orchestrator | support_advisory | packages/beacon-loop/src/runner/orchestrator.ts; state.ts; prompt.ts | implemented | qa |
| implementation-phase-b-ledger | support_advisory | packages/beacon-loop/src/ledger/; harness/ | implemented | qa |
| implementation-phase-c-adapters | support_advisory | packages/beacon-loop/src/agents/; config/load.ts; git/branches.ts | implemented | qa |
| implementation-phase-d-e2e-script | support_advisory | packages/beacon-loop/tests/beacon-loop.test.mjs (TC-033); scripts/e2e-closed-loop.mjs | implemented | qa |
| implementation-automation-retirement | support_advisory | beacon/commands/automation.py; automation/README.md | implemented | generate |
| implementation-tests | support_advisory | packages/beacon-loop/tests/beacon-loop.test.mjs (26 cases); tests/test_v160_beacon_loop_automation_retirement.py | partial | qa |

## 决策记录

- 已接受：R2 change 将 `scope_mode` 提升为 `full_parity`（gnhf runner + manage-oss-sync harness patterns）。
- 已接受：State Model、Parity Matrix、Deferral Ledger 写入 package truth。
- 已接受：D-005..D-008（TUI、telemetry、prevent-sleep、stdin UX）显式 defer 至 v1.6.x patch。
- 已接受：MVP 骨架（TASK-001..018）保留为已完成历史，但 full parity AC-016..AC-030 待 Phase A-D 实现与 QA。
- 已接受：Beacon QA/release 仍是唯一 closure verdict。

## Implementation Candidate Evidence（MVP 骨架）

- `beacon automation` 已退役为 blocking stub。
- `packages/beacon-loop` 提供独立 CLI；`goal` 写入 runtime process records。
- resolver fail-closed 与 `import-evidence` 桥接已实现。

## Implementation Candidate Evidence（Phase A-D — 待 Beacon QA closure）

- Phase A-D 代码路径已实现：`orchestrator` 多轮、`ledger`/`diagnose`/`runtime-*`、`analyze`/`learn`、branch modes、config、claude/acp adapters、TC-033 closed-loop 脚本测试。
- `beacon-loop` 仍不产出 QA/release verdict；closure 需 `beacon qa run` + release gate（TASK-040）。

## Verification Commands

```bash
npm --prefix packages/beacon-loop run build
npm --prefix packages/beacon-loop test
pytest -q tests/test_v160_beacon_loop_automation_retirement.py
beacon validate-feature-package beacon-loop-native-runner-and-automation-retirement --version v1.6.0 --json
```

## 边界

`evidence.md` 是证据索引/read model，不是 final verdict。不得包含 release readiness、QA pass、implementation completion 或 source-of-truth override。
