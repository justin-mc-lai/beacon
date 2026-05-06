# PRD: Beacon v1.3.12 host-LLM requirement deepening and human-loop closure

**Feature**: `beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure`  
**Version**: `v1.3.12`  
**Date**: `2026-05-05`  
**Status**: `freeze-ready`  
**Track**: `main`  
**Scenario**: `requirement_package_governance + host_native_semantic_runtime`  
**Template**: `主 PRD / requirement-deepening`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Prior version summary: `docs/beacon/v1.3.11/SUMMARY.md`
- Prior execution index: `docs/beacon/v1.3.11/execution/index.md`
- Prior runtime governance PRD:
  - `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- Prior PRD anti-drift PRD:
  - `docs/beacon/v1.3.11/prd/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- Prior host runtime line:
  - `docs/beacon/v1.3.6/prd/beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.md`
- Prior LLM requirement compiler repair line:
  - `docs/beacon/v1.3.5/prd/beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler.md`
- Human-facing requirement skills:
  - `skills/beacon/beacon-prd/SKILL.md`
  - `skills/beacon/beacon-user-story/SKILL.md`
  - `skills/beacon/beacon-test-case/SKILL.md`

## 1. 问题

### 1.1 Beacon 已经能形成 requirement closure，但还不够擅长持续深挖 requirement truth

`v1.3.11` 已经把 requirement package 的 formal closure 做得比较完整：

1. `prd / user-story / test-case` 已是正式 requirement truth
2. machine mirrors、audit、gate、doctor repair 已进入主链
3. `implement / qa / release` 已被要求绑定同一份 requirement package

但仍存在一个明显缺口：

> Beacon 已经能把一份需求包冻结下来，但还不够擅长在不改变公开主面的前提下，持续把这份需求包深挖完整。

当前常见不足：

- `user-story` 偏向从现有文本中抽 AC，而不是主动发现缺失故事
- `test-case` 偏向把已有 AC 投影成 matrix，而不是主动展开边界、异常、恢复与风险面
- `prd` 到 `user-story` 到 `test-case` 之间虽然闭合，但信息密度仍不够稳定

### 1.2 当前 requirement compile 更像 projection，而不是 deep requirement compiler

Beacon 当前 requirement 生成链已经具有 host-native semantic runtime 基础，但大多数真实输出仍可能落到：

- rule extraction
- keyword bucketing
- fallback matrix generation
- default command / assertion filling

结果是：

1. 人类能看到“有文档”
2. gate 能看到“有闭环”
3. 但真实交付时仍要人工再补：
   - 角色差异
   - 状态机
   - 边界条件
   - 异常恢复
   - 风险与 downgrade
   - 跨角色与跨阶段能力差异

这说明 Beacon 当前 requirement chain 更接近：

> formal package projector

而不是：

> host-assisted requirement deepening engine

### 1.3 host-native LLM 已存在，但没有被正式提升为 requirement deepening 主能力

Beacon 已经具备以下基础：

- `host-native semantic runtime`
- `capability snapshot / fallback reason / host bridge`
- `prd / user-story / test-case / prototype` 的 host compile 入口

但这些能力当前还没有被正式组织成一个 requirement deepening loop：

1. 围绕 `PRD truth` 发现 requirement gaps
2. 形成 story/test-case candidate 扩展
3. 让人类通过现有 subskill 补齐缺失信息
4. 把补齐结果重新冻结到三份正式文档
5. 让 implement/qa/release 消费更完整的 requirement closure

### 1.4 为什么 `v1.3.12` 现在必须做这件事

如果不在这一版本显式推进：

1. `prd -> user-story -> test-case` 会继续停留在“形式闭环已成立，深挖质量不稳定”
2. host LLM 虽存在，但仍只会作为偶发 compile 辅助，而不是正式 requirement compiler
3. 人类 requirement 补齐动作仍将散落在聊天、临时补文档、手工修测试用例里
4. 后续 `prototype / implement / qa / release` 依然要承受上游 requirement 稀疏带来的返工

所以 `v1.3.12` 的主题不应是新增 stage，而应是：

> **在保持 Beacon 当前能力特性不变的前提下，把 host-native LLM 正式用作 requirement deepening 引擎，并让人类通过现有 subskill 完成补齐与重冻结。**

