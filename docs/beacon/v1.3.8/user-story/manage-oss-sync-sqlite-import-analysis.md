# User Story: manage-oss-sync-sqlite-import-analysis

## Story

作为维护 `oss-sync` 的开发者，我希望 `manage-oss-sync` 能把 GitHub 开源仓统一下载到固定 `oss-sync` 根目录，并把仓库元数据、同步状态、分析结果存到本地 SQLite，这样我既能持续管理镜像，也能把这些仓库当作可查询、可学习的开源知识库来使用。

## Context

- `oss-sync` 是唯一 canonical 根目录，不允许把镜像落到调用方项目。
- 现有 JSON/Markdown 索引要继续保留，但不能再作为唯一机器真相层。
- `manage-oss-sync` 需要从“镜像操作脚本”升级为“镜像管理 + 学习入口”。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | happy-path | 用户执行导入、扫描、同步、查询、分析、学习任一主流程后，仓库文件、SQLite、`repos.json/repos.md`、分析文档之间保持一致，且所有文件都落在 `oss-sync` 根目录内。 |
| AC-002 | validation | 用户输入非 GitHub URL、非法分类、重复目录名、越界路径、非法 classification 或已存在同 upstream 导入时，系统返回明确错误或建议动作。 |
| AC-003 | error-handling | `git clone`、`git fetch/pull`、SQLite 写入、分析文档生成任一环节失败时，系统不会留下无法恢复的半成品状态，并给出恢复方式。 |
| AC-004 | observability | 用户能看到每次操作的仓库级别日志、结果摘要、跳过原因、最后同步时间、分析状态和学习文档路径。 |
| AC-005 | security | 所有敏感操作都被限制在 `/Users/apple/Developer/Personal/oss-sync` 内，不执行第三方仓库脚本，不改动非 `oss-sync` 工作区。 |

## Scenario Breakdown

### Scenario 1: 导入新仓库

- 给一个 GitHub URL。
- 系统自动或按指定 category clone 到 `oss-sync`。
- 系统写入 SQLite `repositories`。
- 系统刷新索引，并把该仓库标记为待分析。

### Scenario 2: 回填已有仓库

- 对当前 `oss-sync` 全量扫描。
- 系统把历史 Git 仓补录到 SQLite。
- 系统重新生成兼容索引文件。

### Scenario 3: 同步默认分支

- 用户同步一个或多个 canonical 仓。
- 系统更新默认分支最新提交与最后同步时间。
- 系统记录仓库级别的同步历史。

### Scenario 4: 分析和学习

- 用户对指定仓库执行 `analyze`。
- 系统生成分析摘要和机器元数据。
- 用户执行 `learn` 后默认得到 `index/learning/` 下的中文学习文档入口。

## Done Definition

- SQLite 数据库存在且可从空初始化。
- 至少 1 个新导入仓库完成从 import 到 learn 的闭环。
- 至少 1 次全量 scan 可以稳定回填当前 `oss-sync`。
- 索引文件与 SQLite 结果一致。

## Metadata

- version: `v1.3.8`
- feature: `manage-oss-sync-sqlite-import-analysis`
- status: `draft`
- generated_at: `2026-04-28T03:05:23.308593+00:00`
