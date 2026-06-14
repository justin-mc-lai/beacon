---
slug: beacon-loop-goal-closed-loop-orchestrator
version: v1.6.0
status: frozen
revision_id: R10
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md
  user_story: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md
  test_case: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parent_feature: beacon-loop-native-runner-and-automation-retirement
---

# 需求真相：Beacon Loop Goal Closed-Loop Orchestrator

## 概述

`beacon-loop-goal-closed-loop-orchestrator` 定义 Beacon v1.6.0 **长任务交付入口**：从用户原话到稳定闭环，**以 gnhf 类 agent 迭代环为执行内核**，Beacon 生命周期与 Skills 边界写入 **iteration prompt + 阶段 harness**，不由模板 CLI 冒充 LLM 推理。

在 `beacon-loop-native-runner-and-automation-retirement`（AC-001..AC-030，frozen）之上：

- **R1–R3** 已在 `packages/beacon-loop` 验证 delivery FSM、harness 记账、gnhf prompt/schema 契约（快照：`packages/beacon-loop.r3-backup-20260610`）。
- **R4（frozen）** 将 **主实现落点** 迁至 **`packages/beacon-run`**（gnhf lineage，源副本 `packages/gnhf`），`beacon-loop` **降级为兼容/只读参考**，不再作为新功能开发面。
- **R5（frozen）** 修复 R4 drill 暴露的 **worktree harness root 错位**、**requirement_clarity TODO 假阳性**、**smoke truth exit 过重**；保留 worktree 产出的 `go-todo-crud-smoke` 材料作为 R5 回归夹具（merge 入主仓，见 Source Advisory）。
- **R6/R7（frozen）** 闭合 **truth_freeze_gate**：R5 drill 在 draft truth 下 promote 到 `generate`，导致 `implement run` **`revision_not_frozen`** 空转；用户确认 **generate 阶段不得在 truth 仍为 draft 时写产品代码**；beacon-run 须在 truth→generate 间 fail-closed 执行 freeze gate（对齐 AC-035 与 beacon-loop 参考实现）。
- **R9（frozen）** change refreeze 事务：`v1.6.1止血` 意图进入 governed change 链；revision 标记与 machine projection 对齐（无新增 AC 正文）。
- **R10（本 revision，draft→freeze）** **v1.6.1 止血 patch**：在 R6/R7 之上闭合三条 Loop Engineering 对齐能力——**worktree+freeze 不断链**、**state spine 文档+查询**、**stop-when 挂钩可执行检查**（禁止 agent 自说自话判 done）。semver **v1.6.1** 为交付标签；requirement 仍落在 **v1.6.0 docs line** 本 feature package。

R4 目标数据流：

```text
utterance
  → intent capture + intent-contract（可保留轻量 FSM 或并入 run package）
  → beacon-run（gnhf Orchestrator）多轮 iteration
        每轮：codex | claude | opencode | acp:* + Beacon phase prompt
        迭代间：beacon harness（resolve / freeze / qa / release invoke）
  → terminal_closed（Beacon evaluator only）
```

Beacon 主生命周期不变：

```text
plan -> truth -> generate -> evaluate -> release
```

长任务执行器 **不** 替代上述阶段权威；它在 **每一轮 agent 调用** 中携带当前阶段剧本，在 **迭代间隙** 调用 harness gate。

### R4：Beacon Run（gnhf 内核）+ Beacon 生命周期 prompt 编排

```text
Layer 0 — Host
  using-beacon / beacon-run skill（launch / steer / companion）
    ↓
Layer 1 — 长任务 CLI（gnhf lineage）
  beacon-run run | resume | stop | runs * | doctor
  （可选兼容别名：beacon-loop goal → 委托 beacon-run，deprecated）
    ↓
Layer 2 — gnhf Orchestrator（每轮都调 agent）
  iteration-prompt + output-schema + notes + git commit/rollback
  agent adapters: codex | claude | opencode | acp:*
    ↓
Layer 3 — Beacon phase digest（写入 prompt，不读 Skill MD）
  当前阶段：plan | truth | generate | evaluate
  允许：beacon-pln-* / beacon-gen-* / beacon-eval-* 职责摘要
  禁止：自证 QA/release、直写 package truth、placeholder 闭环
    ↓
Layer 4 — Harness checkpoints（迭代间 subprocess）
  beacon truth-map resolve | freeze | implement run | qa run | release create
  证据：truth-promotion.json / run evidence（machine-readable）
```

**R4 硬约束**

- **禁止** 默认冷启动路径仅用 `prd-bootstrap` + 模板 `brainstorm` 作为「语义 truth」（AC-056）；模板链仅可作 **harness 回退**，非默认。
- **禁止** 子进程读取 Skill MD 假装执行（D-012）。
- **禁止** 长任务 runner 产出 formal QA/release verdict；evaluator 唯一。

**R3 保留契约（在 beacon-run 中继承）**：`output-schema` strict parse、no-op=false、禁止 agent 自 commit、zero-commit 不得进入 qa_pending。

## Scope Mode

`scope_mode` = **`full_parity`**（delivery orchestrator 层）：

- 用户原话中的能力请求必须在 `intent-contract` + `review-artifact` 中可追溯
- 任何从 full delivery 闭环到「仅 implement stub」的降级必须进入 `Deferral Ledger` 并获用户显式接受
- R2 撤销 D-009..D-011 的 **accepted defer**；D-010 升格为 in-scope（AC-040）；D-009/D-011 改回 in-scope 承诺（见 Parity Matrix / Deferral Ledger）
- **R3** 扩展 **gnhf worker 契约 + Beacon harness implement 路由**（AC-043..AC-052）；与 parent `full_parity` runner 语义合成，不得 silent 保留裸 codex 路径