## 2. 目标

### 2.1 主要目标

在不改变 Beacon 公开主生命周期、不新增一级命令、不篡改 delivery closure 边界的前提下，让 Beacon 能：

1. 围绕 `PRD` 深挖更多用户故事和测试用例，而不是只做已有文本投影
2. 主动挖出角色能力差异、状态机、边界、异常、风险、恢复与 downgrade 语义
3. 将 deepening gap 暴露给 `beacon-prd / beacon-user-story / beacon-test-case` 三个现有人类面 subskill
4. 让人类补齐缺失事实、约束和决策后，重新冻结 `prd / user-story / test-case`
5. 让后续 `prototype / implement / qa / release` 消费更高密度、更可验收的 requirement package

### 2.2 非目标

- 不新增新的一级公开主命令
- 不新增新的公开 lifecycle stage
- 不让 host LLM 直接绕过人类确认改写 frozen truth
- 不把 `implement / qa / release` 的角色改写成 requirement discovery surface
- 不把 Brainstorm 重新扩张成 requirement 主流程常驻步骤
- 不要求无 host runtime 时必须阻断现有 rule path
- 不把 Beacon 改造成开放式需求聊天产品

### 2.3 Truth 与 Human Loop 边界 / 分层

`v1.3.12` 必须明确 requirement deepening 的四层边界：

1. Requirement Truth Layer
   - `prd`
   - `user-story`
   - `test-case`
   - `.machine` requirement materials
2. Deepening Inference Layer
   - host-native semantic compile
   - requirement gap detection
   - story candidate discovery
   - test-case candidate expansion
3. Human Supplement Layer
   - `beacon-prd`
   - `beacon-user-story`
   - `beacon-test-case`
   - 只负责补齐事实、约束、优先级与决策，不承担内部 runtime 理解负担
4. Delivery Closure Layer
   - `prototype`
   - `implement`
   - `qa`
   - `release`

其中：

- inference layer 可以发现缺口，但不能单独宣布 truth 完整
- human supplement layer 负责确认、补齐、裁剪和拒绝候选
- formal truth 只在 requirement 文档与 machine mirrors 中冻结

### 2.4 Diagram Truth 约束

本版本的 requirement deepening 还必须把两个显式图示语义冻结进同一份 truth：

- `branch-flow`
  - 描述 `prd -> brainstorm -> user-story -> test-case -> implement -> qa -> release` 以及 `change` 回流的分支路由
  - 用于说明哪些 gap 只补料，哪些 gap 必须升格为正式变更
- `decision-priority`
  - 描述 `accepted / rejected / deferred`、`pass / pass_with_downgrade / blocked`、以及 `brainstorm / change / help` 的优先级
  - 用于保证补齐、冻结、回流、验收的决策顺序可审计

这两个图示不是新的公开 stage，而是 delivery 计划与 QA 计划必须共同读取的结构化 truth。

## 3. 设计原则

### 3.1 保持当前人类主面不变

对外主流程仍然是：

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

`deepening` 是三个 requirement stage 的内部增强能力，不是新的 public stage。

### 3.2 PRD 仍是 requirement deepening 的锚点

`user-story` 与 `test-case` 的扩展必须围绕 PRD 的：

- problem
- goal
- boundary
- role
- state
- risk
- acceptance promise

进行，而不是仅依赖当前 story/test-case 文本表面结构。

### 3.3 host-native LLM 优先，rule fallback 保留

当 host-native semantic runtime 可用时：

- `prd / user-story / test-case` 应优先走 host-native deepening compile

当 host runtime 不可用时：

- 保留现有 rule fallback
- 显式记录 `fallback_reason`
- 明确当前 requirement package 仍可能存在 deepening gap

### 3.4 深挖结果必须可审计，而不是聊天态蒸发

任何新增 requirement insight 都必须可落盘为 machine-readable evidence，至少说明：

- 发现了什么 gap
- 来源于哪份 truth
- 为什么认为它重要
- 人类是否接受、拒绝或延后

### 3.5 人类补齐必须回写 formal truth，而不是停留在 side notes

通过 subskill 收到的人类补充，最终必须进入：

