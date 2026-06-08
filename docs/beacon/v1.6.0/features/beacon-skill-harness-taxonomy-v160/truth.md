---
slug: beacon-skill-harness-taxonomy-v160
version: v1.6.0
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md
  user_story: docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md
  test_case: docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：Beacon Skill Harness Taxonomy v1.6.0

## 概述

`beacon-skill-harness-taxonomy-v160` 定义 Beacon v1.6.0 的 breaking skill 分类体系。

目标是用 harness-first 的命名和职责模型替换历史上混杂的 host-visible skill 名称：

```text
beacon-<harness>-<function>
```

v1.6.0 接受的 harness 家族为：

- `planner`：拆分粗提示词，判断湖/海规模，读取 truth/source/evidence，并推荐路由。
- `generator`：在已接受的权限边界内创建或更新 truth、实现、原型、设计或交付产物。
- `evaluator`：验证证据，识别漂移或假交付，并阻断或路由面向 release 的决策。
- `governor`：维护 context、archive、memory、hooks、automation、metadata、status 和诊断脚手架。

## 问题

Beacon v1.5.2 已完成 package-authoritative truth 切换，但 skill surface 仍混用历史阶段名、support surface、实现入口、evaluator surface 和 toolkit 命令。

这会让粗粒度用户提示词产生歧义。例如“帮我分析这个 feature”可能在 research、truth 编辑、implementation、QA 或 release 语言之间漂移，缺少稳定的角色边界。

v1.6.0 必须在 skill 名称、共享 preamble 和 hard gate 中显式表达 harness 职责。

## 默认语言策略

Beacon 需求真相默认使用中文表达。除非用户显式指定其他语言，v1.6.0 的 canonical requirement truth、acceptance criteria、test assertions、task ledger、migration docs 和 host-visible skill preamble 都应使用中文作为主语言。

英文术语可作为稳定标识保留，例如 `truth-map resolver`、`features/<slug>/truth.md`、`beacon-<harness>-<function>`、`planner/generator/evaluator/governor`、`AC-*`、`TC-*` 和具体文件路径。英文术语只能辅助精确引用，不能让需求正文、验收语义或操作说明退回英文为主。

生成或迁移 v1.6.0 skill 时，若来源材料为英文，generator 必须把需求真相正文归一为中文；evaluator 必须把“需求真相主语言不是中文”识别为阻断项，除非存在用户明确的非中文例外。

## 生命周期模型

v1.6.0 不再把正常生命周期呈现为：

```text
prd -> user-story -> test-case
```

package-authoritative 生命周期为：

```text
plan
-> truth
-> generate
-> evaluate
-> release
```

canonical requirement authority 仍然是：

```text
truth-map resolver
-> features/<slug>/truth.md
-> features/<slug>/tests.md
-> features/<slug>/tasks.md
-> features/<slug>/evidence.md
```

旧有 `prd`、`user-story` 和 `test-case` 概念只能作为迁移说明、吸收/重建产物或内部兼容路由出现。它们不能继续作为 v1.6.0 的主要 host-visible skill 分类。

## Planner Research Contract

v1.6.0 不新增独立 plan stage。Plan 类 skill 的 canonical support artifact surface 是：

```text
docs/beacon/<version>/research/<feature-slug>.md
```

`research/` 是 planner artifact surface，authority 固定为 `support_advisory`。它可以承载调研、头暴、湖/海判断、证据锚定、风险分析、上下文收缩和路由建议，但不能成为 `requirement_truth`、不能自动写入 `features/<slug>/truth.md`、不能直接进入 implementation、不能给 QA 或 release verdict。

Planner research artifact 必须让结果可路由，而不只是可阅读。每个用于进入主链判断的 research artifact 至少包含：

