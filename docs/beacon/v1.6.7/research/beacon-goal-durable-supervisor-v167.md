---
slug: beacon-goal-durable-supervisor-v167
version: v1.6.7
status: support_advisory
authority: beacon-pln-review
kind: planner_review
proposed_lake: beacon-goal-durable-supervisor-v167
user_intent_ref: "session: goal interrupt analysis + durable supervisor + context/log + zvec exploration"
related:
  - docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md
  - docs/beacon/v1.6.7/features/beacon-loop-goal-v166/truth.md
  - docs/beacon/v1.6.7/research/loop-goal-dynamic-intent-routing-friction-2e306f7a.md
  - beacon/utils/product_goal_runtime.py
  - https://github.com/alibaba/zvec
---

# Research: beacon-goal-durable-supervisor-v167

## architecture

Product Goal durable stack (Beacon-native):

```text
Host agent skill turns (ephemeral)
  → $beacon-goal / CLI
  → product_goal_runtime ledger (GoalRun)
  → opt-in SupervisorSession (beacon goal supervise)
  → workers: ralph (implement) | beacon qa run (qa)
  → verifier refs → complete
  → release human gate
Disk: execution.jsonl + checkpoint.json + optional sqlite FTS (P2)
```

- No second public entry; supervise is a **sub-command** of goal.
- Authority: scorecards/verifier for complete; logs/FTS are support_advisory only.
- zvec is **not** architecture core (optional P2 later).

## business flow

1. User: `beacon goal run "..."` → GoalRun `created/running` (no auto supervise).
2. Optional: `beacon goal supervise --run-id` → SupervisorSession `active` (interval default 120s).
3. Implement/QA work + `heartbeat` / auto heartbeat on interval.
4. Host interrupt or idle stall → `host_interrupted` + checkpoint frozen.
5. User/agent: `resume-pack` → continue `last_substep` / `next_action`.
6. `tick --execute` may dispatch qa/ralph for current stage.
7. Attach verifier → `complete` (never without refs).
8. Release remains human confirmation.

Illegal: auto-supervise on run; complete without verifier; overwrite JSONL; FTS overrides verifier.

---




# Planner Review: beacon-goal-durable-supervisor-v167

## Intent snapshot

| Field | Value |
|-------|--------|
| User intent | Make `$beacon-goal` actually run long-horizon to delivery without silent stall; solve **context full**, **persist execution logs**, explore stable stack; evaluate **zvec** |
| Product pain | Product Goal is a **facade ledger** (tick/stage/history); implement/qa done by host agent turns → turns end / context fills / multi-hour implement with empty history → appears "interrupted" |
| Proposed lake | `beacon-goal-durable-supervisor-v167` = supervisor + heartbeat history + tick drives implement/qa + unified host_interrupt/resume |
| Scope mode | **Lake (boil dry)** for supervisor/heartbeat/tick-semantics/interrupt; **Ocean defer** for multi-machine agent fleet / multi-tenant orchestration SaaS |

## Verdict (can 立项?)

| Question | Answer |
|----------|--------|
| Can project as v1.6.7 lake? | **YES — recommend GO as P0 lake** after change freeze |
| Blocks current release-ready product-goal domain delivery? | **No** (additive capability on already-shipped facade) |
| Truth rewrite of product-goal-runtime? | **Change/refreeze extension** (new ACs), not greenfield ocean |

**Recommended route**: `beacon-gen-change` → freeze `beacon-goal-durable-supervisor-v167` (+ optional small AC patch to `beacon-product-goal-runtime-v167`) → implement → QA.

---

## Problem decomposition (from execution trace)

Trace pattern (`pgr-7e14b35ce09e` style):

1. Facade creates run + auto_tick design in **seconds**
2. Implement runs **hours** with **no goal history heartbeats**
3. Host agent turn ends / context full → process looks dead while `status=running`
4. User says「继续」→ manual resume, not supervisor
5. QA/matrix/FSM gates can block hours more
6. Complete only after verifier attach

Root classes:

| Class | Name | Durable-supervisor owns? |
|-------|------|--------------------------|
| A | Host turn ended | Yes (detect + resume) |
| B | Facade tick doesn't execute work | Yes (tick → worker) |
| C | QA/impl product blockers | Partial (retry/route; not invent green) |
| D | Release human gate | No (keep human) |
| E | blocked_streak≥3 | Already exists; wire to supervisor |

