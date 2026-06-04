# Test Cases: manage-oss-sync-sqlite-import-analysis

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | import 新 GitHub 仓库到自动分类目录 | integration | 仓库被 clone 到 `oss-sync/<category>/<name>`；SQLite `repositories` 新增记录；`repos.json/repos.md` 刷新；`analysis_status = pending`。 |
| TC-002 | AC-001 | 对现有 `oss-sync` 执行全量 scan 回填数据库 | integration | 现有 Git 仓被 upsert 到 SQLite；无数据库时自动建库；索引文件可重建。 |
| TC-003 | AC-001 | sync 一个干净 canonical 仓库 | integration | 系统 fetch/pull 默认分支；更新 `latest_default_branch_commit`、`last_synced_at`；写入 `sync_history`。 |
| TC-004 | AC-001 | query/show 一个已登记仓库 | integration | 可按名称或 upstream 查询；详情包含本地路径、分类、classification、默认分支、最新提交、分析状态。 |
| TC-005 | AC-001 | analyze 指定仓库 | integration | 生成 `oss-sync-analysis.md` 或等效分析文档；`repository_analysis` 写入摘要、技术栈、入口文件等字段；`analysis_status = complete`。 |
| TC-006 | AC-001 | learn 指定仓库 | integration | 默认生成 `index/learning/<owner-repo>.zh-CN.md`；若显式启用 in-repo 模式才写入镜像仓；SQLite 更新 `learning_status` 和 `learning_doc_path`。 |
| TC-007 | AC-002 | 导入非 GitHub URL | unit | 请求被拒绝；返回“仅支持 GitHub URL”类可读错误；不创建目录，不写 SQLite。 |
| TC-008 | AC-002 | 导入到非法 category | unit | 请求被拒绝；返回受支持分类说明；不 clone。 |
| TC-009 | AC-002 | 目标目录已存在且 upstream 不同 | integration | 返回目录冲突；不覆盖现有目录；不写半成品记录。 |
| TC-010 | AC-002 | 同 upstream 同 commit 重复导入 | integration | 返回已存在结果；不重复 clone；可返回已登记仓路径。 |
| TC-011 | AC-002 | 同 upstream 不同 commit 导入 | integration | 系统提示或支持转为 `snapshot`；不会静默覆盖 canonical 仓。 |
| TC-012 | AC-003 | `git clone` 失败 | integration | 导入失败；如已创建目标目录则清理；SQLite 不写脏记录；日志包含失败原因。 |
| TC-013 | AC-003 | `git fetch/pull` 失败 | integration | 原仓保留不变；`sync_history` 记录失败；sync report 显示原因。 |
| TC-014 | AC-003 | SQLite 写入失败 | unit | 当前事务回滚；索引不更新为成功态；错误对用户可读。 |
| TC-015 | AC-003 | analyze 阶段缺少 README | integration | analyze 可降级完成或标记 failed；scan/import 不受阻。 |
| TC-016 | AC-004 | import/sync/analyze 输出日志字段 | integration | 日志至少包含 `operation`、`repo`、`local_path`、`status`、`reason`、`duration_ms`。 |
| TC-017 | AC-004 | show 展示最后同步与学习状态 | integration | 用户可见 `last_synced_at`、`analysis_status`、`learning_status`、`learning_doc_path`。 |
| TC-018 | AC-005 | 操作尝试写出 `oss-sync` 根目录 | unit | 系统拒绝越界路径；不执行任何写操作。 |
| TC-019 | AC-005 | analyze/learn 尝试执行第三方脚本 | unit | 系统不运行仓库内脚本，仅允许静态读取和文档写入。 |
| TC-020 | AC-005 | sync 非 `oss-sync` 工作区 | unit | 系统拒绝非目标根目录仓库，不操作 `products/`、`workspace-ops/`、`cmux/`。 |

## Test Data Notes

- 至少准备 1 个全新 GitHub 仓库 URL。
- 至少准备 1 个已存在于 `oss-sync` 的 canonical 仓库。
- 至少准备 1 个 snapshot 场景或同 upstream 不同 commit 场景。
- 至少准备 1 个没有 `README.md` 的轻量测试仓库或模拟目录。

## Execution Notes

- version: `v1.3.8`
- 每个 AC 至少对应一个可执行 TC。
- `scan`、`sync`、`analyze` 需要优先在测试副本或受控仓库上验证，再跑全量仓库。
