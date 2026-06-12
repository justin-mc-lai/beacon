# Beacon v1 架构缺陷全面审查

> 基于 Understand-Anything 确定性代码图分析（31,948 节点 / 33,955 边 / 6,706 函数 / 105 类）和全面思考五重审视。
> 生成时间：2026-06-11 | Git: 893a3cac

---

## 第一重审视：问题与领域

### 深层次目标

用户表层请求是"列出 Beacon v1 的架构缺陷"，但深层目标是：**理解这些缺陷的因果结构，识别哪些是 v2 重写的硬约束、哪些可以渐进修复，为重写路线提供判断底座。**

### 关键问题

Beacon v1 在 v1.0→v1.6 的多版本迭代中，从一个 Python 脚本集合演进为包含 60+ 命令、142 个 utils 模块、2 个 Node.js 长任务运行器的产品工作流内核。这期间积累了哪些结构性缺陷？这些缺陷的根因是什么？它们之间的关系如何？

### 边界

- 包含：Beacon Python CLI 核心、beacon-loop、beacon-run、skills harness 系统
- 不包含：beacon-console-ui（独立前端）、插件系统（边缘）

### 代价

问题定义错误会导致：v2 重写方向偏差（如过度关注性能而忽略治理强制力）、保留错误的抽象（如保留 beacon-loop/beacon-run 分裂）、遗漏关键能力（如长任务恢复）。

### 领域

| 领域 | 相关度 | 覆盖的问题 |
|------|--------|-----------|
| 有限状态机理论 | 核心 | 状态机缺失、转换约束 |
| 事件溯源 / CQRS | 核心 | 事件推导状态、状态不一致 |
| CLI 工程架构 | 高 | 启动性能、命令注册、eager import |
| 异步编程模型 | 高 | 同步阻塞、busy-wait、中断处理 |
| 证据链 / 审计日志 | 高 | evidence manifest、transaction journal |
| Agent 编排 | 中 | 多 Agent 后端、迭代循环、退避策略 |
| 产品工作流治理 | 中 | harness 分类法、需求真理交付 |

**这一重审视改变了什么**：将问题从"列缺陷清单"重新定义为"理解缺陷的因果结构并识别 v2 硬约束"。

---

## 第二重审视：领域大师理论体系与判断主轴

### 理论体系

**1. 有限状态机理论（Hopcroft & Ullman）**

核心概念：确定性有限自动机（DFA）要求每个状态对每个输入有且仅有一个转换。Beacon 主流程当前是 NFA（非确定性），因为同一输入（如"推进到下一阶段"）可能产生不同结果，取决于调用方代码路径。

思考角度：**状态机的强制力来自编译期穷举匹配，而非运行时约定。** 这直接对应 Beacon 的核心洞察——"CLI 强制执行才是法律"。

**2. 事件溯源（Event Sourcing, Martin Fowler / Greg Young）**

核心概念：状态不直接存储，而是从事件流推导。Beacon 的 `compute_workflow_progress` 正是这种模式。关键约束：**事件溯源需要 snapshot 机制来避免完整回放的性能退化**。Beacon 没有 snapshot，每次都全量回放。

思考角度：**事件溯源的代价是查询性能和状态推导复杂度。没有 snapshot 的事件溯源在数据增长后必然退化。**

**3. 分层架构（Layered Architecture, DDD / Evans）**

核心概念：核心域（core domain）零依赖，基础设施层（infrastructure）实现 IO。Beacon 的 `beacon/utils/` 把 142 个模块全放在一个平面，没有 core/infra 分离。

思考角度：**没有分层意味着核心业务逻辑和 IO/存储/CLI 框架耦合，重写时无法单独替换运行时。**

**4. Actor 模型 / CSP（Hewitt, Hoare）**

核心概念：并发实体通过消息通信，不共享状态。beacon-loop 的 spawnSync 模式正好相反——同步阻塞、共享文件系统状态。

思考角度：**长任务编排的本质是并发 Agent 协调，需要异步消息而非同步阻塞。**

