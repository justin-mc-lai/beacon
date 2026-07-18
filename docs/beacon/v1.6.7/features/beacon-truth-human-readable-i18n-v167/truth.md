---
slug: beacon-truth-human-readable-i18n-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-18: human-readable L0 + Humanizer-zh/blader humanizer norms; zh/en; mount GoalRun main axis"
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-truth-human-readable-i18n-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-truth-human-readable-i18n-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-truth-human-readable-i18n-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-truth-human-readable-i18n-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
ux_required: false
design_deferral: "Docs/prose gate; no product marketing UI"
source_refs:
  - https://github.com/blader/humanizer
  - https://github.com/op7418/Humanizer-zh
  - docs/beacon/v2.0.0/research/beacon-v167-v200-capability-boundary-humanizer-ui-pln-review.md
---

# Requirement Truth: Truth Human-Readable + i18n + Humanizer (v1.6.7 R1)

## 人话

需求包现在经常只有 AI 味的大表，人扫不完。

本湖规定：每个 feature 的 `truth.md` 必须有一层 **人能一眼看懂的摘要**（中文或英文，按 language），再保留给机器/门禁用的合同层（AC、FSM）。

写法规则蒸馏自 [blader/humanizer](https://github.com/blader/humanizer) 与 [Humanizer-zh](https://github.com/op7418/Humanizer-zh)：删空话、别吹、直接说谁-做什么-怎样算完。  
**不能**为了好读删掉 AC ID 或业务状态机。

## User Intent（一行）

人读得懂、中英可配；合同仍可测、可门禁。

## User Decisions（locked — GO 2026-07-18）

| ID | Decision | Value |
|----|----------|-------|
| UD-HR-001 | Dual layer | **L0 人话** + **L1 合同** 同文件；L1 为 gate 权威 |
| UD-HR-002 | Humanizer | 蒸馏 blader/humanizer + op7418/Humanizer-zh 为 Beacon **truth 专用**清单 |
| UD-HR-003 | Technical voice | L1 **中性短句**；禁止博客腔「注入灵魂」改写 AC/FSM |
| UD-HR-004 | i18n | `language: zh \| en \| bilingual`；bilingual 时 L0 中英各一段 |
| UD-HR-005 | Gate | freeze/change **缺 L0 → fail-closed**（reason: `truth_human_l0_missing`） |
| UD-HR-006 | Scope | **新写/变更**的 truth 强制；存量渐进（不一次重写全仓） |
| UD-HR-007 | Axis mount | 挂 **v1.6.7 GoalRun 主轴**（truth hard-gate companion） |
| UD-HR-008 | Skills | `beacon-gen-truth` / `beacon-gen-change` 必须引用本规范 |
| UD-HR-009 | L0 不当权威 | gate **禁止**只读 L0 放行 AC |
| UD-HR-010 | v2 parity | 同语义镜像湖 `beacon-v2-truth-human-readable-i18n` |

## Dual-layer contract

```text
truth.md
  frontmatter: language, slug, AC refs…
  ## 人话  或  ## Plain language     ← L0（humanizer 作用面）
  ## User Intent
  ## User Decisions / Domain FSM / Acceptance Criteria  ← L1
  ## Non-Goals
```

### L0 limits（Must）

| language | Max |
|----------|-----|
| zh | ≤ 40 行 **或** ≤ 800 汉字 |
| en | ≤ 40 lines **or** ≤ 500 words |
| bilingual | 中 + 英各满足上表 |

L0 必答四问：意图 / 能做什么 / 不能做什么 / 怎样算完成。

### Humanizer checklist（truth 专用 — Must 扫描 L0 + 叙述段）

| ID | Ban / Prefer |
|----|----------------|
| H-01 | 删填充：此外、值得注意、综上所述、It is important to note、Furthermore… |
| H-02 | 删吹嘘：至关重要、关键时刻、evolving landscape、seamless、robust、comprehensive（空泛时） |
| H-03 | 破三段式排比与否定式排比堆砌 |
| H-04 | 直接主谓宾；少「作为…的证明」 |
| H-05 | 模糊归因（专家认为/行业报告显示）→ 写具体源或删 |
| H-06 | L1 表格式 AC/FSM **豁免**修辞规则；只要求清晰可测 |
| H-07 | 中文用 Humanizer-zh 词表；英文用 blader 词表 |

Canonical norms files（implement 落盘）:

- `skills/beacon/references/truth-humanizer/truth_prose.zh.md`
- `skills/beacon/references/truth-humanizer/truth_prose.en.md`
- `skills/beacon/examples/truth-human-readable.zh.md`
- `skills/beacon/examples/truth-human-readable.en.md`

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-HR-001 | l0-heading | truth 含 `## 人话` 或 `## Plain language`（按 language）（**Must**） |
| AC-HR-002 | l0-budget | L0 不超过 UD-HR 限额（**Must**） |
| AC-HR-003 | l0-four-q | L0 覆盖意图/能做/不能做/完成（**Must**） |
| AC-HR-004 | humanizer-norms | 规范文件存在且被 gen-truth/change 引用（**Must**） |
| AC-HR-005 | freeze-gate | 缺 L0 → freeze fail-closed `truth_human_l0_missing`（**Must**） |
| AC-HR-006 | l1-authority | gate 校验 AC/FSM 仍读 L1；L0  alone 不足（**Must**） |
| AC-HR-007 | i18n-fm | frontmatter `language` 合法枚举（**Must**） |
| AC-HR-008 | bilingual | language=bilingual 时双 L0 段（**Must**） |
| AC-HR-009 | examples | zh+en 示例可复制（**Must**） |
| AC-HR-010 | axis | 主轴 mount + regenerate后 validate ok（**Must**） |
| AC-HR-011 | incremental | 存量全量蒸馏 **非**本湖 P0；工具支持按 slug 扫（**Should**） |
| AC-HR-012 | no-weaken | humanizer 不得删除/改写 AC ID 语义（**Must**） |

## Domain FSM — TruthProseGate（子机；不得 complete GoalRun）

| State | From | Guard |
|-------|------|-------|
| unchecked | — | open package |
| l0_present | unchecked | heading found |
| l0_budget_ok | l0_present | within limits |
| humanizer_scanned | l0_budget_ok | checklist run |
| pass | humanizer_scanned | no Must fails |
| fail_closed | * | missing L0 / over budget / weaken AC |

Illegal: `fail_closed` → freeze_ready；`TruthProseGate.pass` → GoalRun.completed。

## Non-Goals

- 文学润色、营销文案
- 替换 domain FSM / ui-state-matrix
- 一次改写全部历史 truth
- 用 L0 替代 tests/AC

## done_when（本湖）

- 规范 + 示例落盘
- freeze 门有 reason_code
- 主轴含本湖
- 合同测通过（见 tests.md）
