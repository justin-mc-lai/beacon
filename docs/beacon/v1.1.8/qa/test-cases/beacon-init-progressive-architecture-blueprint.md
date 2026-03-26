# Test Cases: Beacon init 渐进式披露、技术架构主文档与版本演进蓝图（v1.1.8）

**Feature**: beacon-init-progressive-architecture-blueprint  
**Version**: v1.1.8

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已具备当前 init/context 现状与新增目标）
- Gate1 冲突未决判定：Pass（目标聚焦在主入口、架构蓝图、演进蓝图与模式语义）
- Gate2 AC→TC 映射：Pass（覆盖模式、主入口、蓝图文档、索引与兼容性）

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | init 定义 greenfield / takeover 模式 | 两类模式语义清晰 |
| TC-002 | contract | AGENTS 主入口支持渐进式披露 | 明确主入口阅读顺序 |
| TC-003 | contract | AGENTS 区分 greenfield / takeover | 两类项目有不同进入建议 |
| TC-004 | contract | init 生成 `architecture-blueprint.md` | 技术架构主文档存在 |
| TC-005 | contract | init 生成 `version-evolution-blueprint.md` | 版本演进蓝图存在 |
| TC-006 | contract | init 生成 `project-lifecycle-onboarding.md` | 生命周期接管入口文档存在 |
| TC-007 | contract | init 生成 `implementation-archive-index.md` | implement 技术归档索引存在 |
| TC-008 | contract | docs version / runtime version 分离 | `--version auto --runtime-version v1.1.8` 时，docs 落项目自身版本线，context 落 v1.1.8 |
| TC-009 | contract | init 设计支持 `.beacon/state/project-onboarding.json` | onboarding state 与 adoption level 语义明确 |
| TC-010 | readability | 技术接手场景查看 architecture blueprint | 能快速理解系统结构与边界 |
| TC-011 | readability | 技术查看 version blueprint | 能理解当前版与前后版本关系 |
| TC-012 | lifecycle | 项目接管级别可表达 | 可区分 context_only/docs_managed/.../full_lifecycle_managed |
| TC-013 | compatibility | 不破坏现有 managed context / doctor 机制 | 兼容现有 context block 体系 |
| TC-014 | contract | `resolve_target_version(auto)` 优先吃 onboarding docs_version | stray runtime 同名目录不会再抢占 docs line |
| TC-015 | contract | status/help/doctor 输出双版本 | 明确输出 `docs_version` / `runtime_version` / `context_managed_version` |
| TC-016 | diagnostics | doctor 检测 docs/runtime 分离漂移 | 能发现 runtime 同名 docs root 或分离语义异常 |
| TC-017 | scope | 当前 v1.1.8 为设计线 | 文档明确 design-only，不误报已实现 |

## 样板场景

### 场景 A：greenfield 初始化
- 新项目首次引入 Beacon
- 预期：生成主入口与蓝图 skeleton，帮助团队建立统一阅读入口

### 场景 B：takeover 初始化
- 老项目接手后引入 Beacon
- 预期：更强调 current-state architecture / constraints / debt / evolution timeline

### 场景 C：技术接手查看
- 新接手同学先看 AGENTS 主入口
- 预期：能按渐进式顺序快速找到 SUMMARY、execution、architecture、需求与 machine 面

### 场景 D：生命周期接管判断
- 项目已经 init 过，但还没启用 implement/qa/gate 全链
- 预期：通过 onboarding state 能看出当前 adoption level 与下一步建议

### 场景 E：老项目接入新 Beacon
- 项目自身当前文档线是 `v0.1.0` 或 `v1.3.2`
- 运行 Beacon runtime 是 `v1.1.8`
- 预期：不会错误创建 `docs/beacon/v1.1.8/` 空版本线

### 场景 F：项目里误出现 runtime 同名 docs root
- onboarding docs line 是 `v0.1.0`
- runtime line 是 `v1.1.8`
- 目录里却出现 `docs/beacon/v1.1.8/`
- 预期：doctor 给出可疑漂移告警，status/help 仍坚持使用 `v0.1.0`

## 执行语义

- `Pass`：init 增强后的主入口、蓝图和索引设计完整
- `Fail`：仍停留在建目录/写 managed block 粒度
- `Blocked`：init 模式或蓝图结构语义仍有关键冲突
