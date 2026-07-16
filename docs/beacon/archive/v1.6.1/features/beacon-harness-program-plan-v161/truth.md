---
slug: beacon-harness-program-plan-v161
version: v1.6.1
status: frozen
revision_id: R4
source_revision_id: R3
language: zh
change_reason: R4 implementation-first-reconciliation refreeze；承接 R3 真实 program FSM + goal 单入口 + loop v161 对接
canonical_refs:
  prd: docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md
  user_story: docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md
  test_case: docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: true
---

# 需求真相：Beacon Harness Program Plan v1.6.1

## 概述

`beacon-harness-program-plan-v161` 在 v1.6.0 harness / planner review / TIG / loop orchestrator 之上，新增 **版本级 program plan harness**：把海级用户 utterance（如「完整复刻某 GitHub 项目全功能」）编排为 **书籍形真相**——**目录（program-manifest）+ 大纲（module-map）+ 章节（feature 湖）**，对每个湖调用既有 **Truth Freeze Intent Loop（7 轮）** 煮干并 freeze，最后经 **Program Freeze Gate** 证明全书与用户意图 parity closed；**beacon change** 路径保留 change 用户意图并经 plan review 后 refreeze。

本 feature **不**新增 Beacon 主生命周期 stage；**不**让 planner 写 package truth；**不**让 loop/runner 产出 QA/release verdict。

**R3**：收紧 **真实** `--mode program` 外层 FSM；操作者 **长任务单一公共入口** 改为 `beacon-loop goal`（`beacon plan start` 仅 scaffold）；`goal` 与 `plan start` 共享 `program-run-state.json` resume 契约；与 **`beacon-loop-goal-closed-loop-orchestrator-v161` R1**（AC-072..075）对接。

**R4（本 revision，frozen）**：`implementation-first-reconciliation` refreeze；R3 交付范围不变；machine revision 与 R4 实现 writeback / QA / release 投影对齐。操作者文档见 `docs/beacon/archive/v1.6.1/execution/long-task-operator-guide.md`（AC-PBP-027 / TASK-LOOP-A03）。

## User Intent（一行）

v1.6.1 交付版本级海→湖 program harness（umbrella + auto/interactive 双模式、CLI `beacon plan start`）：多轮 plan 拆书、每湖煮干冻结、TIG 防 LLM 假交付、change 后 plan review 与 refreeze 全闭环，与全功能复刻意图一致。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | 确认双模式 program plan：umbrella + auto/interactive 子 skill、CLI `beacon plan start` 治理、操作认知减负、补充冻结 v1.6.1 truth |
| `lake_or_ocean` | **湖**（本 package 冻结 harness 契约；program 运行时面向 **海** utterance） |
| `scope_mode` | `full_parity` |
| `plan_mode`（program 运行时） | `auto` \| `interactive` \| `auto-detect`（umbrella 分类后委派） |
| 强度词 | 全功能、完整复刻、书籍真相、煮干、冻结、change 闭环 |
| 非协商边界 | 不假交付；未拍板 defer 不可 freeze；planner 不写 features truth |

## Alignment Surface（v1.6.1 冻结时必须煮干）

### A. Program artifact contract

- `docs/beacon/archive/v1.6.1/execution/program-plan-contract.md` 为 normative contract
- Program 目录 schema：`program-manifest.md`、`module-map.md`、`feature-graph.json`、`program-parity-matrix.md`、`change-intent-log.jsonl`
- `feature-graph.json` 必填：`program_slug`、`version`、`scope_mode`、`lakes[]`（`slug`、`depends_on`、`parity_subset`、`status`）

### B. Program Plan Loop（P0–P6）

- P0 source inventory → P1 module-map → P2 program pln-review → P3 feature-graph → P4 user ack → P5 per-lake gen-truth 7-round + TIG → P6 program freeze gate
- 海级 utterance **禁止**跳过 P3/P4 直接单湖 truth_fill（对齐 loop orchestrator 反 MVP 骨架）

### C. Per-lake nested truth

- 每个 lake 必须独立 `features/<slug>/` 包，走 v1.6.0 **Truth Freeze Intent Loop** Round 0–7
- 湖级 `lake_or_ocean=湖`；Alignment Surface / Phased Backlog 仅描述该湖 closure

### D. Program Freeze Gate

- 全书 inventory 每条 capability 映射到唯一 lake + frozen truth AC 或 accepted deferral
- 全部 lake `status=frozen`；program deferral ledger 零未决 defer（须 accepted 或 rejected）
- 调用 TIG `mode=block` 于每个 lake；program gate 汇总为 `program-truth-freeze.json`

