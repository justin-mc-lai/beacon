# PRD: Beacon implement 技术实现归档与技术架构落盘（v1.1.8）

## 1. 背景

当前 Beacon `implement` 已具备：

- request/result 契约
- implementation marker
- `implementation-summary-<feature>.json/.md`
- changed_files / verification / artifact_updates

这套链路解决的是：

- implementation stage 如何被 Beacon 正式承接
- 实现结果如何进入 review / verify / gate

但它**还不够服务技术团队的长期查看与接手**。

因为实际技术接手/复盘时，最关心的不只是：
- 哪些文件改了
- 测试跑没跑

而是：
- 这次需求实现对应了哪些模块
- 做了哪些增删改查
- 增加了哪些 API / job / queue / config / env
- 是否涉及数据库表 / migration / schema change
- 如果是多服务项目，改动落在哪些服务边界
- 回滚和兼容风险在哪里

当前 `implementation-summary` 更像**执行摘要**，还不是**技术实现归档文档**。

## 2. 第一性原理结论

### 2.1 技术归档文档的职责

Beacon 在 implementation 完成后，应该产出两类文档：

1. **执行摘要**
   - 给流程/产品/验收看
   - 简洁、面向 closure

2. **技术实现归档**
   - 给技术、接手人、评审人看
   - 细化到模块、文件、接口、数据、风险、回滚

### 2.2 如果只有 execution summary，会发生什么

- 技术接手时仍需自己翻 diff
- 无法快速知道本次实现对系统结构的实际影响
- 数据库/API/配置/任务调度等变更容易漏看
- 版本演进后难以形成“需求 → 代码结构 → 风险”的长期对照面

### 2.3 最合理的并入方式不是“再加一份孤立文档”，而是三层归档

最推荐模型：

1. **Runtime Raw**
   - `.beacon/implement/<run_id>/request.json`
   - `.beacon/implement/<run_id>/result.json`
   - `.beacon/implement/<run_id>/stdout.log`
   - `.beacon/implement/<run_id>/stderr.log`
   - `.beacon/implement/<run_id>/command.txt`

2. **Machine Secondary**
   - `docs/beacon/<version>/.machine/execution/technical-implementation-<feature>.json`

3. **Human Primary**
   - `docs/beacon/<version>/execution/technical-implementation-<feature>.md`

也就是：

> runtime raw → machine archive → human archive

三层一一映射，才能同时满足：
- 技术查看
- review / report / future automation 消费
- 长期版本归档与追溯

## 3. 目标

1. **为 implement 阶段补齐正式技术实现归档面**
2. **让技术团队能直接查看每次需求实现的结构化归档**
3. **让归档信息覆盖代码改动、增删改查、接口、数据库、配置、任务与风险**
4. **让多服务项目也能用统一 schema 输出技术归档**
5. **保持现有 implementation-summary 兼容，不破坏已有实现链路**

## 4. 非目标

1. 不要求 v1.1.8 自动生成完整 ADR 系统；
2. 不要求自动反编译所有业务逻辑到自然语言；
3. 不替代代码评审或数据库 migration review；
4. 不把归档文档做成 deployment runbook 的替代品；
5. 不在 v1.1.8 宣称自动分析所有语言/框架已实现。

## 5. 核心设计

## 5.1 新增技术归档工件

建议在 implementation 完成后，除现有 summary 外，再新增双层正式归档：

```text
docs/beacon/<version>/execution/
├── implementation-summary-<feature>.md
└── technical-implementation-<feature>.md

docs/beacon/<version>/.machine/execution/
├── implementation-summary-<feature>.json
└── technical-implementation-<feature>.json
```

其中：
- `implementation-summary-*`：保持轻量 closure 摘要
- `technical-implementation-*`：面向技术归档
- `.beacon/implement/<run_id>/...`：继续保存原始执行证据

## 5.2 Traceability 主键

技术归档必须贯穿以下主键：

- `feature_slug`
- `version`
- `revision_id`
- `run_id`
- `runner`
- `profile_id`
- `git_commit`
- `services[]`

这样才能稳定追溯：

> 哪个版本、哪个 revision、哪次 implement run、通过哪个 runner/profile，在哪些服务上形成了哪份技术归档。

## 5.3 技术归档最小字段

### A. 基础元信息
- `feature`
- `feature_slug`
- `version`
- `revision_id`
- `run_id`
- `implemented_at`
- `runner`
- `profile_id`
- `git_commit`
- `services[]`

