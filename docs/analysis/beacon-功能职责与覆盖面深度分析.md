# Beacon 深度分析：功能职责与 AI Agent Skill 覆盖面

**分析日期**: 2026-04-20  
**分析版本**: v1.3.3  
**文档状态**: 深度分析报告

---

## 一、核心定位

**Beacon 是一个 Evidence-first Product Workflow Kernel**，它的本质是：

> 把需求澄清、用户故事、PRD、测试用例、执行证据与 gate/release 收敛到一个可审计闭环的产品工作流内核。

### 1.1 设计哲学

Beacon 遵循三个核心原则：

1. **人类极简心智负担** - 人类只面对 6+3 个主命令
2. **证据驱动闭环** - 所有决策必须有可审计的证据链
3. **机器内部消化复杂度** - 复杂的执行逻辑（team/subagent/precheck）对人类透明

### 1.2 架构规模

- **52 个命令模块**，但只有 10 个是人类主面
- **77 个工具模块**支撑核心能力
- **极度克制的对外命令面**

---

## 二、功能架构分层

### 2.1 Core Layer（核心层）

**人类主流程（7段）：**
```
prd → user-story → test-case → prototype → implement → qa → release
```

**辅助命令（3个）：**
- `help` - 导航与帮助
- `status` - 状态查询
- `doctor` - 诊断与修复

### 2.2 Support Layer（支持层）

包含 18 个支持命令：
- `ask`, `skill`, `profile`, `implement`, `verify`, `orchestrate`
- `report`, `review`, `feedback`, `freeze`, `reopen`
- `remember`, `recall`, `resume`, `version`, `evolution-summary`
- `init`, `test-progress`, `debug`

### 2.3 Labs Layer（实验层）

13 个可选分析/模板命令：
- `analyze`, `api-design`, `brainstorm`, `data-dictionary`
- `design`, `jtbd`, `kano`, `lighthouse`
- `memory-friction-evolution`, `moscow`, `persona`
- `roadmap`, `ui-spec`

### 2.4 Compatibility Layer（兼容层）

历史遗留与桥接命令：
- `run`, `team`, `ralph-bridge`
- 外部 adapter：`omx`, `omc`, `gstack`

---

## 三、核心能力矩阵

### 3.1 需求管理能力

| 能力 | 命令 | 职责 | 产物 |
|------|------|------|------|
| 需求思考 | `think` | 需求澄清与问题定义 | 思考记录 |
| PRD 生成 | `prd` | 产品需求文档编写 | `docs/beacon/<version>/prd/<feature>.md` |
| 用户故事 | `user-story` | 转换为可执行用户故事 | `docs/beacon/<version>/user-story/<feature>.md` |
| 测试用例 | `test-case` | 生成验收测试用例 | `docs/beacon/<version>/qa/test-cases/<feature>.md` |
| 原型设计 | `prototype` | 需求驱动的线框图冻结 | `docs/beacon/<version>/prototype/<feature>/` |

**特色能力：**
- **Requirement Traceability** - PRD → User Story → Test Case → Implementation 全链路可追溯
- **Canonical Envelope** - 单一提交源，多写入点事务一致性
- **Anti-drift 机制** - 跨面一致性审计（human/machine/sqlite）

### 3.2 执行管理能力

| 能力 | 命令 | 模式 | 特点 |
|------|------|------|------|
| 实现执行 | `implement` | single/team/ralph | 宿主原生优先 |
| QA 验收 | `qa` | 精确度感知验证 | 浏览器证据 + scorecard |
| 工作流编排 | `workflow` | 自动化流程 | 兼容性入口 |

**三种实现模式：**

1. **Single Mode** - 单代理直接实现
2. **Team Mode** - 宿主原生 bounded team runtime
   - 自动 lane 拆解
   - verifier/repair-handoff-writer/implementation-architect 协作
3. **Ralph Mode** - 宿主原生闭环控制器
   - 自动迭代修复
   - 状态机驱动

