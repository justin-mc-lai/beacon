# Change Record: beacon-loop-goal-closed-loop-orchestrator

- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- change_reason: `goal-delivery-orchestrator-from-utterance-to-stable-closure`
- artifact_role: `change_record_not_requirement_truth`
- truth_source: `false`
- parent_feature: `beacon-loop-native-runner-and-automation-retirement`
- user_decision: `accepted`

## Rationale

用户确认：下一代 `beacon-loop goal "<用户原话>"` 不应仅绑定已冻结 feature truth 后进入 implement loop，而应从**用户目标原话**出发：

1. 洞悉**确定性意图**（`intent-contract`）
2. 自动触发 **planner multi-agent review**
3. 识别并补齐 **Beacon requirement truth**（truth_fill 子链）
4. 编排 **implement → import-evidence → qa → release** 全链
5. 支持长任务 **resume / stop / repair**，稳定交付且不静默 MVP 化

`beacon-loop-native-runner-and-automation-retirement` 已 frozen，覆盖 AC-001..AC-030（runner、harness、E2E import→qa 契约）。该包定义的是 **execution runner**，未定义 **utterance-driven delivery orchestrator**。

Planner review 与 prior 对话已判定：把 plan 意图直接落成 MVP 骨架是漂移根因；本 change 通过 **intent capture + review gate + truth_fill gate + delivery state machine** 在 loop 入口阻断。

## Scope Change

| Before（parent frozen truth） | After（本 feature draft） |
|------------------------------|---------------------------|
| `goal` 必须先 `truth-map resolve` pass | `goal` 可从 utterance 启动；resolve blocked 进入 `truth_fill` |
| `slugify(goal)` 可隐式猜 feature | utterance 与 feature slug **解耦**；feature 由 intent contract + resolver 决定 |
| 闭环止于 import→qa 契约（AC-030） | **delivery 模式**自动 invoke qa/release；QA fail 可回灌 implement |
| runner state machine only | 扩展 **Delivery Loop** state machine（intent→review→truth→implement→eval） |
| 无 intent/review runtime 落点 | 必填 `intent-capture.json`、`intent-contract.json`、`review-artifact.json`、`delivery-state.json` |

## Relationship to Parent Feature

本 feature **扩展** `beacon-loop-native-runner-and-automation-retirement`，不替换其 AC-001..AC-030：

- Parent：TypeScript runner、ledger、harness、agent adapters、implementation loop 语义
- This feature：goal 入口的 **Delivery Orchestrator**（AC-031..AC-039）

实现依赖 parent Phase A-D 能力；本 feature Phase E-H 在 parent 之上叠加。

## R4 Revision（2026-06-11）

- **change_reason**: `R4-pivot-beacon-run-gnhf-agent-orchestration`
- **user_decision**: accepted
- **drill evidence**: 模板 truth_fill 过 gate 但语义空洞；需 gnhf 全迭代 agent + prompt 内 Beacon 生命周期编排

| 决策 | R3（beacon-loop） | R4（beacon-run） |
|------|-------------------|------------------|
| 主实现包 | `packages/beacon-loop` delivery FSM | `packages/beacon-run`（gnhf fork） |
| LLM 介入 |  mainly implement_loop | **每轮 iteration**（truth + generate + repair） |
| truth 冷启动 | 默认 prd-bootstrap 模板链 | 默认 **agent truth phase**；模板仅 fallback |
| R3 代码 | 继续开发 | 冻结备份 `beacon-loop.r3-backup-20260610` |
| CLI 主入口 | `beacon-loop goal` | `beacon-run run`（loop 委托 deprecated） |

新增 AC-053..AC-060；Phase K tasks TASK-080..087。

## R5 Revision（2026-06-11）

- **change_reason**: `R5-worktree-harness-root-clarity-smoke-exit`
- **revision_id**: R5（previous R4 frozen）
- **user_decision**: accepted（planner review REV-101..103 + 用户确认同一 revision；保留 merge `go-todo-crud-smoke` 材料）
- **planner_review_ref**: go-todo-crud-smoke drill；truth-promotion 主仓 path 错位；requirement_clarity inline_marker 假阳性

| ID | 问题 | R5 承诺 |
|----|------|---------|
| REV-101 | worktree agent 写 truth，harness 对主仓 sync | **AC-061** harness projectRoot = worktree |
| REV-102 | slug `go-todo-crud-smoke` 触发 TODO inline_marker | **AC-062** clarity 词界/上下文过滤 |
| REV-103 | smoke 仍要求 sync-materials/freeze | **AC-063** smoke truth exit 轻量化 |
| REV-104 | phases_completed 误导 | **AC-064** phase_promoted + 失败可见 |

**Merge 决策**：worktree 产出的 `docs/beacon/v1.6.0/features/go-todo-crud-smoke/*`、`research/go-todo-crud-smoke.md`、`qa/test-cases/go-todo-crud-smoke.md` 并入主仓，作为 R5 E2E 夹具（draft，非 orchestrator 子 feature truth）。

Phase L tasks TASK-089..095；tests TC-063..TC-067。

## R6/R7 Revision（2026-06-11）

- **change_reason**: `R6-truth-freeze-gate-harness-AC-063-068-reconcile`
- **revision_id**: R7（R6 scope；Beacon revision counter）
- **user_decision**: accepted（planner review REV-FREEZE-001..004；用户确认 generate 不得在 draft truth 下写产品代码）
- **planner_review_ref**: post-R5 go-todo-crud-smoke drill；`revision_not_frozen` 12-iteration 空转

