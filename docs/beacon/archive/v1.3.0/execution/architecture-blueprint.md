# Beacon v1.3.0 架构蓝图

`v1.3.0` 需要把简化版 Codex 原生子代理引入为一种“有边界的阶段能力”，而不是把 Beacon 改造成通用多代理 shell。

## 核心判断

Beacon 不应该成为通用多代理运行时。

Beacon 应该成为一个更清晰的阶段 orchestrator：可以在特定阶段引入受约束 worker lane，同时保持正式工件、release truth 与 gate 模型不变。

## 当前准确口径

`v1.3.0` 当前稳定落地的多代理执行面只包括：

- `implement`
- `qa`

这两个阶段需要多代理，是因为：

1. `implement` 需要 planner / implementer / reviewer / tester 的写能力分工与并行
2. `qa` 需要 verifier / repair-handoff-writer 的验证与 repair handoff 分工
3. 两者都已经具备较成熟的 evidence/writeback/gate 交界面

在补强 `implement-team` 时，需要再明确：

4. `implementation-architect` 属于**实现期架构角色**，不是 requirement / architecture truth owner
5. 它只能读取 frozen requirement materials，并写 execution-scoped implementation architecture note
6. 它不得直接改写 `user-story / prd / test-case / architecture-blueprint`

而以下阶段当前仍应保持单 owner 正式材料面：

- `think`
- `user-story`
- `prd`
- `test-case`

原因不是“这些阶段永远不能扩面”，而是它们当前主要承担 canonical requirement artifact 的正式回写；在这条 release line 中，它们更适合保留单 owner 生成与只读/批判型扩面蓝图，而不是进入多代理并行写回。

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

还应吸收来自 `awesome-codex-subagents` 的一个关键判断：

1. `meta-orchestration` 应与普通执行角色分离治理
2. QA / review / research 不应混成一个泛化 worker
3. 角色目录要按用途分层，而不是把所有 worker 平铺暴露

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

## 当前运行时如何保持稳定

`v1.3.0` 当前的稳定性不是来自“任意子代理都能自由运行”，而是来自 Beacon 自己掌控的 bounded team runtime：

1. 只有显式 surface 会进入 team-mode
2. 角色集合固定且外置配置
3. worker 输出先落到 run-scoped artifacts
4. 正式 writeback 仍由 Beacon stage owner 执行
5. `tmux` 只负责执行与观察，不负责 truth
6. frozen requirement truth 与 execution-scoped architecture note 必须分层治理

当前具体语义是：

- `runtime=file`：稳定生成多角色工件，但不启动真实并行 pane
- `runtime=tmux`：由 Beacon coordinator 创建 tmux session / panes 并等待 worker 完成
- `runtime=auto`：当前保守回退到 `file`

因此，`v1.3.0` 当前应被理解为：

```text
当前已落地 = Beacon bounded team runtime
不是 = 通用 Codex agent platform
```

## 全局配置约束

为保证 `v1.3.0` 的默认行为稳定，Beacon 不应依赖用户全局配置把 `skill.preferred` 或 `implementation.default_runner` 强行钉到外部 runner。

建议规则：

1. 全局配置可以保留 runner 定义
2. 但不应把 `omx` 之类的外部 runner 设成全局默认
3. `implement team-run` / `qa team-run` 的默认多代理路径应由 Beacon 当前 release line 自己决定

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

## 设计规范补充

`v1.3.0` 的设计规范需要再明确三点：

1. 只有 `implement` 与 `qa` 需要多代理稳定运行
2. `think / user-story / prd / test-case` 当前保持单 owner 正式材料面
3. 当前稳定性来自 Beacon bounded coordinator runtime，而不是把正式 writeback 下放给自由 worker
4. `implement-team` 可以增加 `implementation-architect`，但它只属于执行层，不属于需求/设计真相层

## Git workflow contract 也必须进入 versioned materials

`v1.3.0` 的实现阶段不能继续只依赖全局 `beacon.config` 指定：

- 目标分支
- 是否使用 git worktree
- 多服务 workspace 的 service roots

这些信息必须进入当前版本线的 execution materials，至少以 machine-readable contract + human-readable mirror 存在。

推荐理解为：

```text
frozen requirement materials
→ implementation plan
→ git workflow contract
→ branch/worktree preflight
→ implement-team runtime
```

这样才能兼容 rolo 这种多仓 workspace：

- 根目录不是单 git repo
- 真正执行面在多个 service repo
- 当前版本开发线可能是 `feature/<version>-<topic>`
- 是否使用 worktree 必须是 feature/version contract 的一部分

而不是隐藏在全局配置里。

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