**关键机制：**
- **Runtime Readiness Precheck** - 执行前宿主能力检测
- **Delegation Readiness Precheck** - 委托前准备度检查
- **Implementation Plan** - 结构化实现计划与进度追踪
- **Git Workflow Contract** - 分支策略与提交规范

### 3.3 质量保证能力

| 能力 | 实现 | 特点 |
|------|------|------|
| 多层次测试 | ui/api-curl/unit/smoke/visual/functional/interface/contract/integration/regression/exception/compatibility | 11 种测试类型 |
| 精确度校准 | QA Precision Model | 基于历史数据的精确度预测 |
| 证据收集 | Browser Evidence | 截图/视频/日志/断言计数 |
| 穷尽性报告 | Exhaustiveness Report | AC 覆盖度分析 |
| 学习循环 | Learning Loop | 需求重写输入生成 |

**QA 特色：**
- **Feature QA Matrix** - 特性级别的测试矩阵
- **Verification Writeback** - 验证结果回写
- **Flaky Test Handling** - 不稳定测试重跑机制
- **Session Management** - QA 会话状态管理

### 3.4 发布治理能力

| 能力 | 命令 | 职责 |
|------|------|------|
| Gate 检查 | `gate` | 发布门禁检查 |
| Release 管理 | `release` | 版本发布与 scorecard |
| 证据清单 | Evidence Manifest | 交付物清单管理 |
| 冻结/重开 | `freeze`/`reopen` | 需求冻结与重开 |

**Gate 机制：**
- **Takeover Baseline Gate** - 接管基线门禁
- **Profile Gate** - 项目配置门禁
- **Implementation Plan Gate** - 实现计划门禁
- **Release Gate** - 发布门禁

### 3.5 诊断与修复能力

`doctor` 子命令体系：

```bash
beacon doctor setup-context          # 上下文设置
beacon doctor verify-context         # 上下文验证
beacon doctor sync-materials         # 材料同步
beacon doctor setup-codex-hud-hook   # HUD hook 设置
beacon doctor verify-codex-hud-hook  # HUD hook 验证
beacon doctor migrate-compat         # 兼容性迁移（v1.3.3+）
```

**诊断能力：**
- 项目结构完整性检查
- 材料版本对齐验证
- 宿主能力检测
- 配置正确性验证
- 迁移路径规划

---

## 四、技术架构特色

### 4.1 多宿主支持

Beacon 设计为宿主无关，支持：
- **Codex** - 优先落地口径
- **Claude** - 同构语义支持
- 通过 `detect_host_runtime()` 自动检测

### 4.2 状态管理

```
.beacon/
├── state/              # 运行时状态
│   ├── hud-hook/      # HUD hook 状态
│   ├── compat-migration/  # 兼容性迁移
│   └── sessions/      # 会话状态
├── implement/         # 实现执行记录
├── qa/               # QA 执行记录
└── debug/            # 调试输出
```

### 4.3 版本化材料管理

```
docs/beacon/
├── global-boundaries.md    # 全局约束（跨版本）
├── v1.3.3/                # 版本化文档
│   ├── SUMMARY.md
│   ├── prd/
│   ├── user-story/
│   ├── qa/test-cases/
│   ├── prototype/
│   ├── execution/
│   └── release/
└── v1.3.4/                # 下一版本
```

### 4.4 契约驱动设计

**核心契约：**
1. **Technical Review Contract** - 技术审查契约
2. **Implementation Git Workflow Contract** - Git 工作流契约
3. **QA Team Contract** - QA 团队契约
4. **Global Boundaries** - 全局边界约束

### 4.5 证据链管理

```
Evidence Chain:
PRD → User Story → Test Case → Implementation → QA Evidence → Release Scorecard
  ↓       ↓           ↓              ↓              ↓              ↓
 冻结    AC定义    验收场景      代码变更      浏览器证据    发布清单
```

---

## 五、作为 AI Agent Skill 的覆盖面

### 5.1 产品管理维度

