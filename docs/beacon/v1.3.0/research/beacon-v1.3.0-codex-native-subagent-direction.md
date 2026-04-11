# Beacon v1.3.0 调研：简化版 Codex 原生子代理方向

**Date**: `2026-04-10`  
**Reference**:

- `https://github.com/atticus98/codex-turbo`
- `https://github.com/VoltAgent/awesome-codex-subagents`

## 调研问题

如果目标不是“再造一个 agent runtime”，而是“在 Beacon 阶段内增加一条小而可靠的 Codex 原生子代理能力线”，那么 Beacon 应该从 `codex-turbo` 借什么？

## 从 `codex-turbo` 观察到的关键信号

基于当前克隆仓库表面，最值得继承的是：

1. `multi_agent = true` 是 repo-local capability flag，而不是平台重写
2. `max_threads` 与 `max_depth = 1` 让并发保持有界、浅层、非递归
3. 角色配置文件与 launcher 同样重要：
   - `explorer`：只读、取证优先
   - `worker`：可写，但严格局部
4. 主代理负责拆分、等待、整合与最终验收
5. worker 边界非常明确：
   - 不改全局共享模块
   - 不改全局配置
   - 不做项目脚手架
   - 不引入跨模块共享依赖

最相关的 upstream 文件包括：

- `README.md`
- `templates/cn/config.template.toml`
- `templates/en/agents/explorer.toml`
- `templates/en/agents/worker.toml`

## 从 `awesome-codex-subagents` 观察到的关键信号

基于当前仓库结构，另外几个值得吸收的点是：

1. 角色库按类别组织，而不是扁平散落：
   - core development
   - quality/security
   - meta orchestration
   - research / analysis
2. `meta-orchestration` 被单独建模，说明“协调者角色”应与普通执行角色分开治理。
3. QA、review、debug、docs、research 都有单独角色模板，不应全部混进一个泛化 worker。
4. `.toml` 角色目录适合做稳定 catalog，而不是每次临时拼 prompt。

最相关的目录包括：

- `categories/04-quality-security/`
- `categories/09-meta-orchestration/`
- `categories/10-research-analysis/`

## Beacon 应该借的东西

### 1. 受配置与阶段约束的委托

Beacon 不应因为“某阶段存在”就自动拉起子代理。

每个阶段都应显式声明：

- 是否允许 `subagent_mode`
- 允许哪些 worker roles
- worker 必须返回什么证据工件

### 2. 角色契约，而不是自由 prompt

Beacon 已经有阶段语义，因此正确抽象不是“随便 spawn agent”，而是：

- `think.researcher`
- `user-story.story-mapper`
- `prd.risk-critic`
- `test-case.scenario-mapper`
- `qa.verifier`
- `implement.executor`
- `team.coordinator`
- `qa.repair-handoff-writer`

换句话说，Beacon 应该有 stage role registry，而不是拷贝外部 `agents/*.toml`。

### 3. Repo truth 仍由 Beacon 持有

Codex-native child agents 可以帮助生成结果，但 Beacon 自己必须继续持有：

- version truth
- docs/beacon 正式材料
- gate 契约
- release evidence

子代理输出只能是 input evidence，不能成为第二事实源。

## Beacon 不应该借的东西

1. 修改用户 Codex 全局环境
2. “能 delegate 就都 delegate” 的开放式行为
3. 绕过 Beacon writeback 的第二 agent memory plane
4. 让 `think / story / prd / qa` 依赖 tmux 或外部 shell
5. 任何要求 Beacon 修改用户 `~/.codex` 的设计

## 建议方向

采用双层设计：

1. `subagent plan`
   - Beacon 决定某阶段是否允许委托
   - Beacon 写出 stage-local plan，描述 worker role、scope、input、expected output
2. `subagent evidence`
   - worker 结果写入 `.beacon/subagents/<feature>/<run>/`
   - 阶段命令再把它编译回正式 Beacon 工件
3. `team contract`
   - Beacon 显式声明 team surface
   - team 有 coordinator
   - implement team 与 qa team 角色目录独立
   - implement 与 qa 只通过正式工件交接

## 为什么这是正确切法

这样可以保住主链：

`ask/think -> user-story -> prd -> test-case -> qa -> implement -> gate`

同时只在真正有价值的地方，把复杂任务拆成 bounded worker lanes。

## 克隆调研后的进一步结论

第一条真正执行多代理闭环的入口应该是 `implement run`。

原因：

1. Beacon 在这里已经有 runner 语义
2. evidence/writeback 模型在这里最成熟
3. 这里最适合先验证 write-capable child-agent integration

需求与 QA 阶段在早期应优先采用只读、批判或证据型角色。

## 结合两个仓库后的新增判断

`v1.3.0` 不应只说“支持 subagent”，还应该明确：

1. 稳定新增 `team` surface
2. `implement plan` / `implement run` 优先走 implement-team
3. `qa` 优先走 qa-team
4. implement-team 与 qa-team 必须上下文隔离
5. 角色目录应按用途分层，而不是只暴露一个平铺 role 集合

## 额外发现：Beacon 其实不缺新的 version model

Beacon 已经拥有：

- `beacon/version-truth.json`
- `beacon/version-semantics.json`
- `beacon/utils/versioning.py`
- `help/status/doctor/init` 等版本上下文消费面

真正缺少的不是新 model，而是更强的 version semantics governance：

1. 现有字段必须有唯一语义
2. 后续源码只能通过统一层解析版本语义
3. planning prompt 不能误用 current runtime release line 的默认语义