- `outcome`：用户真正要达成的结果；
- `lake_or_ocean`：湖/海判断，以及拆分、标超纲或延后的理由；
- `truth_refs`：已读取的 resolver-selected truth；
- `source_refs`：已读取的源码、接口、外部资料或项目材料；
- `evidence_refs`：已读取或生成的证据；
- `truth_gap`：是否存在需求真相缺口；
- `test_gap`：是否存在验收或覆盖缺口；
- `implementation_risk`：进入 generator 前的实现风险；
- `verification_risk`：进入 evaluator 前的验证风险；
- `recommended_route`：推荐进入 `truth/change/refreeze/generate/evaluate/release/queue/defer` 的哪条路；
- `user_decision`：用户是否接受、拒绝、拆分、排队、延后或升级；
- `promotion_ref`：若被接受进入主链，必须指向对应 truth/change/refreeze/generator/evaluator artifact。

Planner research closure 只能有以下状态：

| Status | Meaning | Allowed next step |
|---|---|---|
| `queued` | 已记录但用户未接受进入主链 | 保持 queue/defer，不写 truth |
| `routeable` | 已形成明确 route recommendation，但还没有用户接受 | 等待用户确认 |
| `promoted` | 用户已确认进入主链，且已有 promotion_ref | 进入 truth/change/refreeze/generate/evaluate |
| `rejected` | 用户拒绝或明确不进入主链 | 不再推动 |
| `deferred` | 用户要求延后或拆分 | 保留 research，不进入 truth |

从 research 进入需求真相必须满足：

```text
research/support_advisory
-> user_decision = accepted/promoted
-> beacon-generator-truth-change 或 beacon-generator-truth-refreeze
-> features/<slug>/{truth,tests,tasks,evidence}.md
-> requirement_clarity
-> freeze
```

没有 `user_decision` 和 `promotion_ref` 的 research 只能作为调研证据，不能被 generator、evaluator 或 release 当作完成依据。

## 共享 Preamble

每个 v1.6.0 host-visible Beacon skill 都必须包含共享生成 preamble：

```text
Beacon v1.6.0 共享 preamble：

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。
```

preamble 必须由中心模板生成或投影到 skill 文件，不能靠手工复制，以避免漂移。

## Harness Hard Gate Injection Contract

v1.6.0 不能只依赖 CLI/function routing 治理 harness 边界。每个 host-visible `SKILL.md` 必须在共享 preamble 之后、正文能力说明之前，注入 harness-specific `HARD GATE` 块。该块是 LLM 进入 skill 后首先执行的硬门禁，用来物理阻断跨 harness 调用、越权写 truth、越权 implementation、越权 QA/release verdict 和假交付闭环。

通用格式：

```text
HARD GATE:
你正在运行 <harness> skill。
禁止调用或执行超出本 harness 边界的 skill、命令、工具或动作。
即使跨界动作看起来方便，也必须停止并路由，不能顺手执行。
唯一允许产物是 <allowed surface>。
如果用户请求需要另一个 harness，输出 route recommendation，并等待用户确认。
```

Planner HARD GATE：

```text
HARD GATE:
你正在运行 planner skill。
禁止调用 implementation/generator/evaluator/release 类 skill。
禁止写代码、搭脚手架、修改 package truth、修改 `.machine/`、给 QA/release verdict。
你的唯一产出是 research/planning artifact、gap/risk 分析、湖/海判断和 route recommendation。
如需进入 truth/change/refreeze/generate/evaluate，必须停止并路由，等待用户确认。
```

Generator HARD GATE：

```text
HARD GATE:
你正在运行 generator skill。
禁止自证完成，禁止给 QA/release verdict，禁止把 placeholder/docs-only/fake-runner/zero-assertion/placeholder-evidence 当成交付闭环。
只能在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact。
如需判断是否通过，必须路由到 evaluator。
```

Evaluator HARD GATE：

```text
HARD GATE:
你正在运行 evaluator skill。
禁止改写 requirement truth，禁止修复 implementation，禁止把 verdict 和 repair 混在同一动作里。
你的唯一产出是 evidence verdict、finding、reason code、block/pass/route recommendation。
如需修复，必须路由到 generator 或 truth/change。
```

