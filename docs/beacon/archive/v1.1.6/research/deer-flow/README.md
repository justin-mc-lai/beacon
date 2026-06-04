# Research: DeerFlow — super agent harness、线程隔离运行时与全栈交付框架

> 来源：`oss-sync/agents/agent-skills/deer-flow/`
> 复核时间：2026-03-24
> 证据等级：A
> 研究目标：为 Beacon v1.1.6 提供 **super-agent runtime、sandbox/thread isolation、skill & MCP extensibility、custom agents、full-stack delivery** 的源码级借鉴

---

## 1. 先给结论

DeerFlow 是这轮样本里**最完整的全栈 super-agent harness** 之一。

它真正解决的问题不是“如何写一个 prompt”，而是：

1. **如何把 agent runtime、sandbox、subagent、memory、skills、MCP 组织成统一执行系统**
2. **如何把 backend harness 与 app/product 层分开演进**
3. **如何让同一个 agent 系统同时服务 Web UI、Gateway API、LangGraph、IM Channels、Docker/K8s 沙箱**
4. **如何把 thread 级工作目录、上传、产物、agent persona、memory 全部落成可管理的数据面**

所以 DeerFlow 对 Beacon 的价值，不在于“功能很多”，而在于它展示了：

- 一个 super-agent 平台的**分层架构**
- 一个 agent runtime 的**线程级隔离契约**
- 一个 extensibility 平台的**skills + MCP + custom agents** 组合方式
- 一个产品化系统的 **gateway / frontend / deployment / governance** 形态

---

## 2. 仓库定位与整体范围（源码复核后）

从根 README、backend README、frontend README、backend docs 与代码结构综合看，DeerFlow 不是单一后端包，也不是单纯 demo 项目，而是一个完整的全栈产品仓库：

- **Root**：统一配置、Makefile、Docker 编排、skills、脚本、CI、issue 模板
- **Backend**：LangGraph agent runtime + FastAPI gateway + channels + harness package
- **Frontend**：Next.js 16 + React 19 聊天工作台
- **Skills**：公开技能包目录，可被 runtime 自动发现
- **Docker/Provisioner**：本地、Docker、Kubernetes provisioner 三类部署路径

这使 DeerFlow 更适合作为 Beacon 的：

- 平台级产品形态参考
- runtime 边界设计参考
- extensibility 设计参考

而不是“单点能力”参考。

---

## 3. 从源码复核到的关键事实

### 3.1 DeerFlow 的后端是显式的 Harness / App 双层架构

`backend/CLAUDE.md` 与 `backend/docs/HARNESS_APP_SPLIT.md` 明确说明 DeerFlow 后端被拆为两层：

- **Harness**：`backend/packages/harness/deerflow/`
  - 可发布框架层
  - 负责 agent、middleware、sandbox、subagents、memory、tools、MCP、skills、models、config
- **App**：`backend/app/`
  - 不发布的应用层
  - 负责 Gateway API、IM channels、custom agent CRUD 等

这是一条对 Beacon 极有价值的架构信号：

> **runtime framework 和 product/application surface 应该显式解耦。**

相比很多 agent 项目把 runtime、API、产品功能混在一起，DeerFlow 已经把“框架层”与“应用层”分开建模。

### 3.2 LangGraph runtime、Gateway API、Frontend、Nginx 是四层运行面

从 root README、backend README、`backend/docs/ARCHITECTURE.md`、`docker/nginx/nginx.local.conf` 可以确认其主运行面为：

- **LangGraph Server (2024)**：agent runtime / thread / streaming
- **Gateway API (8001)**：models / skills / MCP / memory / uploads / artifacts / agents / suggestions / channels
- **Frontend (3000)**：Next.js 工作台
- **Nginx (2026)**：统一入口，拆分 `/api/langgraph/*` 与其他 `/api/*`

这说明 DeerFlow 不是把所有请求都压在一个 API 面上，而是：

- agent 会话走 LangGraph surface
- 配置/管理类能力走 Gateway surface
- 前端默认通过统一反向代理访问

