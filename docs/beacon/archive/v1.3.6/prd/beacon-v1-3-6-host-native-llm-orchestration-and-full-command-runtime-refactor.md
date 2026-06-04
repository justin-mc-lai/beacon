# PRD：Beacon v1.3.6 宿主原生 LLM 编排层与全命令运行时重构

**Feature**: `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`  
**Version**: `v1.3.6`  
**Date**: `2026-04-21`  
**Status**: `frozen-pending-implementation`  
**Track**: `parallel`  
**Scenario**: `host_native_runtime + tooling_surface + delivery_kernel`  
**Template**: `并行 PRD / architecture-migration`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.3.6/SUMMARY.md`
- Execution index: `docs/beacon/archive/v1.3.6/execution/index.md`
- Main PRD in line:
  - `docs/beacon/archive/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md`
- Architecture blueprint:
  - `docs/beacon/archive/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`
- Alignment target:
  - 对齐 `oh-my-codex (OMX)` / `oh-my-claudecode (OMC)` 的宿主 CLI first 运行模型，但保留 Beacon 自己的 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` 生命周期收口。

## 1. 问题

本并行 PRD 用于定义 Beacon `v1.3.6` 的内核迁移线：

> Beacon 不再把“本地 CLI 额外调用外部 LLM API”当成默认智能来源，而是重构为“宿主原生 LLM + Beacon 结构化执行内核”的双层架构。

### 1.1 当前产品定位与当前运行机制不一致

Beacon 当前对外已经是：

- 运行在 Claude / Codex 中的 skill
- 通过 skill surface 引导 `prd / user-story / test-case / prototype / implement / qa / release`
- 对外强调 requirement-driven、freeze/review/gate、稳定交付

但底层实现仍有明显错位：

1. `prd / prototype / intent-router / next-stage inference` 等语义入口仍直接依赖 `BEACON_LLM_API_KEY`。
2. 宿主先理解一次需求，Beacon CLI 再独立理解一次需求，形成双重推理链。
3. 不同命令的智能来源不统一：
   - 有的靠规则；
   - 有的靠外部 provider；
   - 有的靠 runner；
   - 有的仍缺统一 semantic contract。
4. Beacon skill 与 Beacon CLI 的边界仍偏模糊，CLI 仍像“第二个大脑”。

结果是：

> Beacon 看起来像 skill，实际上仍部分运行在“独立 LLM client + workflow CLI”的旧模型里。

### 1.2 当前问题已经不止是 `prototype` 或 `prd` 的局部问题

如果只修某个子命令，会继续留下架构断层：

1. `prd` 改成宿主原生，但 `user-story / test-case / prototype` 仍走 provider，会继续 drift。
2. requirement 侧改成宿主原生，但 `implement / qa` 仍把宿主 team/subagent 当外接 runner，不会形成统一执行心智。
3. `help / status / doctor / release` 若不读取统一 semantic/runtime contract，就无法对全链稳定交付给出一致判断。

因此，本线不是“修一个命令”，而是：

> 把 Beacon 全命令底层统一收口到同一个宿主原生编排内核。

### 1.3 为什么必须对齐 OMC / OMX

`OMC / OMX` 已经证明了另一条更合理的路线：

- 宿主 CLI 才是语义执行引擎
- skill / prompt / agent config 负责行为约束和路由
- 运行时只负责状态、mailbox、tmux/team worker、恢复与可观测性
- orchestration layer 不默认再接一层自己的 provider API

Beacon 如果继续保留当前默认模式，会持续落后于这条成熟模式：

1. 心智更重
2. 配置更碎
3. 语义来源更不透明
4. requirement truth 更容易出现双脑漂移
5. 稳定交付能力更难做成统一 contract

### 1.4 不迁移的后果

如果 `v1.3.6` 不把这条线冻结为正式 PRD，后续会长期出现：