---

## Context full — how to solve

Context full is **not solved by a bigger window alone**. Stacked strategies (stable order):

### Layer 0 — Externalize authority (Must)

| Artifact | Path (proposal) | Role |
|----------|-----------------|------|
| Goal run ledger | `.beacon/state/product-goal/<run_id>.json` | stages, done_when, verifier |
| Heartbeat / history | same + `history[]` append-only | every N minutes / every substep |
| Execution log (JSONL) | `.beacon/state/product-goal/<run_id>/execution.jsonl` | tool/cmd/result/exit |
| Checkpoint pack | `.beacon/state/product-goal/<run_id>/checkpoint.json` | last_substep, open_files, next_action |
| Stage evidence | `.beacon/evidence/**`, QA scorecards | verifier inputs |

**Rule**: LLM context holds **pointer + digest**, never full log.

### Layer 1 — Progressive load (already claimed, enforce)

- Load only current stage skills (product-goal progressive_skills)
- Implement: one lake / one satellite at a time when possible
- QA: sequential lakes (already preferred)

### Layer 2 — Compaction protocol (Must design)

On resume / new host turn, inject only:

```text
1. utterance + done_when + current_stage
2. last 5 heartbeats
3. open blockers + reason_codes
4. checkpoint.next_action (one concrete step)
5. paths to full logs (do not paste)
```

Forbid re-pasting full chat history as source of truth.

### Layer 3 — Subagent / satellite slice (Should)

- Main star keeps orchestration short
- Satellite worktrees hold feature isolation (already planned main_star_satellite_pool)
- Each satellite checkpoint independent → less single-context pressure

### Layer 4 — Optional semantic memory (P2, zvec-fit)

Retrieve similar past failures / prior steps by embedding **only for packing resume context**, never as authority over truth/QA.

---

## Execution logs — can we save them?

**Yes — Must for this lake.** Already partial (`history[]` events); insufficient (implement multi-hour gap with zero events).

### Proposed log contract

```json
{
  "ts": "ISO-8601",
  "run_id": "pgr-...",
  "stage": "implement|qa|...",
  "event": "heartbeat|cmd_start|cmd_end|host_interrupt|blocker|tick|checkpoint",
  "substep": "string",
  "cmd": "optional",
  "exit_code": 0,
  "summary": "≤240 chars",
  "refs": [".beacon/evidence/..."],
  "host": "codex|claude|cli"
}
```

File: `.beacon/state/product-goal/<run_id>/execution.jsonl` (append-only).

### Heartbeat policy

| Trigger | Write |
|---------|--------|
| Every implement substep complete | heartbeat + files changed digest |
| Every `beacon qa run` start/end | cmd_start/cmd_end |
| Every `goal tick` | tick |
| Host turn start/end if detectable | host_resume / host_interrupt |
| Wall clock ≥ N minutes while stage=active | heartbeat (supervisor) |

### Retention

- JSONL under project `.beacon/` (gitignored by default)
- Optional rotate by size (e.g. 50MB)
- Scorecards/evidence remain release authority; logs are **support_advisory** for resume

---

## Durable supervisor — technical stack options

### What "stable" means here

| Need | Stable approach | Fragile approach |
|------|-----------------|------------------|
| Survive agent session death | On-disk state + re-entry CLI | Chat memory only |
| Drive work without LLM | Deterministic workers for tick→qa/cmd | LLM self-claims complete |
| Resume semantics | last_substep + reason_code (loop AC-034 style) | Restart whole goal |
| Multi-hour implement | Heartbeat + checkpoint pack | Hope context holds |
| Complete audit | Existing verifier gate | Self-certify |

### Stack recommendation (Beacon-native first)

```text
Host agent (Codex/Claude) — skill turns (may die)
    → $beacon-goal skill (same-session continue)
    → product_goal_runtime ledger + supervisor loop (NEW)
         - poll run status
         - if idle>N → emit resume_action
         - if stage=qa → invoke beacon qa run
         - if stage=implement → delegate ralph
         - heartbeat writer
    → ralph/impl | qa runner | release human gate
```

