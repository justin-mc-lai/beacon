# User Story: Beacon 原型设计治理与 autoresearch 发散补全闭环（v1.1.12）

**Feature**: `beacon-prototype-design-governance-loop`
**Version**: `v1.1.12`

## Story

**As a** 使用 Beacon 管理需求、原型、设计评审、前端实现与验收闭环的产品负责人 / 设计协作者 / 前端负责人 / QA owner / AI coding agent
**I want** Beacon 把 `autoresearch` 的小面发散能力、`prototype reference-pack-v2` 的结构化编译能力、`$frontend-design` 的生成性设计约束、`$web-design-guidelines` 的正式规则审查，以及项目模式/执行面/learning-plane 的边界治理合并成一个持续迭代闭环，并明确支持参考 GemDesign / Figma 工作方式、但由 Beacon 内部 LLM 直接产出原型的“描述即设计”模式
**So that** 高保真原型不只“结构完整”，还会在每轮中持续补齐页面/状态/边界/视觉系统/可访问性，把“需求描述 → 可交互高保真原型 → freeze/gate”收成正式链路，并把设计审查结果回流到下一轮 bounded iteration，同时避免 Beacon 因版本真相漂移、错误的 native 路由、宽边界 project orchestration 或 takeover 基线缺失而把任务带到错误执行面

## Story Slices

### US-001: Autoresearch 只扩展 prototype/design 的小策略面
作为系统设计者，我希望 autoresearch 只优化页面 inventory、state expansion、design brief extraction、route/fallback completeness、guideline threshold 等小面，而不是直接开放整仓前端自修改。

### US-002: Prototype 生成前必须先编译设计 brief
作为设计协作者，我希望 Beacon 在 `prototype plan/create` 前先从 story/prd/research 中编译出 design brief，而不是把视觉方向留给临场 prompt。

### US-002A: Beacon 要显式支持“描述即设计”模式
作为产品负责人，我希望 Beacon 明确把 LLM 驱动的 `description-as-design` 作为 prototype generation mode，而不是只把设计 brief 当附属备注。

### US-003: `$frontend-design` 成为 generation-side 合同输入
作为前端负责人，我希望 `frontend-design` 的审美方向、字体、色彩、空间、动效和 differentiator 被落成 machine-readable contract，再驱动 reference pack 生成。

### US-004: `$web-design-guidelines` 成为 review-side 正式门禁
作为 QA owner，我希望最新 Web Interface Guidelines 被正式拉入 review/gate，而不只是人工附加检查。

### US-005: Design review finding 必须回流下一轮迭代
作为 Beacon 维护者，我希望 design guideline failures、visual regressions、generic-style findings 与 UX/a11y gaps 能写回 keep/discard 与 next iteration input。

### US-006: 高保真页面既要 truthful，也要 distinct
作为产品负责人，我希望 Beacon 生成的 reference pack 不只是“页面都在”，还必须避免明显通用化审美，具备明确风格方向与共享视觉系统。

### US-007: 设计治理结果可被 implementation / QA / gate 消费
作为 release owner，我希望设计 brief、design-system contract、guideline audit 和 review outcome 都能成为后续实现、测试、gate 与 freeze 的正式输入。

### US-008: 原型要参考 GemDesign/Figma 的工作方式，但由 Beacon 内部直接生成
作为设计协作者，我希望 Beacon 借鉴 GemDesign/Figma 的“需求描述 -> 高保真交互原型 -> 冻结交付”工作方式，但原型本身由 Beacon 内部 LLM 生成，而不是依赖外部设计工具作为主执行面。

### US-009: 版本真相必须单源
作为 release owner，我希望 skill、runtime、release docs 和 current docs line 都读取同一个 machine-readable 版本真相源，而不是靠多处文案拼接推断当前版本线。

### US-010: navigator 必须先看 profile/stage binding 再推荐动作
作为项目交付 owner，我希望 Beacon 的 help / doctor / status 在推荐 implement / verify / review 下一步前，先解析 feature profile、stage binding 与 project mode，而不是默认推荐 Beacon native 路径。

### US-011: project skill orchestration 必须有 capability boundary
作为平台维护者，我希望 Beacon 在运行 project skill orchestration 前先校验 skill 的 supported stage、capabilities 与 evidence contract，而不是把 project profile 节点退化成任意 shell command。

### US-012: learning plane 的 mutation surface 必须 typed
作为 autoresearch 维护者，我希望 Beacon 把 learning plane 至少拆成 qa_policy / design_policy / contract_policy / debug_policy 等类型化小面，而不是继续把多种问题都压进泛化 requirement rewrite。

### US-013: takeover 项目必须先冻结 current-state baseline
作为 takeover 项目负责人，我希望 Beacon 在 architecture / current-state-service-map / refactor-boundaries 和当前版本 freeze 缺失时阻止进入 implement，这样 current-state truth 不会被后续 feature workflow 覆盖。