Governor HARD GATE：

```text
HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。
```

HARD GATE 注入要求：

- HARD GATE 必须出现在每个 v1.6.0 host-visible `SKILL.md` 的共享 preamble 之后。
- HARD GATE 必须按 skill 的 harness 类型生成，不能只使用通用空话。
- HARD GATE 必须显式写出禁止调用的跨 harness skill 类别、禁止动作和唯一允许产物。
- Planner gate 必须物理禁止实现、脚手架、代码写入、truth 写入、`.machine/` 写入、QA/release verdict。
- Generator gate 必须物理禁止自证完成和 gate verdict，并绑定 no-fake-delivery。
- Evaluator gate 必须物理禁止 truth rewrite 和 implementation repair。
- Governor gate 必须物理禁止 truth/implementation/gate verdict，并保持 support/governance-only。
- agent-surface verify 必须扫描 HARD GATE：缺失、位置错误、harness 不匹配、禁止动作不完整或旧 skill alias 中存在 gate 漂移时，v1.6.0 skill package 不能通过。
- CLI/function 层治理仍然保留，但不能替代 `SKILL.md` 内的 HARD GATE。

## Harness 边界

### Planner

Planner skills 允许：

- 判断湖/海；
- 拆分范围并识别可路由缺口；
- 读取 resolver 选中的 truth、source、evidence 和受治理 memory；
- 产出 research 或 planning artifacts；
- 推荐 truth/change/implementation/QA/release 路由。

Planner skills 禁止：

- 写 implementation；
- 声称 QA pass；
- 给出 release verdict；
- 静默修改 frozen truth。

### Generator

Generator skills 允许：

- 当 skill 是 truth generator 时创建或更新 package truth；
- 当 skill 是 implementation 或 artifact generator 时创建 implementation 或 delivery artifacts；
- 通过显式 authority 把已接受的 design/prototype 结果绑定进 Beacon surfaces。

Generator skills 禁止：

- 定义自己的 gate verdict；
- 用 task progress 声称完成；
- 把 placeholder、docs-only、fake-runner、zero-assertion 或 placeholder-evidence 输出当成交付闭环；
- 不经 governed change routing 覆盖 frozen truth。

### Evaluator

Evaluator skills 允许：

- 验证 acceptance proof 和 evidence 充分性；
- 识别 truth drift、fake delivery、missing coverage、placeholder evidence 或 stale assumptions；
- 产出 reason codes 和 repair routes；
- 阻断 release。

Evaluator skills 禁止：

- 直接改写 requirement truth；
- 把 repair implementation 混入 verdict；
- 用单一代理信号通过 release readiness。

### Governor

Governor skills 允许：

- 修复 context 和 environment；
- 同步 generated projections；
- 归档 historical truth；
- 管理 queues、hooks、metadata、memory、status 和 automation scaffolding。

Governor skills 禁止：

- 成为人类主链阶段；
- 定义 requirement truth；
- 在未显式作为 gate/evaluator surface 运行时给出 QA 或 release verdict。

## Breaking Rename Requirement

v1.6.0 host-visible skills 必须使用：

```text
beacon-planner-*
beacon-generator-*
beacon-evaluator-*
beacon-governor-*
```

v1.6.0 host-visible skill package 不得保留旧 skill alias。如果临时需要 CLI 兼容，它属于 CLI migration tooling 或 registry，而不是 host-visible skill names。

## Skill Rename Rewrite Contract

v1.6.0 skill 改名必须是生成式迁移，不是手工散改。迁移器必须读取 Rename Matrix，并对每个 host-visible skill 产出新目录、新 `SKILL.md` frontmatter、新标题、新说明和共享 preamble。

改写规则：

