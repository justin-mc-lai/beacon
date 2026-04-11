# Beacon v1.3.0 架构蓝图

`v1.3.0` 需要把简化版 Codex 原生子代理引入为一种“有边界的阶段能力”，而不是把 Beacon 改造成通用多代理 shell。

## 核心判断

Beacon 不应该成为通用多代理运行时。

Beacon 应该成为一个更清晰的阶段 orchestrator：可以在特定阶段引入受约束 worker lane，同时保持正式工件、release truth 与 gate 模型不变。

## 现有插入点

### 规划入口

- `beacon/commands/ask.py`
- `beacon/utils/intent_router.py`

这里负责识别“下一版本 / 子代理演进 / 新方向调研”等输入，并先把它们送到 `version` 规划面，再细化为阶段级工作。

### 阶段命令

- `beacon/commands/think.py`
- `beacon/commands/user_story.py`
- `beacon/commands/prd.py`
- `beacon/commands/test_case.py`
- `beacon/commands/qa.py`
- `beacon/commands/implement.py`

这些命令仍然必须是唯一正式阶段 owner。

### 现有协同面

- `beacon/utils/implement_native.py`
- `beacon/commands/team.py`
- `beacon/utils/project_skills.py`

它们是引入受约束 subagent adapter 与 evidence model 的最近 seam。

## 建议运行形态

```text
阶段命令
→ 决定 single-surface 或 subagent_mode
→ 写出 subagent plan
→ 运行受约束 worker roles
→ 持久化 worker evidence
→ 汇编回 canonical Beacon artifact
→ gate / release 保持不变
```

## 来自 codex-turbo 的可复用契约

从当前 `codex-turbo` 仓库表面来看，最值得借鉴的是：

1. 委托是 config-gated，而不是默认全开
2. explorer/worker 的角色边界比 launcher 本身更重要
3. write-capable worker 必须有清晰 ownership boundary
4. 递归深度必须浅层可控
5. 主代理必须负责拆分、等待、整合与最终验收

Beacon 应吸收这些契约，而不是吸收其环境配置方式。

## 最小新增构件

1. `beacon/utils/subagent_runtime.py`
   - 角色注册表
   - 计划写入器
   - 证据写入器
   - adapter 响应归一化
2. `.beacon/subagents/<feature>/<run>/`
   - 运行时证据目录
3. `docs/beacon/<version>/.machine/execution/`
   - 可选的 subagent contract 摘要
4. `beacon implement run --runner codex-subagents`
   - 第一条真正执行多代理闭环的 adopter
5. 显性稳定的 team-mode trigger contract
   - `implement plan`
   - `implement run`
   - `qa`
   - 必须统一说明如何进入 team-mode，而不是依赖隐式猜测

## 推进顺序

1. 规划入口与 version routing
2. 共享 subagent runtime helpers
3. `implement run` 的 Codex-native 多代理 adapter
4. `qa` 的 team-mode 与 implement / qa 上下文隔离
5. `think / user-story / prd / test-case / qa` 的只读/批判型扩面
6. gate / release evidence hardening

## 保护规则

1. 不允许 worker 隐式正式回写
2. 不允许绕过阶段 contract
3. 不允许演进成任意 shell DAG 功能
4. 不允许在 Beacon runtime / artifacts 之外再造第二记忆平面
5. 不允许递归 worker 再开 worker
6. 新增版本字段或 resolver 分支前，必须先更新 canonical version-semantics contract
7. `implement` 与 `qa` 的角色执行面必须上下文隔离，只允许通过正式工件与 evidence handoff 交汇

## 版本语义治理

`v1.3.0` 同时要把 Beacon 现有版本词汇重新冻结成单一 managed model。

当前 canonical 字段已经存在于 `beacon/version-truth.json` 与 runtime 消费面中：

- `package_version`
- `runtime_version`
- `docs_default_line`
- `current_runtime_release_line`
- `planning_lines`
- `partial_runtime_supplement_lines`

`v1.3.0` 新增的不是另一份 truth file，而是更强的治理要求：

1. 每个字段都必须只有一个精确定义
2. 每个 resolver 必须明确自己在解析哪种语义
3. `help/status/doctor/init/ask/version` 必须读取同一版本语义 contract
4. 后续源码不允许继续发明重叠概念
