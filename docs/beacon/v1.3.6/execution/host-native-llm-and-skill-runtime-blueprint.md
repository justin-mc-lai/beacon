# Beacon Host-Native LLM And Skill Runtime Blueprint

## Document Intent

这份文档用于冻结 Beacon 的目标设计架构：

> Beacon 作为运行在 Claude / Codex 内的 skill orchestration kernel，默认应优先复用宿主原生大模型能力；本地 CLI 负责编排、结构化约束、事务写入、审阅与冻结，而不是把“再接一个外部 LLM API”当成默认前提。

它不是单点修补 `prototype` 的技术说明，而是对 Beacon 当前整体运行机制的重构蓝图。

---

## 1. 背景判断

当前 Beacon 已经具备三类能力：

1. 人类工作流内核
   - `prd`
   - `user-story`
   - `test-case`
   - `prototype`
   - `implement`
   - `qa`
   - `release`
2. 支撑面
   - `help`
   - `status`
   - `doctor`
3. 机器内部复杂度
   - runtime projection
   - freeze / review / gate
   - SQLite / PocketBase 投影
   - host runtime readiness
   - prompt / intent routing
   - HUD hook / debug capture

但当前 Beacon 仍存在一条核心错位：

- 对外定位上，Beacon 是运行在 Claude / Codex 中的 skill；
- 实现上，Beacon 的语义编译却被设计成“本地 Python CLI 自己再调用一层外部 LLM API”。

这就导致：

- 用户已经在和宿主大模型对话，仍被要求额外配置 `BEACON_LLM_API_KEY`
- 宿主先理解一遍，Beacon CLI 又单独理解一遍，形成双重推理链
- skill surface 与 CLI runtime 的边界不清晰
- 最终产物的语义来源不透明，容易 drift

---

## 2. 当前机制拆解

## 2.1 Skill 层

当前 `skills/beacon/` 的本质是：

- 对 Claude / Codex 的路由提示
- 对人类输出面的约束
- 对推荐命令面的收敛

skill 本身不持有 LLM 推理能力，也不直接修改 Beacon 真相树。

当前 wrapper 行为可简化为：

```text
host prompt
→ skills/beacon/*.md
→ bash skills/beacon/scripts/run_beacon.sh ...
→ python3 -m beacon.main ...
```

这意味着 skill 只是：

- 引导器
- 编排器
- 约束器

不是：

- 宿主推理能力的直接 API

## 2.2 CLI 层

`python3 -m beacon.main` 进入本地 Python 进程后，Beacon 运行在宿主之外的本地执行面。

它的天然能力是：

- 读取项目本地 `docs/beacon` 与 `.beacon`
- 做 rule-based 编译
- 做 canonical envelope 组装
- 做多 sink 写入
- 做 review / freeze / gate
- 做 subprocess orchestration

它天然不具备的能力是：

- 直接调用“当前正在承载此会话的 Claude / Codex 大模型脑内推理”

因此，当 CLI 需要“真实 LLM 语义推理”时，当前实现只能走外部 provider：

```text
Beacon CLI
→ HTTPS API
→ external model
```

## 2.3 当前 LLM 使用点

目前 Beacon 中已有多处“CLI 内部发起 LLM 推理”的设计：

1. workflow next-stage inference
2. prompt / intent router
3. QA plan 辅助推理
4. PRD create 的 LLM 编译
5. prototype create / plan 的 LLM 编译

这些能力都把“真实 LLM”建模为：

- `BEACON_LLM_API_KEY`
- `BEACON_LLM_API_BASE`
- `BEACON_LLM_MODEL`

而不是：

- `host-native llm context`

## 2.4 当前机制的优点

当前实现并非没有价值，它有几个现实优点：

1. Beacon CLI 可以脱离 Claude / Codex 单独运行
2. 测试容易做 deterministic fallback
3. 任何本地 shell 环境都能统一调用同一套 API 协议
4. Beacon 不必依赖某一个宿主厂商的私有能力

## 2.5 当前机制的核心缺陷

它最大的缺陷是：

> 它更像“可独立运行的 CLI + 可选 LLM provider”，而不是“宿主原生 skill kernel”。