✅ **完整覆盖：**
- 需求澄清与问题定义
- PRD 编写与结构化
- 用户故事拆解
- 验收标准定义
- 原型设计（线框图级别）
- 路线图规划（`roadmap`）
- 人物画像（`persona`）
- JTBD 分析（`jtbd`）
- Kano 模型（`kano`）
- MoSCoW 优先级（`moscow`）

❌ **不覆盖：**
- 高保真视觉设计
- 设计系统定稿
- 市场调研
- 竞品分析

### 5.2 工程实施维度

✅ **完整覆盖：**
- 实现计划生成
- 代码实现执行（通过宿主）
- Git 工作流管理
- 分支策略执行
- 团队协作编排
- 迭代修复循环

⚠️ **部分覆盖：**
- 代码审查（通过 `review`，但依赖宿主能力）
- 性能优化（不是核心职责）
- 安全扫描（不是核心职责）

❌ **不覆盖：**
- 直接替代业务代码实现
- 生产运维
- 发布平台集成

### 5.3 质量保证维度

✅ **完整覆盖：**
- 测试用例生成
- 多层次测试执行
- 浏览器自动化测试
- 证据收集与归档
- 精确度校准
- 穷尽性分析
- 回归测试
- 兼容性测试

⚠️ **部分覆盖：**
- 性能测试（可通过扩展）
- 安全测试（可通过扩展）
- 负载测试（不是核心职责）

### 5.4 发布管理维度

✅ **完整覆盖：**
- 发布门禁检查
- 证据清单管理
- 版本 scorecard
- 需求冻结/重开
- 交付物验证
- 可追溯性审计

❌ **不覆盖：**
- CI/CD 平台集成
- 生产部署执行
- 监控告警
- 回滚操作

### 5.5 协作与治理维度

✅ **完整覆盖：**
- 团队协作编排
- 角色分工（verifier/architect/repair-writer）
- 状态同步与 HUD
- 证据链审计
- 合规性检查
- 迁移治理

⚠️ **部分覆盖：**
- 跨团队协作（单项目范围内）
- 知识管理（通过 `remember`/`recall`）

### 5.6 分析与洞察维度

✅ **完整覆盖：**
- 需求分析（`analyze`）
- API 设计（`api-design`）
- 数据字典（`data-dictionary`）
- UI 规格（`ui-spec`）
- 演进摘要（`evolution-summary`）
- 记忆摩擦演进（`memory-friction-evolution`）
- Lighthouse 分析（`lighthouse`）

---

## 六、独特价值主张

### 6.1 与传统工具的差异

| 维度 | 传统工具 | Beacon |
|------|----------|--------|
| 需求管理 | Jira/Confluence | 代码化 + 版本化 + 可审计 |
| 测试管理 | TestRail | 需求驱动 + 证据链 + 精确度校准 |
| 发布管理 | Jenkins/GitLab CI | 门禁驱动 + 证据清单 + scorecard |
| 协作模式 | 人工协调 | AI agent 自动编排 |
| 可追溯性 | 手工维护 | 自动化全链路追溯 |

### 6.2 核心竞争力

1. **Evidence-first** - 所有决策必须有证据支撑
2. **Requirement Closure** - 需求闭环强制执行
3. **Machine-consumable** - 机器可读 + 人类可读双输出
4. **Host-native** - 充分利用宿主 AI 能力
5. **Minimal Human Surface** - 极简人类心智负担
6. **Canonical Driven** - 单一真相源，多点投影
7. **Anti-drift** - 跨面一致性强制保证

### 6.3 适用场景

**最适合：**
- AI-native 产品开发团队
- 需要严格可追溯性的项目
- 快速迭代的产品原型验证
- 需求频繁变更的敏捷项目
- 小型到中型团队（1-10人）

**不适合：**
- 传统瀑布式开发
- 超大型企业级项目（100+人）
- 需要复杂 CI/CD 集成的场景
- 纯运维/DevOps 场景

---

## 七、v1.3.3 演进方向

当前版本（v1.3.3）的核心主题是 **"核心瘦身与外部 skill 降级"**：

### 7.1 收敛目标