### 关键矛盾与判断主轴

**主要矛盾：架构层级的强制力缺失 vs. 代码约定的软约束。**

Beacon v1 的 10 个缺陷不是独立的，它们共享同一个根因：**系统缺少架构层级的强制力**。代码约定（comments、docstrings、conventions）可以被绕过，只有类型系统和显式状态机转换表才能真正做到"CLI 强制执行"。

**次要矛盾：**
- 增长速度 vs. 抽象质量（快速迭代导致巨型文件和重复定义）
- 事件溯源的审计完整性 vs. 查询性能（全量回放退化和 779 run 目录）
- harness 分类法的治理需求 vs. 代码层面的实现混乱

**矛盾主次：** 主要矛盾是强制力缺失，其他缺陷是次要矛盾——它们是强制力缺失的具体表现。

**判断主轴：** v2 重写的核心不是性能优化，而是**将强制力从"代码约定"提升到"类型系统 + 状态机转换表"**。

**矛盾转化条件：** 如果 v2 只重写性能层（如用 Rust 替换 Python）而不建立显式状态机，主要矛盾不会转化——Agent 仍然可以绕过软约束。

**这一重审视改变了什么**：识别出"强制力缺失"是所有缺陷的共同根因，将 v2 的核心目标从"性能重写"重新定义为"架构层级强制力的建立"。

---

## 第三重审视：关键事实与综合理论体系

### 代码图关键事实

Understand-Anything 确定性分析结果：

| 指标 | 值 | 含义 |
|------|-----|------|
| 总节点 | 31,948 | 代码规模巨大 |
| 总边 | 33,955 | 依赖关系密集 |
| 函数节点 | 6,706 | 函数级复杂度 |
| 类节点 | 105 | 面向对象使用极少 |
| 导入边 | 2,031 | 模块间耦合 |
| 层级 | 24 | 目录层级深 |

**高耦合热点**（1-hop import degree 超过 50 的模块）：

| 模块 | 1-hop 度 | 风险 |
|------|----------|------|
| `main.py` | **187** | 入口点耦合全部模块 |
| `runtime.py` | **133** | 运行时是全局单点 |
| `versioning.py` | **113** | 版本解析是全局单点 |
| `artifact_paths.py` | **73** | 路径管理是全局单点 |
| `story_state.py` | **85** | 故事状态被广泛依赖 |
| `help_support.py` | **59** | 帮助系统耦合核心 |
| `gate.py` | **59** | 门控是全局依赖点 |
| `revision_state.py` | **51** | 修订状态被广泛依赖 |

### 10 大缺陷的证据链与因果结构

#### 缺陷 1：主流程无显式状态机