1. 用户已经在 Claude / Codex 中，却还要额外配置 `BEACON_LLM_API_KEY`
2. `prototype`、`prd`、`implement` 各自演化，不共享语义 contract
3. requirement side 与 delivery side 不共用同一个语义入口
4. `help / status / doctor / gate / release` 很难基于统一证据给出可执行判断
5. Beacon 永远停留在“流程很多，但底层不统一”的状态

## 2. 目标

### 2.1 主要目标

将 Beacon 重构为：

```text
宿主原生 LLM 语义层
→ Beacon semantic adapter
→ Beacon structured execution kernel
→ canonical envelope
→ docs/.beacon/runtime projection/review/freeze/gate
```

并把这条模型覆盖到全部公开命令：

- `prd`
- `user-story`
- `test-case`
- `prototype`
- `implement`
- `qa`
- `release`
- `help`
- `status`
- `doctor`

### 2.2 明确目标结果

本线完成后，Beacon 应满足以下状态：

1. 在 Claude / Codex skill 环境中，默认不再要求 `BEACON_LLM_API_KEY`。
2. 宿主大模型成为默认 semantic engine。
3. Beacon CLI 只承担：
   - truth 读取
   - contract validation
   - canonical assembly
   - projection / review / freeze / gate
   - runtime orchestration
4. 所有命令共享同一 semantic envelope contract 与同一 fallback arbitration。
5. `implement / qa` 内部默认能复用宿主原生 team/subagent 能力，但不暴露新的人类主命令。
6. 对人类而言，主流程和命令面保持极简，不因底层增强而膨胀。

### 2.3 非目标

本 PRD 不承担以下内容：

- 不新增新的公开一级主命令
- 不把 Beacon 改造成 OMC/OMX 的直接复制品
- 不放弃纯 CLI 场景的 fallback 运行能力
- 不把 SQLite / PocketBase 升级成正式 requirement 真相
- 不要求一次性支持所有宿主厂商，优先聚焦 Claude / Codex
- 不在本版本内要求全部 UI 产品面同步完成

## 3. 设计原则

### 3.1 宿主优先，provider 退居 fallback

当 Beacon 运行在 Claude / Codex 中时：

- 默认优先使用宿主原生语义能力
- 不默认要求 `BEACON_LLM_API_KEY`
- provider 仅作为 fallback、batch、离线或纯 CLI 模式保留

### 3.2 CLI 去大脑化

Beacon CLI 不应继续充当第二个独立“产品经理 / 设计师 / 需求分析器”。

CLI 的职责收口为：

- truth 读取
- 结构化 contract 校验
- canonical envelope 组装
- 多 sink 投影
- freeze / review / gate / status
- 运行时编排与恢复

### 3.3 全命令同核

所有公开命令必须共享同一套底层能力：

- semantic request contract
- host/provider/rule arbitration
- semantic envelope schema
- canonical projection path
- evidence / fallback / degrade contract

不得再出现每个命令私有一套“如何理解用户意图、如何生成内容、如何降级”的局面。

### 3.4 人类主面不扩张

即使内部引入：

- host-native subagents
- host-native teams
- runtime mailbox
- semantic adapter
- verifier / repair lanes

人类主流程仍保持：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

辅助面仍保持：

- `help`
- `status`
- `doctor`

### 3.5 requirement truth 不被 runtime 模式改写

无论执行走：

- host direct
- host subagent
- host team
- provider fallback
- rule fallback

都只能改变执行形态，不能改变：

- `prd`
- `user-story`
- `test-case`
- `prototype freeze`

定义的 requirement truth。

### 3.6 Align with OMC / OMX, but keep Beacon lifecycle

Beacon 应学习 `OMC / OMX` 的是：

- 宿主 CLI first
- runtime / state / orchestration 分层
- worker / resume / recovery / inspection 能力
- skill / prompt / config 的宿主注入方式

Beacon 不应丢掉的是：

- requirement-driven 主流程
- canonical envelope
- freeze / review / gate
- docs/beacon + `.beacon` 真相树