| Component | Reuse | New |
|-----------|-------|-----|
| Stage ledger | product_goal_runtime | heartbeat API, last_substep |
| Interrupt/resume | loop_goal_state AC-028/034 | **unify into product-goal** |
| Implement loop | ralph boundary | supervisor may call `goal delegate-ralph` |
| QA drive | `beacon qa run` | tick-with-exec / supervisor worker |
| Logs | partial history | execution.jsonl + checkpoint |
| Vector memory | none required | optional zvec later |

### Alternative stacks (evaluated)

| Option | Fit | Notes |
|--------|-----|-------|
| Pure skill discipline only | Weak | Host non-enforcement already frictioned loop |
| External Temporal/Airflow | Overkill | Heavy ops; Beacon is local-first CLI |
| tmux/cli_agent loop (loop dual runtime) | Medium | Good pattern; product-goal should own durable loop |
| LangGraph as core | Risky | Extra dependency; truth/QA authority still Beacon |
| **zvec as core supervisor** | **No** | Vector DB only |

**P0 stable path**: extend Beacon Python CLI + JSON/JSONL state + reuse loop interrupt semantics + ralph/qa workers.  
**P2 optional**: embed zvec for retrieval over logs.

---

## zvec — can this framework be used?

### What zvec is

From [alibaba/zvec](https://github.com/alibaba/zvec) (README / zvec.org):

- **In-process vector database** (Alibaba Tongyi Lab; Apache-2.0)
- Dense/sparse vectors, FTS, hybrid search, WAL durability, DiskANN
- Python / Node / Go / Rust SDKs — embed in app, no separate server
- Schema: CollectionSchema + insert + query by vector/FTS

### What zvec is NOT

| Expectation | Reality |
|-------------|---------|
| Agent orchestrator / supervisor | No |
| Workflow engine / resume FSM | No |
| Goal/tick/QA runner | No |
| Chat memory product out-of-box | No (build retrieval on top) |

### Fit matrix for durable-supervisor

| Supervisor need | zvec role |
|-----------------|-----------|
| Persist stage state | Use JSON ledger; zvec optional index |
| Drive implement/qa | **Cannot** — use CLI workers |
| host_interrupt/resume | **Cannot** — use loop-style state machine |
| Context full → pack relevant past steps | **Yes (P2)** — embed heartbeat lines, hybrid top-k |
| Full-text search over execution.jsonl | **Yes (P2)** — FTS on summary/cmd |
| Crash-safe vector index | WAL strong; still secondary to ledger |

### Recommendation on zvec

| Priority | Decision |
|----------|----------|
| **P0 durable supervisor** | **Do not depend on zvec** |
| **P2 goal-memory-index** | Optional: `beacon goal memory reindex/search` via zvec |
| Risk if zvec on P0 | Native wheels, Python 3.10+, platform CI surface |

**Bottom line**: zvec is a **solid local vector store** for **resume context packing**, **not** the supervisor framework.

P0 prefer: (1) JSONL + checkpoint, (2) sqlite FTS if keyword search needed, (3) zvec when semantic retrieval proven necessary.

---

## Proposed lake design (for change, not freeze yet)

### Lake: `beacon-goal-durable-supervisor-v167`

| Slice | Content | Priority |
|-------|---------|----------|
| S1 Heartbeat + execution.jsonl + checkpoint pack | Must | P0 |
| S2 Goal skill same-session continue + resume CLI parity with loop | Must | P0 |
| S3 `tick --execute` / supervisor poll: drive qa/ralph when stage idle | Must | P0 |
| S4 Unify host_interrupt / last_substep into product-goal | Must | P0 |
| S5 Context packing recipe (digest injection) | Must | P0 |
| S6 Optional zvec-backed memory index | Should/Defer | P2 |

### State model (sketch)

```text
running
  → stage_active (implement|qa|...)
  → host_interrupted (resume → last_substep)
  → stage_blocked (reason_code; streak++)
  → awaiting_verifier
  → completed
  → blocked (streak≥3)
release_human_gate remains orthogonal stop
```

Illegal:

- complete without verifier
- supervisor self-certifies QA green without scorecard
- overwrite execution.jsonl (must append)

### AC candidates (for change)

| AC | Theme |
|----|--------|
| AC-DGS-001 | execution.jsonl append for every heartbeat/cmd |
| AC-DGS-002 | implement idle >N min without heartbeat → host_interrupted or stall flag |
| AC-DGS-003 | resume injects checkpoint pack only (no full chat) |
| AC-DGS-004 | tick --execute can invoke qa run / ralph delegate for current stage |
| AC-DGS-005 | host_interrupt ≠ stage_blocked |
| AC-DGS-006 | complete still requires verifier refs |
| AC-DGS-007 | optional: memory search over logs is non-authoritative |

### Non-goals

- Replace Codex/Claude host
- Multi-cloud agent fleet
- Auto-pass release without human
- Make zvec mandatory

---

## Findings (structured)

| ID | Severity | Confidence | Finding | Evidence |
|----|----------|------------|---------|----------|
| F-01 | P0 | high | Product goal is ledger-only; long implement empty history → false dead | product_goal_runtime.tick; pgr 2.8h gap |
| F-02 | P0 | high | Context full needs externalized logs + packing | progressive load; host turns |
| F-03 | P0 | high | Logs can/should be saved (JSONL+checkpoint) | history[] only coarse |
| F-04 | P0 | high | Supervisor reuses loop interrupt/resume; no dual public entry | loop AC-028/034 |
| F-05 | P1 | high | tick needs execute semantics | tick "record only" |
| F-06 | P1 | med | Host interrupt detection incomplete; need stall + user resume | loop friction |
| F-07 | P2 | high | **zvec is vector DB, not agent framework** | zvec README |
| F-08 | P2 | med | zvec good for P2 semantic log retrieval | FTS+hybrid+WAL |
| F-09 | P1 | high | Verifier/complete/release human gate stay | AC-PGR-008 |
| F-10 | P2 | med | Multi-tenant durable workers → v2 ocean | scope |

## Deferral ledger

| Item | Why deferred | Revisit |
|------|--------------|---------|
| zvec as required dep | P0 stability / CI | P2 memory index |
| Temporal/Airflow | Ops weight | Enterprise multi-host |
| Full chat archive as authority | Violates evidence model | Never for complete |
| Auto-release | Human gate policy | Only if user changes UD |

## Recommended route

```text
User confirms GO
  → beacon-gen-change v1.6.7
     freeze lake beacon-goal-durable-supervisor-v167
  → beacon-gen-implement
  → beacon-eval-qa
  → release human gate
```

**Do not** implement in this review turn.

## Open questions (optional)

1. Supervisor default: opt-in `beacon goal supervise --run-id` vs auto after `goal run`?
2. Heartbeat interval default (e.g. 5 min)?
3. P2 memory: sqlite FTS first or zvec directly?

## One-line synthesis

**可以立项**为 v1.6.7 湖 `beacon-goal-durable-supervisor-v167`：用 **Beacon 自研 durable CLI supervisor + JSONL 执行日志 + checkpoint 上下文打包 + 统一 interrupt/resume** 解长程中断；**上下文满靠外置权威+摘要注入**；**日志必须落盘**；**zvec 可用作 P2 语义检索层，不能当 supervisor 框架**。


## state machine

GoalRun durable states: created → running → stage_active → host_interrupted | stage_blocked → awaiting_verifier → completed | blocked.
SupervisorSession: detached → active → polling → waiting_host | stopped.
Illegal: host_interrupted→completed without verifier; auto-supervise on goal run; overwrite execution.jsonl.


## three-piece map / version projection truth bindings

prd_refs: `docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md` (also `docs/beacon/v1.6.7/prd/beacon-goal-durable-supervisor-v167.md`)
user_story_refs: `docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md` (also `docs/beacon/v1.6.7/user-story/beacon-goal-durable-supervisor-v167.md`)
test_case_refs: `docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/tests.md` (also `docs/beacon/v1.6.7/qa/test-cases/beacon-goal-durable-supervisor-v167.md`)
coverage_notes: AC-DGS-001..014 + legal walks TC-DGS-LEGAL-01..03 + illegal TC-DGS-ILLEGAL-01..04; domain FSM GoalRun + SupervisorSession.
out_of_scope_notes: default daemon; zvec P0 dependency; auto human release; second public entry skill; multi-tenant SaaS.

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-07-18T03:06:30.143239+00:00`
- deep_artifact_root: `docs/beacon/v1.6.7/deep/beacon-goal-durable-supervisor-v167`
- machine_artifact_root: `docs/beacon/v1.6.7/.machine/deep/beacon-goal-durable-supervisor-v167`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/v1.6.7/.machine/deep/beacon-goal-durable-supervisor-v167/release-supplement.json`
- adoption_status: `route_only`
