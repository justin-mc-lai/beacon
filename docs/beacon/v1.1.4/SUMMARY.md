# Beacon v1.1.4 Summary

**主题**: Beacon implement 子命令与自定义实现 Skill 适配  
**状态**: Implemented / Deliverable  
**日期**: 2026-03-20

---

## 本版目标

v1.1.4 的重点不是继续扩模板，而是正式补齐 Beacon 主链里最薄弱的一段：

> **implementation 如何成为一个有契约、有证据、有回填能力的正式动作。**

本版需要回答五个问题：

1. Beacon 是否需要新增顶层 `implement` 子命令；
2. `implement` 与现有 `workflow implementation`、`review spec|quality`、`bridge` 的关系是什么；
3. Beacon 应如何接入用户自定义实现类 AI skill / runner（如 OMX）；
4. Beacon 应如何记录 implementation 的 request/result/evidence，并驱动 review/writeback；
5. Beacon 如何保持“需求交付闭环内核”定位，而不是滑向通用调度器或编码平台。

## 当前结论

- Beacon 已新增顶层：**`implement` 子命令组**；
- Beacon 已新增顶层：**`skill` 子命令组**；
- `implement` 已作为 **implementation stage 的正式适配器动作** 接入 workflow；
- Beacon 没有把 `omx` 写死，而是支持：**runner / skill adapter registry**；
- `docs/beacon/<version>/` 继续是长期事实源；`.beacon/implement/` 只保存运行时 request/result/raw evidence；
- `implement` 完成后可驱动：
  - `review spec`
  - `review quality`
  - execution summary / implementation marker

## 与 OpenSpec 的关系（本版新增）

本版参考 OpenSpec 的不是“照搬 apply 命令”，而是以下产品思路：

1. **显式动作化**：像 `/opsx:apply` 一样，把“实现”做成正式命令，而不是隐藏参数；
2. **配置驱动**：支持 project/global config，不把某个工具写死；
3. **工具适配层**：允许不同 skill / runner 接入，而不是只支持一种 runtime；
4. **物料回路**：实现动作结束后，必须能进入 verify / review / writeback，而不是停在 shell 执行结果。

## 当前阶段记录

- 当前 `v1.1.4` 已完成最小可交付实现；
- 本版实际落地了：
  - `beacon skill detect|list|show|register|prefer|doctor`
  - `beacon implement list-runners|run|status`
  - `workflow implementation` → `implement run` 的正式委托
  - implementation summary / marker / review surfaced recommendations
- 本版仍保守保持：
  - Beacon 不是 scheduler / orchestrator
  - `bridge` 不等于 `implement`
  - gstack 在 MVP 仍以 handoff 适配为主

## 实施阶段（建议顺序）

### 必须先做

1. 新增 `implement run / status / list-runners` 命令面
2. 定义 runner 配置结构（project/global/default）
3. 定义 request/result/runtime evidence schema
4. 打通 implementation marker + execution summary
5. 让 workflow implementation 阶段委托给 `implement run`
6. 让 implement 完成后自动触发 `review spec`
7. 明确 `.beacon/implement/` 与 `docs/beacon/<version>/execution/` 的职责分层

### 其次再做

8. 增加 `review spec --apply-writeback` 能力
9. 增加更多 runner 类型（不仅 OMX）
10. 考虑把 runner registry 与 bridge/runtime 进一步产品化，但不挤入 core narrative

## 设计合理性复审

### 设计上合理的部分
- `implementation` 应该从“command override”升级为正式命令动作；
- `runner` 模型优于“把 omx 写死”；
- request/result 合同化后，Beacon 才能真正消费实现结果；
- `review spec|quality` 作为实现后的回写/验收动作方向正确；
- `implement` 与 `bridge` 分层是必要的。

### 仍需谨慎的部分
1. 不能让 Beacon 变成 scheduler / orchestrator；
2. 不能在 MVP 就自动 patch 全量 PRD/User Story，容易过度写回；
3. 不能把 runner 适配做成无限膨胀的插件市场；
4. 必须保证长期事实源仍是 `docs/beacon/<version>/`；
5. 必须让失败路径具备稳定 reason codes，避免“实现结束了但 Beacon 不知道发生了什么”。

## 本版文档物料

### 主链文档

- `docs/beacon/v1.1.4/user-story/beacon-implement-skill-runner.md`
- `docs/beacon/v1.1.4/prd/beacon-implement-skill-runner.md`
- `docs/beacon/v1.1.4/qa/test-cases/beacon-implement-skill-runner.md`
- `docs/beacon/v1.1.4/qa/test-cases/beacon-implement-skill-runner.ac-test-matrix.json`
- `docs/beacon/v1.1.4/qa/test-cases/beacon-implement-skill-runner.qa9-matrix.json`

### 执行层文档

- `docs/beacon/v1.1.4/execution/boundaries.md`
- `docs/beacon/v1.1.4/execution/latest-feature-usage-guide.md`
- `docs/beacon/v1.1.4/execution/real-project-recipes.md`
- `docs/beacon/v1.1.4/execution/faq-and-troubleshooting.md`
- `docs/beacon/v1.1.4/execution/beacon-vs-openspec-gsd-comparison.md`
- `docs/beacon/v1.1.4/execution/skill-standard-alignment.md`

### 发布/演进文档

- `docs/beacon/v1.1.4/release/v1.1.4.md`
- `docs/beacon/v1.1.4/release/version-evolution-changelog.md`

## 版本说明

- 本稿同时记录 `v1.1.4` 的产品方向与已交付实现；
- 当前 Beacon 运行时已包含 `skill` / `implement` 子命令；
- 当前版本的正式交付仍以 `docs/beacon/v1.1.4/` 为准。
