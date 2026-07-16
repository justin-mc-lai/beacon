---
name: beacon-loop-goal
description: Beacon v1.6.6 governor skill for public cross-harness lifecycle orchestration. Use when the user wants one prompt to route truth -> implement -> QA -> release while preserving every harness hard gate and requiring human confirmation before release.
---

# Beacon Loop Goal

## Overview

Cross-harness orchestrator skill that sequences all Beacon lifecycle skills (truth -> implement -> QA -> release) using a deterministic state machine. Governor harness type - only routes, never executes.

## When to Use

- User wants one prompt to drive the full Beacon lifecycle (truth -> implement -> QA -> release)
- User wants automatic stage transitions with stop-when checks
- User wants error recovery routing to beacon-gov-debug

## Harness

**governor** - This skill only does routing, state tracking, and stage decisions. It never writes truth, implements code, gives QA verdicts, or issues release verdicts.

## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。

## State Machine

```text
idle -> governance_precheck
  -> pass: truth_routing | blocked: governance_repair -> idle
truth_routing -> invoke beacon-gen-truth -> truth_verify
  -> frozen: review_routing | not_frozen: truth_routing (retry) | blocked: error_recovery
review_routing -> invoke beacon-pln-review -> review_verify
  -> implement_ready: standard_execution_precheck
  -> truth_or_change_route: drift_routing
  -> user_decision_required: error_recovery
  -> blocked: error_recovery
standard_execution_precheck -> verify canonical baseline + branch governance + workspace admission
  -> pass: implement_routing
  -> blocked: error_recovery
implement_routing -> invoke beacon-gen-implement -> implement_verify
  -> tests_pass: qa_routing | tests_fail: implement_routing (repair loop, max 3) | blocked: error_recovery
qa_routing -> invoke beacon-eval-qa -> qa_verify
  -> pass: release_gate | fail: implement_routing (repair loop, max 3) | blocked: error_recovery
release_gate -> human_confirmed: invoke beacon-eval-release -> done
  -> human_rejected: idle
error_recovery -> invoke beacon-gov-debug -> resume from blocked stage
```

## Decision Tree

When this skill is invoked, follow this decision tree sequentially:

### Step 0: Initialize

1. Call `loop_goal_state.init()` with version, feature, utterance.
2. Read `run_id` from the returned state.

### Step 1: Governance Precheck

1. Run `beacon plan start --project-root . --version <version> --json`.
2. If blocked, call `loop_goal_state.route_to_error_recovery()` with the reason code, output the `beacon-gov-debug` route, and stop.
3. If pass, call `loop_goal_state.transition(to_stage="truth_routing")` and continue.

### Step 2: Truth Stage

1. Verify the current checkout is on governance `truth_canonical` (`main` or `master`); if not, route to `beacon-gov-debug` with `reason_code=truth_canonical_branch_mismatch` and stop.
2. Route to `beacon-gen-truth`.
3. After it returns, read `docs/beacon/<version>/features/<feature>/truth.md` frontmatter.
4. If `status: frozen`, transition to `review_routing`.
5. If not frozen, stay in `truth_routing`, output the next route, and stop.

### Step 2.5: Planner Review Decision Packet

1. Route to `beacon-pln-review` when lifecycle, state, loop, source parity, deferral, design, or cross-harness risk is present.
2. When runtime evidence is needed, run `beacon planner-review run <feature> --project-root . --version <version> --prompt "<utterance>" --json`.
3. Record the returned artifact with `loop_goal_state.record_review_decision()`.
4. If the review packet has P0/P1 findings, `user_decision_required=true`, or recommends `beacon-gen-truth` / `beacon-gen-change` / `beacon-gen-refreeze`, stop and route instead of implementing.
5. Only transition to `standard_execution_precheck` when the recorded decision packet is implement-ready.

### Step 2.6: Standard Execution Precheck

1. Verify canonical truth/refreeze has been committed on `main` or `master`.
2. Verify the feature worktree contains `truth_baseline_commit`; if not, block with `reason_code=truth_baseline_not_merged`.
3. If feature-local `.machine` revision/projection dirty state or stale refreeze is detected, require a scoped stash/archive quarantine ref before continuing.
4. Require a verification bundle containing `truth-map verify`, `verify-materials --strict`, `git diff --check`, `branch-governance verify`, and workspace admission results.
5. Require `implement check-branch` / workspace admission to pass and record `workspace_admission_ref`.
6. Record the result with `loop_goal_state.record_standard_execution_precheck()`.
7. If the result is blocked, route to `beacon-gov-debug`; only `pass` or `up_to_date` may continue to `implement_routing`.

### Step 3: Implement Stage

1. Route to `beacon-gen-implement`.
2. After it returns, run the feature tests declared by the requirement package.
3. If tests pass, transition to `qa_routing`.
4. If tests fail, increment repair loop; retry implement up to 3 times, then route to `beacon-gov-debug`.

### Step 4: QA Stage

1. Route to `beacon-eval-qa`.
2. If QA passes, transition to `release_gate`.
3. If QA fails, return to `implement_routing` up to the repair limit, then route to `beacon-gov-debug`.

### Step 5: Release Gate (HUMAN GATE - ALWAYS)

1. Stop and wait for human confirmation.
2. Even if `auto_decide=true`, release always requires human confirmation.
3. After confirmation, call `loop_goal_state.check_release_gate(human_confirmed=True)` and route to `beacon-eval-release`.
4. If human rejects, transition to `idle`.

### Error Recovery

1. Route blocked stages to `beacon-gov-debug`.
2. After repair, resume from the blocked stage.
3. If repair cannot complete, stop for manual intervention.

## Skill Routing Matrix

| Stage | Skill to Load | Check After Return |
|-------|--------------|-------------------|
| governance_precheck | CLI: `beacon plan start` | `status=pass` or `blocked` |
| truth_routing | `beacon-gen-truth` | on `truth_canonical` branch? `truth.md status=frozen`? |
| review_routing | `beacon-pln-review` | decision packet allows implement? |
| standard_execution_precheck | CLI: `truth-map verify`; `verify-materials --strict`; `git diff --check`; `branch-governance verify`; `implement check-branch` | canonical baseline committed/merged? workspace admission pass? |
| implement_routing | `beacon-gen-implement` | feature tests pass? |
| qa_routing | `beacon-eval-qa` | verdict=pass? |
| release_gate | `beacon-eval-release` | go/no-go after human confirmation |
| error_recovery | `beacon-gov-debug` | fix applied? |

## Auto-Decide Rules

| Decision Point | Default Behavior | Can Override? |
|---------------|-----------------|---------------|
| truth scope (lake/ocean) | auto-decide | `--human-gate` |
| truth freeze | auto-decide after verify pass | `--human-gate` |
| implement start | auto-decide after truth frozen | `--human-gate` |
| QA start | auto-decide after tests pass | `--human-gate` |
| release start | must human confirm | never |

## State File

State is persisted at `.beacon/state/loop-goal/<run_id>.json` with schema `loop-goal-state.v1`.
Standard execution outputs include `standard_execution_flow_status`, `truth_baseline_commit`, `canonical_refreeze_committed`, `feature_worktree_reconciled`, `stale_feature_refreeze_quarantine_ref`, `verification_bundle_ref`, and `workspace_admission_ref`.

## Boundary

- This skill is a governor skill - it never executes truth, implement, QA, or release.
- It uses sequential skill loading; each skill completes before the next route decision.
- It relies on file-system state, not agent memory.
- Release is always human-gated.
