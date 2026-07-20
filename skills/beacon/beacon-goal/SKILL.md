---
name: beacon-goal
description: "【唯一公共入口】一句话目标 → 自动拆需求/编排/实现/验收直到 done。内部可委托 program、truth、implement(ralph)、qa、release；beacon-loop-goal 仅为 support 发现器，用户不必先调它。"
metadata:
  public_surface: true
  public_id: "goal"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  version: "v1.6.7"
  entry: public_primary
  role: product_goal_facade
---

# Beacon Goal — 唯一公共交付入口

## 你要什么就说什么

```text
$beacon-goal
目标：...
项目：.
版本：...
```

**一句话，跑到验收。** 不要先调 `$beacon-loop-goal`。

## 30 秒用法

见：`skills/beacon/examples/goal-one-shot-30s.md`

## 内部会加载什么（渐进，对用户不可见）

| 阶段 | 可能加载 |
|------|----------|
| 拆海 | beacon-pln-program* |
| 需求 | beacon-gen-truth / change |
| **设计（ux_required）** | **design stage：baseline + 公司模板 + google design.md lint** |
| 实现 | beacon-gen-implement（+ ralph） |
| 验收 | beacon-eval-qa（+ deep） |
| 发布 | beacon-eval-release（人工门） |
| 发现队列 | beacon-loop-goal（**support only**） |

## 并行（可选）

意图含并行/subagent/多湖时：`main_star_satellite_pool` — 卫星 worktree 各啃一湖，合并回主星。

## CLI

```bash
beacon goal run "<目标>" --project . --version <v>
# 可选别名
beacon run "<目标>" --project . --version <v>
beacon goal status|pause|resume|complete|tick ...
```

## Hard rules

## HARD STOP — Implement lane (UD-ENF)

**Before writing any business code** (`beacon/**`, `packages/**`, business tests):

1. Run `beacon workspace admit -p <repo> -v <ver> --feature <slug> --json`
2. **cwd must become** `worktree_path` (under `.beacon/worktrees/...`)
3. Never `git commit` business paths on `main`/`master` — pre-commit will block (`main_implement_forbidden`)
4. Dual-track: admit **both** v1.6.9 and v2.0.0 leaves when shipping dual packages
5. Emergency only: `BEACON_ALLOW_MAIN_IMPLEMENT=1` + `.beacon/evidence/main-implement-exception.json`

If you are on main and about to edit `beacon/**` → **STOP**, admit first.

Install hooks: `beacon doctor setup-git-hooks -p .`
Verify: `beacon doctor verify-git-hooks -p .` · `beacon doctor verify-implement-lane -p . --strict`



## Git worktree 开发规范（渐进加载 always-on）

**必须**打开并遵守：

- 规范：`skills/beacon/references/git-worktree-execution-flow.md`
- 示例：`skills/beacon/examples/git-worktree-process-correct-30s.md`

| 阶段 | 树 |
|------|-----|
| truth / freeze / change | **canonical** `main`/`master` only |
| implement / QA 写路径 | **admitted git worktree**（`beacon workspace admit` → cwd=`worktree_path`） |
| 对齐主干 | `git merge` / `rebase` main → delivery；**禁止**用 cherry-pick 当主对齐路径 |

进入 implement 前须等价完成 standard execution precheck（canonical baseline 已合入 feature、admission pass）。  
CLI 双装（`beacon`/`loom`）≠ 开发 worktree；安装 skill 不会自动 admit。

渐进加载：goal/implement/qa/release stage 的 `references` 必须包含上述 flow（见 `product_goal_runtime.progressive_worktree_refs` / Rust `skill_load_plan.v1`）。


- 禁止自证完成；complete 需 CLI verifier
- **git worktree 规范 always-on**（见下节）；implement 不得在未 admit 的脏 main 上直接写业务
- release 默认人工确认
- 不得要求用户手搓双 skill 流水线
- `ux_required` / 视觉交付时自动插入 design stage：`beacon design baseline --surface auto` + `beacon design lint` 证据

## Harness

Orchestrator/facade：可路由 generator/evaluator；**不**自己发 QA/release verdict。

## Durable long-run (v1.6.7)

Product Goal is durable via **opt-in** supervisor + disk logs. Do **not** expect a single chat turn to finish multi-hour implement/QA.

### Opt-in supervise (not default)

```bash
beacon goal supervise --run-id <id> --interval-sec 120 --once
```

- Default interval: **120 seconds**
- `goal run` does **not** auto-attach supervise
- Not a system daemon; use `--once` or external loop

### Heartbeat / checkpoint / resume-pack

```bash
beacon goal heartbeat --run-id <id> --summary "implemented X" --substep step-1
beacon goal checkpoint --run-id <id> --next-action "run qa for lake Y" --substep step-1
beacon goal resume-pack --run-id <id> --json
```

On host turn interrupt or context full: call **resume-pack**, inject digest only (utterance, stage, last heartbeats, blockers, one next_action, log paths). Never treat full chat as authority.

### tick --execute

```bash
beacon goal tick --run-id <id> --execute
```

May dispatch ralph/qa **plans**; never auto-confirms release; complete still needs verifier.

### Same-session continue

