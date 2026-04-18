# 执行索引（v1.3.4）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `../../global-boundaries.md`
4. `../prd/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
5. `../user-story/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
6. `../qa/test-cases/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
7. `../prd/beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing.md`
8. `../prd/beacon-v1.3.4-runtime-evidence-layering-and-noise-governance.md`
9. `../research/beacon-v1.3.4-management-board-lifecycle-brainstorm.md`
10. `../research/beacon-v1.3.4-one-person-company-ops-board-model.md`
11. `../research/beacon-v1.3.4-real-project-board-acceptance-brainstorm.md`
12. `./beacon-toolkit-lighthouse-real-env-debug-friction-and-deterministic-projection.md`
13. `./real-project-validation-checklist-beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
14. `./doctor-orchestration-blueprint.md`
15. `../prototype/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane/index.html`

## 说明

- `v1.3.4` 的主题不是扩张 Beacon 的人类工作流，而是补齐机器内部跨项目运行态管理层。
- 这条线只回答一个核心问题：
  - Beacon 如何拥有全局项目态、run 态与异常观测能力，同时不破坏本地 truth plane。
- 这条线的正式命名应收口为：
  - `Beacon Runtime Ledger`：机器内部 SQLite 投影账本
  - `Beacon 管理看板`：PocketBase 承载的人类可视化层
- 人类主流程仍固定为：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

- PocketBase 只作为可视化与控制面，不进入正式交付真相叙事。
- `omc`、`omx` 与其他 Beacon 外运行时不进入本版本展示或投影边界。
- `../../global-boundaries.md` 仍是高于所有版本线的唯一全局约束源。

## 这条线的输出目标

1. 讲清 project truth / global projection / visual control plane 的三层边界。
2. 给 `single_repo` 与 `multi_repo_workspace` 两种项目态建立正式建模口径。
3. 约束 SQLite / PocketBase 只能持有投影、索引、观察和运维状态。
4. 定义断库、断 PocketBase、断同步时的降级与重建路径。
5. 为后续 `status` / `doctor` / internal sync 演进提供不扩张命令面的蓝图。
6. 修复 requirement 生成与 analysis toolkit 暴露之间的产品断层，避免版本包文档承诺与 skill surface 脱节。
7. 明确 `Beacon 管理看板` 的生命周期展示模型，以及 CEO / 项目负责人双层视图。
8. 为主 PRD 生成可冻结的看板 prototype 参考包，服务后续实现与 QA。
9. 将主 feature 补成正式 `user-story + test-case`，避免只停留在 PRD 与 prototype。
10. 冻结 Beacon 自身的 machine evidence / runtime cache 分层，并为 `status / qa / release` 定义正式噪音治理规则。
11. 冻结 `beacon doctor` 的职责分层与编排蓝图，避免后续新增职责继续平铺进 `doctor.py`。
12. 把真实环境 debug friction 与 projection 写链风险前置进主 PRD，而不是等实现时再被动修补。
13. 把四个真实项目并板与 Beacon 自并板写成正式验收场景，避免验收只靠 synthetic fixture。
14. 把真实项目并板验收冻结成可执行 checklist，避免后续只验证字段存在、不验证看板语义。
- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`
