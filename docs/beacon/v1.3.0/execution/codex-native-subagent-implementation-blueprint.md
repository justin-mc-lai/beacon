# Beacon v1.3.0 Codex 原生子代理实施蓝图

`v1.3.0` 需要把“子代理方向”收敛成一条可实施、低风险、可验证的多代理集成线。

## 为什么需要这份蓝图

当前规划文档已经说明 Beacon 需要有边界的 Codex-native subagents。

缺的并不是方向，而是执行切口：

1. 第一条可运行集成应落在哪
2. 源码第一批改动应该触达哪些文件
3. 从 `codex-turbo` 应借什么、不该借什么
4. 如何证明“中人 / 英机 / release truth”三者能并存

## 来自 `codex-turbo` 的具体结论

拉取并阅读当前仓库后，最值得继承的是四个点：

1. `multi_agent = true` 是能力开关，不是产品中心
2. `max_threads` 与 `max_depth = 1` 让并发保持有界
3. `explorer` / `worker` 通过角色文件强化职责边界
4. 主代理负责拆解、等待、整合与最终交付

相关 upstream 文件：

- `README.md`
- `templates/cn/config.template.toml`
- `templates/en/agents/explorer.toml`
- `templates/en/agents/worker.toml`

## Beacon 的采用原则

Beacon 应该吸收“契约”，而不是吸收“环境”。

这意味着：

- 不修改用户全局 Codex 配置
- 不把 `codex-turbo` 模板直接复制进 Beacon runtime
- 不把 Beacon 演进成 generic launcher shell

Beacon 应做的是：围绕正式工件与 release truth，编译出阶段级 worker plan。

这也意味着：

- 不通过用户全局配置把外部 runner 变成默认执行面
- `v1.3.0` 的多代理默认入口应由 Beacon release line 自己控制
- 外部 runner 可以存在，但属于显式选择，不属于当前 runtime line 的默认真相
- `beacon.config` 中的 branch/worktree 配置只应作为 seed，不应长期充当实现真相

## 当前现实状态

当前仓内已经落地的是：

- `implement-team`
- `qa-team`
- 多角色 role reports
- team manifest
- implement / qa 上下文隔离
- `tmux` session / pane 映射
- HUD JSON / HTML

当前稳定运行的真实口径还应补充为：

- 多代理只在 `implement` 与 `qa` 两个阶段稳定启用
- `think / user-story / prd / test-case` 仍保持单 owner 正式材料面
- `runtime=file` 负责稳定落盘
- `runtime=tmux` 负责有界并行与可视化
- `runtime=auto` 当前先保守回退到 `file`

但这仍然只是：

```text
多角色证据模型
```

而不是：

```text
真实 Codex 多代理并行 runtime
```

当前实现还没有：

- child-agent spawn/runtime
- 每个 worker 都是独立 Codex 推理会话的通用 agent runtime

这里要精确区分两层：

1. `implement-team` / `qa-team` 的并行 worker 调度、tmux pane、HUD、等待汇总已经落地
2. 但当前 `team worker-run` 仍主要负责把 Beacon coordinator 预先编译好的 role payload materialize 成 role artifacts

因此，当前还没有落地的是“每个 worker 都是独立 Codex 推理会话”的那一层通用 agent runtime。

## 分阶段计划

### Phase 0：规划入口

触点：

- `beacon/utils/intent_router.py`
- `beacon/commands/ask.py`
- `beacon/commands/version.py`

目标：

- 把下一版本子代理演进 prompt 路由到 `version`
- 保持 `ask` 仍是自然语言总入口
- 让版本规划成为这条线的人类主读 top surface
- 保持版本语义显式，不把 docs line 与 runtime line 混在一起

### Phase 0.5：版本语义冻结

触点：

- `beacon/version-truth.json`
- `beacon/version-semantics.json`
- `beacon/utils/versioning.py`
- `beacon/utils/help_support.py`
- `beacon/utils/doctor_diagnostics.py`
- `beacon/commands/init.py`
- `beacon/commands/version.py`
- `beacon/commands/status.py`
- `beacon/commands/help.py`

目标：

- 给现有版本字段冻结唯一语义
- 把字段解析统一归口到 versioning layer
- 阻止调用方在需要 docs 语义时误用 runtime 语义

必须冻结的字段包括：

- `package_version`
- `runtime_version`
- `docs_default_line`
- `current_runtime_release_line`
- `planning_lines`
- `partial_runtime_supplement_lines`

### Phase 1：共享运行时 seam

触点：

- `beacon/utils/subagent_runtime.py`（新）
- `beacon/utils/project_skills.py`
- `beacon/utils/runtime.py`

目标：

- 定义 stage role registry
- 定义 run-scoped plan/evidence schema
- 把 child-agent 输出归一到 Beacon evidence

建议目录形态：

```text
.beacon/subagents/<feature>/<run>/
  plan.json
  summary.json
  workers/
    <role>.json
    <role>.md
```

### Phase 2：implement-first 执行接入

触点：

- `beacon/commands/implement.py`
- `beacon/utils/implement_native.py`
- `beacon/commands/team.py`

目标：