- 新 skill 目录名必须等于 `beacon-<harness>-<function>`。
- `SKILL.md` frontmatter 的 `name` 必须等于新目录名。
- `description` 必须使用中文主语言，并说明 harness 职责、使用场景和不能越权的边界。
- skill 正文必须包含 v1.6.0 共享 preamble。
- skill 正文必须包含 harness boundary：planner 不写 truth/implementation/gate；generator 不自证完成；evaluator 不改 truth/implementation；governor 不成为主链 stage。
- 旧 host-visible skill 目录不得留作 alias、wrapper 或 duplicate skill。
- 如果 CLI 命令仍需临时兼容旧名字，兼容只能出现在 CLI registry/migration tooling，不能出现在 host-visible skill package。
- 迁移完成后，agent surface verify 必须以新 skill 名为 expected set；旧 expected set 必须失败或不存在。
- 文档中的旧 skill 名只能出现在 migration mapping、archive 或 release note，不得作为推荐入口。

按 harness 的 skill 改写策略：

| Harness | Rewrite rule |
|---|---|
| `planner` | 只能写 `research/`、queue/read model 或 route recommendation；不能写 package truth、implementation、QA verdict、release verdict。 |
| `generator` | 可以写 truth 或 implementation/delivery artifacts，但必须受 authority 和 evaluator evidence 约束；不能 claim gate pass。 |
| `evaluator` | 可以生成 verdict、finding、reason code 和 repair route；不能改 truth 或修 implementation。 |
| `governor` | 可以修 context、metadata、archive、hooks、automation、status；不能定义需求真相或成为 lifecycle stage。 |

## Rename Matrix

| Current skill | v1.6.0 skill | Harness | Role |
|---|---|---|---|
| `beacon-brainstorm` | `beacon-planner-brainstorm` | planner | Rough prompt decomposition and route convergence |
| `beacon-deep` | `beacon-planner-deep-analysis` | planner | Complex state/risk/test-delta analysis |
| `beacon-friction-intake` | `beacon-planner-friction-intake` | planner | Friction capture and queue-only governance |
| `beacon-ceo-review` | `beacon-planner-founder-review` | planner | Founder/business challenge |
| `beacon-design-review` | `beacon-planner-design-review` | planner | UX/design challenge |
| `beacon-security-review` | `beacon-planner-security-review` | planner | Security challenge |
| `beacon-performance-review` | `beacon-planner-performance-review` | planner | Performance challenge |
| `beacon-doubt-review` | `beacon-planner-doubt-review` | planner | Assumption challenge |
| `beacon-source-driven` | `beacon-planner-source-driven` | planner | Source evidence anchoring |
| `beacon-context-engineering` | `beacon-planner-context-engineering` | planner | Context reshaping |
| `beacon-truth` | `beacon-generator-truth-package` | generator | Package-authoritative truth umbrella |
| `beacon-prd` | remove or absorb into `beacon-generator-truth-package` | generator | Legacy truth drafting concept |
| `beacon-user-story` | remove or absorb into `beacon-generator-truth-package` | generator | Legacy acceptance concept |
| `beacon-test-case` | remove or absorb into `beacon-generator-truth-package` | generator | Legacy coverage concept |
| `beacon-prd-bootstrap` | `beacon-generator-truth-bootstrap` | generator | Package bootstrap |
| `beacon-change` | `beacon-generator-truth-change` | generator | Governed truth change |
| `beacon-change-refreeze` | `beacon-generator-truth-refreeze` | generator | Governed refreeze chain |
| `beacon-prototype` | `beacon-generator-prototype-binding` | generator | Accepted UI/UX result binding |
| `beacon-implement` | `beacon-generator-implementation` | generator | Implementation planning/execution |
| `beacon-design` | `beacon-generator-design-support` | generator | Design support umbrella |
| `beacon-design-bootstrap` | `beacon-generator-design-bootstrap` | generator | Design capability admission |
| `beacon-design-explore` | `beacon-generator-design-explore` | generator | UI direction exploration |
| `beacon-design-system` | `beacon-generator-design-system` | generator | Component system planning |
| `beacon-design-polish` | `beacon-generator-design-polish` | generator | UI polish support |
| `beacon-design-library` | `beacon-governor-design-library` | governor | Reference lookup |
| `beacon-design-extract` | `beacon-governor-design-extract` | governor | Screenshot/reference extraction |
| `beacon-design-simplify` | `beacon-planner-design-simplify` | planner | Simplicity audit |
| `beacon-qa` | `beacon-evaluator-qa` | evaluator | Acceptance verification |
| `beacon-qa-evo-deep` | `beacon-evaluator-qa-deep` | evaluator | Deep QA support findings |
| `beacon-release` | `beacon-evaluator-release` | evaluator | Release readiness |
| `beacon-real-project-validation` | `beacon-evaluator-real-project` | evaluator | Real project release proof |
| `beacon-documentation-adr` | `beacon-planner-documentation-adr` | planner | ADR/documentation clarity |
| `beacon-doctor` | `beacon-governor-doctor` | governor | Context/environment repair |
| `beacon-debug-recovery` | `beacon-governor-debug-recovery` | governor | Blocker recovery |
| `beacon-status` | `beacon-governor-status` | governor | Board and state visibility |
| `beacon-help` | `beacon-governor-help` | governor | Next-step guidance |
| `beacon-archive` | `beacon-governor-archive` | governor | Historical truth isolation |
| `beacon-learn` | `beacon-governor-learn` | governor | Governed learning |
| `beacon-project-hooks` | `beacon-governor-hooks` | governor | Lifecycle hook contracts |
| `beacon-toolkit-automation` | `beacon-governor-automation` | governor | Scheduled automation assets |
| `beacon-toolkit-branch-governance` | `beacon-governor-branch` | governor | Branch/worktree governance |
| `beacon-toolkit-lighthouse` | `beacon-governor-lighthouse` | governor | Fast source/repo analysis |
| `beacon-toolkit-metadata` | `beacon-governor-metadata` | governor | Deterministic metadata tooling |
| `using-beacon` | remove or replace with `beacon-governor-router` | governor | Host-level router |