这种分离比“单 API 承担一切”更适合复杂 agent 平台。

### 3.3 thread 级隔离是 DeerFlow 的一等契约

`backend/packages/harness/deerflow/config/paths.py` 明确定义了每个 thread 的 host-side 数据布局：

- `threads/{thread_id}/user-data/workspace`
- `threads/{thread_id}/user-data/uploads`
- `threads/{thread_id}/user-data/outputs`

同时约定虚拟路径前缀：

- `/mnt/user-data/workspace`
- `/mnt/user-data/uploads`
- `/mnt/user-data/outputs`

还包括：

- thread_id 安全校验
- 虚拟路径到宿主机路径的安全映射
- 目录初始化与权限设置

这意味着 DeerFlow 并不是“给 agent 一个 cwd”，而是给它一个：

> **线程隔离的数据契约**

这对 Beacon 很重要，因为它回答了：

- 临时工作区在哪
- 用户上传在哪
- 最终产物在哪
- 哪些路径是允许暴露给 agent 的

### 3.4 lead agent 不是裸 agent，而是 middleware-assembled runtime

`backend/packages/harness/deerflow/agents/lead_agent/agent.py` 显示 lead agent 通过 `_build_middlewares(...)` 组装出运行时行为。

当前中间件清单可从代码目录和构建逻辑确认包括：

- `ThreadDataMiddleware`
- `UploadsMiddleware`
- `SandboxMiddleware`
- `DanglingToolCallMiddleware`
- `SummarizationMiddleware`（可选）
- `TodoMiddleware`（plan mode）
- `TitleMiddleware`
- `MemoryMiddleware`
- `ViewImageMiddleware`
- `DeferredToolFilterMiddleware`（tool_search）
- `SubagentLimitMiddleware`
- `LoopDetectionMiddleware`
- `ClarificationMiddleware`
- `ToolErrorHandlingMiddleware`（runtime middlewares builder 中注入）

这说明 DeerFlow 的 agent runtime 是一种：

- 可组合的 middleware pipeline
- 明确的 cross-cutting concern 分层
- 配置驱动的能力开关

而不是把所有逻辑塞进 system prompt 或 agent body。

### 3.5 runtime safety 是代码级设计，不是文档口号

源码里至少能明确看到三类 runtime safety：

1. **Loop detection**
   `loop_detection_middleware.py` 会对工具调用做哈希与滑窗计数：
   - 重复达到阈值注入 warning
   - 超过 hard limit 直接剥离 tool calls，逼 agent 输出最终答案

2. **Tool error degradation**
   `tool_error_handling_middleware.py` 会把工具异常转换成 `ToolMessage(status="error")`，而不是直接让整个会话崩掉。

3. **Subagent concurrency enforcement**
   `lead_agent/prompt.py` 明确有 subagent concurrency 限制提示，`SubagentLimitMiddleware` 则在运行时截断超量 task calls。

这对 Beacon 的借鉴非常大：

> agent runtime 的稳定性必须下沉到 middleware / runtime rule 层，而不是全靠模型“自觉”。

### 3.6 task/subagent 系统是 DeerFlow 的核心执行面之一

`tools/builtins/task_tool.py` 与 `subagents/executor.py` 表明 DeerFlow 的 subagent 机制不是概念展示，而是实装能力：

- 内置 subagent 类型：`general-purpose`, `bash`
- `task` tool 委派任务给子 agent
- 使用后台执行 + 轮询完成
- 同时通过 stream writer 回传：
  - `task_started`
  - `task_running`
  - `task_completed`
  - `task_failed`
  - `task_timed_out`

`subagents/executor.py` 还显示：

- 有独立 scheduler / execution thread pools
- 有 timeout、状态机、AI message 收集
- 会把 sandbox/thread data/parent model/trace id 传入子 agent

这说明 DeerFlow 的 subagent 不是“再起一个对话”，而是：

- 带上下文继承
- 带运行状态
- 带可观测事件
- 带 timeout 的并发执行系统

### 3.7 sandbox 不是附属工具，而是平台核心抽象

