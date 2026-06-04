# Beacon implement writeback flow（v1.1.4 Draft）

## 1. 目标

定义 `implement` 执行结束后，Beacon 如何：

1. 记录 implementation runtime evidence；
2. 写 implementation marker 与 execution summary；
3. 触发 `review spec` / `review quality`；
4. 将实现结果转化为需求物料回填决策。

---

## 2. 总体流程

```text
beacon implement run
  -> resolve runner
  -> write request.json
  -> execute external runner/skill
  -> read result.json
  -> validate result
  -> write implementation marker
  -> write implementation summary
  -> trigger review spec
  -> trigger review quality (optional / post-verify)
  -> expose writeback decisions to docs/beacon/<version>/execution/
```

---

## 3. 分阶段说明

## 3.1 阶段 A：请求生成

Beacon 写：

```text
.beacon/implement/<run_id>/request.json
```

内容至少包括：
- feature/version
- source-of-truth root
- artifact paths
- runner id / skill
- task prompt
- expected result path

### 成功产物
- `request.json`
- `command.txt`

---

## 3.2 阶段 B：外部实现执行

外部 runner 执行：
- command
- skill
- command-skill

输出：
- `stdout.log`
- `stderr.log`
- `result.json`

### 失败语义
- runner 未执行成功：`runner_execution_failed`
- result 未写出：`runner_result_missing`
- result 非法：`runner_result_invalid`

---

## 3.3 阶段 C：Beacon 实现写回

当 result 校验通过后，Beacon 必须自动写：

### runtime
```text
.beacon/state/implementation-<feature>.json
```

### formal docs
```text
docs/beacon/<version>/execution/
├── implementation-summary-<feature>.json
└── implementation-summary-<feature>.md
```

### implementation summary 内容建议
- run_id
- feature
- runner
- skill
- changed_files
- verification summary
- artifact_updates
- next actions

---

## 3.4 阶段 D：spec review 触发

默认建议：

```text
auto_review_spec = true
```

因此，`implement run` 成功后自动调用：

```bash
beacon review spec <feature>
```

### `review spec` 输出职责
- 判断 user-story 是否需要更新
- 判断 prd 是否需要更新
- 判断 test-case 是否需要更新
- 判断 prototype 是否需要更新
- 输出原因与建议

### formal 输出
```text
docs/beacon/<version>/execution/review-spec-<feature>.json
docs/beacon/<version>/execution/review-spec-<feature>.md
```

---

## 3.5 阶段 E：quality review 触发

建议策略：
- `review quality` 默认不在 implement 完成后立刻强制执行；
- 它应更偏向 `verify` 之后触发。

两种模式：

### 模式 1：lazy quality review
```text
implement -> review spec -> verify -> review quality -> gate
```

### 模式 2：eager quality review
```text
implement -> review spec -> review quality(precheck) -> verify -> review quality(final) -> gate
```

MVP 建议使用模式 1。

---

## 4. Artifact Update 语义

Runner result 中建议支持：

```json
{
  "artifact_updates": {
    "user_story": {
      "required": false
    },
    "prd": {
      "required": true,
      "reason": "Implementation contract changed"
    },
    "test_case": {
      "required": true,
      "reason": "Need verification coverage for new runner semantics"
    },
    "prototype": {
      "required": false
    }
  }
}
```

### Beacon 的处理原则

- `required=false`：记录即可
- `required=true`：写入 implementation summary 与 review spec payload
- Beacon 不在 MVP 自动 patch 正文
- Beacon 先做 **writeback decision recording**，再做 **optional apply-writeback**

---

## 5. Writeback Decision Recording

建议在 execution 层统一记录：

```text
docs/beacon/<version>/execution/implementation-summary-<feature>.json
```

其中至少包含：

```json
{
  "artifact_updates": {
    "user_story": {"required": false},
    "prd": {"required": true, "reason": "..."},
    "test_case": {"required": true, "reason": "..."},
    "prototype": {"required": false}
  },
  "recommended_next_actions": [
    "review spec <feature>",
    "update prd/test-case based on runner result",
    "run verify"
  ]
}
```

---

## 6. `--apply-writeback` 的未来扩展

MVP 不建议自动改正文，但后续可以扩展：

```bash
beacon review spec <feature> --apply-writeback
```

### 建议边界
- 只对结构化、低风险更新做自动 patch
- 高风险写回仍输出 suggestion，而不是直接改 PRD
- 所有自动写回都必须生成 execution audit

---

## 7. 与 verify / gate 的连接

实现结束并不代表可放行。

标准链路应为：

```text
implement complete
  -> review spec
  -> update docs if required
  -> verify
  -> review quality
  -> gate
  -> release
```

因此 writeback flow 的职责不是“代替 verify”，而是：
- 在 verify 前让 spec/doc chain 先一致；
- 避免“实现改了但物料还停在旧状态”。

---

## 8. Runtime 与长期事实源分层

## 运行时
```text
.beacon/implement/<run_id>/
```

## 长期事实源
```text
docs/beacon/<version>/execution/
```

### 原则
- request/result/stdout/stderr 属于 raw runtime
- summary/review/writeback decision 属于 formal docs
- 不能把 `.beacon/implement/` 当成正式交付面

---

## 9. 失败路径与 reason codes

建议 writeback flow 相关 reason codes：

- `implement_execution_failed`
- `runner_result_missing`
- `runner_result_invalid`
- `implement_writeback_failed`
- `review_spec_trigger_failed`
- `review_quality_trigger_failed`
- `artifact_writeback_required`
- `artifact_writeback_blocked`

---

## 10. 成功标准

- implementation 完成后有完整 runtime evidence；
- Beacon 自动写 implementation marker 与 execution summary；
- review spec 能输出明确的 artifact update 决策；
- writeback 决策能进入 verify/gate 前的正式链路；
- Beacon 不因 writeback 设计而越界成为自动化修改平台。
