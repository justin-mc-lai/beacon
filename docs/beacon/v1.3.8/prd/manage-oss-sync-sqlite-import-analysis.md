# PRD: manage-oss-sync-sqlite-import-analysis

## 1. Overview

- 目标版本: `v1.3.8`
- 需求描述: 在保持 `/Users/apple/Developer/Personal/oss-sync` 为唯一 canonical 根目录的前提下，增强 `manage-oss-sync`：支持通过 skill 调用下载 GitHub 开源项目到 `oss-sync` 内合适分类；生成和维护索引；使用本地 SQLite 保存开源项目 `upstream`、`owner/repo`、本地目录、分类、`canonical/snapshot`、默认分支、最新默认分支提交、最后同步时间、分析状态；支持在 `manage-oss-sync` 中查询、读取、分析和学习项目，产出基础分析结果与中文学习文档。

## 2. Problem

当前 `manage-oss-sync` 已经具备固定根目录扫描、导入、去重、同步等基础能力，但存在 4 个阻塞问题：

- 机器真相层仅有 `index/repos.json`，缺少稳定可查询的本地数据库。
- 导入流程只负责 `clone + refresh index`，无法跟踪默认分支、最新提交、分析状态。
- 现有索引只描述 Git 元信息，不描述仓库学习价值，例如技术栈、入口文件、README 摘要、分析产物。
- skill 层没有统一的“查询/读取/分析/学习”操作面，难以持续把 `oss-sync` 当成开源知识库使用。

## 3. Goals

- 保持 `oss-sync` 作为唯一 canonical 根目录，不引入“在调用方项目落地副本”的第二套存储模式。
- 让 `manage-oss-sync` 既是镜像管理工具，也是开源仓学习入口。
- 让 SQLite 成为持久化真相层，`repos.json/repos.md` 继续作为兼容和浏览层。
- 让新增仓库从导入开始就具备可查询、可同步、可分析、可学习的闭环。

## 4. Non-Goals

- 不把 `manage-oss-sync` 改造成任意项目根目录下的通用镜像管理器。
- 不支持 GitHub 之外的 forge 首版自动适配，例如 GitLab、Gitee、Bitbucket。
- 不在本期实现复杂全文检索、向量索引、代码 embedding 或 RAG。
- 不自动修改第三方开源仓业务代码，只允许在本地增加学习文档或索引文件。

## 5. Scope

### In Scope

- `manage-oss-sync` skill 文档和脚本增强。
- SQLite 数据库初始化、迁移、回填和日常更新。
- 导入、扫描、同步、查询、分析、学习 6 条主操作链路。
- `repos.json/repos.md`、`dedupe-report.*`、`sync-report.*` 与 SQLite 的一致性约束。
- 中文学习文档和基础分析产物落盘规范。

### Out of Scope

- 跨仓代码 patch 管理。
- 自动生成高保真架构图。
- 自动运行第三方项目测试或安装全部依赖。

## 6. User Outcomes

### Primary User

- 维护 `oss-sync` 的个人开发者/研究者。

### Desired Outcomes

- 给一个 GitHub URL，系统能把仓库放到正确分类并登记到数据库。
- 我能快速知道某个仓库放在哪里、默认分支是什么、最新同步到哪个提交。
- 我能直接查询哪些仓库已经分析过，哪些还没分析。
- 我能为重要仓库沉淀稳定的中文入口文档，而不是每次重新读源码。

## 7. Workflow

### 7.1 Import Workflow

1. 用户提供 GitHub URL，可选提供目标分类、目标目录名、是否允许 snapshot。
2. 系统解析 `owner/repo`，规范化 URL。
3. 系统基于分类规则自动选择 category；若用户显式传入 category，先校验后使用。
4. 系统检查 SQLite 中是否已存在同 upstream 记录。
5. 若不存在，则 clone 到 `oss-sync/<category>/<target-name>`。
6. 系统读取默认分支、当前 HEAD、远程 URL，写入 SQLite。
7. 系统刷新 `repos.json/repos.md`。
8. 系统把该仓库标记为 `analysis_status = pending`。

### 7.2 Scan / Rebuild Workflow

1. 系统递归扫描 `oss-sync/` 下所有 Git 仓库。
2. 系统读取 `remote_fetch`、`branch`、`head_commit`、分类、classification。
3. 系统将扫描结果 upsert 到 SQLite。
4. 系统重新生成 `repos.json/repos.md`。
5. 系统输出回填统计：新增、更新、跳过、异常。

### 7.3 Sync Workflow

