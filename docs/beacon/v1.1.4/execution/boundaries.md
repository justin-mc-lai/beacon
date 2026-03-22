# Boundaries: Beacon v1.1.4 implement / skill-runner 适配边界

**版本**: v1.1.4  
**日期**: 2026-03-20  
**状态**: Draft / Requirement Materials Only

---

## 1. 一句话定位

> `implement` 是 Beacon implementation stage 的正式适配器动作。  
> 它负责把 Beacon 需求物料转译给外部实现 skill / runner，把外部实现结果转译为 Beacon 可追溯证据、implementation marker 与 review/writeback 动作。

---

## 2. 第一性原则

### 2.1 Beacon 在实现阶段真正要解决的问题

Beacon 在实现阶段真正应该解决的是：

1. **承接问题**：需求物料如何被正式交给外部实现器；
2. **契约问题**：外部实现器如何标准化接收 request 并返回 result；
3. **证据问题**：实现动作如何被写成可审计 evidence；
4. **回填问题**：实现后哪些需求物料需要更新，如何进入 review/writeback；
5. **闭环问题**：implementation 如何和 verify / gate / release 接起来。

### 2.2 Beacon 不应把自己变成什么

Beacon 不应因为引入 `implement` 而膨胀成：

- 通用编码平台；
- 通用 agent scheduler / issue runner；
- team runtime 的替代品；
- 只为某一个用户的 OMX skill 写死的单租户工具；
- “外部命令代理层”而无正式物料回路。

---

## 3. 闭环状态机语义

### 3.1 Canonical workflow model 保持不变

Beacon 的 canonical workflow 仍然是：

- `think`
- `user-story`
- `prd`
- `prototype`（条件阶段）
- `test-case`
- `implementation`
- `verify`
- `gate`

### 3.2 `implement` 是 implementation stage 的正式动作，不是新阶段

- `implement` 不新增 workflow stage；
- 它只是把 `implementation` 从“参数占位符”升级为正式动作；
- workflow implementation 阶段应委托给 `implement run`。

### 3.3 `review spec` 与 `review quality` 是 implement 后的正式回路

- `review spec`：在 implement 后判断 PRD / User Story / Test Case / Prototype 是否需要回填；
- `review quality`：在 verify 后判断是否 gate-ready；
- `implement` 自身不应吞掉 review/writeback 语义，而应把结果交给这两个正式动作。

### 3.4 `release` 仍是 post-gate action

- `implement` 的出现不改变 `release` 的语义；
- `release` 仍然只处理 gate 之后的发布动作，不属于 implementation 本身。

---

## 4. 分层边界

## 4.1 Core Workflow Layer

与 `implement` 强相关但仍属于 core 的是：

- `think`
- `user-story`
- `prd`
- `prototype`
- `test-case`
- `workflow`
- `auto-test`
- `gate`
- `release`

这些命令定义需求、验证和放行主链。

## 4.2 Support / Execution Adapter Layer

`implement` 建议归入 support / execution-adapter 语义层：

- `implement`
- `review`
- `status`
- `report`
- `doctor`

职责：
- 承接外部实现；
- 生成/读取 request/result；
- 生成 implementation summary；
- 驱动 writeback 与 gate-ready 判断。

## 4.3 Bridge / Runtime Layer

以下仍然属于 bridge/runtime：

- `run`
- `team`
- `ralph-bridge`

职责：
- 提供实验性 bridge 与 runtime 通道；
- 连接 OMC / OMX / 团队运行时；
- 不是 Beacon implementation 主产品面。

> 结论：`implement` 不应做成 `bridge` 的别名。

---

## 5. Runner / Skill Adapter Boundary

## 5.1 Runner 必须可配置，不得写死 OMX

Beacon 不应把以下逻辑硬编码：

```text
implementation == omx
```

而应设计为：

```text
implementation -> runner registry -> runner instance (omx / custom / command)
```

### 允许的 runner 类型（MVP）

1. `command`
2. `command-skill`

## 5.2 OMX 是首个示例，不是唯一实现器

对于个人用户：
- `omx` 是最强代表性实现 runner；
- 可通过配置指定 skill（如 `$workflows-work`）；
- Beacon 负责拼 task prompt 与读取 result。

对于产品边界：
- OMX 只是 runner example；
- Beacon 必须允许别的 skill / runner 接入。

## 5.3 Beacon 负责的通用 contract

Beacon 必须负责：
- request contract
- result contract
- runtime evidence
- implementation marker
- implementation summary
- review trigger

外部 runner 负责：
- 真正执行编码实现；
- 返回结构化 result；
- 提供 changed_files / verification / artifact_updates 等结果。

---

## 6. Source of Truth Boundary

## 6.1 长期事实源

长期事实源仍然是：

```text
docs/beacon/<version>/
```

特别是：
- `user-story/`
- `prd/`
- `qa/test-cases/`
- `prototype/`（若存在）
- `execution/implementation-summary-*.{json,md}`

## 6.2 运行时状态

运行时状态应位于：

```text
.beacon/implement/<run_id>/
```

包含：
- `request.json`
- `result.json`
- `stdout.log`
- `stderr.log`
- `command.txt`

> `.beacon/implement/` 是 raw runtime，不得冒充长期需求事实源。

---

## 7. In Scope（Beacon 负责）

1. 提供正式 `implement` 子命令；
2. 提供 runner registry / config model；
3. 生成 request contract；
4. 读取并校验 result contract；
5. 写 implementation marker；
6. 写 execution summary；
7. 触发 `review spec` / `review quality`；
8. 将 implementation 接回 verify / gate。

## 8. Out of Scope（Beacon 不直接负责）

1. 真正的代码编辑执行本身；
2. 多代理调度与团队协作 runtime；
3. 所有外部 skill 的深度原生集成；
4. 自动 patch 全量需求文档正文（MVP 阶段）；
5. 取代 OMX/OMC/Codex/Claude 等外部执行器。

---

## 9. 与 oh-my-codex (OMX) 的边界

OMX 的价值在于：
- 团队模式
- 技能与提示词运行时
- 持久状态/计划/恢复
- operator controls

Beacon 应如何与之协作：
- Beacon 输出 implementation contract；
- OMX 执行 skill（如 `$workflows-work`）；
- OMX 返回结构化实现结果；
- Beacon 把结果接回 review / verify / gate。

Beacon 不应承担：
- OMX 的 team/runtime/operator 功能；
- tmux / HUD / mailbox / 多 worker 生命周期；
- OMX 自身 skill 系统的管理。

---

## 10. 失败语义与 reason codes

以下 reason codes 建议作为 `implement` MVP 的正式失败语义：

- `runner_not_configured`
- `runner_request_write_failed`
- `runner_execution_failed`
- `runner_result_missing`
- `runner_result_invalid`
- `implement_execution_failed`
- `implement_writeback_failed`
- `implement_review_trigger_failed`

---

## 11. 成功标准

- Beacon implementation stage 具有正式命令面；
- 用户能用配置接入自定义 skill / runner；
- OMX 可作为首个 runner 示例被标准化接入；
- implement 结果能进入 execution summary + implementation marker + review/writeback 回路；
- Beacon 仍然保持“需求交付闭环内核”的边界，而不是滑向通用 orchestrator。