**证据**：
- [workflow_memory.py:25-26](beacon/utils/workflow_memory.py#L25-L26) 定义 `WORKFLOW_STAGES = ("prd", "user-story", "test-case", "implement", "qa", "release")`，但这只是一个**元组常量**，不是状态机
- [workflow_memory.py:1080-1200](beacon/utils/workflow_memory.py#L1080-L1200) 的 `compute_workflow_progress` 从事件流**逆向推导**状态，没有前置约束
- [planner_review_runtime.py:482-539](beacon/utils/planner_review_runtime.py#L482-L539) 的 `review_state_model()` 有完整 FSM（9 状态、9 allowed_transitions、9 invalid_transitions、4 recovery_paths、5 terminal_states）

**因果**：主流程的状态推进完全依赖 `workflow.py` 命令的迭代逻辑。如果其他命令（如直接调用 `beacon implement`）跳过了 prd→user-story→test-case，没有任何架构层级的阻止。

**后果**：Agent 可以绕过"Truth chain 不可反向改写"原则（global-boundaries.md 规定），因为这只是文档约定。

#### 缺陷 2：阶段定义分散

**证据**（4 处独立定义）：

| 文件:行 | 定义 | 差异 |
|---------|------|------|
| workflow_memory.py:25 | `("prd", "user-story", "test-case", "implement", "qa", "release")` | 无 prototype |
| semantic_runtime.py:37 | `("prd", "user-story", "test-case", "prototype", "implement", "qa", "release")` | 有 prototype |
| llm_loop.py:14 | `("prd", ..., "prototype", ..., "none")` | 有 prototype + none |
| workflow.py:64 | `[("prd", ...), ("user-story", ...), ..., ("prototype", ...)]` | 元组列表 |

**因果**：每次新增阶段（prototype）或特殊状态（none）时，开发者修改了自己熟悉的那个定义点，而没有统一到 canonical source。

#### 缺陷 3：巨型文件

**证据**：

| 文件 | 大小 | 行为 |
|------|------|------|
| prototype_utils.py | **6.8MB** | 全部 UI 原型逻辑 |
| gate.py | **5.0MB** | 5021 行，80+ reason codes |
| implementation_plan.py | **2.6MB** | 实现计划生成 |
| qa_feature.py | **2.3MB** | QA 特征验证 |

**因果**：Beacon 没有子包组织约定。`beacon/utils/` 是一个 142 个文件的平面目录，没有 `beacon.utils.qa/`、`beacon.utils.gate/` 等子包。新功能自然被追加到已有文件而非新建模块。

#### 缺陷 4：eager import

**证据**：[cli_factory.py:69-139](beacon/cli_factory.py#L69-L139) 有 50+ 条 `from .commands.xxx import app as xxx_app`，在 `build_app()` 中全量执行。[__init__.py:15](beacon/__init__.py#L15) 的 `app = create_app()` 在模块导入时即触发。

**因果**：Typer/Click 框架要求在构建 app 时注册所有命令。Python 没有像 Rust 的 lazy static 那样的零成本延迟加载机制。

#### 缺陷 5：beacon-loop 同步阻塞 + busy-wait

**证据**：
- [state.ts:40-46](packages/beacon-loop/src/runner/state.ts#L40-L46)：`while (Date.now() - start < ms) {}` busy-wait
- 25+ 处 `spawnSync` 调用（agents/, git/, ledger/db.ts, beacon-run-delegate.ts）
- ledger/db.ts 每次 `execSql` 都 `spawnSync("sqlite3", ...)` 无连接池

**因果**：beacon-loop 最初为测试场景设计（短退避窗口），`sleepMs` 的注释是"busy-wait for short test backoff windows without async"。后来扩展到生产场景但没有重构为异步。

#### 缺陷 6：状态不完备

**证据**：[workflow_memory.py:1133-1143](beacon/utils/workflow_memory.py#L1133-L1143) 只有 5 种状态判定逻辑：

```python
if completed_by_contract: status = "completed"
elif has_failed: status = "failed"
elif has_skipped and not has_started: status = "skipped"
elif latest_attempt_events: status = "in_progress"
else: status = "not_started"
```

缺失：`crashed`（进程被 kill -9）、`timed_out`（超时）、`interrupted`（SIGINT）、`repairing`（修复中）。

**因果**：事件溯源模式只能识别"有事件"的状态。进程崩溃不会写任何事件，所以崩溃的阶段看起来和"刚启动"一样。

#### 缺陷 7：779 run 目录无清理

**证据**：`.beacon/runs/` 下有 779 个 run 目录。`resolve_workflow_run_id` 需要扫描所有 run 的时间戳来找到最新。事件上限硬编码 5000 条但没有压缩。

**因果**：每次 run 创建一个 JSON 目录，没有 TTL/归档/cleanup 命令。

#### 缺陷 8：beacon-loop/beacon-run 重叠

**证据**：
- beacon-loop 有 12 状态 Delivery FSM + intent 分类 + truth gap scan
- beacon-run 有 4 阶段 PhaseController + 24 agent 模块 + async/await + EventEmitter
- beacon-loop 已通过 `delegateGoalToBeaconRun` 将默认执行委托给 beacon-run
- 但保留了 `--legacy-delivery` 旧路径

**因果**：beacon-run 继承自 gnhf 项目（第三方），beacon-loop 是 Beacon 自研。两者功能重叠但没有统一。

#### 缺陷 9：版本三处不一致

**证据**：
- [__init__.py:4](beacon/__init__.py#L4)：`__version__ = "1.5.2"` — 硬编码
- [version-truth.json:3](beacon/version-truth.json#L3)：`"package_version": "1.5.2"` — JSON 文件
- skills/beacon/metadata.json：`"version": "1.6.0"` — 已超前
- [version_surface.py:22-29](beacon/utils/version_surface.py#L22-L29)：用 8 个正则表达式在 6+ 类文件中搜索和替换版本号

**因果**：没有单一版本来源（single source of truth）。每次发布需要手动同步 3+ 处，遗漏导致漂移。

#### 缺陷 10：token 估算

**证据**：两处独立实现：
- [llm_loop.py:33-34](beacon/utils/llm_loop.py#L33-L34)：`max(1, len((text or "").split()))`
- [prototype_utils.py:4298-4299](beacon/utils/prototype_utils.py#L4298-L4299)：同样的实现

**因果**：使用空格分词估算，对中文（无空格）和代码（标识符消耗更多 token）误差极大。

### 综合理论体系：Beacon v1 缺陷因果图

```
根因：架构层级强制力缺失
 │
 ├── 表现 1：无显式状态机（缺陷 1）
 │    ├── 阶段定义分散（缺陷 2）— 没有强制统一的 canonical source
 │    ├── 状态不完备（缺陷 6）— 没有状态枚举约束
 │    └── Agent 可绕过 truth chain 原则
 │
 ├── 表现 2：快速增长未重构
 │    ├── 巨型文件（缺陷 3）— 无子包组织约定
 │    ├── eager import（缺陷 4）— Typer 框架限制 + 无延迟加载
 │    └── 779 run 目录（缺陷 7）— 无 TTL/归档策略
 │
 ├── 表现 3：运行时架构选择
 │    ├── 同步阻塞 + busy-wait（缺陷 5）— 初始为测试设计，未重构
 │    ├── loop/run 重叠（缺陷 8）— 自研 + 第三方继承，未统一
 │    └── token 估算（缺陷 10）— 简单实现未演进
 │
 └── 表现 4：版本治理不足
      └── 版本三处不一致（缺陷 9）— 无 single source of truth
```

**深层机制**：Beacon v1 的缺陷不是偶然的，而是"代码约定替代架构约束"这一设计选择的必然结果。当一个系统只有软约束时，每个开发者在不同时间点的局部最优决策会逐渐偏离全局一致性。这正是 Beacon 核心洞察所描述的现象——**"Agent 会适应并绕过软性限制"**——不只适用于 AI Agent，也适用于人类开发者。

**这一重审视改变了什么**：建立了缺陷之间的因果结构，识别出"强制力缺失"是单一根因，所有 10 个缺陷都是这个根因在不同维度的表现。

---

## 第四重审视：反方压力与结论前提辩证分析

### 候选解释 1：强制力缺失是根因，v2 必须从架构层级重建

**解释力**：能解释全部 10 个缺陷的因果关联。能解释为什么子流程（planner_review）有 FSM 而主流程没有——子流程是后来设计的，吸取了教训。能解释为什么每次修复一个问题（如新增 prototype 阶段），会在另一个地方产生不一致。

### 候选解释 2：缺陷是快速增长的自然结果，渐进修复即可

**解释力**：能解释缺陷 3（巨型文件）、4（eager import）、7（run 目录积累）、9（版本漂移）——这些都是增长带来的工程债。**但解释不了**缺陷 1（为什么子流程有 FSM 而主流程没有？增长不会导致选择性缺失）。

### 最强反方意见

**"Rust 重写核心的风险大于收益。Beacon 的价值在于 skill 生态和 harness 分类法，不在于底层实现语言。用 Python 重构（加 asyncio、加 Pydantic 状态机、拆分子包）可以在更低成本下解决大部分性能和治理问题。"**

**反方成立的条件**：
1. Python 的 asyncio + Pydantic 状态机能否提供编译期级别的强制力？——不能，Pydantic 只提供运行时校验
2. Python CLI 冷启动能否从 800ms 降到 100ms 以内？——极难，Python 解释器启动本身 ~100ms
3. Python 能否提供单二进制分发？——不能（PyInstaller 等方案体积大、兼容性差）
4. Python 能否替换 busy-wait？——asyncio 可以，但 beacon-loop 是 TypeScript

**反方成立概率**：中等。如果只看性能，Python 重构确实够用。但核心洞察是"强制力"，而非"性能"。Python 无法提供编译期穷举匹配，这是类型系统的根本限制。

### 前提辩证分析

| 前提 | 来源 | 置信度 | 判断动作 |
|------|------|--------|---------|
| "编译期强制 > 运行时约定" | 理论推导（FSM 理论）+ Beacon 自身经验（子流程有 FSM 效果好） | 高 | 前提通过 |
| "Rust 重写后 skill 生态不受影响" | 推测（PyO3 绑定可保持兼容） | 中 | 需补证：PyO3 构建复杂度、wheel 分发可行性 |
| "Rust 核心能解决状态机问题" | 理论（enum 穷举匹配） | 高 | 前提通过 |
| "长任务能力必须统一" | 事实（beacon-loop 委托给 beacon-run） | 高 | 前提通过 |
| "性能是 v2 的次要目标" | 分析（主要矛盾是强制力缺失） | 中 | 需验证：用户对 CLI 启动速度的实际容忍度 |

**这一重审视改变了什么**：识别出 Rust 重写的主要风险在 PyO3 构建复杂度和 skill 生态兼容，而非 Rust 本身。将"Python 重构"作为竞争方案，但确认其在编译期强制力上的根本限制。

---

## 第五重审视：全貌理解与可验证收束

### 全貌理解

Beacon v1 是一个经历了 v1.0→v1.6 共 6 个大版本迭代的产品工作流内核。它的 10 个架构缺陷不是独立的工程债，而是**同一根因——架构层级强制力缺失——在不同维度的表现**：

1. **治理维度**（缺陷 1, 2, 6, 9）：没有显式状态机、阶段定义分散、状态不完备、版本漂移——都是"缺少 canonical source + 编译期校验"的结果
2. **增长维度**（缺陷 3, 4, 7）：巨型文件、eager import、run 目录积累——都是快速增长缺少重构的结果
3. **运行时维度**（缺陷 5, 8, 10）：同步阻塞、loop/run 重叠、token 估算——都是架构选择（Python 同步 + Node.js 双包）的结果

这三组缺陷的交互形成了**恶性循环**：治理缺陷使得运行时修改变得危险（因为无法确定影响范围），增长缺陷使得运行时优化变得困难（因为巨型文件难以理解），运行时缺陷使得治理改善变得不可行（因为同步阻塞限制了中断恢复能力）。

### 长任务能力的核心价值

beacon-loop 的核心价值不是"运行 Agent 迭代"，而是**将需求真相交付（truth delivery）从人工作业变为自动化闭环**：

1. **意图捕获与分类**：将自然语言 goal 转化为 Beacon feature + version + lifecycle route
2. **真理缺口扫描与填充**：检测需求材料缺失，触发 prd/user-story/test-case 生成
3. **Phase 分离**：Agent phases（truth/generate）与 Harness phases（qa/release）的解耦
4. **失败恢复**：连续失败上限 + 指数退避 + git rollback

v2 应保留这 4 个核心价值，并增强：
- 增加 `Crashed`/`TimedOut`/`Interrupted` 状态和恢复路径
- 统一 beacon-loop 和 beacon-run 为单一编排器
- 用 SQLite 替换 JSON 目录，支持高效查询和自动归档

### harness 分类法的架构张力

v1.6.0 的 harness 分类法（pln/gen/eval/gov × 33 skills）带来的张力：

1. **命名映射复杂度**：metadata.json 含 78 个旧别名 → 33 个新名称的 rename matrix。这意味着任何调用方都可能使用旧名或新名，增加了路由复杂度。
2. **Skill 与 CLI 命令不是 1:1**：`beacon-gov-doctor` 对应 `beacon doctor`，但 `beacon-gov-extract` 对应 `beacon design --extract`。这种不一致增加了 v2 的路由设计难度。
3. **Harness 分类是运行时而非编译时**：Python 无法在编译期强制 skill 路由到正确的 harness 类型。v2 可以用 Rust trait（`PlannerSkill`、`GeneratorSkill`、`EvaluatorSkill`、`GovernorSkill`）实现编译时分类。

### Rust 重写核心的风险点

1. **PyO3 构建复杂度**：需要 Rust 工具链 + Python 开发头文件。缓解：CI 预编译 wheel。
2. **JSON 契约兼容**：Rust serde_json 输出必须与 Python json.dumps(ensure_ascii=False, indent=2) 格式一致。缓解：自定义 formatter。
3. **Skill 生态迁移**：33 个 skill 目录的 SKILL.md 中引用的 CLI 命令名必须不变。缓解：Python 兼容层。
4. **迭代治理环**：当前 `.beacon/iteration-governance/` 最新状态为 failed，说明 Beacon 自身的治理环有未解决的阻断项。在 v2 重写期间，v1 的治理环必须继续工作。

### 硬约束 vs. 可渐进修复

| 缺陷 | v2 硬约束？ | 理由 |
|------|------------|------|
| 1. 无显式状态机 | **是** | 这是核心洞察的实现基础 |
| 2. 阶段定义分散 | **是** | 状态机的 canonical source 必须唯一 |
| 5. 同步阻塞 + busy-wait | **是** | 长任务能力的基础 |
| 6. 状态不完备 | **是** | 中断恢复的必要条件 |
| 8. loop/run 重叠 | **是** | 统一编排器的前提 |
| 3. 巨型文件 | 可渐进 | 可先拆分再重写 |
| 4. eager import | 可渐进 | 可用 Python lazy import 缓解 |
| 7. 779 run 目录 | 可渐进 | 可加 cleanup 命令 |
| 9. 版本不一致 | 可渐进 | 可加 single source 脚本 |
| 10. token 估算 | 可渐进 | 可用 tiktoken 库替换 |

### 验证路径

1. **证据**：Understand-Anything 知识图（31,948 节点）已验证模块耦合热点
2. **实验**：v2 P0 阶段（beacon-core + beacon-store）可验证 Rust enum 穷举匹配是否阻止非法转换
3. **实现**：v2 P3 阶段（beacon-orchestrator）可验证 tokio async 是否消除 busy-wait
4. **测试**：v2 P4 阶段（beacon-python）可验证 PyO3 绑定是否保持 skill 兼容
5. **验收**：v2 P6 阶段可验证 `.beacon/` 数据迁移无损

**这一重审视改变了什么**：将 10 个缺陷分类为硬约束和可渐进修复，为 v2 实施优先级提供判断依据。

---

## 最终判断

Beacon v1 的 10 个架构缺陷共享同一个根因：**架构层级强制力的缺失**。这不是增长的自然结果，而是设计选择——用代码约定代替类型系统约束——的必然产物。v2 重写的核心目标不是性能优化，而是**将强制力从"代码约定"提升到"类型系统 + 显式状态机转换表"**。6 个缺陷（1,2,5,6,8 + 状态机相关）是 v2 硬约束，必须在 Rust 核心中从零建立；4 个缺陷（3,4,7,9,10）可渐进修复。Rust 重写的主要风险在 PyO3 构建复杂度和 JSON 契约兼容，而非 Rust 本身的能力。结论可信度：**高**（因果结构完整、代码证据充分、反方意见已被编译期强制力 vs 运行时约定的根本限制所回应）。