- PRD 承诺面
- User Story acceptance / story boundary
- Test Case coverage / scenario family

而不能只停留在临时聊天上下文或 implementation note。

### 3.6 delivery closure 只能消费更完整 truth，不能自行补 truth

`prototype / implement / qa / release` 可以报告 gap、drift、risk，但不能替代 requirement stage 做正式需求补齐。

## 4. 范围

### In scope

- PRD-centered requirement deepening contract
- host-native story discovery
- risk/state/boundary/exception oriented test-case expansion
- human supplement protocol for `beacon-prd / beacon-user-story / beacon-test-case`
- deepening evidence / gap register / candidate rationale
- accepted/rejected/deferred candidate writeback contract
- human-confirmed re-freeze semantics for requirement package

### Out of scope

- 新的交互式 requirement cockpit
- 独立 requirement analyst agent 公共产品面
- 自动绕过人类审批冻结需求
- 改写 `prototype / implement / qa / release` 现有命令职责
- 强制所有项目依赖外部 provider API

## 5. 功能需求

### FR-001 Beacon 必须为 PRD 建立 requirement deepening envelope

围绕单份 PRD，Beacon 必须能稳定抽出并结构化表达至少以下 requirement 维度：

- `actors`
- `capability_differences`
- `state_machine`
- `happy_paths`
- `negative_paths`
- `boundary_conditions`
- `exceptions`
- `recovery_paths`
- `risks`
- `open_questions`

该 envelope 不是新的 public truth 文档，而是三份 formal truth 的推导源。

### FR-002 `user-story` 必须从 PRD 主动发现缺失故事，而不只抽取现有 AC

当 host-native deepening 可用时，`user-story` 必须能基于 PRD envelope 发现至少以下类型的候选故事：

- 主角色目标故事
- 次角色/对立角色能力差异故事
- 状态转换故事
- 异常与恢复故事
- 权限/约束差异故事
- 运营/审计/治理类补充故事

并且必须区分：

- `already_frozen`
- `candidate_missing`
- `deferred`

### FR-003 `test-case` 必须从 PRD 与 story 主动扩展覆盖族群

当 host-native deepening 可用时，`test-case` 不得只把当前 AC 映射成默认 matrix，而必须显式评估并展开：

- happy
- negative
- boundary
- exception
- recovery
- compatibility
- permission
- stale-data / drift
- downgrade / fallback

并为每个覆盖族群给出：

- 来源 truth
- 覆盖理由
- 是否已正式冻结

### FR-004 三个 subskill 必须成为同一套补齐协议的人类面

`beacon-prd / beacon-user-story / beacon-test-case` 必须共享一套 requirement supplement contract，至少支持：

- machine 发现 gap
- 人类回答/确认/拒绝
- 将结果落入正确文档层级
- 记录补齐原因与来源

禁止出现：

- PRD gap 只能在 PRD 面补，story/test-case 无法承接
- story gap 只能手工改 markdown，机器无痕
- test-case gap 只能临时记在 QA note

### FR-005 Beacon 必须为 requirement deepening 保存 gap register 与 candidate ledger

针对单个 feature，系统必须至少保存：

- `gap_id`
- `gap_type`
- `source_truth_ref`
- `candidate_kind`
- `candidate_payload`
- `rationale`
- `confidence`
- `human_decision`
- `writeback_target`
- `resolved_at`

其目标是支持持续深挖，而不是每次重跑后丢失上次发现。

### FR-006 人类确认后的补齐必须触发正确 writeback

当人类接受某个 deepening candidate 后，Beacon 必须能明确将其路由到：

- PRD promised surface
- User Story story boundary / acceptance criteria
- Test Case scenario family / executable coverage

而不是无差别追加到任意文档尾部。

### FR-007 requirement re-freeze 必须保持 anti-drift 一致性

`v1.3.12` 的 deepening writeback 必须继续遵循 `v1.3.11` 已冻结的 anti-drift 要求：

- human truth 可修订
- machine mirror 必须重投影
- stale mirror 必须可审计
- requirement package 断裂必须阻断后续 gate

### FR-008 host-native capability 与 downgrade 必须显式进入 requirement contract

每次 `prd / user-story / test-case` 深挖都必须记录：

