---
slug: loom-goal-steering-codex-continuation
version: v2.0.0
status: support_advisory
authority: beacon-pln-review
review_id: pln-review-20260719t133240z
runtime_evidence: .beacon/state/planner-review/beacon-v2-goal-durable-longrun/pln-review-20260719t133240z.json
source_primary: oss-sync/agents/tools/codex@0fb559f0f6 (codex-rs/ext/goal/templates/goals/*)
target_primary: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md
related:
  - docs/beacon/v2.0.0/features/loom-goal-trace-bundle/truth.md
  - docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/truth.md
  - oss-sync/index/analysis/openai-codex-goal-vs-beacon-loom-v2.md
user_utterance: "v2.0.0 下一步要落地 把 Codex continuation.md 蒸馏进 Loom steering 合同"
generated_at: 2026-07-19T13:35:00+08:00
recommended_route: beacon-gen-change
user_decision_required: false
user_decisions_applied:
  hang: durable-longrun (1A)
  objective_updated: Must (2A)
  complete_path: awaiting_verifier (3A)
  route: beacon-gen-change GO (4A)
  applied_at: 2026-07-19
planner_boundary:
  truth_write_allowed: false
  code_write_allowed: false
  machine_write_allowed: false
  qa_verdict_allowed: false
  release_verdict_allowed: false
---

# Planner Review: Codex continuation.md → Loom Steering 合同

## intent_snapshot

| 字段 | 值 |
|------|-----|
| original | 下一步要落地：把 Codex `continuation.md` 蒸馏进 Loom steering 合同（v2.0.0） |
| strong_signals | 「落地」「蒸馏」「合同」— 要求进入 truth/AC/tests 层，而非仅 research 笔记 |
| source | OpenAI Codex Goal extension templates: `continuation.md` + 姐妹模板 `budget_limit.md` / `objective_updated.md` |
| non_negotiable | 必须保留长程 fidelity / completion audit / blocked≥3；**不得**削弱为「只 inject resume-pack 路径」的半截实现 |
| boundary | 不把 Codex 的 model self-complete 原样当 Loom complete；Loom complete 仍需 verifier |
| out_of_scope_this_review | 微信日更 cron、RecurringJob 产品化（另案）；本 review 只收 steering 蒸馏 |

## scope_mode

**`full_parity`（对 Codex Goal steering 模板面）** + **Beacon-native 完成门增强**

- Runtime builder 默认标成 `brownfield_takeover` **过弱**；用户意图是对 Codex continuation 蒸馏做全，不是 brownfield 局部补丁。
- 降级为 MVP（只抄一句 “continue working”）**禁止**，除非 deferral ledger 经用户 accept。

## 湖/海判断

| 判断 | 结论 |
|------|------|
| 主湖 | **扩展** `beacon-v2-goal-durable-longrun`（AgentDriver inject 面）— 同一 GoalRun / longrun 轴 |
| 可选新湖 | 若希望 slug 语义独立：`loom-goal-steering-distill`（仍挂 product-goal-parallel program 轴） |
| 海 | 通用 cron、公众号发布、任意 job kind — **本轮不进** |

推荐：**change 进 durable-longrun**（最小面），program axis 增 mount 一行；若用户要独立 feature 包再拆新 slug。

---

## source_capability_inventory（Codex Goal steering）

| ID | Source capability | Source location | Target landing |
|----|-------------------|-----------------|----------------|
| S-ST-01 | Active goal idle auto-continuation | `GoalRuntimeHandle::continue_if_idle` + `on_thread_idle` | AgentDriver requeue inject path |
| S-ST-02 | Continuation steering template | `ext/goal/templates/goals/continuation.md` | Loom steering asset + AC |
| S-ST-03 | Objective-as-data (untrusted/user data) | `<objective>` + escape_xml | inject 时 objective 当数据非更高优先级指令 |
| S-ST-04 | Scope fidelity（不缩 objective） | continuation “Keep the full objective intact” | longrun turn inject 强制 fidelity 段 |
| S-ST-05 | Work-from-evidence（worktree 权威） | continuation “Work from evidence” | 与 resume-pack digest 并列；**不得**用 full chat 替代 |
| S-ST-06 | Completion audit（逐条证据） | continuation “Completion audit” | **对齐但升级**：audit 后仍走 verifier gate，不直接 model complete |
| S-ST-07 | Blocked audit（≥3 consecutive goal turns） | continuation + update_goal tool text | 已有 stage_blocked streak≥3；需 **模型侧文案 + 计数定义** 写进 steering 合同 |
| S-ST-08 | Budget wrap-up template | `budget_limit.md` | halt_budget 时 inject wrap-up；禁伪 complete |
| S-ST-09 | Objective updated template | `objective_updated.md` | 用户改目标后 inject（若 Loom 支持 edit objective） |
| S-ST-10 | Agent tools get/create/update_goal | `ext/goal/src/tool.rs` + `spec.rs` | Loom 侧：status 由 ledger/driver 权威；**不**让 agent 工具绕过 verifier |
| S-ST-11 | Accounting tokens/time | thread_goals accounting | durable longrun budget ACs 已有；steering 需展示 remaining |
| S-ST-12 | Continuation deferral | `thread_goal_continuation_deferrals` | Driver 侧 deferral（用户 pause / plan mode / safety） |
| S-ST-13 | Plan mode 不挂 goal 进度 | extension on_turn_start Plan clear | collaboration mode 边界（可选） |

---

## parity_matrix

| Source capability | Target truth today | Target tests today | Status | Deferral |
|-------------------|--------------------|--------------------|--------|----------|
| S-ST-01 idle continue | AC-V2-DLR-008 auto-requeue | TC-V2-DLR-008 / LEGAL-01 | **partial** — 有 requeue，无 steering 内容合同 | none |
| S-ST-02 continuation.md 全文语义 | **missing**（truth 只写 inject resume-pack） | **missing** | **missing** | none — **本轮 Must** |
| S-ST-03 objective-as-data | missing | missing | **missing** | none — Must |
| S-ST-04 scope fidelity | missing | missing | **missing** | none — Must |
| S-ST-05 worktree evidence | resume-pack digest authority (UD-V2-DLR-005) | TC-V2-DLR-006 | **partial** — 有 digest 权威，无 Codex 级 fidelity 文案 | none — Must 补 steering 段 |
| S-ST-06 completion audit | AC-V2-DLR-010 verifier complete | TC-V2-DLR-010 / ILLEGAL-01 | **partial** — 门更严但缺 pre-verifier 审计指令 | none — Must（Beacon 增强版） |
| S-ST-07 blocked≥3 模型侧 | GoalRun blocked streak≥3 | TC 有 interrupt≠blocked | **partial** — 状态有，steering/定义「goal turn」缺 | none — Must |
| S-ST-08 budget wrap-up | AC-V2-DLR-012 halt_budget | TC-V2-DLR-012 / ILLEGAL-03 | **partial** — 有 halt 无 wrap-up template | none — Must |
| S-ST-09 objective_updated | missing | missing | **missing** | **pending user** — 若 v2 暂无 edit-objective 可 defer |
| S-ST-10 agent goal tools | 非目标（ledger 权威） | — | **intentional non-parity** | accepted-by-design（勿照搬 self-complete 工具） |
| S-ST-11 budget display in prompt | partial via config | partial | **partial** | none — Should |
| S-ST-12 deferral | missing explicit | missing | **missing** | **pending** — 可 P1 |
| S-ST-13 plan mode | missing | missing | **missing** | **pending** — P2 |

**覆盖率（Must 项）**：约 2/9 full + 4/9 partial + 3/9 missing → **不可称 steering 已落地**。

---

## state_model（steering 注入轴 — 建议写入 change）

### Entities

| Entity | Key | Notes |
|--------|-----|-------|
| SteeringTemplate | template_id | `continuation` \| `budget_limit` \| `objective_updated` |
| SteeringRender | run_id + turn_id | rendered markdown/text injected into host turn |
| GoalTurnCounter | run_id | consecutive turns with same blocker_id（blocked audit） |
| InjectBundle | turn_id | **ordered**: steering(template) + resume-pack digest + next_action |

### AgentDriver inject 状态补充

| State / Event | Guard | Inject payload |
|---------------|-------|----------------|
| requeue → turn_active | status active & budget ok | **continuation** + resume-pack + next_action |
| halt_budget | token/turn exhaust | **budget_limit** wrap-up only；禁新实质工作指令 |
| objective_changed | user edit objective | **objective_updated** + digest |
| pause / user_stop | — | no auto inject |
| plan_mode (if any) | plan collaboration | 不计 goal accounting / 不 auto complete |

### Illegal

| ID | Illegal |
|----|---------|
| I-ST-001 | requeue 只 inject resume-pack，省略 continuation 语义（当 AC Must 后） |
| I-ST-002 | continuation 指示 agent `update_goal complete` 绕过 verifier |
| I-ST-003 | full chat 替代 resume-pack 权威 |
| I-ST-004 | budget_limit 后仍鼓励开新实质工作 |
| I-ST-005 | 第 1 次 blocker 即 blocked（未满 3 goal turns） |

### Beacon 增强（相对 Codex 必保留）

```text
Codex:  completion audit → update_goal(complete)
Loom:   completion audit → awaiting_verifier → verifier refs → completed
        release 永不 auto
```

---

## findings（合成；含 runtime lanes + 人工加固）

### F-ST-001 — P0 | intent-fidelity + source-parity

- **issue**: 用户要求把 Codex `continuation.md` **蒸馏进合同**；当前 `beacon-v2-goal-durable-longrun` 只规范 “inject resume-pack only”，**没有** steering 模板、fidelity、completion/blocked audit 合同。若直接 implement，会假交付为「有 requeue 即 steering」。
- **confidence**: 100
- **authority**: user_quote + source_evidence + package_truth
- **evidence_refs**:
  - user utterance
  - `oss-sync/agents/tools/codex/codex-rs/ext/goal/templates/goals/continuation.md`
  - `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md`（How one-shot works / AC-V2-DLR-006/008）
  - runtime: `pln-review-20260719t133240z.json` → route `beacon-gen-change`
- **affected**: truth.md, tests.md, tasks.md, program axis mount, possible `skills/loom|beacon` longrun 说明
- **route**: `beacon-gen-change`（或独立新 slug 后 `beacon-gen-truth`）
- **user_decision_required**: true
- **autofix_allowed**: false

### F-ST-002 — P1 | source-parity

- **issue**: 姐妹模板 `budget_limit.md` / `objective_updated.md` 与 continuation 同属 Codex Goal steering 包；只蒸馏 continuation 会留下预算收尾与目标变更缺口。
- **confidence**: 90
- **authority**: source_evidence
- **route**: change 中 Must 含 budget_limit；objective_updated 需用户确认是否本轮
- **user_decision_required**: true（objective_updated 范围）

### F-ST-003 — P1 | state-machine

- **issue**: InjectBundle 顺序与 illegal inject 未进 State Model；Driver FSM 写 “inject resume-pack only” 与未来 multi-part inject 冲突。
- **confidence**: 85
- **route**: change 更新 AgentDriver FSM + illegal 表
- **user_decision_required**: false（结构必须，语义用户已要）

### F-ST-004 — P1 | coverage-shape / evidence-proof-shape

- **issue**: 现有 TC 无 “rendered steering contains fidelity/completion/blocked audit sections” 类断言；也无 golden file 对比 Codex 蒸馏清单。
- **confidence**: 85
- **route**: tests.md 增 TC-V2-ST-*；fixture 锁定必含段落
- **user_decision_required**: false

### F-ST-005 — P0 | route-boundary / anti-fake-delivery

- **issue**: 不可把 Codex `update_goal(complete)` 蒸馏成 Loom agent 自证 complete。合同必须写 **Completion audit → awaiting_verifier**，保留 AC-V2-DLR-010/011。
- **confidence**: 100
- **authority**: package_truth（durable-longrun + global-boundaries）
- **route**: change 显式 Non-Goals + illegal I-ST-002
- **user_decision_required**: false（硬边界）

### F-ST-006 — P2 | performance-boundary

- **issue**: 每 turn 注入全文 continuation 可能挤占 context；需规定与 resume-pack 的合并策略（固定短文案 + digest，禁止重复整段 jsonl）。
- **confidence**: 70
- **route**: change 规定 token budget for steering render；可截断展示 remaining 字段
- **user_decision_required**: false

### F-ST-007 — P2 | simplification-risk

- **issue**: 「蒸馏」易被简化成 3 行 prompt。用户 full_parity 下，Must 段（fidelity / completion audit / blocked audit / budget wrap-up）不可删减为 MVP 口号。
- **confidence**: 80
- **route**: truth 用 checklist + tests golden 防缩水
- **user_decision_required**: true 若有人提议砍段

### F-ST-008 — P3 | maintainability

- **issue**: 模板落点建议固定：`skills/beacon/references/goal-steering/` 或 `docs/beacon/v2.0.0/fixtures/steering/` + runtime 嵌入路径；避免散落 Python 字符串。
- **confidence**: 60
- **route**: change tasks 指定单一资产路径
- **user_decision_required**: false

### Runtime lanes（透明）

- `execution_mode`: single_process_multi_reviewer（无 parallel subagent 宣称）
- runtime findings 多为 generic P2；**本 synthesis 以上人工加固 findings 为准**。

---

## deferral_ledger

| deferral_id | capability | reason | impact | user_decision | expiry | route |
|-------------|------------|--------|--------|---------------|--------|-------|
| DEF-ST-01 | S-ST-09 objective_updated 模板 | v2 可能尚未产品化 “edit goal objective” UX | 用户改目标后无 steering 重定向 | **pending** | next change | change 可选 Must / defer |
| DEF-ST-02 | S-ST-10 create/update_goal agent tools | 与 verifier 门冲突；ledger 权威 | 无 Codex 式工具面 | **accepted-by-design** | permanent unless redesign | 文档 Non-Goals |
| DEF-ST-03 | S-ST-12 continuation deferral table | 可后置 | pause/plan 竞态边缘 | **pending** | after Must steering | change P1 |
| DEF-ST-04 | S-ST-13 plan mode accounting clear | collaboration mode 可选 | plan 污染执行会计 | **pending** | P2 | later |
| DEF-ST-05 | RecurringJob / 微信日更 cron | 用户前序场景但本轮非目标 | 周期唤醒仍靠 host | **accepted this slice** | separate lake | research only |
| DEF-ST-06 | MVP 三行 prompt | 违反 full_parity | 假蒸馏 | **rejected** | — | 禁止 |

---

## promotion_diff（accept 后 gen-change 必须写入）

### A. User Decisions（建议新增）

| ID | Value |
|----|-------|
| UD-V2-ST-001 | Steering 资产以 Codex Goal templates 为 source；蒸馏进 Loom/Beacon longrun inject |
| UD-V2-ST-002 | InjectBundle 顺序：`steering(template)` → `resume-pack digest` → `next_action` |
| UD-V2-ST-003 | Must 语义段：scope fidelity、work-from-evidence、completion audit、blocked≥3、budget wrap-up |
| UD-V2-ST-004 | Completion audit **不**授权 model self-complete；仅推进 `awaiting_verifier` |
| UD-V2-ST-005 | 模板权威路径单源（references 或 fixtures）；runtime 禁止私自缩短 Must 段 |
| UD-V2-ST-006 | objective_updated：本轮 **GO / DEFER**（待用户选） |

### B. Acceptance Criteria（建议 AC-V2-ST-00x 或并入 DLR）

| AC | Must/Should | 描述 |
|----|-------------|------|
| AC-V2-ST-001 | Must | 存在规范 `continuation` 模板；含 Codex 对齐 Must 段 checklist |
| AC-V2-ST-002 | Must | Driver requeue→turn_active **必须** render+inject continuation（非仅 digest） |
| AC-V2-ST-003 | Must | objective 按 untrusted user data 处理（非 system override） |
| AC-V2-ST-004 | Must | completion audit 段存在且 **禁止** 指示绕过 verifier 的 complete |
| AC-V2-ST-005 | Must | blocked audit 段：≥3 consecutive goal turns；定义 goal turn 含 auto-requeue |
| AC-V2-ST-006 | Must | budget_limit 模板；halt_budget 时 inject；禁新实质工作 |
| AC-V2-ST-007 | Must | tests：golden/section presence + illegal inject 用例 |
| AC-V2-ST-008 | Should | remaining tokens/turns 字段渲染 |
| AC-V2-ST-009 | Should/Defer | objective_updated 路径 |

### C. Tests 义务

- TC-V2-ST-001 section presence vs checklist  
- TC-V2-ST-002 requeue inject order  
- TC-V2-ST-003 no-self-complete language  
- TC-V2-ST-004 budget wrap-up inject  
- TC-V2-ST-ILLEGAL-01 inject digest-only when steering required  
- TC-V2-ST-ILLEGAL-02 steering encourages verifier bypass  

### D. Non-Goals（写死）

- 不引入 Codex 式 agent `update_goal(complete)` 为权威  
- 不把 full chat 当 resume 权威  
- 本 lake 不做 cron daemon  

---

## recommended_route

```text
beacon-gen-change
  target: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/
  optional alternate: new feature loom-goal-steering-distill (if user wants separate slug)
  then (after freeze): beacon-gen-implement
  not now: beacon-eval-qa / release / direct implement
```

**Stop conditions before implement**

1. 用户确认 scope_mode = full_parity（steering Must 段）  
2. 用户对 DEF-ST-01（objective_updated）选 GO 或 DEFER  
3. 用户确认挂靠 **durable-longrun change** vs **新 slug**  

---

## 用户决策问卷（请回复编号）

1. **挂靠面**  
   - A（推荐）：change `beacon-v2-goal-durable-longrun`  
   - B：新建 `loom-goal-steering-distill` feature 包  

2. **objective_updated**  
   - A：本轮 Must 一起蒸馏  
   - B：Defer 到后续  

3. **complete 语义**  
   - A（推荐/硬边界）：audit 后只进 awaiting_verifier  
   - B：不允许（会破坏 Beacon truth）  

4. **是否进入 change**  
   - A：GO — 执行 `$beacon-gen-change`  
   - B：先只保留本 research  

---

## 一句话结论

> 当前 longrun 合同覆盖 **续跑机制（requeue + digest）**，未覆盖 **续跑认知（Codex continuation 蒸馏）**。  
> 下一步合法路径是 **`beacon-gen-change` 写入 steering 合同与测试义务**，禁止跳过 truth 直接实现。  
> 蒸馏必须 **全量 Must 段 + Beacon verifier 增强**，禁止 MVP 三行 prompt 假交付。