```
Core = 6+3 human minimal surface
     + host-native implement/qa
     + contract/evidence/gate kernel

Compatibility = external skill adapters
              + profile/orchestration legacy
              + deprecated bridge surfaces
```

### 7.2 关键变化

1. **宿主原生优先** - 移除 `omx/omc/gstack` 内置 adapter
2. **兼容性统一治理** - 通过 `doctor migrate-compat` 统一迁移
3. **QA 默认行为收敛** - 不再隐式触发外部编排
4. **HUD 轻量增强** - Ralph/Team HUD 闭环观测
5. **文档主面收口** - 只教 6+3，兼容性单独文档

### 7.3 全局约束（17 条）

Beacon 遵循 17 条全局约束（`global-boundaries.md`），核心包括：

1. 人类主流程固定为 7 段，不得扩张
2. 不新增公开一级主命令
3. `implement` 与 `qa` 仍是唯一执行入口
4. team/subagent/precheck 默认留在机器内部
5. 预检查必须内嵌到 `implement` / `qa`
6. `prd → user-story → test-case → acceptance` 是立项根本
7. 所有 implement lane 都必须绑定同一份 requirement truth
8. requirement traceability 必须可被 review-spec / gate 检查
9. `prototype` 必须是闭环推理产物，不得退化为静态模板
10. 多写入点必须采用 canonical 驱动与事务一致提交
11. 跨面 anti-drift 一致性必须可审计
12. 宿主上下文必须唯一
13. 外部运行时只可作为调研借鉴
14. 外部规范仓库只可借鉴吸收，不形成默认依赖
15. 默认行为边界必须同时约束 Beacon 自身与目标项目
16. 默认行为边界必须包含四类轻量原则（显式假设/简单优先/外科手术式改动/目标驱动验证）
17. 人类输出必须极简，机器输出必须完整

---

## 八、总结

Beacon 是一个**高度专注、边界清晰、证据驱动**的产品工作流内核。它的核心价值不在于功能的广度，而在于：

### 8.1 核心价值

1. **深度整合** - 需求→实现→验收→发布的全链路闭环
2. **证据驱动** - 所有环节都有可审计的证据链
3. **AI-native** - 充分利用 AI agent 能力，但保持人类极简心智负担
4. **工程严谨** - 契约驱动、状态机控制、事务一致性保证

### 8.2 覆盖面特征

作为 AI agent skill，Beacon 的覆盖面是**纵向深度优于横向广度**的典范：

- ✅ **深度覆盖**：产品工作流垂直领域的极致深度
- ✅ **证据闭环**：从需求到发布的完整可追溯链
- ✅ **质量保证**：11 种测试类型 + 精确度校准 + 穷尽性分析
- ✅ **治理能力**：门禁机制 + 契约驱动 + 迁移治理
- ⚠️ **有限广度**：不试图替代所有开发工具
- ❌ **明确边界**：不做运维、不做 CI/CD 平台、不做高保真设计

### 8.3 设计智慧

Beacon 的设计体现了几个重要的工程智慧：

1. **克制** - 52 个命令模块，只暴露 10 个给人类
2. **分层** - Core/Support/Labs/Compatibility 清晰分层
3. **收敛** - v1.3.3 继续瘦身，而不是扩张
4. **证据** - Evidence-first 不是口号，是强制执行的架构约束
5. **契约** - 通过契约而非代码耦合来保证质量
6. **闭环** - 需求闭环是立项根本，不可妥协

### 8.4 最终评价

Beacon 不试图做所有事情，但在产品工作流这个垂直领域做到了：

- **最小人类心智负担**（6+3 命令）
- **最强证据链保证**（全链路可追溯）
- **最严格的一致性**（canonical 驱动 + anti-drift）
- **最灵活的执行**（single/team/ralph 三模式）

这是一个**为 AI-native 时代设计的产品工作流内核**，它的价值在于把复杂度留给机器，把简洁留给人类，把严谨留给工程。

---

**文档版本**: 1.0  
**最后更新**: 2026-04-20  
**分析深度**: 完整（代码库 + 文档 + 架构）