- requested mode
- effective mode
- host capability snapshot
- fallback reason
- downgrade impact

并且 downgrade 不得伪装成“与 host deepening 等价”。

### FR-009 deepening 输出必须保留拒绝与延后语义

人类对候选 requirement 的处理不应只有“接受”：

- 接受：进入 formal truth
- 拒绝：保留 rejection reason
- 延后：进入 deferred queue，并说明不进入当前 freeze 的原因

否则 requirement deepening 会重新制造隐式 scope creep。

### FR-010 delivery closure 必须能读取 requirement deepening completeness

后续 `prototype / implement / qa / release` 至少必须能读取：

- 当前 feature 是否仍有 high-severity unresolved gaps
- 当前 package 是否存在 host downgrade
- 哪些 risks 已进入 test-case coverage
- 哪些角色/状态/异常仍未冻结

其目标不是让 delivery 层自己补需求，而是让它知道 requirement completeness 的真实边界。

## 6. 数据 / 状态 / 集成

### 6.1 Truth 来源

本版本 requirement deepening 只能围绕以下正式 truth 进行：

- `docs/beacon/<version>/prd/`
- `docs/beacon/<version>/user-story/`
- `docs/beacon/<version>/qa/test-cases/`
- `docs/beacon/<version>/.machine/`
- `.beacon/state/`

### 6.2 Deepening 状态层

建议的最小 machine 状态至少包括：

- requirement deepening envelope
- gap register
- candidate ledger
- supplement decision log
- writeback projection record

### 6.3 Host runtime 集成边界

本版本要求 host-native semantic runtime 成为 deepening 首选路径，但仍允许：

- env/file transport 作为兼容输入
- provider-backed host 作为次优路径
- rule fallback 作为保底路径

其优先级必须清晰可审计。

### 6.4 冻结决定

为使 `v1.3.12` 可以作为正式 requirement package 冻结，当前版本固定以下决定：

1. requirement deepening envelope 的 machine 落点固定为：
   - `docs/beacon/v1.3.12/.machine/requirement/<feature>.freeze-contract.json`
   - `docs/beacon/v1.3.12/.machine/requirement/<feature>.completeness.json`
2. gap register、candidate ledger、supplement decision log 必须按 `feature + revision_id` 挂接，当前 requirement freeze revision 固定为 `R1`
3. 人类补齐的正式提交路径固定为：
   - `decision log`
   - `writeback projection`
   - `truth refreeze`
   而不是允许直接只改 markdown 不留机读决策痕迹
4. `prototype` 的 requirement admission 规则固定为：
   - high-severity unresolved gap -> `blocked`
   - 关键 coverage family 缺失 -> `blocked`
   - host downgrade 但 fallback contract 完整 -> `pass_with_downgrade`
   - 其余可审计 deferred 项 -> `warning but not block`
5. 三个 public skill 现有 `v1.3.9` 文案视为文档版本漂移，不改变 `v1.3.12` requirement truth；真正 blocking 的是补齐协议与 freeze contract 是否完整

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| LLM 深挖引入 scope creep | 高 | 引入 accepted/rejected/deferred 语义，所有候选都必须经过人类确认 |
| 深挖结果无法稳定落回三份 formal truth | 高 | 为 PRD / user-story / test-case 定义明确 writeback target |
| host 不可用时系统表现退化但用户无感 | 高 | 记录 capability snapshot / fallback reason / downgrade impact |
| deepening 证据蒸发成聊天历史 | 中 | 引入 gap register 与 candidate ledger 落盘 |
| delivery 层开始反向补需求 | 高 | 明确 prototype/implement/qa/release 只能读取 completeness，不可改写 truth |

## 8. 验收标准

### AC-001 Beacon 能围绕 PRD 产出完整的 requirement deepening envelope

对于单个 feature，系统至少能从 PRD 中稳定识别：

- 角色
- 角色差异
- 状态
- 主路径
- 边界
- 异常
- 恢复
- 风险

并形成 machine-readable envelope。

### AC-002 `user-story` 能从 PRD 主动发现缺失故事

对于至少一个真实 feature，系统必须能证明：