## 背景

### 问题

1. Parent feature 要求 resolve pass 才能 `goal`，但用户常从**未冻结 truth** 的自然语言目标启动
2. `slugify(goal)` 隐式猜 feature，易造成 intent 漂移与 MVP 骨架化
3. AC-030 E2E 止于 import→qa 驱动，未编排 **truth 补齐** 与 **qa fail 回灌**
4. `beacon-pln-review` 的 intent/parity 契约未在 loop 入口强制执行
5. **R3**：`implement_loop` 使用裸 `codex exec`，未对齐 gnhf `output-schema` 契约，也未经 `beacon implement run` harness worker（真跑可 success 但 0 commit）
6. **R4（drill 证据）**：模板 `truth_fill` 5s 过 gate 但 truth 空洞；LLM 仅在 implement 单层介入，与「一句话复刻」意图偏离——需 gnhf 全迭代 + prompt 内 Beacon 编排
7. **R5（go-todo-crud-smoke drill）**：`beacon-loop goal` + `--worktree` + `--beacon` 时 agent 在 worktree 写 truth，但 truth exit harness 对 **主仓** 跑 `sync-materials` → `test_case_sync_failed`；agent 死磕 `freeze` 又被 slug/path 中 `TODO` 的 `inline_marker` 误杀；`scope_mode: smoke` 仍绑定 full sync/freeze 链，无法进入 `generate`
8. **R6 drill 根因（post-R5）**：truth exit 仅 `resolve`/`sync-materials` **未执行 freeze** 即 promote 到 `generate`；agent 在 draft truth 下写 Go CRUD 代码；`generate` exit `implement run` 反复 **`revision_not_frozen`** / **`legacy_cutover_required`**，12 iteration cap 空转

### 依赖

本 feature **扩展** parent，不替换：

| Parent | This feature |
|--------|--------------|
| AC-001..AC-030 runner/harness/E2E | AC-031..AC-052 delivery + harness（R3 已完成于 beacon-loop 备份） |
| `packages/beacon-loop`（R3 快照） | R4 主实现迁至 `packages/beacon-run`（gnhf fork） |
| `.beacon/loop/runs/<id>/` 或 gnhf run dir | 统一 run evidence 契约 |

## Parent Feature Dependency Matrix

| Parent AC | 本 feature 依赖说明 |
|-----------|---------------------|
| AC-003 goal entrypoint | 保留；扩展 `--mode` |
| AC-004..AC-005 resolver | 扩展：blocked 时进入 truth_fill，非仅 abort |
| AC-016..AC-021 orchestrator | `implement_loop` 子状态复用 |
| AC-022..AC-025 ledger/diagnose | delivery-state 写入同一 ledger |
| AC-030 E2E import→qa | 扩展为 AC-039 全链 E2E |

## Command Contract

**R4 主入口（权威）**：

```bash
beacon-run run "<utterance>" [options]
# 或 stdin / --prompt-file；agent: --agent codex|claude|opencode|acp:...
```

**兼容入口（deprecated，R4 Phase K 实现委托）**：

```bash
beacon-loop goal "<utterance>" [options]
```

`beacon-loop` modes（`--mode`，默认 `delivery`）在 R4 中 **映射** 为 beacon-run phase preset，而非独立 FSM 实现：

| Mode | 行为 |
|------|------|
| `delivery` | 全链：intent → review → truth_fill（条件）→ implement → import → qa → release invoke |
| `execute-only` | 仅 implement_loop；**必须** frozen truth + `--feature` |
| `intent-only` | 只写 intent-capture + intent-contract |
| `review-only` | intent + planner review artifact，不实现 |

Green-Light 默认策略（R2 / AC-040）：

- **默认一律绿灯、尽可能不打断**：`delivery` 模式不因规则 classifier 的 `ambiguous`  alone 进入 `user_decision_pending`。
- 规则 classifier（AC-032）仍 deterministic；当 confidence 低或 `ambiguous=true` 时，**默认**走 LLM intent tie-break（见下）并 **continue**。
- 仅 **hard stop** 允许打断：`intent_drift` 未 `--ack-intent-drift`、P0 planner finding（truth authority / illegal scope cut）、illegal state transition、repair cap、truth frozen gate fail。
- planner review `synthesis.recommended_route` 与 Beacon lifecycle route（如 `truth_fill` / `implement_loop`）为 **默认续跑依据**；不要求交互式 AskUser UI。

人机门控 flags（**opt-in strict**，非默认打断）：

```bash
--strict-interrupt      # opt-in：恢复 P0/P1 停等（等价旧 --ask-on P0,P1 严格模式）
--ask-on P0,P1          # deprecated alias；默认 delivery 不启用
--ack-intent-drift      # utterance 与 frozen intent_snapshot 冲突时必须显式确认（hard stop）
--feature <slug>        # 显式 feature；禁止仅靠 slugify(utterance)
```

移除 `--auto-decide deferrals` 作为 ambiguous 默认门控；deferral ledger 中 **无** `user_decision=accepted` 的 scope cut 不得 silent 继续（与 AC-034 一致）。

## Intent Contract Schema

`intent-contract.json` 为 runtime 权威（非 package truth），但必须 deterministic 且可审计。

必填字段：