After routing next stage, **continue in the same session** (load implement/qa skills). If the host turn ends, resume via `resume-pack` + `supervise --once` rather than restarting the whole goal.

## Longrun AgentDriver (v1.6.7 Path C)

One-shot uninterrupted multi-turn execution (no typing「继续」each host turn):

```bash
beacon goal run "<目标>" --longrun --project . --version v1.6.7
# optional: run driver loop in-process (needs BEACON_HOST_GOAL_BRIDGE_CMD)
beacon goal run "<目标>" --longrun --driver-loop
beacon goal driver start --run-id <id>
beacon goal driver status --run-id <id>
beacon goal driver stop --run-id <id>
```

**Intent markers** (skill → longrun=true): 长跑 / 不中断 / 直到验收 / 自动续 / longrun / until done

**Rules**
- Default `goal run` does **not** start driver (idle)
- `--longrun` attaches durable supervisor + AgentDriver for **this run only**
- Each turn injects **InjectBundle**: steering (Codex distill templates under `docs/beacon/v2.0.0/fixtures/steering/`) → **resume-pack digest** → next_action (not full chat/jsonl). Completion audit only prepares **awaiting_verifier**; never self-certify complete.
- Complete still needs verifier; release always human
- Env: `BEACON_HOST_GOAL_BRIDGE_CMD` with `{prompt_file}` `{run_id}` `{project}`
- Budget defaults: max_agent_turns=32, turn_timeout_sec=3600, heartbeat=120s

## GoalRun main axis (v1.6.7 UD-AXIS)

On **change** that touches promise/stage/parallel/longrun/entry/domain:

```bash
beacon goal axis generate --program beacon-product-goal-domain-delivery-v167 -v v1.6.7
beacon goal axis validate --program beacon-product-goal-domain-delivery-v167 -v v1.6.7
# then refreeze affected feature
beacon change "<feature>" --project . --version v1.6.7 --refreeze-chain
```

Artifact: `docs/beacon/<ver>/programs/<program>/goalrun-main-axis.md`
Submachines cannot complete GoalRun; complete needs verifier; release human.

## v2.0.0 / Loom main axis

```bash
beacon goal axis generate -v v2.0.0 --program beacon-v2-product-goal-parallel-v200
beacon goal axis validate -v v2.0.0 --program beacon-v2-product-goal-parallel-v200
```

Axis embeds Loom dual-install, optional subagent, and trace mounts. Same UD-AXIS rules as v1.6.7.



## v1.6.8 Production ops

```bash
# Hotfix mode (not a second public skill entry)
beacon goal run "生产：…" --mode hotfix --from-version <tag> --forward-port <branch> --rollback-notes "…"

# Longrun default: project goal.longrun_default=true (new projects)
beacon goal run "…" -v v1.6.8
beacon goal run "…" --no-longrun   # opt-out

# Fleet / dual-version
beacon version fleet
beacon doctor init-dual-version --previous-baseline release/v1.6.7 --next-feature main
beacon doctor repair-evidence-manifest -v v1.6.8
beacon doctor align-run-id --run-id <id>
```

Program: `beacon-prod-ops-hardening-v168`. Philosophy shared with Loom/v2.


## Multi-version dual-track (v1.6.8\\v2.0.0)

One sentence may name multiple versions; Beacon decomposes into parallel tracks + lakes:

```bash
beacon goal multi-version-plan "双轨 v1.6.8\\v2.0.0 leaf-admit + InjectBundle" --json
beacon goal run "v1.6.8\\v2.0.0 并行修复" --project . --version auto --longrun
```

Rules:
- Each track uses leaf admit: `beacon/<version>/<feature-slug>`
- Implement never soft-falls back to main without admission
- Complete still needs verifier per track; release human

## Host subagent keyword gate (v1.6.8)

**Default: single-thread.** Host Codex/Claude agents spawn only when utterance contains global tokens (`子代理` / `subagent` / `多代理` / …) or explicit flag, and not negated (`不要子代理` / `--no-subagent`).

**UD-SA-001:** `并行` / `多湖` alone enable **satellite worktrees**, not host agents.

```bash
beacon doctor install-subagent-pack -p . --host-runtime codex --pack minimal
beacon doctor install-subagent-pack -p . --host-runtime claude --pack minimal
beacon doctor verify-subagent-runtime -p . --host-runtime codex --require-agents --json
```

Examples: `skills/beacon/examples/subagent-keyword-off-30s.md`, `subagent-review-on-30s.md`, `subagent-research-on-30s.md`.

Enhancement only: cannot_complete_goal; no auto-release; no second public entry.

## Public surface (Scheme A — 1+6)

See `skills/beacon/references/public-surface-1plus6.md`.

`$beacon-goal` is the **only** long-run facade. The six public harness verbs are plan/truth/design/implement/qa/release (synonyms to Rust PUBLIC_ABILITIES).

## Implement admission hard gate (v1.6.9 / v2.0.0)

Before implement write dispatch (`tick --execute` → ralph):

1. `ensure_goal_implement_admission` → `workspace admit` (+ force leaf worktree if contract optional)
2. switch existing worktree or `git worktree add`; pool lease when pooled; merge main
3. fail → goal blocked; never implement on main without admission
4. release remains human; complete needs verifier

Ref: `skills/beacon/references/git-worktree-execution-flow.md`