从 backend README、`config.example.yaml`、`docker-compose*.yaml`、`paths.py` 可确认 DeerFlow 支持至少三类执行模式：

- **LocalSandboxProvider**：本地执行
- **AioSandboxProvider**：Docker-based container sandbox
- **Provisioner / Kubernetes mode**：借助 provisioner 在宿主 K8s 中拉起 sandbox pods

并且 Docker/K8s 不是“另一个 demo 跑法”，而是已写进主流程：

- `make docker-start`
- `scripts/docker.sh`
- `docker-compose-dev.yaml`
- `docker-compose.yaml`

这说明 DeerFlow 的执行环境是抽象成 provider 的，而不是把“本地 shell”写死。

### 3.8 extensibility 是 skills + MCP + community tools 的组合，不是单一插件系统

DeerFlow 的扩展能力至少分三层：

1. **Skills**
   `skills/` 下有大量 public skill packs，`skills/loader.py` 会递归发现 `SKILL.md`，并结合 `extensions_config.json` 决定 enabled 状态。

2. **MCP Servers**
   `config/extensions_config.py` 与 `backend/docs/MCP_SERVER.md` 显示：
   - 支持 stdio / SSE / HTTP transport
   - 支持 OAuth 配置
   - 可以动态启停 MCP servers

3. **Community Tools**
   `community/` 下已经集成：
   - Tavily
   - Jina AI
   - Firecrawl
   - image_search
   - aio_sandbox
   - InfoQuest

也就是说，DeerFlow 的扩展不是“单一 skill 市场”，而是：

> **workflow skills + protocol tools + community adapters 的叠加式扩展模型。**

### 3.9 custom agents 是产品级一等功能，而不只是内部配置

`backend/app/gateway/routers/agents.py` 与 frontend `core/agents/*` 可见：

- custom agent 通过 API 做 CRUD
- agent 名称有严格 pattern 校验
- 每个 agent 由：
  - `config.yaml`
  - `SOUL.md`
  组成
- 前端已有 Agent Gallery、Agent 创建页、Agent 专属聊天页

这说明 DeerFlow 不是仅有一个“lead_agent”，而是在产品层支持：

- 用户定义 agent identity/persona
- 每个 agent 带独立配置与 SOUL
- 前端和后端都围绕 agent 实体有管理界面

这对 Beacon 很重要，因为它提示：

- custom agent 不一定要是运行时 hack
- 它可以是平台内的正式资源对象

### 3.10 memory 是持久化数据面，而不是简单 prompt 注入

`agents/memory/updater.py` 表明 DeerFlow 的 memory system 具备：

- 持久化 JSON 存储
- mtime-based cache invalidation
- LLM 驱动更新
- upload event scrubber（避免把临时上传记成长期记忆）
- global memory 与 per-agent memory 并存

`paths.py` 也显示：

- 全局 `memory.json`
- 每个 agent 自己的 `memory.json`
- 全局 `USER.md`

这说明 DeerFlow 已经把 memory 当成：

- 持久化对象
- 可区分 scope（global vs per-agent）
- 需要清洗的长期上下文层

### 3.11 uploads / artifacts / present_files 构成明确的产物链路

从 `uploads.py`、`present_file_tool.py`、backend docs `FILE_UPLOAD.md`、前端 artifacts hooks 可以看到完整链路：

- 用户文件上传到 thread-scoped uploads 目录
- 可转换文档自动转 Markdown
- agent 通过虚拟路径访问上传内容
- 最终 deliverables 必须放到 outputs 目录
- 通过 `present_files` tool 把 outputs 中的文件显式暴露给用户界面
- 前端再通过 artifact URL 拉取展示

这是一个非常重要的设计点：

> **上传、工作区、输出区、最终展示是四个不同语义层。**

很多 agent 项目只有“文件读写”，DeerFlow 则把文件生命周期做成了产品契约。

### 3.12 frontend 不是薄壳，而是为 LangGraph 量身定制的状态化工作台

根据前端源码：