1. 系统只对 `canonical` 且工作树干净的仓库执行同步。
2. 系统执行 `git fetch --all --prune`。
3. 系统识别默认分支，优先取 `origin/HEAD` 指向分支；若不可得，回退 `main/master/当前分支`。
4. 系统执行 `git pull --ff-only origin <default-branch>`。
5. 系统更新 SQLite 中的 `latest_default_branch_commit`、`last_synced_at`、`sync_status`。
6. 系统重新生成索引和 sync report。

### 7.4 Analyze Workflow

1. 系统针对目标仓库读取顶层目录、README、常见清单文件。
2. 系统提取技术栈、包管理器、入口文件、主要目录、启动方式、是否带 `skills/`、`docs/`、`examples/`。
3. 系统生成机器可读分析文件和人类可读分析文档。
4. 系统将 SQLite 中的 `analysis_status` 从 `pending` 更新为 `complete` 或 `failed`。

### 7.5 Learn Workflow

1. 系统默认在 `oss-sync/index/learning/` 下写入托管式中文学习文档。
2. 内容至少包含：仓库做什么、怎么启动、关键入口、适合学习什么、与 `oss-sync` 其他仓关系。
3. 只有在用户显式要求时，系统才在镜像仓内写入 `README.zh-CN.md` 或 `docs/usage.zh-CN.md`。
4. 若用户显式要求且原仓 README 可安全补链，则系统可以在本地主 README 增加中文入口说明。
5. 系统更新 SQLite 中的 `learning_doc_path` 和 `learning_status`。

## 8. Command Surface

本期不要求引入新的复杂 CLI 框架，但 `manage-oss-sync` 至少要支持以下稳定操作面：

- `scan`
  - 扫描 `oss-sync`，回填 SQLite，并生成索引。
- `import`
  - 导入一个 GitHub 仓库到指定或自动判定分类。
- `sync`
  - 同步全部或指定仓库的默认分支最新提交。
- `query`
  - 按 `name`、`owner`、`repo`、`category`、`classification`、`analysis_status` 查询。
- `show`
  - 展示单仓库详情，包括本地路径、默认分支、最新提交、分析和学习状态。
- `analyze`
  - 为单仓库或一批仓库生成分析产物。
- `learn`
  - 为单仓库生成中文学习文档。

## 9. SQLite Truth Layer

SQLite 文件路径固定为：

- `oss-sync/index/oss-sync.db`

### Required Tables

#### `repositories`

- `id`
- `name`
- `owner`
- `repo`
- `upstream_url`
- `normalized_upstream_url`
- `local_path`
- `category`
- `classification`
- `default_branch`
- `current_head_commit`
- `latest_default_branch_commit`
- `remote_fetch`
- `remote_push`
- `is_dirty`
- `analysis_status`
- `learning_status`
- `learning_doc_path`
- `last_scanned_at`
- `last_synced_at`
- `created_at`
- `updated_at`

唯一键：

- `local_path`

索引约束：

- `normalized_upstream_url`
  - 非唯一，允许 `canonical` 与 `snapshot` 共存

#### `repository_analysis`

- `id`
- `repository_id`
- `readme_path`
- `readme_title`
- `summary`
- `primary_language`
- `tech_stack_json`
- `package_managers_json`
- `entrypoints_json`
- `top_level_dirs_json`
- `docs_paths_json`
- `examples_paths_json`
- `skills_paths_json`
- `analysis_version`
- `analyzed_at`

#### `sync_history`

- `id`
- `repository_id`
- `branch`
- `before_commit`
- `after_commit`
- `action`
- `reason`
- `created_at`

### Migration Rule

- 首次运行 `scan` 时如果数据库不存在，必须自动初始化。
- 若数据库已存在但缺表或缺列，必须执行前向兼容迁移。
- 不要求首版引入独立 migration framework，但必须有脚本内版本号和幂等迁移逻辑。

## 10. Index Compatibility

SQLite 是机器真相层，但以下文件必须继续保留：

- `index/repos.json`
- `index/repos.md`
- `index/dedupe-report.json`
- `index/dedupe-report.md`
- `index/sync-report.json`
- `index/sync-report.md`

兼容要求：

- `repos.json` 的关键信息必须可从 SQLite 重建。
- SQLite 与 `repos.json` 不一致时，以最新一次成功扫描/同步写入的 SQLite 为准。
- `repos.md` 仍作为人类浏览入口，但允许新增列，如默认分支、分析状态、最后同步时间。

## 11. Analysis Outputs

每个仓库分析后至少生成以下一种产物：

- `index/analysis/<owner-repo>.md`

并可选生成机器文件：

- `index/analysis/<owner-repo>.json`

分析内容至少包含：

- 仓库定位
- upstream 与本地路径
- 默认分支与当前提交
- README 摘要
- 技术栈与关键依赖线索
- 顶层目录结构
- 入口文件和启动路径
- `skills/`、`docs/`、`examples/` 等学习价值目录
- 建议的阅读顺序