| ID | 问题 | R6/R7 承诺 |
|----|------|------------|
| REV-FREEZE-001 | beacon-run 无 truth_freeze_gate | **AC-068** harness freeze gate + generate entry frozen check |
| REV-FREEZE-002 | AC-063 与 AC-035 分裂 | **AC-063 reconcile**：smoke 跳过 sync-materials，**不**跳过 freeze |
| REV-FREEZE-003 | truth phase 不允许 freeze CLI | **AC-068** phase-prompt allowed harness |
| REV-FREEZE-004 | implement preflight 空烧 iteration | **AC-068** demote + cutover repair route |

Phase M tasks TASK-096..100；tests TC-068..TC-070；TC-065 断言更新。

## R2 Revision（2026-06-10）

- **change_reason**: D-010 默认 LLM intent tie-break + green-light 非打断；撤销 D-009/D-011 accepted defer
- **revision_id**: R2（previous R1）
- **user_decision**: accepted

| ID | R1 | R2 |
|----|----|-----|
| D-009 | accepted defer 串行 review | **rejected** → AC-041 in scope |
| D-010 | accepted defer 规则停等 | **rejected** → AC-040 in scope |
| D-011 | accepted defer AskUser/CLI flags | **rejected** → AC-042 lifecycle auto-route |

## Accepted Deferrals（R1 — superseded by R2）

| ID | Capability | Decision | Revisit |
|----|------------|----------|---------|
| D-009 | 并行 review lane 真多进程（非 subprocess 串行） | ~~`accepted`~~ **rejected R2** | AC-041 |
| D-010 | LLM tie-break 意图分类（默认仅规则确定性） | ~~`accepted`~~ **rejected R2** | AC-040 |
| D-011 | 交互式 `AskUserQuestion` 门控 UI（CLI 先用 flags） | ~~`accepted`~~ **rejected R2** | AC-042 |

R2 起 **无 accepted defer**；未实现能力以 AC-040..042 + parity matrix `missing` 跟踪。

## Non-Deferrals（must land in this feature truth）

- AC-031..AC-042 全部进入 package truth / tests
- Delivery Loop State Model + illegal transition 测试
- Deterministic intent classification contract
- Automatic planner review artifact 落盘
- truth_fill 子链（经 Beacon generator CLI，loop 不直写 truth）
- truth frozen gate before implement_loop
- delivery 模式 qa/release invoke + QA fail 回灌
- E2E utterance → release（verdict 来自 Beacon evaluator）

## Promotion Diff

进入 `features/beacon-loop-goal-closed-loop-orchestrator/` 的新增承诺：

- `Scope Mode` = `full_parity`（delivery orchestrator 层）
- `Intent Contract Schema`
- `Delivery Loop State Model`
- `Orchestrator Modes`（delivery / execute-only / intent-only / review-only）
- `Truth Fill Subchain Contract`
- `Parent Feature Dependency Matrix`
- AC-031..AC-042 与 tests/tasks Phase E-I

## R3 Revision（2026-06-10）

- **change_reason**: `gnhf-harness-worker-parity` — beacon-loop 须完整对齐 gnhf「Skill→CLI 编排→Worker」模型，且 Worker 面为 Beacon harness CLI（pln/gen/eval），implement 子循环经 `beacon implement run`，禁止裸 `codex exec` bypass
- **revision_id**: R3（previous R2）
- **user_decision**: accepted（用户确认进入 `beacon-gen-change`）
- **planner_review_ref**: R3 parity matrix F-101..F-108（gnhf + harness orchestration gap）

| 层级 | gnhf 对标 | R2 现状 | R3 承诺 |
|------|-----------|---------|---------|
| Host skill | `gnhf/SKILL.md` launch/steer/companion | 无一等 loop host skill | AC-043 agent surface |
| CLI 编排 | `gnhf` unified entry | `beacon-loop goal` ✅ | 保持 |
| Worker 契约 | `codex exec --json --output-schema` | 裸 `exec --skip-git-repo-check` | AC-045..AC-046 |
| Implement worker | Codex 通用 coding agent | 裸 codex，未接 harness | **AC-044** `beacon implement run` |
| Delivery harness 路由 | N/A（gnhf 单 worker） | truth/qa 用 beacon CLI；implement bypass | **AC-048..AC-049** stage→worker 表 |
| No-op / QA 门控 | no-op=false；halt | rollback 有，仍进 QA | **AC-047** |
| 真 E2E | 真 codex + commit | fixture 可 green，真跑空转 | **AC-051** |

R3 **无新 accepted defer**；D-012「子进程读 Skill MD」为 **blocked**（与 v1.6 harness taxonomy 冲突）。

## Next Route

1. ~~用户审阅本 change + truth/tests 草案~~（R1/R2 已完成）
2. ~~**R3**：审阅 truth/tests Phase J~~ → refrozen
3. ~~**R4**：beacon-run gnhf fork~~ → refrozen
4. **R5（当前）**：审阅 truth/tests Phase L（AC-061..064）→ `beacon-gen-implement` Phase L → `beacon change ... --refreeze-chain`
5. `beacon-eval-qa` + opt-in TC-067（go-todo-crud-smoke E2E）
