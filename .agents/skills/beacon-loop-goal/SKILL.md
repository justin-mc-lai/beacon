# Beacon Loop Goal

## Overview

Cross-harness orchestrator skill that sequences all Beacon lifecycle skills (truth → implement → QA → release) using a deterministic state machine. Governor harness type — only routes, never executes.

## When to Use

- User wants one prompt to drive the full Beacon lifecycle (truth → implement → QA → release)
- User wants automatic stage transitions with stop-when checks
- User wants error recovery routing to beacon-gov-debug

## Harness

**governor** — This skill only does routing, state tracking, and stage decisions. It never writes truth, implements code, gives QA verdicts, or issues release verdicts.

## HARD GATE

You are running a governor skill.
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。

## State Machine

```text
idle → governance_precheck
  → pass: truth_routing | blocked: governance_repair → idle
truth_routing → invoke beacon-gen-truth → truth_verify
  → frozen: implement_routing | not_frozen: truth_routing (retry) | blocked: error_recovery
implement_routing → invoke beacon-gen-implement → implement_verify
  → tests_pass: qa_routing | tests_fail: implement_routing (repair loop, max 3) | blocked: error_recovery
qa_routing → invoke beacon-eval-qa → qa_verify
  → pass: release_gate | fail: implement_routing (repair loop, max 3) | blocked: error_recovery
release_gate → human_confirmed: invoke beacon-eval-release → done
  → human_rejected: idle
error_recovery → invoke beacon-gov-debug → 修复后回到对应阶段
```

## Decision Tree

When this skill is invoked, follow this decision tree sequentially:

### Step 0: Initialize
1. Call `loop_goal_state.init()` with version, feature, utterance
2. Read run_id from the returned state

### Step 1: Governance Precheck
1. Run `beacon plan start --project-root . --version <version> --json` (governance precheck)
2. If `blocked`:
   - Call `loop_goal_state.route_to_error_recovery()` with reason_code
   - Output: "Governance precheck blocked. Route to beacon-gov-debug."
   - STOP
3. If `pass`:
   - Call `loop_goal_state.transition(to_stage="truth_routing")`
   - Go to Step 2

### Step 2: Truth Stage
1. **Route to `beacon-gen-truth`** — tell the agent to load this skill
2. After beacon-gen-truth returns:
   - Read `docs/beacon/<version>/features/<feature>/truth.md` frontmatter
   - If `status: frozen`:
     - Call `loop_goal_state.transition(to_stage="implement_routing", outputs={"truth_frozen": True})`
     - Go to Step 3
   - If `status != frozen`:
     - Stay in `truth_routing` — truth is not ready
     - Output: "Truth not frozen. Continue with beacon-gen-truth."
     - STOP (wait for next invocation)

### Step 3: Implement Stage
1. **Route to `beacon-gen-implement`** — tell the agent to load this skill
2. After beacon-gen-implement returns:
   - Run tests: `python3 -m pytest tests/test_v166_*.py -q`
   - If tests pass:
     - Call `loop_goal_state.transition(to_stage="qa_routing", outputs={"tests_pass": True})`
     - Go to Step 4
   - If tests fail:
     - Call `loop_goal_state.increment_repair_loop()`
     - If repair loop count <= MAX_REPAIR_LOOPS:
       - Stay in `implement_routing` — retry
       - Output: "Tests failed. Retry implement. Repair loop <n>/3."
       - STOP (wait for next invocation)
     - If repair loop count > MAX_REPAIR_LOOPS:
       - Call `loop_goal_state.route_to_error_recovery()`
       - Output: "Max repair loops exceeded. Route to beacon-gov-debug."
       - STOP

### Step 4: QA Stage
1. **Route to `beacon-eval-qa`** — tell the agent to load this skill
2. After beacon-eval-qa returns:
   - Read QA verdict from `.beacon/qa-status.json` or QA output
   - If `pass`:
     - Call `loop_goal_state.transition(to_stage="release_gate", outputs={"qa_verdict": "pass"})`
     - Go to Step 5
   - If `fail`:
     - Call `loop_goal_state.increment_repair_loop()`
     - If repair loop count <= MAX_REPAIR_LOOPS:
       - Call `loop_goal_state.transition(to_stage="implement_routing")`
       - Output: "QA failed. Back to implement. Repair loop <n>/3."
       - STOP
     - If repair loop count > MAX_REPAIR_LOOPS:
       - Call `loop_goal_state.route_to_error_recovery()`
       - STOP

### Step 5: Release Gate (HUMAN GATE — ALWAYS)
1. **STOP and wait for human confirmation**
2. Even if `auto_decide=true`, release ALWAYS requires human confirmation
3. Output: "QA passed. Release gate reached. Human confirmation required."
4. When human confirms:
   - Call `loop_goal_state.check_release_gate(human_confirmed=True)`
   - **Route to `beacon-eval-release`** — tell the agent to load this skill
   - After beacon-eval-release returns:
     - Call `loop_goal_state.transition(to_stage="done", outputs={"release_verdict": "go"})`
     - Output: "Loop goal complete. Feature delivered."
5. When human rejects:
   - Call `loop_goal_state.transition(to_stage="idle")`
   - Output: "Release rejected. Returning to idle."

### Error Recovery (any stage blocked)
1. **Route to `beacon-gov-debug`** — tell the agent to load this skill
2. After beacon-gov-debug returns with fix:
   - Read current_stage from state
   - Resume from the blocked stage
3. If cannot fix:
   - Output: "Error recovery failed. Manual intervention required."
   - STOP

## Skill Routing Matrix

| Stage | Skill to Load | Check After Return |
|-------|--------------|-------------------|
| governance_precheck | CLI: `beacon plan start` | `status=pass` or `blocked` |
| truth_routing | `beacon-gen-truth` | `truth.md status=frozen`? |
| implement_routing | `beacon-gen-implement` | pytest exit code 0? |
| qa_routing | `beacon-eval-qa` | verdict=pass? |
| release_gate | `beacon-eval-release` | go/no-go (HUMAN CONFIRMED) |
| error_recovery | `beacon-gov-debug` | fix applied? |

## Auto-Decide Rules

| Decision Point | Default Behavior | Can Override? |
|---------------|-----------------|----------------|
| truth scope (lake/ocean) | auto-decide | `--human-gate` |
| truth freeze | auto-decide (verify pass) | `--human-gate` |
| implement start | auto-decide (truth frozen) | `--human-gate` |
| QA start | auto-decide (tests pass) | `--human-gate` |
| **release start** | **MUST human confirm** | **NEVER** |

## State File

State is persisted at `.beacon/state/loop-goal/<run_id>.json` with schema `loop-goal-state.v1`.

## Boundary

- This skill is a **governor** — it never executes truth/implement/QA/release
- It uses **sequential skill loading** — each skill completes before the next is loaded
- It relies on **file-system state** — not agent memory
- **Release gate is always human-gated** — no exceptions
