# Release Checklist: debug-feedback-loop（v1.1.0）

## 0. 发布目标

确保 Debug Feedback Loop 在业务环境可用，并满足：

- 反馈可采集、可归因、可入库、可复盘；
- OMC/OMX/team 可形成可控桥接闭环；
- 文档与实现在持续变更下保持强一致。

## 1. Pre-Release（发布前）

### 1.1 需求链更新（滚动基线）

- [ ] `think` 已更新（开放问题与边界清晰）
- [ ] `user-story` 已更新（AC 与优先级明确）
- [ ] `prd` 已更新（FR/NFR 与数据模型明确）
- [ ] `test-case` 已更新（AC->TC 全覆盖）

### 1.2 Spec Fingerprint

- [ ] 已生成 user-story/prd/test-case fingerprint
- [ ] fingerprint 文件已纳入 evidence manifest
- [ ] gate strict 可读取并校验 fingerprint

### 1.3 Debug Feedback Pipeline

- [ ] `.beacon/state/debug-feedback/<run_id>.jsonl` 可写入
- [ ] `.beacon/state/feedback-candidates/<run_id>.json` 可生成
- [ ] `beacon feedback sync latest --project-root <root>` 可写入 memory-v1
- [ ] `recall memory` 可检索新增反馈项

### 1.4 Bridge Strategy

- [ ] 默认 bridge 策略为 hint-only（不执行）
- [ ] 显式桥接开关在测试环境验证通过
- [ ] bridge 执行结果已写入 lifecycle + memory

## 2. 执行步骤（建议顺序）

```bash
# 1) 安全规划
beacon ask "继续上次workflow并评估阻塞项" --plan-only --json

# 2) 主链推进
beacon workflow continue --project "<root>" --version "v1.1.0" --run-id "<run-id>" --auto --interactive --hud

# 3) （可选）OMC/OMX 协同
omc run --project-root "<root>" --task "继续推进 debug-feedback-loop（version=v1.1.0, run_id=<run-id>）"
omx run --project-root "<root>" --task "执行 debug-feedback-loop 下一轮迭代（version=v1.1.0, run_id=<run-id>）"

# 4) team 治理闭环
beacon team start "debug-feedback-loop 交付协作" --runtime tmux --project "<root>"
beacon team review spec pass --reviewer pm --project "<root>"
beacon team review quality pass --reviewer qa --project "<root>"
beacon team evaluate 0 0 --project "<root>"

# 5) 反馈回灌与放行
beacon feedback sync latest --project-root "<root>"
beacon gate check release --mode strict --project-root "<root>"

# 6) 审计报告
beacon report generate latest --machine --project-root "<root>" --version v1.1.0 --write-summary
```

## 3. Go / No-Go 判定

### Go 条件

- [ ] Gate Release = Pass（strict）
- [ ] AC Must 全通过（见 AC->TC 矩阵）
- [ ] Memory 回灌完成且可检索
- [ ] Fingerprint 一致性校验通过
- [ ] docs-example CI 通过

### No-Go 条件

- [ ] 出现 `coverage_incomplete` / `ac_tc_evidence_chain_broken`
- [ ] 出现 `memory_lifecycle_missing` / `memory_feedback_unsynced`
- [ ] 出现 fingerprint mismatch 或 bridge 结果未审计

## 4. 回滚策略

- [ ] 关闭 bridge 执行开关，退回 hint-only；
- [ ] 停用 debug 归因自动写入，仅保留 raw 采集；
- [ ] 回滚至上一稳定版本 spec fingerprint；
- [ ] 保留 `.beacon/state/debug-feedback/*.jsonl` 作为故障复盘证据。

## 5. 发布后观察（24h / 72h）

- [ ] reason_code Top N 分布是否稳定
- [ ] router_false_positive 比例是否下降
- [ ] missing_intent_mapping 是否显著下降
- [ ] bridge 执行失败率是否在可接受阈值内
- [ ] memory-v1 增量是否存在异常重复（upsert 失效）