### E. Governance / anti-gaming

- Program/lake freeze 前 **禁止** agent 自证 closure；权威在 CLI（TIG、verify-closure、freeze）
- Program 层 extend maker≠checker：P6 不得仅凭 planner artifact 存在即 pass，必须 machine-readable lake freeze 证据
- 软 TC、空壳 AC、无效 runner 证据由既有 TIG 拦截（不重复发明）

### F. Change closure

- `beacon-gen-change` 开 revision 时 **append** `change-intent-log.jsonl`（utterance、affected_slugs、scope_mode）
- Change 后 **mandatory** `beacon-pln-review` + `promotion_diff`（frozen vs change intent）
- User ack 后更新 graph 或单湖 truth → gen-truth rounds → TIG → `beacon-gen-refreeze`；结构变更时重跑 P6

### G. Integration surfaces（R2：双模式 skill + CLI）

**认知减负原则**：操作者长任务只记 **`beacon-loop goal "<utterance>"`**（薄委托 `beacon-run`）；program scaffold 用 **`beacon plan start`** 或 host skill **`beacon-pln-program`**；`plan_mode` 由显式 flag 或 umbrella **一次**澄清完成，不在子 skill 层重复盘问。

**Skill 三层（稳定触发）**：

| Skill | Harness | 角色 | 触发 |
|-------|---------|------|------|
| `beacon-pln-program` | planner | program scaffold **推荐入口**（`plan_mode` 分类 + 委派）；长 FSM 仍由 `beacon-loop goal` 续跑 | `/beacon-pln-program`、`beacon plan start` |
| `beacon-pln-program-auto` | planner | 子 skill：机器 P0、分段 P4 ack | 仅 umbrella 委派或 `--mode auto` |
| `beacon-pln-program-interactive` | planner | 子 skill：BR 轮 + `beacon-pln-brainstorm` | 仅 umbrella 委派或 `--mode interactive` |

- 子 skill **不得**作为与 umbrella 并列的 casual 公共目录项宣传；host 可安装三 skill 以支持 description 级稳定匹配，但 operator docs 只强调 umbrella。
- Auto P0 消费 `beacon-pln-source`；Interactive BR 消费 `beacon-pln-brainstorm`；P2 均 mandatory `beacon-pln-review`。
- `plan_mode` 与 classifier `reason` 写入 `program-manifest.md` frontmatter。

**CLI 治理层（normative，Phase E 实现）**：

```bash
beacon plan start "<utterance>" \
  --project-root . --version <version> --program <program-slug> \
  --mode auto|interactive|auto-detect \
  --source <url> --json
```

- `beacon plan auto` / `beacon plan interactive` 为 `start --mode` 的稳定别名（实现可选）。
- CLI 与 skill 共享同一 P0–P4 artifact 路径（`programs/<slug>/`）；不得出现第二套 plan 目录。
- `beacon-run --mode program` 外层 FSM 在 P4 ack 后嵌套 per-lake delivery；内层不替代 umbrella 分类；状态与 run-dir `program-run-state.json` 及 `programs/<slug>/` 对齐（AC-PBP-029）。
- `beacon-loop goal` 为海级长任务 resume 面；`plan start` 后 **不得** 要求 operator 重 scaffold 才能续跑外层 FSM。

**废弃 R1 模糊表述**：不再「`beacon-pln-program` 或 brainstorm program mode 二选一」；以 **umbrella + 双子 skill + CLI start** 为唯一 normative 组合。

## Phased Backlog（不在 v1.6.1 单包 closure）

| ID | Capability | reason | recommended_route |
|----|------------|--------|-------------------|
| PB-001 | 全自动 OSS AST capability 抽取 | 假 inventory 风险 | post-v1.6.1 research |
| PB-002 | Host parallel subagent repo 深扫 | 依赖 planner review multi-agent runtime | v2 / planner-review runtime |
| PB-003 | 独立 judge LLM program 审查 | D-le-001 类 defer | v2 |

## Deferral Ledger

| deferral_id | capability | reason | impact | user_decision | expiry_or_revisit | recommended_route |
|-------------|------------|--------|--------|---------------|-------------------|-------------------|
| D-PBP-001 | PB-001 AST 抽取 | v1.6.1 默认 source-driven + 人工 ack | 立项需人工 inventory | accepted | post-v1.6.1 | beacon-pln-source |
| D-PBP-002 | PB-002 parallel repo scan | runtime 未统一 | P0 可半自动 | accepted | v2.0.0 | beacon-pln-review-runtime |
| D-PBP-003 | PB-003 judge LLM | 成本/一致性 | P2 review 仍用现有 reviewer | accepted | v2.0.0 | defer |

