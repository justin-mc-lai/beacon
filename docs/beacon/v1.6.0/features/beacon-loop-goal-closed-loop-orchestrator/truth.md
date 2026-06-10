---
slug: beacon-loop-goal-closed-loop-orchestrator
version: v1.6.0
status: frozen
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

`beacon-loop-goal-closed-loop-orchestrator` 定义 Beacon v1.6.0 下一代长任务入口：**从用户目标原话到稳定交付的全链编排**。

在 `beacon-loop-native-runner-and-automation-retirement`（AC-001..AC-030，frozen）提供的 **execution runner** 之上，本 feature 将 `beacon-loop goal "<utterance>"` 升级为 **Delivery Orchestrator**：

```text
utterance
  → intent capture + deterministic intent contract
  → automatic planner multi-agent review
  → truth gap scan + truth_fill (Beacon generator CLI)
  → implement_loop (parent orchestrator)
  → import-evidence → beacon qa → beacon release
  → terminal_closed (Beacon evaluator only)
```

`beacon-loop` 仍不产出 formal QA/release verdict，不直接写 package truth，不改变 v1.6.0 human-facing lifecycle：

```text
plan -> truth -> generate -> evaluate -> release
```

### R3：gnhf + Beacon Harness Worker 对齐模型

Beacon 适配 gnhf 三层，**不是**在子进程里加载 Skill MD：

```text
Layer 0 — Host
  using-beacon / beacon-loop host skill（launch / steer / companion）
    ↓
Layer 1 — CLI 编排器
  beacon-loop goal | resume | stop | runs * | doctor
    ↓
Layer 2 — Delivery 长任务链（Beacon 特有）
  intent_review → truth_fill → implement_loop → eval chain → repair_from_qa
    ↓
Layer 3 — Harness Worker（beacon CLI，Skill 的可执行投影）
  pln: beacon planner-review run
  gen-truth: beacon prd-bootstrap / truth / freeze …
  gen-implement: beacon implement run --runner <runner>   ← R3 强制
  eval: beacon qa run / release create
    ↓
Layer 4 — Agent backend（仅 implement runner 内部）
  codex exec + output-schema（与 gnhf CodexAgent 同级契约）
```

**禁止**：`implement_loop` 直接 `spawn codex` 绕过 `beacon implement run`（AC-044）。**禁止**：子进程读取 `$beacon-pln-review` 等 Skill 文件假装执行（D-012 blocked）。

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

### 依赖

本 feature **扩展** parent，不替换：

| Parent | This feature |
|--------|--------------|
| AC-001..AC-030 runner/harness/E2E | AC-031..AC-039 delivery orchestrator |
| `packages/beacon-loop` orchestrator | `intent/` + `delivery/` 模块 |
| `.beacon/loop/runs/<id>/` runtime package | 扩展 runtime artifacts |

## Parent Feature Dependency Matrix

| Parent AC | 本 feature 依赖说明 |
|-----------|---------------------|
| AC-003 goal entrypoint | 保留；扩展 `--mode` |
| AC-004..AC-005 resolver | 扩展：blocked 时进入 truth_fill，非仅 abort |
| AC-016..AC-021 orchestrator | `implement_loop` 子状态复用 |
| AC-022..AC-025 ledger/diagnose | delivery-state 写入同一 ledger |
| AC-030 E2E import→qa | 扩展为 AC-039 全链 E2E |

## Command Contract

正式入口不变：

```bash
beacon-loop goal "<utterance>" [options]
```

新增 orchestrator modes（`--mode`，默认 `delivery`）：

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

## Truth Fill Subchain Contract

当 `truth-map resolve` blocked 或 review 判定 truth gap（AC-034）：

```text
truth-promotion.json 记录：
  beacon truth bootstrap / gen-truth / gen-change / refreeze 调用序列
loop 禁止直接修改 features/*/truth.md
truth frozen 后重新 resolve，直到 pass 或 terminal_aborted
```

禁止 silent MVP：truth_fill 不得默认写入 `scope_mode=mvp` 除非 `deferral_ledger` 有 `user_decision=accepted`。

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

Parent Phase A-D 必须先满足或与本 feature Phase E 并行不冲突。Phase J 依赖 Phase E-G 的 delivery plumbing，**替换** implement 层的裸 codex 路径。

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

## Source Advisory

| Artifact | Role |
|----------|------|
| `docs/beacon/v1.6.0/change/beacon-loop-goal-closed-loop-orchestrator.md` | change record |
| `docs/beacon/v1.6.0/research/beacon-loop-goal-closed-loop-orchestrator.md` | promoted research |
| `features/beacon-loop-native-runner-and-automation-retirement/truth.md` | parent frozen truth |
| `features/beacon-pln-review-intent-parity-state-machine-v160/truth.md` | planner review contract |
| `/Users/apple/Developer/Personal/oss-sync/agents/agent-systems/gnhf` | gnhf orchestrator + codex adapter 源对标 |

本文件为 package-authoritative requirement truth（**draft**，**R3 revision**，reopened via `beacon-gen-change`）。