```json
{
  "schema_version": "1.0",
  "utterance": "<verbatim>",
  "intent_class": "delivery_closed_loop | research | patch | execute_bound",
  "scope_mode": "full_parity | mvp | patch | research | brownfield_takeover | compatibility_only",
  "closure_shape": {
    "requires_truth": true,
    "requires_implementation": true,
    "requires_qa": true,
    "requires_release": true
  },
  "capability_requests": [],
  "strong_intent_signals": [],
  "feature_slug": "<string>",
  "version": "v1.6.0",
  "determinism": {
    "classifier": "beacon-loop-intent-v1",
    "rules_hash": "<sha256>",
    "confidence": 0.0,
    "ambiguous": false
  }
}
```

分类规则（确定性，AC-032）：

| 信号 | `intent_class` | `scope_mode` |
|------|----------------|--------------|
| 闭环 / 交付 / 验收 / release / truth 补齐 | `delivery_closed_loop` | 默认 `full_parity` |
| 完整复刻 / 做全 / 不要 MVP / parity | — | `full_parity` |
| 仅修 bug / hotfix | `patch` | `patch` |
| 调研 / 探索 / brainstorm | `research` | `research` → route `beacon-pln-brainstorm`，不进入 implement |
| frozen truth + 只跑实现 | `execute_bound` | 继承 truth `scope_mode` |

`ambiguous=true` 时 **不得** 因 ambiguous alone 进入 `user_decision_pending`；须走 AC-040 LLM tie-break 并默认 continue。`user_decision_pending` 仅用于 hard stop 后的显式恢复或 opt-in strict 模式。

## Runtime Artifact Contract

Run 目录扩展（相对 parent）：

```text
.beacon/loop/runs/<run-id>/
  intent-capture.json       # utterance + normalized + captured_at
  intent-contract.json      # deterministic intent package
  review-artifact.json      # planner multi-agent output
  truth-promotion.json      # truth_fill 子链记录（CLI calls, exit codes）
  delivery-state.json       # Delivery Loop state machine
  run-package.json          # parent 字段 + delivery_mode + intent_refs
  ... (parent artifacts)
```

`runtime_json_role` 必须为 `runtime_process_record`，**不是** requirement truth。

## Delivery Loop State Model

`state_machine_required`: **true**

本 state machine **包含** parent runner 状态作为子图 `implement_loop`。

### States

| State | 含义 |
|-------|------|
| `intent_capture` | 写入 intent-capture + intent-contract |
| `intent_review` | 运行 planner review runtime |
| `user_decision_pending` | hard stop 或 opt-in strict 后等待用户恢复（**非** routine ambiguous） |
| `truth_gap_scan` | resolve + parity 缺口扫描 |
| `truth_fill` | 编排 beacon gen-truth / gen-change / refreeze |
| `truth_freeze_gate` | 等待 frozen truth |
| `implement_loop` | parent orchestrator 活跃（子状态见 parent truth） |
| `evidence_import` | import-evidence 子进程 |
| `qa_pending` | beacon qa run 已 invoke，等待 verdict |
| `release_pending` | beacon release 已 invoke，等待 verdict |
| `repair_from_qa` | QA fail，回灌 implement_loop |
| `terminal_closed` | Beacon qa+release 闭环完成 |
| `terminal_aborted` | 用户 abort 或不可恢复 cap |

### Allowed Transitions

```text
intent_capture -> intent_review
intent_review -> truth_gap_scan | user_decision_pending | terminal_aborted
user_decision_pending -> intent_review | truth_gap_scan | terminal_aborted
truth_gap_scan -> truth_fill | implement_loop | terminal_aborted
truth_fill -> truth_freeze_gate
truth_freeze_gate -> implement_loop | truth_fill(retry) | terminal_aborted
implement_loop -> evidence_import | cap_reached(parent) | terminal_aborted
evidence_import -> qa_pending
qa_pending -> release_pending | repair_from_qa | terminal_aborted
repair_from_qa -> implement_loop
release_pending -> terminal_closed | repair_from_qa | truth_fill(route change)
```

### Invalid Transitions

- `intent_capture` → `implement_loop`（禁止跳过 review）
- `truth_gap_scan` → `implement_loop` 当 truth 未 frozen（AC-035）
- `implement_loop` → `terminal_closed`（禁止 loop 自证完成）
- `qa_pending` → `terminal_closed` 未经 Beacon release 面
- 任意状态 → 直接写 `features/*/truth.md`（禁止 loop 直写 truth）

### Side Effects

| Transition | Artifacts |
|------------|-----------|
| `intent_capture` | `intent-capture.json`, `intent-contract.json` |
| `intent_review` | `review-artifact.json` |
| `truth_fill` | `truth-promotion.json` 追加 CLI 记录 |
| `truth_freeze_gate` | `delivery-state.json` 记录 frozen refs |
| `qa_pending` | 记录 `beacon qa` command + stdout JSON path |
| `release_pending` | 记录 `beacon release` command + stdout JSON path |
| `terminal_closed` | `summary.md` 含 beacon verdict refs，非 loop verdict |

## Automatic Planner Review Contract

`delivery` 与 `review-only` 模式必须调用 Beacon planner review runtime（AC-033）：

- 实现落点：`beacon/utils/planner_review_runtime.py` 或等价 CLI subprocess
- 产出 `review-artifact.json`，必填：
  - `intent_snapshot`
  - `scope_mode`
  - `parity_matrix`（当 source/parity 信号存在）
  - `deferral_ledger`
  - `findings` + `synthesis.recommended_route`
  - `runtime_evidence_only: true`
  - `formal_verdict_authority: false`

Review gate：

- P0 finding → **hard stop**（`terminal_aborted` 或需 `--ack-intent-drift` / explicit strict flag）
- P1 finding → **默认 green-light continue**；写入 `review-artifact.json` 与 `notes.md`，由 `recommended_route` 驱动下一跳（truth_fill / implement_loop 等）
- `deferral_ledger` 含 `user_decision: pending` → block `truth_fill` / `implement_loop`（scope cut 仍须用户主权）
- `scope_mode=full_parity` 且 parity missing 无 accepted defer → route truth_fill