## State Model

### ProgramPlanState

States: `program_intent_captured` → `plan_mode_selected` → `program_inventory` → `program_reviewed` → `feature_graph_ack` → `lakes_truth_in_progress` → `lakes_frozen` → `program_frozen` → `program_delivery` | `program_change_open` → `program_change_review` → `program_refreeze` → `program_frozen`

Invalid: `program_intent_captured` → `lakes_frozen`（跳过 graph ack）；`program_intent_captured` → `program_inventory` without `plan_mode_selected`；`program_change_open` → `program_delivery`（未 review/refreeze）

Recovery: `program_change_open` 可 resume 到 `program_change_review`；lake TIG block 回 `lakes_truth_in_progress`

Terminal: `program_frozen`（plan closure）；`program_delivery` 子状态由 loop delivery FSM 接管

### ChangeSubState

Append-only `change-intent-log.jsonl`；每次 change 必须 `promotion_diff` 后才可 refreeze

## Parent / Upstream Dependency Matrix

| Upstream | 本 feature 依赖 |
|----------|----------------|
| harness taxonomy rough prompt routing | program 路由归约 outcome + 湖/海 |
| pln-review intent/parity/deferral | P2、change review |
| TIG AC-TIG-* | 每湖 freeze + refreeze block |
| loop orchestrator intent/review/truth_fill | `--mode program` 嵌套 |

## 验收标准

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-PBP-001 | program-contract | `execution/program-plan-contract.md` 存在且定义 program 五文件 schema 与 P0–P6。 |
| AC-PBP-002 | version-line | `docs/beacon/archive/v1.6.1/SUMMARY.md` 声明 v1.6.1 program harness 与 v1.6.0 继承关系。 |
| AC-PBP-003 | research-promoted | `research/beacon-harness-program-plan-v161.md` 含 `user_decision=promoted` 与 `promotion_ref`。 |
| AC-PBP-004 | feature-graph-schema | CLI 或 validator 校验 `feature-graph.json` 必填字段（`program_slug`、`lakes[].slug`、`depends_on`、`parity_subset`）。 |
| AC-PBP-005 | sea-no-single-lake | 海级 utterance（`lake_or_ocean=海`）在缺 P4 ack 时 block 单湖 freeze/program freeze。 |
| AC-PBP-006 | lake-nested-7round | 每个 lake 进入 program P5 前必须记录 `truth-promotion.json` 或等价证据，证明 7-round loop 完成或 block 原因。 |
| AC-PBP-007 | program-freeze-gate | `beacon program freeze`（或 doctor 等价）输出 `program-truth-freeze.json`；零 orphan capability、零未决 defer。 |
| AC-PBP-008 | tig-per-lake | Program P6 汇总前每个 lake 必须通过 `beacon doctor verify-truth-integrity <slug> --mode block`。 |
| AC-PBP-009 | verify-closure-per-lake | 每个 lake freeze 前 `beacon skill package verify-closure` pass。 |
| AC-PBP-010 | planner-boundary | Program plan harness 不写 `features/*/truth.md`；违规被 skill HARD GATE 或 eval 阻断。 |
| AC-PBP-011 | full-parity-default | Program manifest 含「完整复刻/全功能/parity」信号时默认 `scope_mode=full_parity`。 |
| AC-PBP-012 | parity-matrix-program | `program-parity-matrix.md` 每行含 source capability、target lake、target AC ref、status、deferral。 |
| AC-PBP-013 | change-intent-log | `beacon-gen-change` program 路径 append `change-intent-log.jsonl` 条目（utterance、slugs、timestamp）。 |
| AC-PBP-014 | change-review | Change 后 mandatory pln-review 产出 `promotion_diff` 对照 change intent 与 frozen truth。 |
| AC-PBP-015 | change-refreeze | User ack 后 `beacon-gen-refreeze` + TIG block；结构变更重跑 AC-PBP-007。 |
| AC-PBP-016 | run-mode-program | `beacon-run`（`beacon-loop goal` 委托）实现 **真实** `--mode program` 外层 FSM（P0–P6），状态写入 `program-run-state.json`；**禁止** 仅以 CLI help 暴露 `mode`/`prevent-sleep` 视同本 AC 闭合；P4 user ack 前不得 spawn per-lake delivery。 |
| AC-PBP-017 | public-planner-route | 存在 **`beacon-pln-program`** umbrella skill；实现 Phase E 时同步 CLI `beacon plan start`。 |
| AC-PBP-018 | maker-checker-program | P6 pass 必须含 machine-readable 每湖 frozen 证据；不得仅 planner JSON 自报。 |
| AC-PBP-019 | deferral-sovereignty | Program/lake deferral 未决时 block program freeze 与 refreeze。 |
| AC-PBP-020 | no-new-lifecycle-stage | 文档与 skill 不新增 plan/truth/generate/evaluate/release 之外的主 stage。 |
| AC-PBP-021 | state-model-truth | 本 package `truth.md` 含 ProgramPlanState 与 ChangeSubState（见上）。 |
| AC-PBP-022 | state-model-tests | `tests.md` 覆盖非法跳过 graph ack、change 未 review refreeze、TIG block 恢复路径。 |
| AC-PBP-023 | dual-mode-skill-triad | `skills/beacon/` 存在 `beacon-pln-program`、`beacon-pln-program-auto`、`beacon-pln-program-interactive` 且含 HARD GATE；auto/interactive 声明 delegation-only。 |
| AC-PBP-024 | cli-plan-start | `beacon plan start --help` 暴露 `--mode auto\|interactive\|auto-detect` 与 `--program`；或 BLOCKED:Phase-E。 |
| AC-PBP-025 | plan-mode-classifier | `program-plan-contract.md` 定义 deterministic `plan_mode` 分类规则与低置信度停问。 |
| AC-PBP-026 | umbrella-delegation | Umbrella skill 正文要求委派子 skill；子 skill 禁止写 `features/*/truth.md`。 |
| AC-PBP-027 | cognitive-load-single-entry | truth/SUMMARY 声明 **长任务** 单一公共入口为 `beacon-loop goal`；`beacon plan start` / `beacon-pln-program` 为 program scaffold + `plan_mode`；artifact 仅 `programs/<slug>/`。 |
| AC-PBP-028 | interactive-brainstorm-bridge | Interactive 子 skill 要求 BR 阶段调用 `beacon-pln-brainstorm`；auto 子 skill 要求 P0 对齐 `beacon-pln-source`。 |
| AC-PBP-029 | goal-resume-state | `beacon-loop goal` 与 `beacon plan start` 共享 resume 状态（`programs/<slug>/program-run-state.json` 或 run-dir 等价）；`plan start` 后 `goal` 须 resume 而非重 scaffold；状态含 `program_slug`、`plan_mode`、`program_phase`、`next_action`。 |
| AC-PBP-030 | loop-orchestrator-handoff | 对接 `beacon-loop-goal-closed-loop-orchestrator-v161` R1（AC-072..075；upstream v1.6.0 R10）：`--mode program` 嵌套 per-lake delivery 不得破坏 AC-068 `truth_freeze_gate`；eval supplement opt-in 不得 gate qa/release。 |

