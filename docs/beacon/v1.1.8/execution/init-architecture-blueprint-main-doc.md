# init 技术架构主文档蓝图（v1.1.8 Draft）

> 目的：让 `beacon init` 不只是建目录，而是为技术和 agent 建立项目级主入口与阅读顺序。

## init 后建议存在的主文档

```text
docs/beacon/<version>/execution/
├── architecture-blueprint.md
├── version-evolution-blueprint.md
├── project-lifecycle-onboarding.md
├── implementation-archive-index.md
└── boundaries.md
```

## AGENTS 主入口建议的渐进式披露顺序

1. `SUMMARY.md`
2. `execution/index.md`
3. `execution/architecture-blueprint.md`
4. `prd/` / `user-story/` / `qa/test-cases/`
5. `.machine/`

## 生命周期接管状态

建议同时落盘：

```text
.beacon/state/project-onboarding.json
```

最小字段：

- `project_mode`
- `lifecycle_adoption_level`
- `runtime_version`
- `architecture_blueprint_ready`
- `version_blueprint_ready`
- `implementation_archive_enabled`
- `qa_managed`
- `gate_managed`
- `next_recommended_stage`

## 建议的接管级别

- `0 = context_only`
- `1 = docs_managed`
- `2 = architecture_managed`
- `3 = implementation_managed`
- `4 = qa_gate_managed`
- `5 = full_lifecycle_managed`

## Greenfield 模式建议强调

- 系统目标
- 初始模块划分
- 关键边界
- 未来演进蓝图 skeleton

## Takeover 模式建议强调

- current-state architecture
- bounded contexts / service map
- known debt / constraints
- 版本演进时间线

## 主文档最低内容要求

### architecture-blueprint.md
- 系统定位
- 分层结构
- 模块/服务图
- 数据流/调用链
- 外部依赖
- 数据库/缓存/队列
- 部署环境
- 边界与约束

### version-evolution-blueprint.md
- 当前版本定位
- 相对上一版 delta
- planned / implemented / deprecated capability map
- 未来版本递进方向

### implementation-archive-index.md
- 当前版本技术实现归档入口
- 按 feature 列出 technical-implementation 文档

### project-lifecycle-onboarding.md
- 当前项目模式（greenfield / takeover）
- 当前接管级别
- 已启用的 Beacon stage
- 推荐阅读顺序
- 推荐下一步