## LLM Intent Tie-Break Contract（AC-040）

当 `intent-contract.json` 中 `determinism.ambiguous=true` 或 `determinism.confidence` 低于 tie-break 阈值时：

1. loop 调用 **LLM intent tie-break** adapter（subprocess 至 Beacon 或 host LLM surface；**不得**写 package truth）
2. 落盘 `intent-tiebreak.json`，必填：
   - `utterance`、`rules_classifier_output`、`llm_resolution`（`intent_class`、`scope_mode`、`feature_slug` 建议）
   - `confidence`、`rationale_summary`（审计用，非 formal verdict）
   - `tiebreak_authority: llm_default_green_light`
   - `runtime_evidence_only: true`
3. 合并结果写回 **runtime** `intent-contract.json` 的 `tiebreak` 字段；`rules_hash` 不变
4. **默认** `transition → truth_gap_scan`（continue）；**禁止**仅因 ambiguous 进入 `user_decision_pending`

Hard stop 例外（不打 green-light）：

- LLM tie-break 失败且 strict 模式
- P0 planner finding
- `intent_drift` 未 ack
- 用户显式 `--strict-interrupt`

## Truth Enrichment Contract（R4 取代默认模板 truth_fill）

当 `truth-map resolve` blocked 或 review 判定 truth gap（AC-034、AC-056）：

**默认路径（R4）**

1. `beacon-run` 进入 **truth phase** iteration（agent bin 执行）
2. iteration prompt 含：utterance、OSS/source refs（若 utterance 含 repo）、parity/state-machine 义务、禁止直写 package truth
3. agent 产出 research/parity 材料 → host 或 harness 写回 **经 gen-truth 路由** 的受治理面
4. 迭代间 harness：`beacon truth-map rebuild-machine`、`beacon freeze` 等；记入 `truth-promotion.json`
5. frozen 后 `resolve` pass 才进入 generate phase

**回退路径（非默认）**

- `beacon prd-bootstrap` / 模板 `brainstorm` 仅当 `--truth-bootstrap=fallback` 或 doctor 明示缺 agent backend 时启用；不得作为 drill 默认。

禁止 silent MVP：不得默认 `scope_mode=mvp` 除非 `deferral_ledger` 有 `user_decision=accepted`。

## Delivery Mode Evaluator Chain

`--mode delivery` 在 `implementation_candidate` 后自动（AC-036）：

```bash
beacon-loop import-evidence <run-id>
beacon qa run <feature> --project . --version v1.6.0 --json
beacon release create/check ... --json
```

Loop output 必须包含：

```json
{
  "closure_verdict": "not_provided_by_beacon_loop",
  "beacon_qa_verdict_ref": "<path or embedded summary>",
  "beacon_release_verdict_ref": "<path or embedded summary>",
  "delivery_state": "<machine_state>"
}
```

QA fail（AC-037）：`qa_pending` → `repair_from_qa` → `implement_loop`，将 qa findings 注入 `notes.md`，直至 cap 或 qa pass。

## Harness Stage Worker Routing Contract（R3 / AC-048）

`implement_loop` 与 delivery 各 stage 必须通过 **frozen worker 路由表** 调用 Beacon harness CLI，不得硬编码裸 agent spawn（实现可读 `beacon/utils/project_skills.py` registry 或等价 frozen JSON）。

| Delivery state / sub-loop | Harness | Worker command（权威形态） |
|---------------------------|---------|---------------------------|
| `intent_review` | pln | `beacon planner-review run <feature> --project … --json` |
| `truth_fill` / `truth_freeze_gate` | gen-truth | `beacon prd-bootstrap` / `beacon truth …` / freeze 链（见 Truth Fill Subchain） |
| **`implement_loop`** | **gen-implement** | **`beacon implement run "<feature>" --project … --version … --runner <runner> --json`** |
| `repair_from_qa` → implement | gen-implement | 同上；notes 含 qa findings |
| `qa_pending` | eval | `beacon qa run … --json` |
| `release_pending` | eval-release | `beacon release create … --json` |

默认 `--runner`：`codex-subagents`（可经 `~/.beacon-loop/config.yml` 或 CLI 覆盖，但 **不得** 回退为 loop 内裸 `codex exec`）。

`truth-promotion.json` 与 run artifacts 必须记录 **实际 worker command**（含 runner id）。

## Gnhf Worker Parity Contract（R3 / AC-045..AC-047）

对齐 `kunchenguid/gnhf` 的 Codex worker 语义（经 implement runner 或统一 adapter 暴露）：

1. 每 run 写入 `output-schema.json`（与 gnhf `buildAgentOutputSchema` 等价字段：`success`, `summary`, `key_changes_made`, `key_learnings`, optional `should_fully_stop`）
2. Codex/implement worker 调用须带 **`--json` + `--output-schema <path>`**（或 implement runner 内部等价）
3. **Iteration prompt** 须 gnhf 级：`notes.md` 只读、禁止 agent commit、no-op（无 diff 且无 meaningful learnings）= **`success: false`**
4. stdout 解析 **strict**：无法 schema 校验则 iteration failure，不得 loose parse 为 success
5. **Delivery hard gate（AC-047）**：no-op iteration 或 zero commit 时 **禁止** `implement_loop` → `evidence_import` / `qa_pending`；须 `iteration_fail_rollback` 或 cap，且 `delivery-state` 记录 `reason_code=implement_no_op_blocked`

