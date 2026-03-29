# Beacon v1.1.10 Lifecycle, Memory, And State

## 为什么这一层重要

Beacon 不是一次性文档生成器。

它要支持：

- 多阶段 requirement lifecycle
- 中断后恢复
- QA 会话复用
- 实现归档
- debug feedback 与学习回流

所以状态面是核心架构，不是附属细节。

## 主要状态面

| Surface | Main Files |
| --- | --- |
| Story state | `beacon/utils/story_state.py` |
| Revision state | `beacon/utils/revision_state.py` |
| Workflow memory | `beacon/utils/workflow_memory.py` |
| QA runtime/session | `beacon/utils/qa_runtime.py`, `beacon/commands/qa.py` |
| Control/exhaustion | `beacon/utils/control_plane.py`, `debug` |
| Learning loop | `beacon/utils/learning_loop.py` |

## 三个最重要的状态对象

### 1. Story state

负责：

- 当前 feature 的 requirement item 投影
- AC / task / test item 状态
- revision 绑定

### 2. Revision state

负责：

- 当前版本下某 feature 的 `draft/frozen/...` 文档状态
- baseline hash
- delivery status

### 3. Workflow memory

负责：

- 生命周期推进时的阶段上下文
- 中断恢复与继续执行
- 写回与阶段衔接

## Runtime state 在哪里

`.beacon/` 是运行态真相面，常见目录：

- `.beacon/qa/`
- `.beacon/qa/sessions/`
- `.beacon/implement/<run_id>/`
- `.beacon/state/`
- `.beacon/debug/`

## QA 会话为什么单独存在

浏览器 QA 往往需要：

- 登录
- cookies
- storage state
- runner profile

所以 Beacon 通过 session manifest 保存：

- `origin`
- `runner_type`
- `profile_ref`
- `cookies_ref`
- `storage_state_ref`
- `scopes`
- `expires_at`

这让后续 replay、delta rerun、story-exhaustive QA 可以更稳定。

## 生命周期主链

```text
draft
→ frozen
→ implemented
→ verified
→ accepted / released
```

代码里这个主链不会只落在一个对象里，而是分散在：

- story state
- revision state
- writeback
- gate/release

理解 Beacon，要把它们视为一套协作状态面。