## 12. Validation Rules

- 仅接受 GitHub URL。
- 禁止把 repo clone 到 `oss-sync` 根目录之外。
- 若目标目录已存在：
  - 同 upstream 同 commit，拒绝重复导入并返回已存在结果。
  - 同 upstream 不同 commit，可提示转为 `snapshot`。
  - 不同 upstream 同目录名，必须报冲突。
- classification 只能是 `canonical` 或 `snapshot`。
- category 必须属于受支持分类。

## 13. Error Handling

- `git clone` 失败时，不写入半成品 SQLite 记录；若目录已创建需自动清理。
- `git fetch/pull` 失败时，保留仓库现状并写入 `sync_history`。
- README 或分析文件缺失不应使 scan/import 失败，只影响 `analysis_status`。
- SQLite 写入失败时必须终止当前事务并返回明确错误。

## 14. Observability

关键操作需要标准化日志字段：

- `operation`
- `repo`
- `local_path`
- `category`
- `classification`
- `status`
- `reason`
- `duration_ms`

至少在以下步骤打点：

- import start / success / failure
- scan start / finish
- sync repo start / finish / skip
- analyze repo start / finish / failure
- learn doc start / finish / failure

## 15. Security and Boundaries

- 只允许操作 `/Users/apple/Developer/Personal/oss-sync` 及其子目录。
- 禁止自动移动 `products/`、`workspace-ops/`、`cmux/` 等非 `oss-sync` 工作区。
- 不执行来自第三方仓库的未审计脚本，只做静态读取与 Git 操作。
- 不自动推送、提交或修改上游远程。

## 16. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | 用户通过 `manage-oss-sync import <github-url>` 可以把 GitHub 开源仓导入到 `oss-sync` 的正确分类目录，并完成 SQLite 登记与索引刷新。 |
| FR-002 | AC-001 | 用户通过 `manage-oss-sync scan` 可以从现有 `oss-sync` Git 仓库重建 SQLite 记录，并重新生成 `repos.json/repos.md`。 |
| FR-003 | AC-001 | 用户通过 `manage-oss-sync sync` 可以同步全部或指定 canonical 仓库的默认分支，并在 SQLite 中记录最新提交和最后同步时间。 |
| FR-004 | AC-001 | 用户通过 `manage-oss-sync query/show` 可以按名称、上游、分类、状态查询并读取单仓库详情。 |
| FR-005 | AC-001 | 用户通过 `manage-oss-sync analyze` 可以生成仓库分析产物，并更新 `analysis_status` 与 `repository_analysis`。 |
| FR-006 | AC-001 | 用户通过 `manage-oss-sync learn` 可以生成中文学习文档，并把文档路径登记到 SQLite。 |
| FR-007 | AC-002 | 系统必须校验 URL、分类、目录冲突、classification 和根目录边界，并返回可读错误。 |
| FR-008 | AC-003 | Git 和 SQLite 失败路径必须可恢复，且不得留下不一致的半成品记录。 |
| FR-009 | AC-004 | 所有主流程必须输出可追踪日志和结构化结果摘要。 |
| FR-010 | AC-005 | 所有文件写入和 Git 操作必须限定在 `oss-sync` 根目录内。 |

## 17. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | happy-path | 导入、扫描、同步、查询、分析、学习 6 条主链路在固定 `oss-sync` 根目录下可闭环执行，且 SQLite、索引文件、落盘产物彼此一致。 |
| AC-002 | validation | 非 GitHub URL、非法分类、目录冲突、越界路径、重复导入等输入会返回明确错误或建议动作。 |
| AC-003 | error-handling | Git 和 SQLite 异常不会留下不可解释的脏状态；失败可通过重新执行 `scan` 或 `sync` 恢复一致性。 |
| AC-004 | observability | 每次操作都能看到仓库级别的结果、原因、跳过说明和必要日志字段。 |
| AC-005 | security | 所有敏感写操作仅发生在 `oss-sync` 根目录及其子目录，不执行第三方仓库脚本，不改动非目标工作区。 |

## 18. Risks

- 分类规则继续演化，SQLite 若把 category 设计死，会增加后续迁移成本。
- 默认分支不一定叫 `main/master`，需要优先读取远程 HEAD，避免同步错分支。
- 学习文档若直接写进第三方仓目录，后续 pull 可能出现工作树变脏，需要明确接受该副作用或约束写入位置。

## 19. Release Guard

- `qa` 前至少验证一次空数据库初始化流程。
- `qa` 前至少验证一次已有 70+ 仓库的回填扫描流程。
- `qa` 前至少验证一次导入后分析与学习文档产出流程。
- 通过 `qa` 验证 AC 关闭状态后方可进入 release 评审。