- 不只复述当前 story 文本
- 至少新增一类缺失故事候选
- 明确该候选属于角色差异、状态机、异常恢复或治理补充中的一种

### AC-003 `test-case` 能从 PRD/story 主动扩展风险与边界覆盖

对于至少一个真实 feature，系统必须能证明：

- 不只输出默认 `AC -> TC` matrix
- 至少明确补出 boundary / exception / recovery / downgrade 中的两类覆盖
- 每类覆盖都能追溯到对应 truth 与风险理由

### AC-004 三个人类面 subskill 能完成 requirement 补齐闭环

对于至少一个真实 feature，系统必须能证明：

- machine 能报告 gap
- 人类能通过现有 `beacon-prd / beacon-user-story / beacon-test-case` 入口补齐
- 补齐结果会回写 formal truth
- 回写后 machine materials 会同步更新

### AC-005 host-native 与 fallback 路径可区分

在 host 可用与 host 不可用两类场景下，系统必须能证明：

- `effective_mode` 可区分
- `fallback_reason` 可追溯
- downgrade 不会被误判为完整 deepening

### AC-006 requirement re-freeze 不破坏 anti-drift

当通过 human-loop 补齐 requirement 后，系统必须能证明：

- human truth 与 machine mirror 一致
- stale mirror 可被 audit 发现
- requirement package 仍可通过正式 gate 验证

### AC-007 delivery layer 可读取 requirement completeness

`prototype / implement / qa / release` 至少必须能读取：

- unresolved gap count
- high-risk unresolved categories
- downgrade/fallback status
- role/state/risk coverage completeness

并用于解释“为什么当前不够 freeze-ready / implement-ready / release-ready”。

## 9. 成功指标

- 主指标：围绕单份 PRD 需要人工额外口头补需求的次数显著下降
- 辅指标：`user-story / test-case` 中由 PRD 主动挖出的新增高价值条目数量上升
- 交付指标：`prototype / implement / qa` 因上游 requirement 稀疏导致的返工减少
- 质量指标：host downgrade 场景被显式识别，而不是静默混入正常 requirement compile

## 10. 依赖与冻结决策

- requirement deepening envelope 的正式 machine 合同落点固定在：
  - `docs/beacon/v1.3.12/.machine/requirement/`
- gap register、candidate ledger、supplement decision log 固定按 `feature revision` 维度治理
- 人类补齐动作固定采用：
  - `decision log -> writeback projection -> truth refreeze`
- `prototype` admission 的最小阻断规则固定为：
  - `high-severity unresolved gap`
  - `critical coverage family missing`
  - `host downgrade without explicit fallback contract`
- public skill 文案版本漂移记录为非阻断遗留项；只有当它导致 truth 路由错误时才升级为 blocker

## 10.1 Requirement Freeze Verdict

对于本 feature，`v1.3.12` requirement package 的冻结结论定义为：

- `requirement_freeze_verdict = pass`
- `implementation_verdict = pending`
- `qa_execution_verdict = pending`

解释：

- 三份 requirement 文档已经对齐到同一条 deepening 主线
- freeze 阶段允许“实现未开始”，但不允许“requirement contract 未定”
- 后续如果 `.machine` completeness、decision trail、writeback target 任一失配，结论必须降级为 `blocked`

## 11. Diagram Truth Layer

### 11.1 Diagram Types

- `story-discovery-flow`
- `state-machine`
- `risk-coverage-map`

### 11.2 State Axes

- `requirement_gap_axis`
- `unseen_role_difference`
- `unseen_state_transition`
- `unseen_boundary_case`
- `unseen_exception_path`
- `unseen_recovery_path`
- `human_decision_axis`
- `accepted`
- `rejected`
- `deferred`
- `compile_mode_axis`
- `host_native`
- `provider_backed_host`
- `rule_fallback`

### 11.3 Propagation Contract

- Deepening findings must not remain only in inference output.
- Accepted findings must propagate into formal truth and machine mirrors.
- Rejected or deferred findings must stay queryable for future rounds without silently reappearing as accepted truth.

---

**Created**: 2026-05-05  
**Version**: v1.3.12  
**Status**: draft  
**Memory Context**: v1.3.11 requirement closure + host-native semantic runtime + human-loop requirement deepening
