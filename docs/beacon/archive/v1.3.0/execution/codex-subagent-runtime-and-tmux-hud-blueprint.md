# Beacon v1.3.0 Codex Subagent Runtime / tmux HUD Blueprint

`v1.3.0` 要真正满足两个参考项目给 Beacon 带来的要求，不能停留在“多角色证据模型”。

必须进一步落到三件事：

1. 真正的 subagent spawn/runtime
2. 并行 worker 调度
3. tmux 或 pane 级可视执行展示

---

## 1. 先明确当前缺口

当前 `implement team-run` 与 `qa team-run` 已经做到：

- 显式 team surface
- 固定角色集合
- 角色报告落盘
- implement / qa 上下文隔离
- `tmux` session / pane 创建与等待
- HUD JSON / HTML 输出

但它们**还没有**做到：

- 真实 child-agent spawn
- 每个 worker 都是独立 Codex 推理会话

也就是说，当前实现更接近：

```text
Beacon bounded team runtime
```

而不是：

```text
Codex-native 多代理并行执行 runtime
```

为了避免误解，当前准确口径是：

- `implement-team` / `qa-team` 已经支持有界并行 worker 调度
- `tmux` 已经是可用执行后端，而不是纯蓝图
- 但 worker 仍主要负责 materialize Beacon coordinator 预编译的 role payload

---

## 2. 正确目标

Beacon 在 `v1.3.0` 的正确目标不是“新增一个更好看的 team report”，而是：

```text
Beacon stage owner
→ coordinator
→ bounded Codex subagents
→ parallel worker runtime
→ run-scoped evidence
→ tmux/HUD live visibility
→ canonical Beacon writeback
```

这里的关键不是“有几个角色名”，而是：

- 角色真的被 spawn 出去
- worker 能稳定并行
- 人类能实时观察执行状态
- 最终正式工件仍由 Beacon 主命令负责

当前实现对应关系应明确写成：

```text
当前实现
→ Beacon coordinator 先编译 role payload
→ worker-run materialize role artifacts
→ tmux/HUD 提供并行执行与可视化
→ canonical writeback 仍回到 Beacon stage owner
```

---

## 3. 最小运行时架构

### 3.1 三层结构

#### Layer A：Stage owner

仍然是：

- `implement run`
- `qa run`
- 后续扩展到 `think / user-story / prd / test-case`

这些命令继续持有：

- version truth
- package truth
- writeback ownership
- gate/release ownership

并且在 `v1.3.0` 当前 release line 下，只有两个 stage owner 真正需要多代理运行：

- `implement run`
- `qa run`

其他阶段：

- `think`
- `user-story`
- `prd`
- `test-case`

当前都应保持单 owner surface，不需要进入并行 team runtime。

#### Layer B：Coordinator runtime

新增一个共享运行时层，例如：

- `beacon/utils/subagent_runtime.py`
- `beacon/utils/subagent_tmux.py`

负责：

- spawn child agents
- 分发 role prompt / scope
- 限制并发度
- 等待 worker 结束
- 汇总 worker 输出
- 写 run-scoped evidence

#### Layer C：Display plane

新增一个稳定展示面，例如：

- `.beacon/state/team-hud/<team_name>.json`
- `docs/beacon/<version>/execution/codex-subagents/<feature>/<run>/index.html`

负责：

- 展示 team / worker 状态
- 展示 tmux session / pane mapping
- 展示 review gates
- 展示 artifact links
- 展示 handoff / blocker / completion

展示层**不直接依赖终端输出格式**，而是依赖 runtime state。

---

## 4. `implement-team` 的真正运行合同

### 4.1 角色

第一批 implement-team 角色继续用：

- `planner`
- `implementation-architect`
- `implementer`
- `reviewer`
- `tester`

但角色不再只是静态 report 名字，而应对应真实 worker lane。

当前实现里的精确语义是：

- `planner` 先由 coordinator 串行完成
- `implementation-architect` 在 implementer 之前产出 execution-scoped 架构边界说明
- `implementer / reviewer / tester` 在 `tmux` 模式下进入并行 pane
- 这是一条有界并行线，而不是自由 fan-out

### 4.2 运行时 contract

每个 worker 至少要有：

