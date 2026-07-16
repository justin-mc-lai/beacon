# Long-Task Operator Guide (v1.6.1)

Human-facing operator surface for **lake/sea long tasks** on the pre-main delivery line. Normative requirement truth remains in feature packages; this guide is the **read model** operators should bookmark.

Authority: `support_advisory` (not package truth). Bindings: `beacon-loop-goal-closed-loop-orchestrator-v161` (AC-072), `beacon-harness-program-plan-v161` (AC-PBP-027).

## What to remember

| Role | Command / surface | Owns |
|------|-------------------|------|
| **Long-task primary entry** | `beacon-loop goal "<utterance>"` | Scope classify (湖/海), resume, delegate to `beacon-run`, optional eval supplement |
| **Program scaffold only** | `beacon plan start "<utterance>" --program <slug> …` | `programs/<slug>/` layout, `plan_mode`, manifest — **not** the full long FSM |
| **Host program planner** | `/beacon-pln-program` (umbrella skill) | Same scaffold contract as `plan start`; delegates auto/interactive sub-skills |

**Rule:** For end-to-end long work (海级 program + per-lake delivery), start or resume with **`beacon-loop goal`**. Use **`beacon plan start`** only to scaffold program artifacts before or alongside `goal`.

## Typical flows

### Lake utterance (湖)

```bash
beacon-loop goal "实现 beacon X 的 Y 能力" \
  --project-root . --version v1.6.1 \
  --mode delivery
```

- Skips program outer FSM.
- Runs per-lake delivery (upstream v1.6.0 R10 loop).

### Sea utterance (海)

```bash
# Optional: scaffold program directory + plan_mode first
beacon plan start "完整复刻某 GitHub 项目" \
  --project-root . --version v1.6.1 \
  --program my-program \
  --mode auto-detect

# Authoritative long-task entry (resume OK after plan start)
beacon-loop goal "完整复刻某 GitHub 项目" \
  --project-root . --version v1.6.1 \
  --mode program \
  --program my-program
```

- Outer **ProgramPlanState** P0–P6 via `beacon-run --mode program` (delegated).
- State file: `programs/<slug>/program-run-state.json` (shared with `plan start`).
- P4 user ack **gates** per-lake delivery spawn.
- Inner per-lake delivery still obeys upstream `truth_freeze_gate` (AC-068).

### Ambiguous scope (UD-007)

When lake/sea confidence is low, `beacon-loop goal` asks **one** multiple-choice question (non-dry-run). Answer is written to `intent-contract.json` or `program-manifest.md`. Dry-run does not block on MCQ.

### Opt-in eval supplement (never gates QA/release)

```bash
beacon-loop goal "<utterance>" --eval-matrix --eval-scorecard
```

Artifacts under run-dir: `eval-matrix.json`, `eval-scorecard.json` with `formal_verdict_authority=false`.

## Resume contract (AC-PBP-029 / AC-072)

After `beacon plan start`, **`beacon-loop goal` must resume** the same `program_slug` — do not re-scaffold to continue the outer FSM.

Shared state fields (minimum): `program_slug`, `plan_mode`, `program_phase`, `next_action`.

```bash
beacon-loop goal "<same utterance>" \
  --program my-program --mode program --dry-run   # inspect spine / next action
```

## What `beacon plan start` does **not** do

- Does **not** replace `beacon-loop goal` for long FSM execution.
- Does **not** produce formal QA or release verdicts.
- Does **not** write `features/*/truth.md` (planner boundary).
- Does **not** skip P4 ack before spawning per-lake delivery in program mode.

## Related contracts

| Doc | Purpose |
|-----|---------|
| `docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md` | Loop v1.6.1 delta (AC-072..075) |
| `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | Program harness + P0–P6 (AC-PBP-*) |
| `docs/beacon/archive/v1.6.1/execution/program-plan-contract.md` | Program directory schema + plan_mode |
| `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` | Upstream frozen R10 per-lake delivery |

## Formal verdict authority

Only Beacon evaluator surfaces (`beacon qa run`, `beacon release check`) issue formal QA/release verdicts. Eval supplement and planner artifacts are advisory.