## Non-goals

- 不实现被复刻 OSS 产品本身（如 oh-my-claudecode）的业务代码
- 不替代 truth-map resolver 权威
- 不让 program artifact 自动成为 package truth（须 promote + gen-truth）
- 不在 v1.6.1 交付 PB-001..003

## Delivery Phases

| Phase | 范围 | AC |
|-------|------|-----|
| A | docs line + contract + research promote | AC-PBP-001..003 |
| B | feature-graph validator + sea guard | AC-PBP-004..005 |
| C | program freeze gate + TIG aggregation | AC-PBP-007..009 |
| D | change-intent-log + review + refreeze | AC-PBP-013..015 |
| E | beacon-run program mode + planner triad + CLI plan start | AC-PBP-016..018, AC-PBP-023..028 |
| F | state machine tests + eval | AC-PBP-021..022 |
| G | R3 real program FSM + goal resume + loop handoff | AC-PBP-016, AC-PBP-027, AC-PBP-029, AC-PBP-030 |

## Revision History

| revision | summary |
|----------|---------|
| R1 | Initial freeze：覆盖书籍 program harness、海湖、治理、change 闭环 |
| R2 | 双模式 program plan：umbrella + auto/interactive 子 skill、CLI `beacon plan start`、plan_mode FSM、cognitive-load 单一入口 |
| R3 | 真实 `--mode program` FSM；`beacon-loop goal` 为长任务主入口；goal/plan 共享 resume；loop orchestrator v161 对接 |
| R4 | implementation-first-reconciliation refreeze；operator guide；R3 范围冻结 + R4 writeback/QA/release 对齐 |