- `worker_id`
- `role`
- `status`
- `allowed_scope`
- `input_refs`
- `output_schema`
- `runtime`
- `tmux_session`
- `tmux_pane_id`
- `started_at`
- `ended_at`
- `artifact_paths`

### 4.3 并行规则

- `planner` 先行
- `implementation-architect` 在 implementer 之前完成，且不得改写 frozen docs
- `implementer` 启动后，`reviewer` 与 `tester` 可在 bounded policy 下并行或半并行
- 默认 `max_depth = 1`
- 不允许 worker 再 spawn worker
- 默认 `max_threads` 明确写入 runtime config

当前稳定运行策略还应补充为：

- 只有 `implement` / `qa` 允许进入这条并行线
- `runtime=file` 提供无 tmux 的稳定落盘与 HUD
- `runtime=auto` 当前保守等价于 `file`
- 不通过用户全局 runner 偏好覆盖这条 release-line 默认行为

---

## 5. tmux 展示页应该怎么做

### 5.1 不要把 tmux 当展示真相源

tmux 只应该是执行载体，不应该是唯一可视面。

原因：

- pane 文本格式不稳定
- 重连困难
- 不适合 gate 读取
- 不适合做长期 evidence

### 5.2 tmux 应提供的最小能力

- 创建 session：`beacon-<feature-slug>-<run-id>`
- 为每个 role 分配 pane/window
- 在 pane 标题中标出 role
- 把 pane_id 写回 runtime state
- 支持 attach / list / capture-pane

### 5.3 HUD / HTML 页面应该展示

- team name
- feature / version / run_id
- current stage
- runtime mode：`file|tmux|auto`
- tmux session name
- 每个 role 的：
  - status
  - pane id
  - artifact links
  - latest event
- review gate status
- handoff status
- acceptance / gate blockers

---

## 6. 推荐命令面

### 实现阶段

```bash
beacon implement sync-git-workflow "<feature>" --project . --version v1.3.0 --json
beacon implement dev-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
beacon implement team-plan "<feature>" --project . --version v1.3.0
beacon implement team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
beacon team hud --team "<team-name>" --project . --json
beacon team page --team "<team-name>" --project .
```

### QA 阶段

```bash
beacon qa team-plan "<feature>" --project . --version v1.3.0
beacon qa team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
beacon team hud --team "<team-name>" --project . --json
beacon team page --team "<team-name>" --project .
```

### Team HUD

```bash
beacon team hud --team <team-name> --project . --json
beacon team page --team <team-name> --project .
```

---

## 7. 源码落点

第一批建议触达：

- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/commands/team.py`
- `beacon/utils/implement_native.py`
- `beacon/utils/team_surface.py`
- `beacon/utils/subagent_runtime.py`（新）
- `beacon/utils/subagent_tmux.py`（新）
- `beacon/utils/team_hud.py`（新）

---

## 8. 分阶段落地顺序

### Phase A：Runtime contract

- 新增 worker runtime schema
- 新增 `runtime=file|tmux|auto`
- 新增 team HUD state

### Phase B：tmux backend

- 真的创建 tmux session/panes
- 记录 pane/session mapping
- 支持 attach / capture

### Phase C：implement-team 真并行

- `planner` 先行
- `implementer/reviewer/tester` 进入 bounded 并行
- 输出真正的 worker runtime events

### Phase D：qa-team 真并行

- verifier
- repair-handoff-writer
- 保持 implement / qa 上下文隔离

### Phase E：HTML/HUD 页面

- 从 runtime state 生成稳定可视页
- 作为人类主读运行面

---

## 9. 退出标准

只有当以下条件都满足时，才能说 Beacon 真正支持了稳定的 Codex 多角色 implement：

1. `implement team-run --runtime tmux` 会真实 spawn 多个 worker
2. worker 是 bounded parallel，而不是顺序伪并行
3. tmux session / pane 映射可观测
4. HUD/HTML 页面能实时显示 worker 状态
5. 最终仍由 Beacon 正式 writeback，而不是 worker 直接改 formal truth
6. gate/release 继续只读取 Beacon formal artifacts
7. `qa team-run --runtime tmux` 会真实 spawn verifier / repair-handoff-writer
8. `implement` 与 `qa` 是仅有的稳定多代理运行面
9. `think / user-story / prd / test-case` 仍保持单 owner 正式材料面