### B. 需求实现摘要
- `implementation_scope_summary`
- `business_goal_summary`
- `acceptance_scope[]`

### C. 代码结构变更
- `changed_files[]`
- `modules_touched[]`
- `additions[]`
- `modifications[]`
- `deletions[]`
- `refactors[]`

### D. CRUD / 数据面
- `data_operations[]`
  - create
  - read
  - update
  - delete
- `db_changes[]`
  - new_tables[]
  - altered_tables[]
  - indexes[]
  - migrations[]
- `cache_changes[]`
- `event_contract_changes[]`

### E. 接口与集成
- `api_changes[]`
  - new_endpoints[]
  - changed_endpoints[]
  - removed_endpoints[]
- `external_integrations[]`
- `queue_or_job_changes[]`
- `cron_changes[]`

### F. 配置与部署面
- `config_changes[]`
- `env_changes[]`
- `feature_flags[]`
- `deployment_notes[]`

### G. 验证与风险
- `verification[]`
- `known_risks[]`
- `rollback_notes[]`
- `compatibility_notes[]`
- `artifact_updates`

## 5.4 “没有变化”也必须显式记录

技术归档不能只记录“有变的东西”，还必须允许明确写：

- `db_changes: none`
- `new_tables: []`
- `api_changes: none`
- `env_changes: none`

否则读者会误以为 Beacon 没采集到，而不是确实没有。

## 5.5 适配多服务项目

技术归档必须支持：

```json
{
  "services": [
    {
      "name": "marketing_primary_fe",
      "role": "frontend",
      "changed_files": []
    },
    {
      "name": "marketing_sys",
      "role": "backend",
      "changed_files": []
    }
  ]
}
```

这样像 Rolo 这类多服务项目，才能形成真正的技术接手文档。

## 5.6 归档不等于源码 diff 替代品

技术归档应回答：
- 为什么改
- 改在哪
- 哪类影响最大
- 数据/API/配置是否受影响

而不是把 git diff 原文塞进文档。

## 6. 功能需求

### FR-001 implement 完成后新增技术归档工件

成功实现后必须支持写：
- `docs/beacon/<version>/.machine/execution/technical-implementation-<feature>.json`
- `technical-implementation-<feature>.md`

### FR-002 技术归档必须保留三层归档关系

同一条 implement 结果必须能在：
- runtime raw
- machine archive
- human archive

三层之间形成可追溯映射。

### FR-003 技术归档必须带 traceability 主键

至少包含：
- `feature_slug`
- `version`
- `revision_id`
- `run_id`
- `runner`
- `profile_id`
- `git_commit`
- `services[]`

### FR-004 技术归档必须覆盖代码变更分类

至少区分：
- 新增
- 修改
- 删除
- 重构

### FR-005 技术归档必须覆盖数据面

至少覆盖：
- CRUD
- migration
- 新表/改表/索引
- cache/event changes

### FR-006 技术归档必须覆盖接口与任务面

至少覆盖：
- API
- queue/job
- cron
- external integrations

### FR-007 技术归档必须覆盖配置和环境面

至少覆盖：
- config changes
- env changes
- feature flags
- deployment notes

### FR-008 技术归档必须支持多服务输出

归档 schema 必须支持单仓单服务与多服务结构。

### FR-009 技术归档与 implementation-summary 共存

不能用技术归档替换 implementation-summary，而应双层并存。

### FR-010 技术归档能服务技术接手与版本复盘

文档应足够结构化，能作为：
- 技术评审回看
- 二开接手
- 版本演进归档
- 风险复盘输入

### FR-011 当前版本先冻结设计语义

v1.1.8 当前只冻结 schema、文档位置、字段与输出语义，不宣称已实现。

## 7. 建议技术查看文档模板

建议 Markdown 结构至少为：

1. 需求实现概览
2. 涉及服务/模块
3. traceability 元信息
4. 代码改动总览
5. CRUD / 数据库变更
6. API / 任务 / 集成变更
7. 配置 / 环境变量 / Feature Flag
8. 验证结果
9. 已知风险与回滚说明
10. 后续建议

## 8. 验收语义

### Pass
- implement 技术归档的字段、落盘位置、阅读对象、输出语义都明确
- 能覆盖代码/接口/数据库/配置/风险/回滚
- 支持单服务与多服务项目

### Fail
- 仍停留在 execution summary 粒度
- 无法给技术接手人提供真正可消费的归档文档
- 没有数据/API/配置层信息

### Blocked
- 归档 schema 与现有 implement summary / artifact_updates 仍存在关键冲突