## 4. 范围

### In scope

- Host semantic adapter 抽象
- Claude/Codex host adapter
- provider/rule fallback arbitration
- 统一 semantic envelope schema
- `prd / user-story / test-case / prototype` 的宿主原生语义编译
- `implement / qa` 的宿主原生 team/subagent 编排接入
- `release / help / status / doctor` 的统一 runtime/evidence contract
- 统一 canonical projection / review / freeze / gate
- `BEACON_LLM_API_KEY` 从默认前置降级为 fallback 配置
- 命令面、skill 面、文档面的一致更新

### Out of scope

- 完整重做 Beacon UI 产品面
- 引入新的公开 team 一级主命令
- 把每个宿主的私有高级能力都做成可配置矩阵
- 用在线服务替代本地 truth tree

## 5. 命令面目标模型

## 5.1 公开命令不变，底层能力统一

| 命令 | 对人类职责 | 目标底层模式 |
|---|---|---|
| `beacon prd` | 冻结问题、目标、边界、承诺面 | host-native semantic compile + canonical PRD projection |
| `beacon user-story` | 编译角色目标与 AC | host-native semantic compile + schema validation |
| `beacon test-case` | 编译验收场景与覆盖矩阵 | host-native semantic compile + traceability projection |
| `beacon prototype` | 生成低保真 freeze 草图包 | host-native semantic compile + fixed output template + freeze/review |
| `beacon implement` | 唯一实现入口 | host-native orchestrated execution + requirement-bound run contract |
| `beacon qa` | 唯一验收入口 | host-native verification orchestration + evidence ledger |
| `beacon release` | 发布判定与 scorecard | unified gate + runtime/requirement evidence aggregation |
| `beacon help` | 当前下一步建议 | unified workflow/runtime inference, not ad hoc rules only |
| `beacon status` | 板面、阶段、健康态 | unified projection read model |
| `beacon doctor` | 诊断、修复、重建 | same truth/runtime contract, not sidecar system |

## 5.2 内部执行面可以增强，但只作为内部能力

允许在内部引入：

- host-native subagent fanout
- host-native team coordination
- verifier lane
- repair lane
- resume/recovery state
- runtime mailbox / ledger

但这些都必须被 `implement / qa / doctor / status` 消化，不新增公开一级主流程。

## 6. 功能需求

### FR-001 建立统一 Host Semantic Adapter

Beacon 必须引入统一 `HostSemanticAdapter` 抽象，至少定义：

- 当前宿主类型识别
- semantic request 输入 contract
- semantic response 输出 contract
- 宿主可用性探测
- 降级原因与 capability flags

### FR-002 建立统一 Semantic Envelope

所有语义生成结果，不论来自：

- Claude host
- Codex host
- external provider
- rule fallback

都必须先收口为统一 semantic envelope，再进入 canonical projection。

该 envelope 至少包含：

- `mode`
- `host_type`
- `generator`
- `input_refs`
- `semantic_payload`
- `constraint_hits`
- `open_questions`
- `fallback_reason`
- `evidence`

### FR-003 `prd / user-story / test-case / prototype` 必须共享同一编译框架

这四个 requirement 命令必须使用统一流程：

```text
truth read
→ semantic request build
→ host/provider/rule arbitration
→ semantic envelope
→ schema validation
→ canonical projection
→ review/freeze/evidence
```

不得再各自维护私有 API client、私有 prompt body、私有 fallback 语义。

### FR-004 `prototype` 必须保留“固定输出模板 + LLM 生成内容 + freeze/review”

`prototype` 的目标模式必须明确为：

- 固定输出模板负责结构骨架
- 宿主语义负责页面职责、布局草图、状态流转、跳转关系、组件契约
- freeze/review 保持现有校验路径

规则：

> 模板负责收口格式，不负责生成业务语义。

### FR-005 `implement` 必须成为宿主原生执行编排入口