Parent runner AC-016..AC-019 语义在 implement 路径上 **不得弱于** gnhf。

## Source Capability Inventory

| 能力 | 源证据 | 落点 |
|------|--------|------|
| utterance intent classification | `intent_router.py` + `planner_review_runtime.py` | `packages/beacon-loop/src/intent/` |
| multi-agent review | `beacon-pln-review` + compound-parity | `review-artifact.json` |
| delta truth change | OpenSpec changes/specs 模式 | `truth-promotion.json` |
| phase-gated truth | Spec Kit | truth_fill 顺序 |
| plan/execute split | gstack plan modes | `--mode` |
| runner loop | parent gnhf parity | `implement_loop` 子状态 |
| qa fail retry | gstack qa loop | `repair_from_qa` |
| **gnhf Host skill** | `skills/gnhf/SKILL.md` | **AC-043** agent surface / using-beacon |
| **gnhf codex schema** | `gnhf/src/core/agents/codex.ts` | **AC-045** output-schema + strict parse |
| **gnhf iteration prompt** | `templates/iteration-prompt.ts` | **AC-046** runner prompt template |
| **Beacon implement runner** | `beacon implement run --runner codex-subagents` | **AC-044** implement_loop worker |
| harness registry | `project_skills.builtin_skill_registry` | **AC-048** stage worker routing |

## Parity Matrix

| Source capability | Target truth | Target tests | Target evidence | Status | Deferral |
|-------------------|--------------|--------------|-----------------|--------|----------|
| parent runner AC-001..030 | parent truth | parent tests | parent evidence | covered | none |
| intent capture verbatim | AC-031 | TC-031 | intent-capture.json | **implemented R2** | none |
| deterministic classify | AC-032 | TC-032 | intent-contract.json | **implemented R2** | none |
| auto planner review | AC-033 | TC-033 | review-artifact.json | **implemented R2** | none |
| truth_fill on resolve blocked | AC-034 | TC-034 | truth-promotion.json | **implemented R2** | none |
| frozen gate before implement | AC-035 | TC-035 | delivery-state.json | **implemented R2** | none |
| delivery qa/release invoke | AC-036 | TC-036 | summary.md | **implemented R2** | none |
| qa fail repair loop | AC-037 | TC-037 | notes.md + delivery-state | **implemented R2** | none |
| delivery state resume | AC-038 | TC-038 | delivery-state.json | partial | none |
| full chain E2E | AC-039 | TC-039 | e2e script | partial | none |
| parallel review lanes | AC-041 | TC-043 | review-artifact.json | partial | none |
| LLM intent tie-break default green-light | AC-040 | TC-042 | intent-tiebreak.json | partial | none |
| Beacon lifecycle auto-route (no AskUser UI) | AC-042 | TC-044 | delivery-state.json | partial | none |
| **Host skill launch/steer/companion** | **AC-043** | **TC-045** | agent surface docs | **missing R3** | none |
| **implement via beacon implement run** | **AC-044** | **TC-046** | truth-promotion + iteration logs | **missing R3** | none |
| **output-schema + strict JSON** | **AC-045** | **TC-047** | output-schema.json | **missing R3** | none |
| **gnhf iteration prompt + no-op=false** | **AC-046** | **TC-048** | prompt.md | **missing R3** | none |
| **no-op blocks qa_pending** | **AC-047** | **TC-049** | delivery-state.json | **missing R3** | none |
| **harness stage worker routing** | **AC-048** | **TC-050** | worker-route.json | **missing R3** | none |
| **repair_from_qa harness worker** | **AC-049** | **TC-051** | truth-promotion.json | **missing R3** | none |
| **parent runner no regression** | **AC-050** | **TC-052** | npm test regression | **missing R3** | none |
| **doctor implement runner check** | **AC-052** | **TC-054** | doctor --json | **missing R3** | none |
| **真 implement runner E2E ≥1 commit** | **AC-051** | **TC-053** | e2e + git log | **missing R3** | none |
| **beacon-run truth_freeze_gate（beacon-loop parity）** | **AC-068** | **TC-068..070** | truth-promotion.json + beacon-phase.json | **missing R7** | none |

## Deferral Ledger

| deferral_id | capability | reason | impact | user_decision | expiry_or_revisit | recommended_route |
|-------------|------------|--------|--------|---------------|-------------------|-------------------|
| D-009 | （已撤销 defer）并行 review lane 真多进程 | R1 误 accept 串行替代 | 延迟真并行能力 | **rejected** | R2 implement | beacon-gen-implement |
| D-010 | （已撤销 defer）LLM 默认 tie-break | R1 误 accept 规则停等 | 打断 delivery 绿灯流 | **rejected** | R2 AC-040 | beacon-gen-implement |
| D-011 | （已撤销 defer）AskUserQuestion / CLI flag 主门控 | R1 解法偏离用户意图 | 人工 flag babysitting | **rejected** | R2 AC-042 | beacon-gen-implement |

R2 起：**不得**再将 D-009..D-011 作为 accepted defer 引用；未实现能力以 AC-040..AC-042 + parity matrix 跟踪。

| deferral_id | capability | reason | impact | user_decision | expiry_or_revisit | recommended_route |
|-------------|------------|--------|--------|---------------|-------------------|-------------------|
| D-012 | 子进程直接读 Skill MD 执行 | 与 v1.6 harness taxonomy 冲突 | 假 harness、无 HARD GATE | **blocked** | R3 | 使用 beacon CLI worker |
| D-013 | implement 继续裸 codex bypass | R2 真跑 0 commit | 假 delivery | **blocked** | R3 AC-044 | beacon-gen-implement |

