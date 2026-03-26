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
- `docs_version`
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

## docs version / runtime version 分离规则

这是 init 的关键规则：

- `docs_version`
  - 决定文档写到哪个 `docs/beacon/<version>/`
  - 应跟随项目自身版本线

- `runtime_version`
  - 决定 `AGENTS.md / CLAUDE.md` 的 Beacon managed version marker
  - 应跟随当前 Beacon 工具版本

推荐使用：

```bash
python3 -m beacon.main init \
  --project <project_root> \
  --version auto \
  --runtime-version v1.1.8 \
  --project-mode takeover \
  --apply
```

这意味着：
- 项目 docs 不会被误写成 Beacon 自己的版本号
- context guidance 仍然可以指向最新 Beacon runtime

## 运行期闭环要求

分离规则不能只停留在 `init` 参数层，还必须进入运行期：

- `resolve_docs_version()`
  - 解析项目 docs line
  - `auto` 优先读取 onboarding state 的 `docs_version`

- `resolve_runtime_version()`
  - 解析 Beacon runtime line
  - 默认跟随当前 Beacon toolkit version

- `resolve_target_version()`
  - 作为兼容入口继续存在
  - 但内部必须等价于 `resolve_docs_version()`

## status / help / doctor 的双版本输出

这三个入口必须显式展示：

- `docs_version`
- `runtime_version`
- `context_managed_version`

否则即使 init 已修正，人在使用阶段仍会再次把两条版本线混淆。

## doctor 需要新增的漂移诊断

doctor 至少需要新增：

- `docs_runtime_separation_integrity`
- runtime 同名 docs root 的可疑误建检测

典型问题：

- onboarding 记录的是 `v0.1.0`
- Beacon runtime 是 `v1.1.8`
- 项目却误出现 `docs/beacon/v1.1.8/`

此时：

- `status/help` 应继续使用 onboarding 的 `docs_version`
- `doctor` 应明确提示这是可疑漂移

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
- `docs_version`
- `runtime_version`
- 当前项目模式（greenfield / takeover）
- 当前接管级别
- 已启用的 Beacon stage
- 推荐阅读顺序
- 推荐下一步
