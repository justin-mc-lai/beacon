# Beacon CLI 分层重构方案（v1.1.3 Draft）

## 1. 问题陈述

当前 Beacon CLI 的主要问题不是“命令不够”，而是“命令混层”：

1. `command_catalog.py` 直接暴露 40 个扁平命令；
2. core、support、labs、bridge 长期共用同一叙事层；
3. `intent_router.py` 默认路由过宽，模板型命令与主链命令同权；
4. `prompt` / `ask` / `work` / `run` 等存在重复入口与重复抽象；
5. 文档已经收口到 `docs/beacon`，但 CLI 表面仍未收口。

---

## 2. 目标架构

Beacon CLI 重构目标不是“做更多”，而是“分层清晰”。

### Layer A: Core Workflow Layer

**默认产品面**

- `think`
- `user-story`
- `prd`
- `prototype`
- `test-case`
- `workflow`
- `auto-test`
- `gate`
- `release`

### Layer B: Support & Governance Layer

**支撑核心主链**

- `status`
- `report`
- `doctor`
- `feedback`
- `remember`
- `recall`
- `resume`
- `version`
- `evolution-summary`
- `init`
- `test-progress`
- `debug`
- `ask`

### Layer C: Labs Layer

**可选安装 / 显式调用，不默认宣传**

- `analyze`
- `api-design`
- `brainstorm`
- `data-dictionary`
- `design`
- `jtbd`
- `kano`
- `moscow`
- `persona`
- `roadmap`
- `ui-spec`
- `wireframe`

### Layer D: Bridge / Experimental Layer

**桥接型与运行时型能力**

- `run`
- `team`
- `ralph-bridge`

---

## 3. 目录与模块建议

目标目录：

```text
beacon/commands/
├── core/
├── support/
├── labs/
├── bridge/
└── __init__.py
```

推荐拆分：

- `core/`: 主链命令
- `support/`: 观测、报告、诊断、记忆
- `labs/`: 模板/研究类命令
- `bridge/`: runtime / bridge / experimental

---

## 4. command_catalog 重构

当前：

- 单一 `SUPPORTED_SUBCOMMANDS`

目标：

```python
CORE_COMMANDS = (...)
SUPPORT_COMMANDS = (...)
LABS_COMMANDS = (...)
BRIDGE_COMMANDS = (...)
DEPRECATED_COMMANDS = (...)

DEFAULT_USER_SURFACE = CORE_COMMANDS + SUPPORT_COMMANDS
ALL_COMMANDS = DEFAULT_USER_SURFACE + LABS_COMMANDS + BRIDGE_COMMANDS + DEPRECATED_COMMANDS
```

价值：

1. README 与 skill 自动同步时可按层输出；
2. `cli_factory` 可按层注册；
3. `intent_router` 可按层限流；
4. `doctor` / `report` 可明确哪些命令处于 deprecated/experimental 状态。

---

## 5. cli_factory 重构

### 5.1 默认注册策略

默认注册：

- core
- support

条件注册：

- labs
- bridge

条件方式可选：

1. **最小变更**：仍同一包内注册，但 README/help 默认隐藏 labs/bridge；
2. **推荐方案**：labs/bridge 改为二级 namespace；
3. **长期方案**：labs/bridge 拆为独立包。

### 5.2 推荐命名空间

```bash
beacon think ...
beacon workflow ...
beacon gate ...

beacon labs analyze ...
beacon labs persona ...

beacon bridge team ...
beacon bridge run ...
beacon bridge ralph ...
```

---

## 6. intent_router 收口策略

### 6.1 默认只路由 core/support

`ask` 默认只处理：

- core intents
- support intents

即默认支持：

- think / user-story / prd / prototype / test-case / workflow / auto-test / gate / release
- status / report / doctor / resume / feedback / remember / recall / version / init / test-progress

### 6.2 labs 只能显式调用

对 `analyze / persona / jtbd / roadmap / ui-spec` 等：

- 不再默认作为强路由目标；
- 只有在用户明确说出命令或命名空间时才触发。

### 6.3 bridge 默认不经 ask 自动路由

- `team`
- `run`
- `ralph-bridge`

这些命令应显式调用，避免自然语言入口把 Beacon 误导成 orchestrator。

---

## 7. 兼容性与废弃路径

| 当前入口 | 目标入口 | 处理策略 |
|----------|----------|----------|
| `prompt optimize` | `ask --plan-only` | 先告警，后弃用 |
| `save` | `remember` / `resume` | 先告警，后弃用 |
| `work` | `workflow start` | 仅保留 alias |
| `run workflow` | `workflow start/continue` | 文档与 help 优先引导迁移 |
| `team` | `bridge team` / 外部 orchestrator | 降级为 experimental |

推荐策略：

1. **v1.1.3**：先写文档和 deprecation warning；
2. **v1.1.4**：完成 catalog/router/help 分层；
3. **v1.2.0**：移出默认 README/help，仅保留兼容别名；
4. **后续大版本**：移除废弃入口。

---

## 8. phased rollout

### Phase 1 — 文档与契约收口（v1.1.3）

- 产出本文件与命令收口矩阵
- 明确 retain / migrate / deprecate
- README 先出草案

### Phase 2 — Registry / Router 收口（v1.1.4）

- `command_catalog` 分层
- `intent_router` 默认只路由 core/support
- `prompt` / `work` / `save` 增加 deprecation warning

### Phase 3 — Namespace / Package 拆分（v1.2.x）

- `labs` 命令迁出默认表面
- `bridge` 命令迁出默认表面
- README/skill/help 完成同步重写

---

## 9. 成功标准

- 用户第一次看到 Beacon 时，能立刻理解它是“需求闭环系统”，不是“模板大杂烩”；
- 默认 README / help / ask 都不会再把 labs/bridge 与 core 混为一谈；
- 命令层级能直接映射到代码目录与文档结构；
- 后续实现层收口可以按阶段推进，而不是一次性硬切。