## Delivery Phases

| Phase | 范围 | AC |
|-------|------|-----|
| E | intent capture/classify + delivery-state 骨架 + review subprocess | AC-031..AC-033 |
| F | truth_fill 子链 + truth_freeze_gate | AC-034..AC-035 |
| G | delivery mode qa/release + qa fail 回灌 | AC-036..AC-037 |
| H | resume delivery-state + parallel review + E2E | AC-038..AC-039 |
| I | R2 green-light intent + lifecycle auto-route | AC-040..AC-042 |
| **J** | **R3 gnhf worker 契约 + harness implement runner + no-op QA gate** | **AC-043..AC-052** |
| **K** | **R4 beacon-run（gnhf fork）+ 全迭代 agent + Beacon phase prompt + 非模板 truth** | **AC-053..AC-060** |
| **L** | **R5 worktree harness + clarity + smoke exit reconcile** | **AC-061..AC-064** |
| **M** | **R6/R7 truth_freeze_gate + AC-063 reconcile + generate frozen gate** | **AC-063, AC-068** |
| **N** | **R10 v1.6.1 止血：Loop Engineering 对齐（patch，非 v2）** | **AC-069..AC-071** |

Parent Phase A-D 必须先满足。Phase J 已在 `beacon-loop` R3 备份中落地。Phase K **以 `packages/beacon-run` 为主实现面**，可复用 R3 的 prompt/schema/evidence 契约与 `intent/` 薄适配层。

## Non-goals

- 替代 `beacon truth-map resolver`
- 新增 Beacon 主生命周期 stage
- loop 写 package truth 或 `.machine` requirement projection
- loop 声明 QA pass / release ready / feature complete
- 复制 manage-oss-sync OSS 镜像业务
- Mastra / LangGraph 作为主 runtime

## Acceptance Criteria