- 技术栈：Next.js 16 + React 19 + TypeScript + Tailwind 4 + LangGraph SDK + React Query
- 线程流：`useThreadStream()` 使用 LangGraph SDK `useStream`
- 状态管理：主要依赖
  - React Query（服务端状态）
  - LangGraph `useStream`（实时线程状态）
  - React Context（thread/artifacts/subtasks/i18n）
  - localStorage（本地设置）
- 页面结构：
  - landing
  - workspace/chats
  - workspace/agents
  - demo/mock mode

更关键的是它的部署假设：

- 默认认为前端和 `/api/*` / `/api/langgraph/*` 在同一反向代理下
- build 与 runtime env 分离
- `NEXT_PUBLIC_STATIC_WEBSITE_ONLY` 能把前端切成静态演示站模式

这说明 DeerFlow 前端不是“任意聊天壳”，而是高度贴合其 backend surfaces 的工作台。

### 3.13 DeerFlow 有较完整的工程治理，但偏后端优先

从仓库治理面可确认：

- 有 `CONTRIBUTING.md`、`SECURITY.md`
- 有 backend unit-tests CI：`.github/workflows/backend-unit-tests.yml`
- 有 issue template：`runtime-information.yml`
- backend 测试文件约 40 个，覆盖 memory、sandbox、skills、MCP、subagent、title、uploads、config 等
- frontend 目前**没有测试框架**，CLAUDE.md 也明确提示只做 lint/typecheck/build

这意味着 DeerFlow 的工程成熟度体现在：

- 后端 runtime 与 config 安全性较强
- 前端治理更偏工程约束而非测试闭环

---

## 4. 本次修正了哪些旧口径

### 旧口径 1：DeerFlow 只是一个 deep research agent

**修正后：不成立。**

更准确的说法是：

- DeerFlow 2.0 是 super agent harness
- research 只是能力面之一
- 仓库已经覆盖 runtime、sandbox、skills、MCP、memory、channels、frontend、custom agents 等多层结构

### 旧口径 2：DeerFlow 的关键价值只是“sub-agent”

**修正后：过窄。**

subagent 很强，但真正的平台价值来自：

- harness/app split
- thread-scoped data contract
- middleware runtime safety
- extensibility stack
- product surfaces（gateway + frontend + channels）

### 旧口径 3：它可以直接作为 Beacon 的近期功能清单

**修正后：风险很高。**

Beacon 更该学习的是 DeerFlow 的：

- 分层架构
- 数据与运行契约
- 可扩展面设计

而不是在短期内复制它的完整功能广度。

---

## 5. 与 Beacon 的真实可比维度

| 维度 | DeerFlow 的强项 | Beacon 可借鉴点 |
|------|-----------------|-----------------|
| Runtime architecture | 强 | harness/app split、LangGraph/gateway/front-end 分层 |
| Thread isolation | 强 | `workspace / uploads / outputs` 三分数据面 |
| Runtime safety | 强 | middleware-based loop guard、tool-error degradation、subagent limits |
| Extensibility | 强 | skills + MCP + community tools + custom agents |
| Productization | 强 | gateway routes、frontend workspace、channels、Docker/K8s |
| QA hierarchy | 中 | 后端测试较完整，但不是 gstack 那种 QA 金字塔 |
| Declarative workflow | 中 | 有 runtime/config surfaces，但不如 GSD 2 那样 definition/graph 中心化 |

---

## 6. 对 Beacon 的具体借鉴建议

### 适合吸收

1. **Harness / App split**
   - 把 Beacon 运行时框架层与产品/API/UI 层解耦

2. **线程级数据契约**
   - 明确 `workspace / uploads / outputs` 三种语义目录
   - 明确虚拟路径与真实路径映射

3. **middleware-based runtime safety**
   - loop detection
   - tool error downgrade
   - subagent concurrency limit
   - clarification / todo / memory / uploads 作为独立 concern

4. **扩展面分层**
   - workflow skills
   - protocol adapters / MCP
   - community tool adapters
   - custom agents

5. **custom agent 资源化**
   - 通过 `config.yaml + SOUL.md` 表达 agent identity 与约束
   - 让 agent 成为平台内可 CRUD 的对象

