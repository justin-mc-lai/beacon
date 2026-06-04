# User Story: Beacon v1.4.0 LLM decision surface and learning loop evolution

## Story Boundary

- version: `v1.4.0`
- feature: `beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution`
- status: `freeze-ready`
- upstream_prd: `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- current_revision: `R1`
- source_revision: `R0`

本故事线覆盖 Beacon 在 `v1.4.0` 中继续减重、释放宿主 LLM 推理与判断能力的正式拆解。目标不是新增平行命令或新 truth 系统，而是在保持 `truth / contract / gate` 独占纪律不变的前提下，复用已存在的 `ask`、learning plane、diagram truth、semantic runtime、host bridge 等能力，把它们升格为正式的 skill decision surface，并推动 Python 从“判断主载体”退回“护栏与写入主载体”。

## Diagram Truth

- `branch-flow`
  - `frozen truth -> compiled contract -> skill decision surface -> canonical route -> python guardrail -> gate / projection writeback`
  - `freeform user intent -> beacon ask -> route preview or controlled execution`
  - `requirement complexity -> diagram / semantic inputs -> deeper reasoning -> prd / user-story / test-case`
  - `learning evidence -> typed learning contract -> progressive disclosure -> next skill run`
- `decision-priority`
  - `truth > compiled contract > gate verdict > skill decision protocol > legacy python heuristics`
  - `existing capability reuse > new command invention > new truth directory invention`
  - `host-visible protocol > hidden fallback reasoning`
- `state-machine`
  - `thin_surface -> thickened_surface -> governed_surface -> stable_surface`
  - `latent_learning -> readable_learning -> injected_learning -> audited_learning`
  - `implicit_modeling -> diagram_aware -> semantic_aware -> gate_consumed`
  - `python_overloaded -> dual_read -> reduced_python -> guardrail_only`

## Story 1: 核心 skill 必须从薄 operator rule 升级为正式 decision surface

作为 Beacon 产品 owner，我希望 `prd / user-story / test-case / implement / qa / release` 这些核心 skill 不再只暴露稀薄 operator rule，而是形成稳定、可被宿主 LLM 直接消费的 decision surface，这样已有能力才能真正转化为更强的一次性判断质量，而不是继续依赖 Python 深处的 fallback。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | thickened-core-skills | 至少 `beacon-prd`、`beacon-user-story`、`beacon-test-case`、`beacon-implement`、`beacon-qa`、`beacon-release` 六个核心 skill 必须进入统一厚化治理。 |
| AC-002 | stable-sections | 每个核心 skill 至少必须具有 `Inputs Contract`、`Decision Protocol`、`Anti-Inertia Notes`、`Learning Notes`、`Backstop CLI` 五类稳定段落。 |
| AC-003 | host-readable-contract | 这些段落必须能被宿主 LLM 直接消费，避免“凭印象调用”与“只靠代码兜底”。 |
| AC-004 | no-truth-write-surface | skill surface 可以解释、建模、路由、建议，但不得成为新的 frozen truth 直写入口。 |

## Story 2: `beacon ask` 必须被冻结为正式的自然语言路由入口

作为 Beacon 使用者，我希望系统正式承认 `beacon ask` 已经存在，并把它治理成边界清楚的自然语言入口，而不是继续处于“有能力但半隐式”的状态，这样 freeform intent 能稳定被收束到合法的 Beacon surface。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | ask-is-real-surface | 系统必须明确 `beacon ask` 是现实中的公开入口，而不是待新增命令。 |
| AC-102 | ask-plan-default | `ask` 必须继续以 `plan-only` 作为默认安全模式。 |
| AC-103 | ask-execute-bounded | `ask --execute` 必须被限定为路由到合法既有 surface，且不得绕过 `implement / qa / gate` 独占入口。 |
| AC-104 | ask-no-freeform-writeback | `ask` 不得直接自由写入 frozen truth、gate verdict 或 release 状态。 |

## Story 3: `ask`、`brainstorm`、`change` 必须建立清晰分工

作为 requirement governance owner，我希望自然语言入口、只读收敛面、frozen truth 变更路由三者分工稳定，这样宿主 LLM 和人类都不会把 `ask`、`brainstorm` 误读成新的主流程 stage 或 truth 写面。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | ask-route-role | `ask` 必须被定义为自然语言入口、路由、计划预览与受控执行面。 |
| AC-202 | brainstorm-read-only-role | `brainstorm` 必须被定义为只读收敛、矛盾识别、开放问题澄清与路线建议面。 |
| AC-203 | change-truth-route | 任何触及 frozen truth 的正式变更都必须回到 `change` 路由，而不是停留在 `ask` 或 `brainstorm`。 |
| AC-204 | no-new-stage-confusion | 三者都不得替代 `prd -> user-story -> test-case -> implement -> qa -> release` 主链。 |

## Story 4: Learning plane 必须进入核心 skill 的渐进披露闭环

作为宿主 LLM，我希望在进入核心 skill 时可以读取与当前 `feature / host / runner / domain` 相关的 learning hint，而不是每次都从零推断，这样 Beacon 已经积累的经验才能被真正复用。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | reuse-learning-kernel | learning 披露必须复用现有 `learning_loop.py` typed contract 能力，而不是再造一套并行 learning 系统。 |
| AC-302 | progressive-disclosure | 系统必须支持按 `feature -> host -> runner -> domain` 顺序做 learning 渐进披露。 |
| AC-303 | learning-is-hint | learning 只能作为 hint / route input，不得直接定义 truth、gate verdict 或 release-ready。 |
| AC-304 | stale-downgrade | learning note 必须支持 stale / superseded / downgrade 语义，避免旧经验持续误导。 |

## Story 5: requirement 三件套必须具备 diagram-aware 深度思考协议

作为 requirement author，我希望 `prd / user-story / test-case` 在遇到复杂问题时被正式要求检查 `branch-flow / state-machine / decision-priority / state axis`，而不是继续用模板直接填空，这样输出才能体现状态、转移、异常路径与不变量层面的真实推理。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | diagram-trigger | 当复杂度达到 diagram truth 触发条件时，三件套不得直接生成模板化输出。 |
| AC-402 | state-transition-reasoning | `prd / user-story / test-case` 必须显式围绕状态、转移、异常路径、不变量进行建模推理。 |
| AC-403 | state-axis-awareness | 当问题具备明确状态轴时，输出必须显式识别并复用 state axis。 |
| AC-404 | diagram-consistency | 相关 requirement 输出必须与现有 diagram truth 保持一致。 |

## Story 6: semantic trace 必须成为 requirement 深度思考的共享词汇输入

作为 requirement 与实现对齐治理 owner，我希望三件套优先复用 semantic trace 中的官方状态名、动作名、模块名、页面名，而不是继续各写各的词汇，这样 requirement 与实现语义才不会长期漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | semantic-shared-input | semantic trace 必须成为 `prd / user-story / test-case` 的共享输入之一。 |
| AC-502 | official-vocabulary-reuse | 生成内容时应优先复用官方状态名、动作名、模块名、页面名。 |
| AC-503 | no-second-truth | semantic trace 可作为校验与映射输入，但不得独立升格为新的 truth root。 |
| AC-504 | wording-drift-reduction | 系统必须能减少 requirement 文本与 semantic trace 的长期词汇漂移。 |

## Story 7: requirement 建模增强必须优先升格现有 diagram 与 semantic，而不是直接新建五件 truth 目录

作为 Beacon 架构 owner，我希望 requirement 建模增强先用“升格现有能力”的方式推进，而不是立即新增一整套业务模型目录，这样 Beacon 能继续减重，而不会因治理升级反而重新变重。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | reuse-existing-modeling | 第一阶段必须优先升格现有 `diagram truth + semantic dictionary`。 |
| AC-602 | minimal-extension-only | 如确需补充 `events / invariants / entities` 等概念，也必须以最小增量方式进入。 |
| AC-603 | no-forced-five-folders | 本轮不得把完整 `business-model/` 五件目录作为前置完成条件。 |
| AC-604 | governance-before-expansion | 只有在现有建模层无法支撑质量闭环时，才允许考虑更重的结构扩展。 |

## Story 8: Python 必须从判断主载体退回护栏与写入主载体

作为内核维护者，我希望 Python 继续保留事实采集、schema 校验、contract 写入、gate 写入等机器职责，但逐步退出主要决策协议与解释职责，这样 Beacon 才能真正释放宿主 LLM 的推理与路由能力。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-701 | python-four-duties | Python 主职责必须收敛为事实采集、schema 校验、contract/projection 写入、gate 阻断与 verdict 写入。 |
| AC-702 | explanation-moves-up | 大段策略文案、主要决策协议、宿主使用说明、误区纠正等解释性逻辑应优先迁入 skill surface。 |
| AC-703 | preserve-fail-closed | 即使迁出解释逻辑，Python 仍必须保持 fail-closed 护栏角色。 |
| AC-704 | no-language-migration-fetish | 本轮目标是迁职责而不是迁语言，不得把减重误做成语言迁移项目。 |

## Story 9: `qa / implement / prd / release` 必须纳入同一轮 Python 瘦身治理

作为演进 owner，我希望 Python 职责瘦身不要只盯 `qa`，而是把 `qa / implement / prd / release` 一并纳入治理，这样系统真正重的判断负担才能被整体削减。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-801 | four-modules-covered | `beacon/commands/qa.py`、`implement.py`、`prd.py`、`release.py` 至少都必须进入瘦身分析范围。 |
| AC-802 | classify-read-vs-judge | 每个目标模块都必须区分“事实/写入逻辑”和“解释/判断逻辑”。 |
| AC-803 | migrate-judgment-first | 迁移优先级必须先针对解释/判断逻辑，而不是先动写入与护栏逻辑。 |
| AC-804 | shared-governance-view | 四类模块必须使用同一套迁移判断标准，而不是各自独立演进。 |

## Story 10: 判断逻辑迁移必须采用双读对账后再切主

作为平台稳定性 owner，我希望任何从 Python fallback 迁到 skill decision surface 的判断，都先经过双读与一致性回归，这样系统不会因为“释放 LLM”而引入隐性 verdict 漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-901 | dual-read-required | 新旧判断逻辑切换前必须先进行双读对账。 |
| AC-902 | reason-consistency | 对账至少要覆盖 blocked reason、downgrade/fallback 路线、gate 结果一致性。 |
| AC-903 | fail-closed-cutover | 一致性不足时必须保留旧 Python 作为主判定器，迁移必须 fail-closed。 |
| AC-904 | compatibility-window | 切主后仍需保留一段兼容窗口与 legacy fallback。 |

## Story 11: 核心 skill 的版本叙事必须先统一到 `v1.4.0`

作为宿主上下文治理 owner，我希望在厚化 skill surface 之前，先把核心 skill 的版本叙事统一到当前 `v1.4.0` 线，这样宿主 LLM 读到的 operator rule、docs line、runtime line 才不会彼此打架。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1001 | version-line-aligned | 核心 skill 不得继续混用 `v1.3.9 / v1.3.12 / v1.4.0` 的漂移叙事误导宿主。 |
| AC-1002 | operator-rule-synced | skill surface 的 operator rule 必须与当前运行时现实和 docs line 对齐。 |
| AC-1003 | runtime-docs-host-consistent | runtime line、docs line、host-native line 的解释必须相互一致。 |
| AC-1004 | version-fix-before-thickening | 版本面校准必须早于或至少并行于 skill 厚化，不得继续后置。 |

## Story 12: support surface 必须能解释 route 推荐原因

作为人类操作者，我希望当 Beacon 推荐我走 `brainstorm`、`change`、`implement`、`qa` 或某个 support surface 时，系统能解释为什么推荐、当前采用了哪些 learning hint，而不是只抛出命令名，这样判断才真正对人可用。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1101 | route-why-visible | `help / status / doctor / ask` 至少应能解释推荐该 route 的原因。 |
| AC-1102 | learning-use-visible | 若某次推荐采用了 learning hint，系统必须能说明采用了什么类别的 hint。 |
| AC-1103 | brainstorm-change-clarity | 系统必须能清楚说明何时建议去 `brainstorm`，何时必须回到 `change`。 |
| AC-1104 | action-over-command-dump | 人类面默认输出应优先给出动作理由，而不是只给命令列表。 |

## Story 13: prototype 必须作为本 feature 的条件触发 requirement handoff

作为 requirement governance owner，我希望这条 feature 虽然遵守“prototype 非全局默认必经层”的轻量原则，但由于它确实存在 route surface、状态显示、导航关系和交互契约 handoff 需求，所以在 `test-case` 之后被条件触发进入 `prototype`，把这些内容冻结成可审阅线框包，这样实现阶段接到的是一个完整 handoff，而不是只拿抽象规则直接编码。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1201 | prototype-stage-conditionally-required | 本 feature 必须明确声明：`prototype` 虽非全局默认必经层，但对当前 feature 属于 `test-case` 之后、`implement` 之前被条件触发的正式 stage。 |
| AC-1202 | route-surface-frozen | prototype 必须覆盖核心 skill decision surface、`ask / brainstorm / change` route surface 的页面职责与信息分层。 |
| AC-1203 | state-nav-interaction-frozen | prototype 必须至少冻结 state visibility、navigation contract、interaction contract。 |
| AC-1204 | no-implement-ready-before-prototype | 在 prototype 相关产物未冻结前，本 feature 不得表述为 `implement-ready`。 |

## Story 14: requirement gate 必须从 machine 预写前置收敛到 human truth + 最小 freeze receipt

作为 runtime governance owner，我希望 `implement / qa / release` 的 requirement gate 在保持 fail-closed 强度的同时，不再把 machine-side requirement materials 与长期 mirror 双写当成默认主链前置，而是收敛到 human truth 完整性、最小 freeze receipt 与确定性编译能力，这样 Beacon 才能同时满足“唯一冻结真相”和“继续减重”。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1301 | human-truth-hard-gate | hard gate 必须继续要求 human PRD / user-story / test-case 完整，且在条件触发时要求 prototype 完整。 |
| AC-1302 | machine-derived-not-truth | machine-side user-story、AC matrix、story scenario map、envelope、candidate ledger、decision log 等 requirement materials 必须被明确降级为 compiled projection / cache / audit evidence，而不是第二真相或默认前置。 |
| AC-1303 | deterministic-rebuild-before-block | 当 machine projection 缺失时，若能从当前 frozen human truth 确定性重建，则系统必须优先重建或按需编译，而不是直接 route 到 change。 |
| AC-1304 | minimal-freeze-receipt-hard-gate | strong gate 仍必须保留最小 freeze receipt 校验；若 baseline hash / revision receipt 证明 human truth 已漂移，系统必须继续 fail-closed 并 route 到 `beacon-change`。 |

## Delivery Notes

- 本 story package 的目标不是直接约束代码实现细节，而是把“继续减重 Beacon、释放 LLM 推力能力”的方向拆成可执行故事。
- 本轮主轴是：
  - 核心 skill thickening
  - `ask` 治理
  - learning 渐进披露
  - diagram / semantic 驱动的 requirement 深度思考
  - Python 双读迁移
  - version surface 校准
  - prototype handoff closure
- 下一阶段应基于本 story package 进入 `test-case`，冻结 route 边界、learning stale 降级、diagram-aware 输出、dual-read 一致性回归等验收矩阵。

## Freeze Notes

- 当前 story package 的冻结前提不是“代码已完成”，而是：
  - 核心 story 分组已经完整
  - `ask / brainstorm / change` 的职责边界已经清楚
  - learning、diagram、semantic、python guardrail 四层关系已经清楚
  - 迁移路线已明确要求 dual-read before cutover
  - prototype 已被明确补入 requirement 主链
- 如果后续 `test-case` 无法把：
  - `ask --execute` 边界契约
  - learning hint 渐进披露与 stale 降级
  - diagram-aware requirement reasoning
  - semantic 词汇复用
  - Python 双读一致性回归
  - prototype handoff contract
  做成正式验收对象，则本 story package 应从 `freeze-ready` 退回 `blocked`。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 13 |
| Status | freeze-ready-r2 |
| Created | 2026-05-08 |
| Change Scope | skill-surface / ask-governance / brainstorm-boundary / learning-disclosure / diagram-semantic-reasoning / python-dual-read / version-surface |
