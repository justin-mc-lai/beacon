# PRD: Beacon Memory v1 改造（v1.0.3）

## 1. 背景

Beacon v1.0.2 已具备可用 workflow 与 QA9 主链，但在记忆闭环与状态机健壮性上存在关键断点：

1. 记忆只追加、不可修订
2. 检索仅关键词，缺语义与分层召回
3. feedback 未基于真实失败原因闭环修订
4. lifecycle 失败后难恢复
5. `workflow --auto --skip` 存在假 completed 风险
6. workflow 主状态机缺 gate 阶段
7. `release check` 仍为模拟检查

## 2. 目标

1. 建立 Memory v1：支持 add/update/archive/revision 与哈希去重
2. 建立分层召回：index -> timeline -> detail
3. 建立 reason_code 驱动 feedback 修订闭环
4. 修复 lifecycle：失败可恢复，重试轨迹可审计
5. 修复 workflow completed 语义，纳入 gate 主状态机
6. 将 release check 改为真实工件校验

## 3. 范围

### 3.1 In Scope（v1.0.3）

- `memory-v1.json` 数据结构与迁移
- `workflow-lifecycle` attempt 语义
- remember/recall/feedback/workflow/resume/release 命令契约增强
- `gate --mode dry-run` 非阻断语义统一
- AC→TC 可执行矩阵与回归测试

### 3.2 Out of Scope（v1.0.3）

- 完整向量数据库服务化部署
- 全量多模型语义检索平台化
- 全自动记忆质量评分系统（仅预留字段）

## 4. 用户与场景

- Tech Lead：需要确认 workflow 闭环真实完成
- QA Lead：需要 reason_code -> 修复动作 -> 证据可追溯
- Dev：需要失败可恢复、续跑可控、反馈可修订

## 5. 功能需求

### FR-1 Memory Revision 语义

- 记忆条目新增 `status/superseded_by/revision_of/content_hash/reason_codes`
- `remember add` 支持 upsert/revision
- 禁止相同哈希重复污染

### FR-2 Layered Recall

- `recall memory` 支持 `--layer index|timeline|detail`
- `remember search` 支持 `--mode keyword|semantic|hybrid`
- detail 支持按 ids 批量取回

### FR-3 Feedback 自反馈

- `feedback extract` 从 gate/auto-test/manual 提取候选
- `feedback apply` 执行 add/update/archive
- `feedback sync` 内部转发 extract+apply

### FR-4 Lifecycle 可恢复

- lifecycle 事件支持 `attempt_id/attempt_seq`
- stage 状态按“最新 attempt 终态”判定
- 支持 `failed -> retry -> completed`

### FR-5 Workflow 完整闭环

- `workflow start --auto` 完成前强制 `closure_complete=true`
- `--skip` 仅记 `skipped`，不计 completed
- 主状态机升级为 7 阶段（含 gate）

### FR-6 Resume 推进执行

- `resume <run_id>` 保留只读
- 新增 `resume continue`，按 next_stage 推进

### FR-7 Release 真实工件

`release check` 必须校验：
1. `.beacon/auto-test-status.json`
2. `.beacon/gate-report.json`
3. `.beacon/evidence-manifest.json`
4. 覆盖率工件（pytest-cov / coverage.json）

### FR-8 Gate Dry-Run 非阻断

- `gate --mode dry-run` 输出问题但不阻断
- dry-run 退出码固定 0

## 6. 数据结构需求

### 6.1 Memory v1

- 文件：`.beacon/memory/memory-v1.json`
- 字段：`memory_id/type/status/content/content_hash/source/evidence_ref/reason_codes/confidence/tags/revision_of/superseded_by`

### 6.2 Lifecycle v2

- 文件：`.beacon/memory/workflow-lifecycle.json`
- 字段：`attempt_id/attempt_seq/supersedes_event_id`

### 6.3 Feedback Artifacts

- `.beacon/state/feedback-candidates/<run_id>.json`
- `.beacon/state/feedback-apply-report/<run_id>.json`

### 6.4 Reason Registry

- `.beacon/config/reason-registry.json`
- 统一 gate reason_code 与修复动作映射

## 7. 命令契约（摘要）

- `beacon remember add --upsert --revision-of <id> --reason-code <code>`
- `beacon remember search --mode hybrid --layer index`
- `beacon recall memory --layer timeline --ids id1,id2`
- `beacon feedback extract <rid> --source gate`
- `beacon feedback apply <rid>`
- `beacon workflow start --auto --skip ...`（强制 closure_complete）
- `beacon resume continue <run_id>`（亦支持 `--run-id <run_id>`）
- `beacon release check <version>`（真实工件）

## 8. 非功能需求

1. 向后兼容：旧 remember/recall 参数仍可运行
2. 可观测：新增反馈与生命周期工件可审计
3. 可恢复：失败重试不丢轨迹
4. 一致性：dry-run 语义统一为“可演练不阻断”

## 9. 里程碑

- M1（P0）状态机与 release check 修复
- M2（P1）feedback extract/apply + layered recall
- M3（P2）语义索引与 consolidation（decay/merge/prune）

## 10. 验收标准

- AC 全通过（见 user-story 与 test-case）
- workflow 完成态必须满足 closure_complete 且 gate pass
- release check 无模拟路径
- lifecycle 支持失败恢复与重试覆盖
