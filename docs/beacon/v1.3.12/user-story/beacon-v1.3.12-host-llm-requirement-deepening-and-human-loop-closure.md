# User Story: Beacon v1.3.12 host-LLM requirement deepening and human-loop closure

## Story Boundary

- version: `v1.3.12`
- feature: `beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure`
- status: `freeze-ready`
- upstream_prd: `docs/beacon/v1.3.12/prd/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- current_revision: `R1`
- source_revision: `R0`

本故事线覆盖 Beacon 在 `v1.3.12` 中把 `prd / user-story / test-case` 从 formal package projection 提升为 host-assisted requirement deepening closure。它不新增公开 stage，不替代 `implement / qa / release`，而是要求现有 `beacon-prd / beacon-user-story / beacon-test-case` 成为统一的人机补齐主面，并把补齐结果重新冻结进三份正式 requirement 文档。

## Diagram Truth

- `branch-flow`
  - 人类补齐与回流必须经过 `prd -> brainstorm -> user-story -> test-case -> implement -> qa -> release` 的显式分支路由
  - `change` 只接收需要改 truth 的分支，不接收单纯补覆盖的候选
- `decision-priority`
  - `accepted / rejected / deferred` 决定候选是否写回 truth
  - `pass / pass_with_downgrade / blocked` 决定 delivery 层是否可以继续前进
  - 当二者冲突时，优先级必须显式记录，而不是默默覆盖

## Story 1: PRD 必须先被编译成可持续深挖的 requirement envelope

作为 Beacon requirement owner，我希望单份 PRD 不再只是 markdown 文本，而是先被编译成稳定的 requirement deepening envelope，这样后续 story discovery 与 test-case expansion 都建立在同一套结构化 truth 上。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | requirement-envelope | Beacon 能围绕单份 PRD 结构化生成 `actors / capability_differences / state_machine / happy_paths / negative_paths / boundary_conditions / exceptions / recovery_paths / risks / open_questions` 十类 requirement 维度。 |
| AC-002 | prd-anchored-inference | envelope 的所有推导都必须绑定明确 `source_truth_ref`，证明其来源于当前 PRD 或同 feature 已冻结 requirement materials，而不是脱离 truth 的自由扩写。 |
| AC-003 | machine-readable-envelope | deepening envelope 必须落为 machine-readable artifact，并可被 `user-story / test-case / delivery completeness` 读取。 |
| AC-004 | envelope-not-public-stage | envelope 是 requirement compile 的内部推导面，不新增新的公开 lifecycle stage，也不要求人类长期理解内部 runtime 细节。 |

## Story 2: `user-story` 必须围绕 PRD 主动发现缺失故事，而不是只复述现有 story/AC

作为产品负责人，我希望 `user-story` 在 host-native deepening 可用时，能够围绕 PRD 主动发现角色差异、状态转换、异常恢复和治理补充故事，这样 requirement package 的故事层不再只是一份轻量转录稿。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | story-discovery | `user-story` 至少能发现主角色目标故事、次角色/对立角色能力差异故事、状态转换故事、异常恢复故事、权限/约束差异故事、治理补充故事六类 candidate。 |
| AC-102 | story-candidate-status | 每个 story candidate 至少要区分 `already_frozen / candidate_missing / deferred / rejected` 四类状态，而不是只给出一份匿名建议清单。 |
| AC-103 | not-just-ac-reprojection | 对至少一个真实 feature，`user-story` 必须能证明自己产出的新增候选不只是复述当前 markdown 中已有 AC 文本。 |
| AC-104 | story-writeback-target | 当人类接受某个 story candidate 后，系统必须明确把它写回到 `story boundary / acceptance criteria / metadata scope` 中的正确位置。 |

## Story 3: `test-case` 必须围绕 PRD 与 story 主动扩展风险、边界、异常与 downgrade 覆盖

作为交付与 QA 负责人，我希望 `test-case` 能围绕 PRD 和 story 主动扩展风险驱动的覆盖族群，而不是仅把当前 AC 机械映射成默认 matrix。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | risk-coverage-families | `test-case` 至少显式评估并展开 `happy / negative / boundary / exception / recovery / compatibility / permission / stale-data-or-drift / downgrade-or-fallback` 九类覆盖族群。 |
| AC-202 | traceable-coverage-rationale | 每一类新增 coverage candidate 都必须带 `source_truth_ref / rationale / risk_family / writeback_target`，说明为什么要测。 |
| AC-203 | beyond-default-matrix | 对至少一个真实 feature，`test-case` 必须能证明自己补出的覆盖项不只是默认 `AC -> TC` 机械映射。 |
| AC-204 | executable-coverage-writeback | 人类接受某个 coverage candidate 后，系统必须能把它写回正式 `qa/test-cases` 文档及对应 machine coverage artifact。 |

## Story 4: 三个 public subskill 必须共享统一的人机补齐协议

作为 Beacon 操作者，我希望 `beacon-prd / beacon-user-story / beacon-test-case` 不再各自形成不同的补问与写回语义，而是共享统一 supplement protocol，这样 requirement 补齐是可持续、可审计、可重放的。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | supplement-contract | 三个 public subskill 至少共享一套 `gap discovery -> human decision -> writeback target -> audit trail` 的补齐协议。 |
| AC-302 | stage-appropriate-routing | PRD-level gap 可以被上游 story/test-case 面引用，但最终写回位置必须明确落在 PRD、Story 或 Test Case 的正确层，而不是任意追加。 |
| AC-303 | decision-spectrum | 人类对候选 requirement 的处理至少支持 `accepted / rejected / deferred` 三类决定，并要求记录原因。 |
| AC-304 | no-silent-manual-patch | 人类补齐 requirement 后，系统必须留下 machine-readable decision log，而不是允许 story/test-case 只在 markdown 里静默手工修改。 |

## Story 5: deepening evidence、candidate ledger 与 anti-drift re-freeze 必须成为正式 requirement package 资产

作为 requirement governance owner，我希望 Beacon 把 deepening 过程中发现的 gap、候选、决定、写回和 freeze 结果都做成正式 machine assets，并继续遵守 `v1.3.11` 已冻结的 anti-drift 规则。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | candidate-ledger-fields | candidate ledger 至少记录 `gap_id / gap_type / source_truth_ref / candidate_kind / candidate_payload / rationale / confidence / human_decision / writeback_target / resolved_at`。 |
| AC-402 | revision-transaction-binding | 当候选被接受并写回 formal truth 时，系统必须能把该决定绑定到 `revision_id / source_hash / transaction_id`，避免后续 re-freeze 无法判断属于哪一轮 truth。 |
| AC-403 | anti-drift-preserved | human-loop 补齐后的 requirement package 仍必须满足 machine mirror 重投影、stale mirror 可审计、断裂时 fail-closed 的 anti-drift 规则。 |
| AC-404 | future-rounds-queryable | 被 rejected 或 deferred 的 candidate 不得消失在聊天历史中，而必须保留为未来 requirement round 可查询对象。 |

## Story 6: delivery layer 必须能读取 requirement completeness，并基于它解释 readiness

作为交付负责人，我希望 `prototype / implement / qa / release` 至少能读取 requirement completeness，而不是在 requirement 稀疏时继续假装上游已经冻结完整。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | completeness-read-model | delivery layer 至少能读取 `unresolved_gap_count / high-risk unresolved categories / downgrade-fallback status / role-state-risk coverage completeness`。 |
| AC-502 | readiness-verdict | 系统必须明确 requirement completeness 的至少三种 verdict：`pass / pass_with_downgrade / blocked`。 |
| AC-503 | deterministic-blocking | 对于 high-severity unresolved gaps、不可接受的 host downgrade、或关键 coverage family 缺失，delivery layer 必须能解释为什么当前不够 `freeze-ready / implement-ready / release-ready`。 |
| AC-504 | no-delivery-truth-rewrite | delivery layer 可以读取 completeness、报告 risk、触发回流，但不得绕过 `prd / user-story / test-case` 主链自行改写 requirement truth。 |

## Story 7: `Beacon Acceptance Kit v1` 必须成为统一验收 contract

作为 Beacon delivery owner，我希望 Beacon 把 `skill-contract / scenario-suite / trace-scorecard / real-project-proof` 收敛成一套统一验收 contract，这样 `prd / user-story / test-case / status / board / implement` 可以共用同一份验收底座，而不是各自理解各自的验收标准。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | unified-acceptance-contract | 系统必须把 `skill-contract / scenario-suite / trace-scorecard / real-project-proof` 作为统一验收底座投影为 machine-readable artifact，并允许 `prd / user-story / test-case / status / board / implement` 共用读取。 |
| AC-602 | layered-verdict-ladder | 系统必须显式产出 `Contract Pass / Scenario Pass / Trace Pass / Real Project Pass / Regression Pass` 五层 verdict，且任何更高层级都不能补偿更低层级失败。 |

## Story 8: `status / board` 与真实项目验证必须投影同一套验收底座

作为人类操作者，我希望 `status / board` 能直接看到卡在哪个子 gate，并能跳回具体补料项；同时真实项目验证、release proof 和回归检查必须消费同一套 Acceptance Kit 结果，这样验收不会在不同面之间打架。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-701 | board-gate-projection | `status / board` 至少必须显示当前卡点、对应补料项、以及可跳回 `user-story / test-case` 的入口。 |
| AC-702 | real-project-shared-proof | `real-project-validation`、release proof 与回归检查必须读取同一套 Acceptance Kit 结果与证据链，并把 `real_project_proof` 作为 release 侧正式证明输入。 |

## Delivery Notes

- 本故事线是 `v1.3.12` requirement deepening 的正式 story package，不代表已经实现。
- 它的目标不是新增 requirement public stage，而是把既有 `prd / user-story / test-case` 压成一个可持续的人机补齐闭环。
- 下一阶段应基于本 story 进入 test-case 与 machine artifacts 设计、再进入实现与 gate 验证。

## Freeze Notes

- 当前 story package 的冻结前提不是“所有代码完成”，而是：
  - story candidate family 已定义完整
  - writeback target 已固定
  - supplement decision spectrum 已固定
  - delivery completeness read model 已固定
- 如果后续实现无法产出 machine-readable decision trail、candidate ledger 或 completeness verdict，则本 story 必须从 `freeze-ready` 退回 `blocked`。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 13 |
| Status | freeze-ready-requirement-deepening-r1 |
| Created | 2026-05-05 |
| Change Scope | prd-envelope / story-discovery / risk-coverage-expansion / supplement-protocol / candidate-ledger / anti-drift-refreeze / completeness-read-model |