| AC ID | Acceptance Criteria |
|-------|---------------------|
| AC-031 | `beacon-loop goal "<utterance>"` 在 run 目录写入 `intent-capture.json`（verbatim utterance）与 `intent-contract.json`；不得丢失用户原话。 |
| AC-032 | 意图分类对相同 `utterance` + `rules_hash` 产出相同 `intent_class` 与 `scope_mode`；`determinism.rules_hash` 可复算。 |
| AC-033 | `delivery` 与 `review-only` 模式自动调用 planner review runtime，写入 `review-artifact.json`，含 `intent_snapshot`、`scope_mode`、`findings`、`runtime_evidence_only=true`。 |
| AC-034 | `truth-map resolve` blocked 或 review 判定 truth gap 时，进入 `truth_fill` 子链并记录 `truth-promotion.json`；禁止 silent MVP 降级。 |
| AC-035 | truth 未 frozen 时禁止进入 `implement_loop`；`execute-only` 模式必须 `--feature` 且 resolve pass。 |
| AC-036 | `--mode delivery` 在 implementation candidate 后自动 invoke import-evidence、beacon qa、beacon release；loop 输出 `closure_verdict=not_provided_by_beacon_loop` 与 beacon verdict refs。 |
| AC-037 | beacon qa fail 时进入 `repair_from_qa` 并回灌 `implement_loop`（findings 写入 notes），直至 cap 或 qa pass。 |
| AC-038 | `delivery-state.json` 记录 Delivery Loop 全状态；`resume` 可恢复；illegal transition 有测试阻断。 |
| AC-039 | E2E 契约：utterance → review artifact → truth frozen → implement → import → qa → release invoke；formal verdict 仅来自 Beacon evaluator。 |
| AC-040 | **Green-light LLM tie-break**：`delivery` 默认启用；规则 `ambiguous`/低 confidence 时写 `intent-tiebreak.json` 并 **continue**；不得仅因 ambiguous 进入 `user_decision_pending`；hard stop 仅限 intent drift 未 ack、P0 finding、illegal transition、cap。 |
| AC-041 | **并行 review lane**：planner review runtime `execution_mode=parallel_subagent_review`（或等价真并行）；`review-artifact.json` 含 per-lane evidence ref。 |
| AC-042 | **Beacon lifecycle auto-route**：无 AskUser UI；loop 消费 `review-artifact.synthesis.recommended_route` 与 Beacon gov route 续跑；`--strict-interrupt` 为 opt-in。 |
| AC-043 | **Host skill 对齐 gnhf**：agent surface（`using-beacon` 或等价）文档化 `beacon-loop goal` 的 Hands-Off / Companion launch、steer prompt 模板、hard stop 条件；Skill 给 Host 看，不进入 subprocess。 |
| AC-044 | **`implement_loop` harness worker**：必须 subprocess `beacon implement run "<feature>" … --runner <runner> --json`；loop **禁止**直接 `spawn codex exec`（测试与 doctor 可检测 bypass）。 |
| AC-045 | **output-schema 契约**：每 run 写 `output-schema.json`；worker 使用 `--output-schema` + strict JSON 校验；parse 失败 = iteration failure。 |
| AC-046 | **gnhf iteration prompt**：prompt 模板对齐 gnhf（notes 只读、no-op=false、验证后再 JSON、禁止 agent commit）；落盘 `prompt.md` / `iteration-*-prompt.txt`。 |
| AC-047 | **no-op delivery gate**：no-op iteration 或 zero commit 时禁止进入 `evidence_import` / `qa_pending`；`delivery-state` 记录 `implement_no_op_blocked`。 |
| AC-048 | **Harness stage worker 路由表**：frozen contract 映射 delivery state → harness → beacon CLI；`truth-promotion.json` 记录 worker command + runner id。 |
| AC-049 | **`repair_from_qa` harness 一致性**：回灌 `implement_loop` 时使用与 AC-044 相同 implement runner，不得回退裸 codex。 |
| AC-019 | **Parent failure backoff（继承 parent）**：`implement_loop` 复用 parent orchestrator AC-019：agent-reported failure 立即下一轮；retryable hard error 指数退避；连续失败达上限 abort；no-op iteration 计为 failure。 |
| AC-050 | **Parent runner 语义不回归**：接入 AC-044 后，parent AC-016..AC-019（多轮、caps、stop-when、notes、no-op failure）在 implement 路径仍 pass；delivery-state 与 runner state 合成正确。 |
| AC-051 | **真 implement runner E2E**：非 fixture-only 路径下，delivery 跑通且 worktree **≥1 commit** 后才允许 `qa_pending`（verdict 仍 Beacon evaluator）。 |
| AC-052 | **`beacon-loop doctor`** 检查 implement runner 可用性、Codex、`output-schema` 路径；`--diagnose` 给出 repair route。 |
| AC-053 | **`packages/beacon-run`** 自 `packages/gnhf` fork，保留 gnhf `Orchestrator` + `createAgent`（codex/claude/opencode/acp）；CLI `beacon-run run` 为 R4 主入口。 |
| AC-054 | **Beacon phase prompt**：每轮 iteration prompt 注入当前 Beacon 阶段、allowed/forbidden harness 命令、Skills 职责摘要（非 subprocess 读 MD）；落盘 `beacon-phase.json` + prompt 正文。 |
| AC-055 | **全迭代 agent backend**：truth/generate/repair 阶段均通过 agent adapter 执行；不得仅 implement 单层调 codex。 |
| AC-056 | **非模板 truth 默认**：冷启动默认走 agent truth phase；`prd-bootstrap` 模板链仅 `--truth-bootstrap=fallback`；drill utterance 须产出含 OSS/parity 信号的 research 而非纯脚手架 AC。 |
| AC-057 | **Harness 阶段检查点**：迭代间强制可记账 harness 调用（resolve/freeze/qa/release）；`truth-promotion.json` 含 phase + command + exit_code。 |
| AC-058 | **beacon-loop 降级**：`packages/beacon-loop` 冻结为 R3 参考；新 AC 实现于 `beacon-run`；`beacon-loop goal` 可委托 beacon-run（deprecated 文档化）。 |
| AC-059 | **Core CLI 契约对齐**：`beacon implement run` 支持 `--output-schema`（与 AC-045 一致）；branch/dirty preflight 错误须 doctor 可诊断。 |
| AC-060 | **真项目 drill E2E**：greenfield + utterance（gum choose/filter）经 beacon-run：≥1 agent iteration on truth、≥1 commit on generate、qa invoke；verdict 仅 Beacon evaluator。 |
| AC-061 | **Worktree harness project root**：`beacon-run --worktree --beacon` 时，truth/generate/qa/release harness subprocess 的 `--project-root` / `--project` **必须与 agent `effectiveCwd`（worktree）一致**；禁止对主仓跑 greenfield feature 的 `sync-materials` / `verify-context`；`truth-promotion.json` 记录的 command 须含 worktree 绝对路径。 |
| AC-062 | **Requirement clarity domain vocabulary**：`requirement_clarity` 的 `inline_marker`（TBD/TODO/??? 等）须用词界或上下文过滤，**不得**因 feature slug、路径、`canonical_refs` 行、frontmatter 中的合法领域词（如 `go-todo-crud-smoke`）误 block `freeze`；须含回归 fixture：`go-todo-crud-smoke` 材料完整时 clarity gate PASS。 |
| AC-063 | **Smoke truth exit（reconciled）**：当 target feature `scope_mode=smoke` 或 `minimal_smoke` 时，truth phase exit **不得**要求 `beacon doctor sync-materials`；但 **在 promote 到 `generate` 之前** 仍须通过 **`truth_freeze_gate`**（见 AC-068）：`truth-map resolve` PASS + `features/<slug>/truth.md` package ready + **`beacon freeze` PASS**。AC-035 对 smoke **无例外**。 |
| AC-064 | **Phase promotion visibility**：harness exit 失败时 `beacon-phase.json` 须区分 `phases_completed`（agent 迭代完成）与 `phase_promoted`（harness 放行）；TUI / `gnhf.log` 须输出结构化 `harness_exit_failed`（含 `reason_code`、command、exit_code）。 |
| AC-068 | **`truth_freeze_gate`（beacon-run）**：`packages/beacon-run` 在 truth→generate 间 **必须** fail-closed 执行 freeze gate，对齐 Delivery Loop `truth_freeze_gate` 与 beacon-loop `truth-fill` 末尾 `beacon freeze` 链。**禁止** draft truth 下 `phase_promoted=true` 或 agent 进入 `generate` 写产品代码。truth exit 序列：`resolve` →（full_parity：`sync-materials`）→（按需 `sync-requirement-clarity`）→ **`beacon freeze --json`**；失败时 `phase` 保持 `truth`，`reason_code=truth_not_frozen`。`generate` **entry** 须 `isFeatureTruthFrozen===true`，否则不得 `run_agent`。`generate` exit 若 preflight 为 `revision_not_frozen` 或 `legacy_cutover_required`，须 **phase demote** 到 truth freeze repair（可 harness 尝试 `beacon truth-cutover run … --apply`），**不得** 空烧 iteration cap。truth phase `allowed_harness` 须含 `beacon freeze`。`truth-promotion.json` 须记录 freeze/cutover command。 |
| AC-069 | **v1.6.1 — worktree+freeze 不断链（E2E）**：在 `go-todo-crud-smoke` 回归夹具上，`beacon-loop goal "<utterance>" --worktree --beacon --feature go-todo-crud-smoke --version v1.6.0` **必须** 完成：`truth-promotion.json` 内全部 harness 的 `--project-root`/`cwd` = worktree；**不得** 出现 `test_case_sync_failed`（主仓 sync）；**不得** 在 draft truth 下进入 `generate`；truth frozen 后 **必须** promote 到 `generate` 且 `implement run` **不得** 因 `revision_not_frozen` 空转。强化 AC-061 + AC-068 的 **real-project opt-in E2E**（`BEACON_RUN_E2E_GO_TODO=1`）。 |
| AC-070 | **v1.6.1 — state spine 文档+查询**：新增 execution 文档 `docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md` 定义 **单一 operator 进度账本**：权威文件（`beacon-phase.json`、`run-package.json`、`.beacon/loop/runs/<id>/`、`ledger`）与 **done / in_progress / next_action** 语义。CLI **`beacon-loop spine show [--run-id]`**（或等价 `status --spine`）输出 machine-readable JSON：`phase`、`phases_completed`、`phase_promoted`、`next_harness`、`authoritative_paths[]`、`run_id`；**不得** 要求 operator 手工拼四份 state 文件。 |
| AC-071 | **v1.6.1 — stop-when 可执行检查（maker≠checker）**：当 `--stop-when <condition>` 非空时，loop **禁止** 仅因 agent structured output / summary 自报「stop-when matched」而终止 iteration 环。每轮 agent 后 **必须** 至少执行一种 **外部可验证检查**：**(a)** 已配置的 harness gate（默认：`beacon qa run` 或 phase-appropriate harness）exit 0；**(b)** `--stop-check-cmd` 显式 shell 命令 exit 0；**(c)** lifecycle phase 已达 terminal harness（qa/release evaluator）。Agent 自报 alone → `reason_code=stop_when_unverified`，**continue** 下一 iteration 或进入 repair（不得 silent done）。对齐 [Loop Engineering `/goal`](https://addyosmani.com/blog/loop-engineering/)「写代码的人不能给自己打分 done」；**defer** 独立 judge 小模型至 v2（D-le-001）。 |

### Loop Engineering 对齐（R10 normative reference）

| Osmani 原语 | Beacon v1.6.1 落地 | AC |
|-------------|---------------------|-----|
| `/goal` run-until-verifiable-done | `beacon-loop goal` → `beacon-run` + phase harness | AC-039, AC-071 |
| Worktrees | `--worktree` harness root = agent cwd | AC-061, AC-069 |
| Skills | Host skills + phase digest（非 subprocess 读 MD） | AC-054, AC-043 |
| Sub-agents maker≠checker | pln/gen/eval/gov + harness subprocess | AC-033, AC-071 |
| State / memory spine | disk artifacts + **spine show** | AC-070 |
| Automations heartbeat | hooks（非 loop 包内 schedule） | non-goal；D-le-002 |

**scope_mode（R10）**：`patch` + `compatibility_only`。**Non-goals（R10）**：v2 Rust orchestrator、独立 judge 模型服务、Automations Tab 对等物。

### R5 Harness Contract（worktree + smoke）

```text
beacon-loop goal → beacon-run (--worktree --beacon)
  agent cwd = worktree
  harness ctx.projectRoot = worktree   # AC-061
```

### R6/R7 Harness Contract（truth_freeze_gate）

```text
truth agent iteration (package ready, should_fully_stop=true)
  → truth exit entry: resolve PASS + smokeTruthPackageReady (smoke only)
  → truth_freeze_gate harness:
      smoke:     resolve → sync-requirement-clarity (if needed) → freeze
      full_parity: sync-materials → sync-requirement-clarity (if needed) → freeze
      legacy:    truth-cutover run --apply --resume-intent implement (on cutover_required)
  → phase_promoted=true ONLY when isFeatureTruthFrozen===true
  → generate entry: frozen gate (fail-closed; no product code agent iteration if draft)
  → generate exit: implement run (requires frozen; demote on revision_not_frozen)

scope_mode reader: smoke | minimal_smoke → smoke path   # AC-063
requirement_clarity: domain slug/path tokens ≠ inline placeholder   # AC-062
```

**R5/R6 回归夹具**：`features/go-todo-crud-smoke` + utterance「在 examples/go-todo-crud 实现最小 Go HTTP CRUD…」；**须先 frozen** 再 generate；implement 完成后 ≥1 commit 于 `examples/go-todo-crud/`。

## Source Advisory

| Artifact | Role |
|----------|------|
| `docs/beacon/v1.6.0/change/beacon-loop-goal-closed-loop-orchestrator.md` | change record |
| `docs/beacon/v1.6.0/research/beacon-loop-goal-closed-loop-orchestrator.md` | promoted research |
| `features/beacon-loop-native-runner-and-automation-retirement/truth.md` | parent frozen truth |
| `features/beacon-pln-review-intent-parity-state-machine-v160/truth.md` | planner review contract |
| `packages/gnhf` | R4 工作副本（fork 为 `packages/beacon-run`） |
| `/Users/apple/Developer/Personal/oss-sync/agents/agent-systems/gnhf` | 上游对标 |
| `features/go-todo-crud-smoke/` | R5 回归夹具（worktree merge，smoke scope） |
| `docs/beacon/v1.6.0/research/go-todo-crud-smoke.md` | smoke drill research（support_advisory，已 accept merge） |

本文件为 package-authoritative requirement truth（**R8 revision frozen**，R6/R7 truth_freeze_gate scope）。
