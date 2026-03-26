# Beacon v1.1.6 原生 implement + 生命周期闭环蓝图

## 1. 问题陈述

当前 Beacon 的 implementation 阶段具备“发单能力”，但还没有“执行内核”。

具体表现为：
- `implement.py` 主要负责 adapter orchestration
- `user_story.py` 还不是 machine-backed object
- `workflow.py` 有 stage 事件，但缺少正式业务状态机
- `review.py` 产出报告但不会驱动 item 状态变化

因此 v1.1.6 的目标不是补命令，而是补内核。

## 2. 双层状态机

### 2.1 文档/需求生命周期

```text
Draft → Refined → Frozen → Superseded → Archived
```

### 2.2 实现/交付生命周期

```text
Idle → Implementing → Implemented → Verifying → Accepted → Released
```

### 2.3 异常与重入

```text
Blocked / Failed / Reopened
```

## 3. 核心对象

### Feature
- feature_slug
- version
- title
- current_revision_id
- lifecycle_status

### Revision
- revision_id
- feature_slug
- source_revision_id
- reason
- doc_status
- delivery_status
- baseline_hash
- superseded_by

### Story
- story_id
- revision_id
- title
- priority
- status
- items[]

### StoryItem
- id
- kind (`ac` / `task` / `test`)
- text
- required
- status
- implemented_by_run_id
- verified_by_run_id
- accepted_at
- changed_in_revision

### ImplementationRun
- run_id
- revision_id
- target_story_ids
- target_item_ids
- runner
- status
- changed_files
- verification
- summary

## 4. 原生执行模型

### `native-single`
适合：
- 单 story
- 小范围修改
- 低 blast radius

执行原则：
1. 读取 frozen revision
2. 找出未完成 items
3. 生成 implementation work package
4. 单 agent 实现
5. 产出 run summary
6. 自动 writeback
7. 进入 verify

### `native-team`
适合：
- 多 story
- 中高复杂度
- 需要 review + test 并行

最小角色集：
- Planner / Orchestrator
- Implementer
- Reviewer
- Tester

## 5. 闭环条件

一个 revision 只有在以下条件同时满足时，才能视为 accepted：

1. required AC 均已 verified
2. required TEST 均已 passed
3. spec review 不为 fail
4. quality review 不为 fail
5. gate 检查通过

## 6. 关键设计原则

- 没有 frozen，不允许 implement
- 没有 item id，不允许 writeback
- 没有 run 绑定 revision，不允许 accept
- reopen 必须新建 revision，不允许直接污染旧 revision

## 7. 结果目标

v1.1.6 完成后，Beacon 应从：

> 有 workflow stage 的需求 kernel

升级为：

> 具备 native implement、revision 生命周期、item 级 writeback 与任意阶段可重入闭环能力的交付内核

