# Beacon v1.0.0 文档补充说明（对齐 v1.0.1 MVS 方案）

## 目的

将 v1.0.0 核心文档补充对齐到  
`docs/beacon/v1.0.1/research/beacon-fidelity-mvp-solution.md` 的 MVS 设计理念，确保：

1. 业务不失真
2. 测试用例全面
3. 自动化测试不假通过
4. 按用户故事最小 MVP 小粒度实现

## 本次补充范围

- `prd/beacon-core.md`
  - 新增 v1.0.1 MVS 补充章节
  - 扩展 Blocked 条件（traceability / evidence / heuristic / mvp_scope_drift）
- `user-story/beacon-core.md`
  - 新增 US-008（不失真与最小切片交付）
  - 增加 6 条 AC
- `qa/test-cases/beacon-core.md`
  - 新增 TC-008（8 条验证用例）
  - 更新执行摘要与覆盖矩阵统计

## 说明

本文件仅作为 v1.0.0 文档层补充说明，不代表实现代码已全部完成。  
后续代码落地建议直接按 v1.0.1 research 方案推进 gate 与 auto-test 规则。