`beacon implement` 必须保持唯一实现入口，同时具备：

- 绑定 requirement truth
- 选择宿主 direct / subagent / team 的内部执行模式
- 维持 run contract、artifact contract、resume contract
- 统一记录 runner 选择与 fallback 原因

不再把“真正智能执行”理解为 Beacon 外挂 runner 的偶发能力，而是理解为：

> Beacon 在宿主能力之上的正式 orchestration kernel。

### FR-006 `qa` 必须成为宿主原生验收编排入口

`beacon qa` 必须：

- 绑定 `prd / user-story / test-case`
- 能调度宿主原生 verifier / review / repair 协作
- 统一记录证据、失败原因、回归建议、再运行建议
- 把 QA 结果稳定投影到 gate / release

### FR-007 `help / status / doctor / release` 必须读取同一 runtime/evidence truth

这四个命令不得再基于互相割裂的推测逻辑。

它们必须统一读取：

- workflow state
- semantic envelope evidence
- canonical projection state
- runtime run state
- freeze/review/gate verdict

从而给出一致判断。

### FR-008 `BEACON_LLM_API_KEY` 不再是默认前置

Beacon 在 host mode 下：

- 不要求 `BEACON_LLM_API_KEY`
- 不因缺少 provider 配置而默认降为“能力缺失”
- 只在明确需要 provider fallback 时才读取 provider 配置

### FR-009 保留纯 CLI fallback，但明确标记其语义地位

当 Beacon 不运行在 Claude/Codex skill 环境中时，允许：

- provider mode
- rule mode

继续工作。

但必须显式标记：

- 当前不是 host-native mode
- 当前使用的是哪种 fallback
- fallback 对 freeze/review 结论的影响

### FR-010 全命令必须共享统一 degrade / fallback contract

所有命令都必须统一记录：

- `selected_mode=host|provider|rule`
- `fallback_reason`
- `requested_mode`
- `effective_mode`
- `capability_snapshot`

这样 `help / status / doctor / release` 才能解释清楚：

- 当前为什么这样跑
- 为什么没有走宿主
- 为什么走了降级

### FR-011 命令面与 skill 面说明必须同步

`skills/beacon/*`

以及：