这与 Beacon 当前产品定位不一致。

---

## 3. 目标设计原则

Beacon 后续架构应遵守以下原则。

### 3.1 宿主优先

如果 Beacon 运行在 Claude / Codex 中，默认应优先复用宿主推理能力。

### 3.2 CLI 去大脑化

Beacon CLI 不应成为第二个“独立思考的产品经理 / 设计师 / 分析师”。

CLI 的主职责应该是：

- 读取 truth
- 接收语义 envelope
- 做合同校验
- 做规范化
- 做 canonical 投影
- 做 freeze / review / gate

### 3.3 双层结构

Beacon 必须明确区分两层：

1. `semantic generation layer`
   - 由宿主 LLM 或可选 provider 生成
2. `structured execution layer`
   - 由 Beacon CLI 执行

### 3.4 provider 不应是默认前提

外部 API provider 仍可保留，但只能是：

- 纯 CLI 场景 fallback
- batch compile fallback
- host 缺席场景 fallback

不能继续作为默认前提。

### 3.5 canonical 仍然唯一

不论语义来自宿主还是 provider，最终都必须进入同一个 canonical envelope，再投影到：

- human sink
- machine sink
- runtime projection sink

---

## 4. 目标架构总图

目标结构应为：

```text
Host Runtime Layer
  = Claude / Codex session
  = skill routing
  = host-native semantic reasoning

Beacon Semantic Adapter Layer
  = semantic request contract
  = semantic envelope normalization
  = host/provider/rule mode arbitration

Beacon Structured Execution Layer
  = python3 -m beacon.main
  = contract validation
  = canonical envelope assembly
  = human/machine/sqlite projection
  = review/freeze/status/gate

Truth Layer
  = docs/beacon/<version> + .beacon + managed context

Projection Layer
  = SQLite / PocketBase / board / runtime ledger
```

核心流程应变成：

```text
truth materials
→ host-native semantic reasoning
→ semantic envelope
→ beacon structured validation
→ canonical envelope
→ sinks + review/freeze/status
```

而不是：

```text
truth materials
→ beacon cli
→ external provider
→ beacon cli
→ sinks
```

---

## 5. 模块分层

## 5.1 Host Runtime Layer

职责：

- 承接人类请求
- 使用宿主上下文理解当前项目 / feature / stage
- 根据 Beacon skill 规则生成语义结果
- 把结果作为结构化输入交给 Beacon CLI

该层可见对象：