### US-014: 项目 service-slice 文档只能作为只读 contract input
作为 profile 项目 owner，我希望类似 rolo 的 service-slice map、boundary docs、QA evolution blueprint 只被 Beacon 用作 gate / drift / verify 的只读输入，而不是被误吸收为 Beacon core 的通用执行脚本面。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Small Editable Surface | autoresearch 仅允许优化 prototype/design 的 prompt policy、rule policy、design brief extractor、guideline mapping、review thresholds |
| AC-002 | Design Brief Artifact | `prototype plan` 之前必须产出 `design-brief.json`，包含 audience、tone、visual direction、typography intent、color intent、motion intent、differentiator |
| AC-002A | Description-as-Design Mode | design brief 必须显式包含 `design_generation_mode=description-as-design` 或等价字段，并可声明 interactive prototype required |
| AC-003 | Frontend-design Contract | `frontend-design` 输出被规范化为 `design-system-contract.json` 或等价 artifact，供 prototype renderer 消费 |
| AC-004 | Distinct Aesthetic Guard | design contract 必须能表达并约束“禁止 generic AI aesthetic”，至少覆盖字体、配色、布局/空间、动效策略 |
| AC-005 | Shared Token Discipline | high-fidelity pages 必须受共享 token 驱动，不允许 page-level 失控硬编码绕过视觉系统 |
| AC-006 | Guideline Audit Artifact | `prototype review` 或 `review design` 必须产出 `web-guideline-review.json`，记录规则版本、finding、severity、file refs |
| AC-007 | Web Guideline Gate | 正式 gate 必须可消费 icon button label、skip link、focus-visible、reduced-motion、form labeling、URL state、semantic heading、image dimensions 等关键规则 |
| AC-008 | Visual Review Outcome | Beacon 必须能输出 `design_review_outcome`，至少区分 `pass / revise / blocked` |
| AC-009 | Iteration Writeback | design findings 必须回写 next iteration input，至少覆盖 page additions、state additions、design-brief edits、guideline fixes |
| AC-010 | Keep / Discard Governance | 每轮 design/prototype policy 迭代必须写入 keep/discard ledger，不满足 benchmark 或 gate 的变更必须 discard |
| AC-011 | Consumer Compatibility | implementation / qa / gate / freeze 均可消费 design brief、design-system contract、guideline audit artifacts |
| AC-011A | Design Mode References | design brief / design-system contract 必须可声明 GemDesign/Figma 风格的工作方式参考，但语义必须明确为 Beacon 内部生成模式 |
| AC-012 | Backward Compatibility | 未启用 design governance 的旧 prototype line 不被破坏，但必须显式标记不具备 design-governed guarantee |
| AC-013 | Version Truth Source | skill / runtime / release docs / current docs line 必须读取统一的 machine-readable 版本真相源，并显式区分 planning line 与 runtime line |
| AC-014 | Profile-aware Navigator | help / doctor / status 在推荐 implement / verify / review 前必须先解析 project mode、feature binding、profile gate 与 stage-local execution surface |
| AC-015 | Capability-bounded Orchestration | project skill orchestration 运行前必须校验 `supported_stages`、`capabilities`、`evidence_contract`，不满足则 blocked |
| AC-016 | Typed Learning Surfaces | learning plane 至少拆出 `qa_policy`、`design_policy`、`contract_policy`、`debug_policy`、`rewrite_policy`、`benchmark_policy` |
| AC-017 | Takeover Baseline Gate | takeover 项目在缺少 architecture/current-state/refactor-boundary/freeze baseline 时不得进入 implement |
| AC-018 | Read-only Project Contract Inputs | 项目 boundary / service-slice / QA evolution 文档只可作为 verify/review/gate 的只读 contract input，不可变成 Beacon core 的默认执行面 |

## First-principles Loop

Beacon 在这条线上的正确闭环应该是：

```text
version truth / project mode / execution surface
→ story / prd / research
→ bounded autoresearch divergence
→ design brief convergence
→ prototype plan / page-spec compilation
→ reference-pack rendering
→ web-guideline audit
→ design review outcome
→ continue_decision
→ next iteration keep/discard
→ freeze / gate only if trusted
```

不是：

```text
生成 HTML
→ 人工看起来差不多
→ freeze
```

## Notes

- `v1.1.11` 已经解决“结构 truthful”的主问题；`v1.1.12` 解决“设计 truthful”的主问题。
- `v1.1.12` 还必须解决“边界 truthful”的问题，否则 design governance 会被错误执行面带偏。
- `frontend-design` 的职责是生成性约束，不是后置 lint。
- `web-design-guidelines` 的职责是正式审查，不是风格灵感。
- autoresearch 应回流 design/prototype policy，而不是直接无限制改页面代码。
- Beacon core 应优化判断系统，不应吞并项目执行系统。
