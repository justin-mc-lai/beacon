# Test Cases: Beacon implement 技术实现归档与技术架构落盘（v1.1.8）

**Feature**: beacon-implement-technical-architecture-archive  
**Version**: v1.1.8

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已具备当前 implement summary 现状与用户新增目标）
- Gate1 冲突未决判定：Pass（目标聚焦在技术归档，不替代现有 summary）
- Gate2 AC→TC 映射：Pass（覆盖工件、代码、数据库、接口、配置、多服务与可读性）

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | implement 完成后生成技术归档工件 | 存在 `technical-implementation-<feature>.json/.md` |
| TC-002 | contract | implementation summary 与技术归档共存 | 两类工件同时存在，职责不同 |
| TC-003 | contract | 三层归档关系 | runtime raw / machine archive / human archive 可对应追溯 |
| TC-004 | contract | traceability 主键齐全 | 至少包含 feature_slug/version/revision_id/run_id/runner/profile_id/git_commit/services[] |
| TC-005 | contract | 代码改动分类 | 至少区分新增/修改/删除/重构 |
| TC-006 | contract | 数据面归档 | 明确 CRUD / db_changes / migrations / indexes |
| TC-007 | contract | 接口与任务面归档 | 明确 API / queue / cron / external integration changes |
| TC-008 | contract | 配置与环境面归档 | 明确 config/env/feature flag/deployment notes |
| TC-009 | contract | 无相关变化时显式 none | 文档不留隐式空白 |
| TC-010 | integration | 多服务项目归档 | 可按 service 输出改动结构 |
| TC-011 | readability | 技术接手人查看归档 | 能快速理解改动位置、影响面与风险 |
| TC-012 | scope | 当前 v1.1.8 为设计线 | 文档明确 design-only，不误报已实现 |

## 样板场景

### 场景 A：单服务实现
- 只改一个 Python/Ruby/TS 服务
- 预期：文档仍清晰列出模块、CRUD、API、配置与验证

### 场景 B：多服务实现
- 前端 + 后端 + 下游服务同时改
- 预期：归档能按 service 维度拆分展示，不混成一团

### 场景 C：无数据库改动
- 本次实现没有新增表/改表
- 预期：文档显式写 none/[]，避免歧义

### 场景 D：追溯到具体 run/revision
- 技术接手人需要从技术归档一路回溯到 revision、implement run 和原始 request/result
- 预期：通过 traceability 主键可稳定定位 machine archive 与 runtime raw

## 执行语义

- `Pass`：技术归档 schema、阅读面和落盘位置明确
- `Fail`：仍停留在 execution summary 粒度
- `Blocked`：技术归档字段与 implement 现有契约存在关键冲突