- 当前对话上下文
- 当前代码库上下文
- skills/beacon/*
- docs/beacon/*

它不负责：

- 直接写 Beacon canonical
- 直接更新 SQLite / PocketBase

## 5.2 Semantic Adapter Layer

这是后续 Beacon 最关键的新层。

职责：

- 定义统一语义请求合同
- 定义统一语义输出合同
- 在三种模式间做仲裁：
  - `host`
  - `api`
  - `rule`
- 做基础字段规范化和缺省补足

目标输出统一为：

```json
{
  "requested_mode": "auto|host|api|rule",
  "generator_mode": "host|api|rule",
  "semantic_contract_version": "1.x",
  "feature": "...",
  "version": "...",
  "semantic_payload": {}
}
```

其中：

- `host` 表示语义由 Claude / Codex 产出
- `api` 表示语义由 Beacon 外部 provider 产出
- `rule` 表示完全 deterministic fallback

## 5.3 Structured Execution Layer

职责保持不变，但边界要更加纯粹：

- 读 source materials
- 校验 source completeness
- 校验 semantic payload 合同
- 组装 canonical envelope
- 生成 human / machine / sqlite sinks
- 运行 review / freeze / status / gate

这一层不应继续默认自己发起“再找一个外部模型思考”的动作。

## 5.4 Projection Layer

沿用现有 Beacon 设计：

- SQLite Runtime Ledger
- PocketBase 控制面
- 管理看板 / 查看器

该层继续只做 projection，不做 truth owner。

---

## 6. 核心模式设计

## 6.1 新的模式定义

后续 Beacon 所有语义编译型命令建议统一支持：

- `--mode auto`
- `--mode host`
- `--mode api`
- `--mode rule`

禁止再把 `llm` 直接等同于 `api`。

因为在 Beacon 目标设计里：

- `host` 也是 LLM
- `api` 也是 LLM
- `rule` 不是 LLM

所以真正要区分的是“语义来源”，而不是“是不是 LLM”。

## 6.2 auto 仲裁顺序

建议统一改为：

```text
auto
→ host
→ api
→ rule
```

判断顺序：

1. 若当前运行在 Claude / Codex skill 会话中，且存在可用 host semantic adapter，则优先 `host`
2. 若无 host adapter，但存在 provider 配置，则退到 `api`
3. 若以上都无，则退到 `rule`

## 6.3 host 模式合同

`host` 模式下：

- 不要求 `BEACON_LLM_API_KEY`
- 允许由宿主先生成结构化语义 JSON
- Beacon CLI 只验证并落盘

## 6.4 api 模式合同

`api` 模式下：

- 仍允许使用 `BEACON_LLM_API_KEY`
- 作为纯 CLI / batch runner fallback
- 允许 headless 环境下独立工作

## 6.5 rule 模式合同

`rule` 模式继续保留：

- deterministic
- test-friendly
- offline fallback
- 最小可用降级

---

## 7. 各 stage 的目标落点

## 7.1 PRD / User Story / Test Case

这些 requirement compile stage 最适合优先改造为 host-first。

原因：

- 本身就高度依赖宿主上下文理解
- 需要读取当前对话中的真实意图
- 用户天然认为这是在和宿主大模型协作

目标机制：

```text
user request
→ host semantic draft
→ beacon contract validation
→ markdown/material sinks
```

## 7.2 Prototype

`prototype` 是最需要 host-first 的阶段。

因为它的语义必须来自：

- PRD
- User Story
- Test Case

而不是固定模板。

它应该变成：

```text
requirement truth
→ host-generated page semantics
→ beacon shell template + validator
→ canonical freeze package
```

其中模板只负责：

- 输出结构
- 文件布局
- review/freeze 合同

不负责页面真实语义。

## 7.3 Implement / QA / Release

这些阶段的“主要执行”仍然更多是：

- orchestration
- verification
- evidence closure

因此它们不需要强行全部 host-native 化。

更合理的改法是：

- 保持 execution / verification 逻辑在 CLI
- 只把需要语义推理的子任务改成 host-first

---

## 8. 对当前 Beacon 特性的兼容要求

这条目标架构必须兼容当前 Beacon 已有特性。

## 8.1 7+3 人类面不变

保持：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release

help
status
doctor
```

不会因为引入 host-native 语义层而新增一级公开主命令。

## 8.2 prototype freeze / review / status 机制不变

即使改成 host-first：

- canonical envelope
- interaction map
- state flow map
- component catalog
- coverage report
- review / freeze / status / gate

这整套合同仍然保留。

## 8.3 runtime ledger / PocketBase 不变

host-native 只改变“语义如何被生成”，不改变：

- SQLite Runtime Ledger
- PocketBase 控制面
- Beacon 管理看板

的定位。

## 8.4 prompt / intent router 要同步升级

当前 prompt router 也存在“rule / api llm”双轨。

后续应统一升级为：

- host router
- api router
- rule router

以保持整体模型一致。

## 8.5 doctor / status 要能看见 generator source

后续所有 stage 输出都应显式记录：

- `requested_mode`
- `generator_mode`
- `fallback_reason`
- `semantic_source`

这样 `status/review/doctor/gate` 才能解释：

- 这份材料是宿主生成的
- 还是 provider 生成的
- 还是 rule fallback 产出的

---

## 9. 数据合同建议

## 9.1 Semantic Envelope

新增统一中间层：

```json
{
  "schema_version": "1.0",
  "feature": "...",
  "version": "...",
  "stage": "prd|user-story|test-case|prototype",
  "semantic_source": {
    "mode": "host|api|rule",
    "host_runtime": "codex|claude|none",
    "model_label": "...",
    "fallback_reason": ""
  },
  "payload": {}
}
```

## 9.2 Canonical Envelope

semantic envelope 通过 CLI 校验后，再进入已有 canonical：

```text
semantic envelope
→ normalized stage contract
→ canonical envelope
→ sinks
```

规则：

- semantic envelope 不是最终提交真相
- canonical envelope 才是最终单向投影源

## 9.3 Review Metadata

每份 review / freeze / status 都应包含：

- 语义来源
- 合同验证是否通过
- 是否发生 host→api→rule fallback

---

## 10. 宿主集成方式建议

## 10.1 不直接依赖对话内私有上下文对象

Beacon 不应把设计建立在某个宿主的私有 SDK 上，否则会导致：

- Codex 可用，Claude 不可用
- 或 Claude 可用，Codex 不可用

更稳妥的方式是定义 Beacon 自己的 host semantic contract。

## 10.2 两种宿主集成路径

### 路径 A：前置生成

宿主先根据 Beacon skill 规则生成结构化 JSON，再调用 CLI：

```text
host LLM
→ semantic json
→ beacon ... --semantic-input file.json
```

优点：

- 简单
- 易测试
- 无需 Beacon CLI 直接接宿主 SDK

### 路径 B：stdin 协议

宿主通过 stdin 把 JSON 交给 CLI：

```text
host LLM
→ stdout/staged json
→ beacon ... --semantic-input -
```

优点：

- 更适合 hook / pipeline
- 可减少中间文件

建议优先做路径 A，再兼容路径 B。

## 10.3 host runtime 标记

当前 Beacon 已有 `host_runtime` 概念。

后续建议扩展为：

- `host_runtime`
- `semantic_host_available`
- `semantic_source_mode`

但不要把“能识别自己在 Codex/Claude 中”误等于“已经能调用宿主模型”。

---

## 11. 迁移策略

## 11.1 第一阶段

先在语义编译型 stage 中增加：

- `host|api|rule`
- `semantic_input`
- `semantic_source`

不移除现有 `api` 路径。

## 11.2 第二阶段

把以下 stage 默认改成 `auto=host>api>rule`：

- `prd`
- `user-story`
- `test-case`
- `prototype`

## 11.3 第三阶段

调整 docs、skill 文案和用户预期：

- 不再把 `BEACON_LLM_API_KEY` 作为默认前置
- 明确其为“纯 CLI fallback”

## 11.4 第四阶段

把 intent router、workflow next-stage inference、qa plan 等辅助 LLM 面统一升级到同一模式体系。

---

## 12. 风险与约束

## 12.1 风险：宿主能力不可编程

Claude / Codex 对“让本地 Python 直接调用宿主脑内推理”未必提供统一接口。

因此 Beacon 不能假设：

- 只要在宿主里运行
- CLI 就天然可以访问宿主模型

这也是为什么需要 semantic adapter contract。

## 12.2 风险：host 与 api 输出漂移

同一 stage 在 host 与 api 下可能出现不同语义风格。

应对：

- 统一 semantic contract
- 强化 canonical validator
- 对 review / freeze 暴露语义来源

## 12.3 风险：规则模式被弱化后失去可测试性

不能移除 `rule`。

因为：

- CI
- offline
- deterministic tests
- regression compare

都仍需要 `rule` 模式。

## 12.4 风险：宿主生成内容不稳定

Beacon 不能因为改成 host-first 就放弃机器合同。

必须坚持：

- semantic contract validation
- anti-noise guardrail
- traceability
- freeze contract

---

## 13. 完成判定

这份目标架构真正落地的判定标准应为：

1. `prd/user-story/test-case/prototype` 默认不再要求 `BEACON_LLM_API_KEY`
2. 在 Claude / Codex skill 环境下可通过 host semantic contract 产出正式材料
3. `api` 仍可作为纯 CLI fallback 工作
4. `rule` 仍可作为 deterministic fallback 工作
5. `review/freeze/status/gate` 能明确显示语义来源与 fallback 轨迹
6. Beacon CLI 继续保持“结构化执行内核”定位，不退化成另一个独立的大模型产品

---

## 14. 一句话收口

Beacon 的正确目标不是：

> 在 Claude / Codex 里再包一层需要额外 key 的 LLM CLI。

而应该是：

> 以 Claude / Codex 为默认语义引擎，以 Beacon CLI 为结构化执行与冻结内核，在必要时保留 API / rule fallback 的三层可退化架构。
