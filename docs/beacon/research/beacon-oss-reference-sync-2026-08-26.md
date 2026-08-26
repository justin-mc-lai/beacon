# Research: Beacon 对齐第三方 spec skill 同步更新摘要（2026-08-26）

**日期**：2026-08-26
**目的**：按 `docs/beacon/research/beacon-open-source-reference-source-map.md` 维护的 canonical mirror 清单，把落后上游的 beacon 对齐第三方 spec skill 同步到最新，并提取更新要点供 beacon 演进参考。
**镜像**：`/Users/apple/Developer/Personal/oss-sync/`
**同步工具**：`manage_oss_sync.py sync`（官方入口，维护 SQLite truth 层 + index）
**关联任务**：`.trellis/tasks/08-26-sync-agent-reach-spec-skills`

---

## 1. 同步结果

- 共检查 28 个 canonical mirror：**13 个本就最新，15 个落后**。
- 15 个落后仓中 **14 个已同步到上游 HEAD**，1 个（`oh-my-pi`）因 GitHub 网络 SSL 断连（LibreSSL SSL_ERROR_SYSCALL）持续失败，待网络恢复后重试。
- 同步同时刷新 `oss-sync/index/repos.json` / `repos.md` / `sync-report.md` / SQLite truth 层。

## 2. 各仓更新要点（new commits 数 + 对 beacon 相关的关键变化）

| 仓库 | 新提交数 | 关键更新（beacon 相关） |
|---|---|---|
| `gstack` | 17 | v1.60→v1.69。**content binding**（evidence ledger、tracker trust envelope、fail-closed hooks）；guard 静默失败修复波（“guards failing open / silent failures”）；plan-mode auto-select at review scope gate；外部贡献安全审查。与 beacon evidence-first / fail-closed 同构 |
| `superpowers` | 1 | **v6.3.0**：Devin CLI + Hermes Agent 支持；brainstorming 三分支路由；SDD/Codex 效率修复 |
| `ralph-orchestrator` | 3 | **OMP（oh-my-pi）backend adapter**；OrcaRouter 识别为 models.dev 命名 provider；CI 允许 fork PR checkout |
| `ralphex` | 18 | worktree plan 归档修复（只提交 plan 路径、失败真实上报）；**review agent 禁止再 spawn 子 agent**；OAuth 凭证 bind mount 加固；detect claude 个人 spend limit |
| `ralph-tui` | 19 | **内置 Grok CLI 与 Antigravity（agy）agent plugin**；doctor 插件加载失败修复；resume --headless 流式输出 |
| `deer-flow` | 158 | 托管 subagents + delegation scopes；**统一 capacity + durable batch 执行**；sandbox:execute 授权强制（Phase 3）；RAGFlow 只读检索；分支会话；scheduler 忙任务排队 |
| `openspec` | 168 | **Zed Agent 支持**（host surface 再扩）；init 语言选项；archive 不再 dead-end capability retirement；opencode 参数透传 |
| `gsd-2` | 0（本就最新） | — |
| `bmad-method` | 84 | **禁止 detached review subagent 派发**；review 内容改走 path 传递；claims falsification pass（边角猎手）；Grok 作为 tool target；UTF-8 控制台流修复 |
| `karpathy-autoresearch` | 0 | — |
| `memevolve` | 0 | — |
| `autoagent` | 0 | — |
| `statsclaw` | 0 | — |
| `awesome-design-md` | 0 | — |
| `mempalace` | 348 | v3.8.0。**cross-handle cache 失效 + filtered id 查找（sqlite_exact）**；MCP stale-library write guard；logstream watch 校验与 checkpoint 修复；UTF-8 YAML 读写成 |
| `spec-kit` | 181 | **1.0.0 / 1.0.1 发布**；workflow switch 步骤强化校验（case block 必填、值剥离、条件 { } 拒绝）；社区目录新增（Taco Review、Azure Cosmos DB、Spec Inventory、Inventory Alignment preset）；project adoption guide |
| `mattpocock-skills` | 144 | 新技能 retro / implement-spec；**跨 skill 调用标准化为“一次一个 Skill tool call”**；**stop skills calling other user-invoked skills**；skill 触发词显式化；全仓 em-dash 清理 |
| `everything-claude-code` | 92 | tasteforge-video、council-multi-model（异构 Codex review）、**skill activation triggers 声明进 description**；ito-baskets 收敛；installer 安全加固（Windows reparse/no-follow）；Pi adapter 薄层 |
| `loopx` | 1055 | **quota 体系大量加固**（fail closed without scheduler receipt、spend artifact paths、visible Goal settlement causality）；control-plane **typed planning horizon**；lark 结算序列化；scheduler heartbeat-bound follow-ups（对齐 beacon S4 预算缺口） |
| `oh-my-pi` | ⏳ 待重试 | GitHub SSL 断连，未同步（镜像仍停留在 5039b33a） |
| `kun` | 已到最新 | 合并 develop（993f3152） |

## 3. 对 beacon 演进的要点提取

1. **S4 预算缺口的现成参考**：`loopx` 的 quota fail-closed + spend artifact path + settlement causality 机制，是 `beacon-longrun-stability-analysis-2026-08.md` 指出的 Beacon S4（预算）缺口最直接的可蒸馏对象。
2. **review subagent 递归护栏**：`ralphex` / `bmad-method` 都不约而同禁止 review agent spawn 自己的子 agent（detached dispatch）——与 Beacon `trellis-check` 子 agent 自豁免规则同一设计取向，可作 spec 沉淀佐证。
3. **skill 调用与触发标准化**：`mattpocock-skills` 与 `everything-claude-code` 都强调 skill 触发词/激活声明进 description、跨 skill 调用单一化——对齐 beacon skill anatomy 与 trigger 元数据实践。
4. **host surface 扩张趋势**：`openspec` 加 Zed、`superpowers` 加 Devin/Hermes、`bmad-method` 加 Grok——第三方 skill 普遍多宿主化，beacon 的 `.claude/.agents/.cursor` 多 surface 材质化方向一致。
5. **验证能力仍是主线**：`deer-flow` 的 sandbox:execute 授权、`mempalace` 的 stale-library write guard，与 `beacon-agent-coding-methodology-cursor-poteto-2026-08.md` 的 M1（验证 > 生成）互相印证。

## 4. 遗留

- `oh-my-pi` 待网络恢复后重跑：`manage_oss_sync.py sync --fetch-timeout 200 agents/agent-systems/oh-my-pi`