## 验收标准

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | lifecycle-language | v1.6.0 用户可见文档把生命周期描述为 `plan -> truth -> generate -> evaluate -> release`，而不是 `prd -> user-story -> test-case`。 |
| AC-002 | package-authority | v1.6.0 truth 仍由 resolver 选择的 `features/<slug>/{truth,tests,tasks,evidence}.md` 承载；generated JSON 和 legacy triptych surfaces 不能赢得 authority。 |
| AC-003 | harness-prefix | 每个 v1.6.0 host-visible skill 都使用 `beacon-<harness>-<function>`，其中 harness 只能是 `planner/generator/evaluator/governor`。 |
| AC-004 | no-old-skill-aliases | v1.6.0 host-visible skill package 不保留旧 skill aliases，例如 `beacon-brainstorm`、`beacon-prd`、`beacon-user-story`、`beacon-test-case`、`beacon-implement`、`beacon-qa` 或 `beacon-release`。 |
| AC-005 | shared-preamble | 每个 v1.6.0 host-visible skill 都包含共享生成 preamble，覆盖湖/海、先搜再造、用户主权、不假交付和 harness 边界。 |
| AC-006 | planner-hard-gate | Planner skills 只能产出 research/planning artifacts 和 route recommendations；不能写 implementation、frozen truth、QA verdicts 或 release verdicts。 |
| AC-007 | generator-hard-gate | Generator skills 可在自身 authority 内产出 truth 或 implementation artifacts，但不能缺少 evaluator evidence 就声称完成，也不能用 fake delivery 闭环。 |
| AC-008 | evaluator-hard-gate | Evaluator skills 负责判断 evidence 并 route/block，但不能改写 truth，也不能把修复 implementation 混入 verdict。 |
| AC-009 | governor-hard-gate | Governor skills 管理 context、archive、memory、hooks、automation、metadata 和 status，不能成为人类主链阶段。 |
| AC-010 | rough-prompt-routing | 粗粒度用户提示词必须先被归约为 outcome、source/truth/evidence refs、湖/海分类、truth gap、test gap、implementation risk、verification risk 和推荐 harness route。 |
| AC-011 | no-fake-delivery | Placeholder implementation、docs-only completion、fake runner evidence、zero assertions 或 placeholder evidence 都不能满足 implementation、QA 或 release closure。 |
| AC-012 | migration-docs | Migration docs 必须定义 old-to-new skill mapping、旧 alias 移除、CLI compatibility boundary 和 operator next steps。 |
| AC-013 | default-truth-language-zh | 除非用户显式指定其他语言，Beacon v1.6.0 的需求真相、验收标准、测试断言、任务台账、迁移说明和 host-visible skill preamble 默认以中文为主语言；英文只能作为稳定术语或路径标识保留。 |
| AC-014 | planner-research-contract | v1.6.0 把 `docs/beacon/<version>/research/<feature-slug>.md` 定义为 planner artifact surface，authority 为 `support_advisory`；research 必须包含 outcome、湖/海、truth/source/evidence refs、gaps、risks、recommended_route、user_decision 和 promotion_ref，才能被路由或升级。 |
| AC-015 | research-to-truth-promotion | Research artifact 不能自动成为需求真相；只有 `user_decision=accepted/promoted` 且存在 `promotion_ref` 时，才能通过 `beacon-generator-truth-change` 或 `beacon-generator-truth-refreeze` 进入 package truth 并冻结。 |
| AC-016 | skill-rename-rewrite-contract | v1.6.0 skill 改名必须生成新 `beacon-<harness>-<function>` host-visible skill，更新 frontmatter/name/description/preamble/boundary，移除旧 host-visible aliases，并把旧名限制在 migration/archive/release notes。 |
| AC-017 | harness-hard-gate-injection | 每个 v1.6.0 host-visible skill 必须在共享 preamble 后注入 harness-specific `HARD GATE`，显式禁止跨 harness skill 调用、越权写 truth、越权 implementation、越权 QA/release verdict 和假交付闭环，并声明唯一允许产物；agent-surface verify 必须扫描并阻断缺失或不匹配的 gate。 |