6. **上传-产物链路产品化**
   - 上传、转换、工作区、中间产物、最终展示分层处理

### 暂不建议直接照搬

1. **整套 full-stack 广度**
   - frontend workspace
   - IM channels
   - Docker + K8s provisioner
   - 官网/营销站/静态 demo 模式

2. **一次性复制 DeerFlow 的所有扩展面**
   - skills、MCP、community adapters、custom agents 同时做会导致范围失控

3. **把 LangGraph/具体实现细节当作必须选型**
   - Beacon 该学的是架构原则，不是被具体技术栈绑定

---

## 7. 对 Beacon v1.1.6 的优先级判断

如果把 DeerFlow 映射到 Beacon 的近期设计，我会把它拆成三层：

### P0（近期就值得吸收）
- Harness / App split
- 线程级目录契约（workspace / uploads / outputs）
- middleware-based runtime safety

### P1（下一阶段可吸收）
- custom agents 资源化
- skills + MCP 的双层扩展模型
- upload → artifact → present 的产品链路

### P2（长期再考虑）
- IM channels
- provisioner / Kubernetes sandbox
- 全量 Next.js 工作台与静态 demo 模式

---

## 8. 关键证据文件

### 根目录与产品面
- `oss-sync/agents/agent-skills/deer-flow/README.md`
- `oss-sync/agents/agent-skills/deer-flow/CONTRIBUTING.md`
- `oss-sync/agents/agent-skills/deer-flow/SECURITY.md`
- `oss-sync/agents/agent-skills/deer-flow/Makefile`
- `oss-sync/agents/agent-skills/deer-flow/config.example.yaml`
- `oss-sync/agents/agent-skills/deer-flow/extensions_config.example.json`

### Backend / Harness / App
- `oss-sync/agents/agent-skills/deer-flow/backend/CLAUDE.md`
- `oss-sync/agents/agent-skills/deer-flow/backend/README.md`
- `oss-sync/agents/agent-skills/deer-flow/backend/docs/ARCHITECTURE.md`
- `oss-sync/agents/agent-skills/deer-flow/backend/docs/HARNESS_APP_SPLIT.md`
- `oss-sync/agents/agent-skills/deer-flow/backend/docs/API.md`
- `oss-sync/agents/agent-skills/deer-flow/backend/docs/FILE_UPLOAD.md`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/config/paths.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/config/extensions_config.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/subagents/executor.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/tools/builtins/task_tool.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/tools/builtins/present_file_tool.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/app/gateway/app.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/app/gateway/routers/agents.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/app/gateway/routers/skills.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/app/gateway/routers/uploads.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/app/channels/service.py`

### Frontend
- `oss-sync/agents/agent-skills/deer-flow/frontend/AGENTS.md`
- `oss-sync/agents/agent-skills/deer-flow/frontend/CLAUDE.md`
- `oss-sync/agents/agent-skills/deer-flow/frontend/README.md`
- `oss-sync/agents/agent-skills/deer-flow/frontend/package.json`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/core/api/api-client.ts`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/core/threads/hooks.ts`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/core/config/index.ts`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/core/skills/api.ts`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/core/mcp/api.ts`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/core/uploads/api.ts`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/app/workspace/agents/page.tsx`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/env.js`

### 部署 / CI / 治理
- `oss-sync/agents/agent-skills/deer-flow/docker/docker-compose-dev.yaml`
- `oss-sync/agents/agent-skills/deer-flow/docker/docker-compose.yaml`
- `oss-sync/agents/agent-skills/deer-flow/docker/nginx/nginx.local.conf`
- `oss-sync/agents/agent-skills/deer-flow/.github/workflows/backend-unit-tests.yml`
- `oss-sync/agents/agent-skills/deer-flow/.github/ISSUE_TEMPLATE/runtime-information.yml`

---

## 9. 一句话总结

DeerFlow 对 Beacon 的最大启发不是“功能全”，而是：

> **它把 super-agent 平台拆成了可分层演进的 runtime、数据契约、扩展面和产品面，并且这些边界已经在源码里被清晰实现。**

