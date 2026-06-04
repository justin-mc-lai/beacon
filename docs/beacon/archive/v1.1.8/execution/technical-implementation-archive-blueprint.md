# 技术实现归档蓝图（v1.1.8 Draft）

> 目的：给技术团队一个可长期查看的实现归档模板。它不是 execution summary 的替代品，而是面向技术接手/复盘/版本归档的扩展文档。

## 推荐文件形态

```text
.beacon/implement/<run_id>/
├── request.json
├── result.json
├── stdout.log
├── stderr.log
└── command.txt

docs/beacon/<version>/execution/
├── implementation-summary-<feature>.md
└── technical-implementation-<feature>.md

docs/beacon/<version>/.machine/execution/
├── implementation-summary-<feature>.json
└── technical-implementation-<feature>.json
```

## 三层归档关系

1. **runtime raw**
   - 保存原始 request/result/stdout/stderr/command
2. **machine archive**
   - 保存结构化技术归档真相
3. **human archive**
   - 保存技术查看文档投影

三层必须可相互追溯。

## 推荐章节

1. 需求实现概览
2. 涉及服务 / 模块
3. 代码改动总览
4. 关键文件改动说明
5. CRUD / 数据库变更
6. API / 队列 / 定时任务 / 外部集成变更
7. 配置 / 环境变量 / Feature Flag
8. 验证结果
9. 已知风险 / 回滚说明
10. 后续建议

## 最小 JSON 字段

- `feature`
- `feature_slug`
- `version`
- `revision_id`
- `run_id`
- `runner`
- `profile_id`
- `git_commit`
- `services[]`
- `changed_files[]`
- `additions[]`
- `modifications[]`
- `deletions[]`
- `refactors[]`
- `data_operations[]`
- `db_changes`
- `api_changes`
- `queue_or_job_changes[]`
- `config_changes[]`
- `env_changes[]`
- `verification[]`
- `known_risks[]`
- `rollback_notes[]`

## 注意

- 没有数据库/API/ENV 变化时，也必须显式写 none/[]
- 多服务项目必须支持按 service 视角归档
- 该文档适合技术查看，不适合替代产品向 execution summary
- 必须能通过 `feature_slug + version + revision_id + run_id` 回溯到 runtime raw 与 machine archive