- README
- AGENTS.md
- docs/beacon/<version>/*

都必须更新到同一叙事：

> Beacon 是宿主原生 LLM 编排层，CLI 是结构化执行内核，provider 只是 fallback。

### FR-012 requirement traceability 与 runtime traceability 必须合流

每一次 requirement 产出、implement run、qa run、release verdict 都必须共享可追溯链：

- 来源 requirement
- 语义生成模式
- 执行模式
- evidence artifacts
- gate verdict

不得再让 requirement side 和 runtime side 成为两套独立世界。

## 7. 架构要求

### 7.1 目标分层

目标分层固定为：

```text
Host Runtime Layer
  = Claude / Codex session
  = host-native reasoning
  = host-native subagent/team capability

Beacon Semantic Adapter Layer
  = capability detect
  = mode arbitration
  = semantic request/response contract

Beacon Structured Execution Kernel
  = truth read
  = schema validation
  = canonical assembly
  = projection/review/freeze/gate/status
  = runtime orchestration

Truth Layer
  = docs/beacon/<version> + .beacon

Projection Layer
  = runtime ledger + SQLite + board + read model
```

### 7.2 canonical envelope 仍然唯一

不论语义从哪里来，最终都只能是：

```text
semantic envelope
→ canonical envelope
→ human/machine/projection sinks
```

任何命令都不得绕开 canonical 直接写最终结果。

### 7.3 实现与验收仍必须绑回 requirement truth

`implement / qa / release` 无论内部使用 direct、subagent、team 哪种方式，都必须绑定同一 requirement truth：

- `prd`
- `user-story`
- `test-case`
- `prototype`

runtime mode 只能改变执行形态，不能改变验收定义。

## 8. 迁移阶段

### Phase 1：Requirement 命令统一到 host-native semantic compile

覆盖：

- `prd`
- `user-story`
- `test-case`
- `prototype`

交付目标：

- 抽出统一 semantic adapter
- 去掉各自私有 provider client
- 形成统一 envelope / fallback contract

### Phase 2：Execution 命令统一到 host-native orchestration kernel

覆盖：

- `implement`
- `qa`
- `release`

交付目标：

- 统一 runner/runtime contract
- 接入 host-native subagent/team 能力
- requirement traceability 与 runtime traceability 合流

### Phase 3：Support 命令统一到同一 truth/read model

覆盖：

- `help`
- `status`
- `doctor`

交付目标：

- 同一 capability snapshot
- 同一 runtime/evidence truth
- 同一 degradation explanation

### Phase 4：Provider default 降级与文档收口

交付目标：

- `BEACON_LLM_API_KEY` 不再出现在默认路径文案
- skill / README / docs 全部改写为宿主优先叙事
- provider 保留为 fallback 合法路径

## 9. 验收标准

### AC-001 宿主模式默认可用

在 Claude / Codex skill 环境下执行：

- `beacon prd`
- `beacon prototype`
- `beacon implement`
- `beacon qa`

默认不需要 `BEACON_LLM_API_KEY`，且都能产生可追溯的 host-native mode evidence。

### AC-002 全命令共享统一 mode contract

任意公开命令的 machine output 或 evidence 中，都能看到统一字段：

- `requested_mode`
- `effective_mode`
- `fallback_reason`
- `capability_snapshot`

### AC-003 requirement 与 execution 语义入口统一

`prd / user-story / test-case / prototype / implement / qa / release` 不再各自维护独立的 LLM 调用方式，而是共享同一 semantic adapter。

### AC-004 公开命令面不膨胀

迁移完成后，人类公开主面仍然只有：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

辅助面仍只有：

- `help`
- `status`
- `doctor`

### AC-005 `prototype` 仍满足固定模板与 freeze/review

迁移完成后，`prototype` 仍保留：

- 固定输出模板
- freeze/review 校验
- 人机隔离与 canonical 投影

但其页面语义改由宿主原生 LLM 驱动，而不是固定模板填空或强依赖 provider。

### AC-006 implement/qa 能解释内部编排选择

当 `implement` 或 `qa` 使用：

- direct
- subagent
- team
- fallback provider
- rule fallback

都必须能通过 evidence / status / doctor 清楚解释：

- 为什么选择该模式
- 它绑定了哪份 requirement truth
- 当前是否存在降级或风险

## 10. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 宿主差异导致 adapter 抽象失真 | 高 | 先聚焦 Claude/Codex 两类 host，统一最小 contract，不一次抽象所有厂商 |
| requirement 命令与 execution 命令整合面过大 | 高 | 按 Phase 1/2/3 分段落地，先统一 semantic adapter，再统一 execution kernel |
| 旧 provider 调用残留造成双路径 drift | 高 | 统一切到 arbitration 层，禁止命令私自直连 provider |
| 迁移期间 status/help/doctor 判断失真 | 中 | 优先让 support 命令读取 capability snapshot 与 unified evidence，而不是依赖历史猜测规则 |
| 人类面误以为要学习更多内部模式 | 中 | 坚持“不增公开一级命令”，所有新复杂度只留在内部 |

## 11. 成功判定

当以下结论同时成立时，可认为本线完成：

1. Beacon 的默认叙事已从“workflow CLI + optional provider”切换为“host-native orchestration kernel”。
2. `BEACON_LLM_API_KEY` 不再是默认前置。
3. requirement side 与 execution side 共享同一 semantic/runtime contract。
4. `help / status / doctor / release` 能基于统一 truth 给出一致判断。
5. Beacon 在能力模型上与 `OMC / OMX` 对齐到同一代际，但仍保留 Beacon 自己的 requirement-driven 生命周期与 freeze/review/gate 内核。