- 增加 `--runner codex-subagents`
- 为 `implement plan` 与 `implement run` 提供显性稳定的 team-mode 触发契约
- 提供 `implement dev-run` / `implement sync-git-workflow` 这类围绕 frozen baseline 的执行面准备入口
- 证明 leader -> child-agent -> evidence -> canonical writeback 闭环
- 保持 `native-single` / `native-team` 可用
- 明确区分“证据 team-mode”与“真实 subagent runtime”

为什么从这里开始：

- `implement run` 已有 runner 语义
- 它已有最丰富的执行证据面
- 它最适合作为 write-capable delegation 的首个验证面
- 它也是唯一天然需要 planner / implementer / reviewer / tester 并行分工的阶段
- 并且它是引入 `implementation-architect` 的唯一合理落点：该角色属于执行层，而不是需求真相层

### Phase 2.2：Git workflow contract materialization

触点：

- `beacon/utils/implementation_plan.py`
- `beacon/commands/implement.py`
- `beacon/utils/git_alignment.py`

目标：

- 把 branch/worktree/service-directory 约束从 config seed materialize 到 versioned execution materials
- 保证 `implement check-branch` / `doctor verify-git-alignment` / `gate check release` 优先读取 versioned contract
- 让 rolo 这类 workspace root 在根目录不是单 git repo 时也有正式 git workflow truth

### Phase 3：阶段扩面

触点：

- `beacon/commands/think.py`
- `beacon/commands/user_story.py`
- `beacon/commands/prd.py`
- `beacon/commands/test_case.py`
- `beacon/commands/qa.py`

目标：

- 为选定阶段增加显式 `subagent_mode`
- 默认仍保留 single-surface
- 只允许阶段批准的角色进入

建议首批角色：

- `think`：`researcher`、`critic`
- `user-story`：`story-mapper`、`ac-reviewer`
- `prd`：`requirement-parser`、`risk-critic`
- `test-case`：`scenario-mapper`、`coverage-checker`
- `qa`：`verifier`、`repair-handoff-writer`

这些阶段在 implement adapter 稳定前，应优先采用只读、批判或证据型角色。

并且在 `v1.3.0` 当前 release 口径下，需要明确：

- `think`
- `user-story`
- `prd`
- `test-case`

都不应默认进入多代理运行。

原因：

1. 它们当前主要承担 canonical requirement writeback
2. 它们的价值主要是结构化与批判，不是并行写能力
3. 让这些阶段保持单 owner，更符合 Beacon 的 source-of-truth 约束

### Phase 3.5：QA team-mode 与上下文隔离

触点：

- `beacon/commands/qa.py`
- `beacon/commands/team.py`
- `beacon/utils/subagent_runtime.py`

目标：

- 为 `qa` 提供显性稳定的 team-mode 触发方式
- verifier 与 repair-handoff-writer 通过 team-mode 协作
- `implement` 与 `qa` 的执行上下文严格隔离

隔离规则：

- QA 不直接继承 implement 的私有上下文
- QA 只消费正式 requirement artifacts、implementation evidence、handoff 摘要
- 不把实现期对话当作 QA 真相源

### Phase 3.8：tmux / HUD 可视执行

触点：

- `beacon/commands/team.py`
- `beacon/utils/subagent_runtime.py`
- `beacon/utils/subagent_tmux.py`
- `beacon/utils/team_hud.py`

目标：

- `implement team-run --runtime tmux`
- `qa team-run --runtime tmux`
- 为每个 role 创建 pane / window
- 持久化 session / pane mapping
- 输出稳定 HUD / HTML 页面

要求：

- 展示层读取 runtime state，而不是直接解析终端文本
- tmux 是执行载体，不是 release truth
- worker 实时状态必须可观测
- `planner` 仍可由 coordinator 串行先行，后续角色再进入并行 pane

### Phase 4：release-truth 硬化

触点：

- `beacon/commands/review.py`
- `beacon/commands/gate.py`
- `beacon/commands/release.py`
- `docs/beacon/<version>/.machine/execution/`

目标：

- 摘要 delegated run metadata，但不新造第二 truth plane
- 让 release/gate 继续读取 Beacon 工件，而不是 raw transcripts
- 让 blocked worker evidence 在正式 review/gate 输出里可见

## 非目标

1. 把 `codex-turbo` 当成 Beacon 运行时依赖
2. 从 Beacon 反向生成用户全局 Codex 配置
3. 把 tmux 编排变成强依赖
4. 允许 free-form DAG execution
5. 允许多层递归 child-agent tree
6. 让实现上下文与测试上下文混在同一 worker lane 里
7. 通过用户全局配置把 `omx` 等外部 runner 设成当前 release line 的默认 runner

## 退出标准

1. `implement run --runner codex-subagents` 能端到端生成 run-scoped evidence
2. 阶段级 `subagent_mode` 保持默认关闭
3. evidence 缺失或损坏时，正式 writeback 必须阻塞
4. release/gate 能理解 delegated run，而不改变 Beacon 的 release-truth 模型
5. 人类主读中文与机器主读英文的双轨 contract 已被测试锁死
6. `implement plan` / `implement run` / `qa` 都具备显性稳定的 team-mode 触发方式
7. QA 与 implement 只通过正式工件和 evidence handoff 协作
8. `implement-team` 不再只是顺序角色模拟，而是支持真实 bounded subagent runtime
9. tmux / pane 级可视执行可稳定展示 worker 生命周期