## 非目标

| Item | Rationale |
|---|---|
| 把 support surfaces 做成 lifecycle stages | Global boundaries 要求 support surfaces 保持 route/challenge/diagnose surfaces |
| 重新引入 PRD/user-story/test-case 作为 v1.6.0 主 skill 名 | v1.5.2 已经把 authority 切到 feature package truth |
| 允许 generator skills 自证完成 | 仍然需要 evaluator evidence |
| 在 v1.6.0 保留 host-visible old skill aliases | 本次迁移为 clarity 明确 breaking |
| 未经 QA/release 就把 v1.6.0 提升为 runtime release | Version line 先作为 planning 开启；release promotion 是独立流程 |
| 强制翻译稳定技术标识 | 文件路径、命令名、skill 名、AC/TC ID 和协议名必须保持可精确引用 |
| 把 research 目录升级成 truth 目录 | research 是 planner support artifact surface；requirement authority 仍属于 feature package truth |
| 允许 skill 改名保留旧入口 wrapper | v1.6.0 host-visible skill package 是 breaking rename，不保留旧 alias |
| 只依赖 CLI/function routing 治理 harness 边界 | LLM 首先消费 `SKILL.md`，HARD GATE 必须在 skill prompt 内物理阻断越权动作 |

## Authority

本 feature 的 authoritative requirement source 是以下 package：

- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md`
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md`
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tasks.md`
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/evidence.md`

Support research 只是 upstream evidence：

- `docs/beacon/v1.5.2/research/beacon-skill-harness-taxonomy-v160.md`
