# Beacon v1.3.4 总览

**主题**：Beacon Runtime Ledger 与 Beacon 管理看板  
**状态**：规划线  
**日期**：2026-04-18

---

## 一句话总结

`v1.3.4` 的目标不是把 Beacon 的正式交付真相搬进数据库，而是在不破坏 `6+3` 人类主面的前提下，为 Beacon 增加一个机器内部全局运行态投影层，并把人类可见面收口成 `Beacon 管理看板`：

```text
project truth
  = docs/beacon + .beacon
machine projection
  = Beacon Runtime Ledger
visual plane
  = Beacon 管理看板 (PocketBase)
```

其中：

- `docs/beacon/<version>/` 继续是正式 requirement / delivery tree
- `.beacon/` 继续是项目本地运行态与证据面
- `Beacon Runtime Ledger` 是机器内部 SQLite 投影账本，只负责跨项目注册、run 追踪、进度聚合、异常观测
- `Beacon 管理看板` 是 PocketBase 承载的人类可视化层，只负责可视化、管理、备份，不持有正式发布真相
- `omc`、`omx` 与其他 Beacon 外运行时不进入本版本的正式投影或展示范围

## 为什么要做这条线

当前 Beacon 在单项目内已经有足够强的本地运行态与证据能力，但跨项目、跨仓、跨 workspace 仍缺少统一可观测面：

1. `slow_uni_bmtop` 这类单仓项目，本地 `.beacon/` 已足够丰富，但缺少跨项目对比、异常总览与 run 聚合。
2. `rolo` 这类多服务 workspace，根目录不是单一 git repo，运行态既有 root 级 `.beacon/`，又有多个 child repo，需要更强的项目/仓边界建模。
3. 现有状态主要落在本地 markdown / json / runtime 文件中，适合项目内闭环，但不利于机器级全局索引、检索、视图和备份。
4. 用户要求即使全局状态层缺失，也必须允许项目从 Beacon requirement materials 继续推进，因此新层只能是 projection / control plane，不能变成新的 truth owner。

## 当前版本目标

1. 定义 Beacon 全局运行态投影层的分层边界。
2. 建立跨项目 project registry、git scope registry、feature package registry、run tracking、health snapshot 的统一模型。
3. 明确 `single_repo` 与 `multi_repo_workspace` 两种项目类型。
4. 定义 `Beacon 管理看板` 在 Beacon 中的正确定位：
   - CEO 多项目总览
   - 项目负责人详情下钻
   - 生命周期主轴展示
   - PocketBase 承载的管理、REST / realtime、备份能力
5. 建立“丢失 SQLite / PocketBase 后可从本地 truth 重建”的恢复合同。

## 范围

### In scope

- 机器内部全局 SQLite 运行态数据库（`Beacon Runtime Ledger`）
- 基于 PocketBase 的控制面与管理界面（`Beacon 管理看板`）
- project / git scope / run / event / artifact / health 的建模
- 单仓项目与多仓 workspace 的统一抽象
- 从 `docs/beacon` 与 `.beacon` 重建全局状态的恢复路径
- 一人公司场景下 CEO / 项目负责人双层视图

### Out of scope

- 把正式 requirement / release 真相迁移进 SQLite
- 让 PocketBase 成为新的主流程入口
- 新增新的公开一级主命令
- 让 Beacon 跨宿主桥接多套外部运行时
- 让 DB 状态覆盖本地项目证据
- 把 `omc` / `omx` / 其他 Beacon 外运行时纳入正式投影

## 推荐阅读顺序

1. `./execution/index.md`
2. `./execution/architecture-blueprint.md`
3. `./execution/boundaries.md`
4. `./execution/project-skill-qa-evolution-blueprint.md`
5. `./source-architecture/index.md`
6. `../global-boundaries.md`
7. `./prd/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
8. `./user-story/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
9. `./qa/test-cases/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
10. `./prd/beacon-v1.3.4-runtime-evidence-layering-and-noise-governance.md`
11. `./user-story/beacon-v1.3.4-runtime-evidence-layering-and-noise-governance.md`
12. `./qa/test-cases/beacon-v1.3.4-runtime-evidence-layering-and-noise-governance.md`
13. `./prd/beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing.md`
14. `./user-story/beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing.md`
15. `./qa/test-cases/beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing.md`
16. `./research/beacon-v1.3.4-management-board-lifecycle-brainstorm.md`
17. `./research/beacon-v1.3.4-one-person-company-ops-board-model.md`
18. `./research/beacon-v1.3.4-real-project-board-acceptance-brainstorm.md`
19. `./execution/real-project-validation-checklist-beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
20. `./prototype/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane/index.html`

## 当前版本包起点

`v1.3.4` 当前采用“主 PRD + 并行 PRD”起步：

- `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`
- `beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing`
- `beacon-v1.3.4-runtime-evidence-layering-and-noise-governance`

其中：

- 主 PRD 负责 `Beacon Runtime Ledger`、`Beacon 管理看板`、multi-project 建模与恢复合同
- 并行 PRD 负责修正 `v1.3.3` 暴露出的 product friction：
  - `prd create` 仍是通用模板生成器
  - memory/friction toolkit 存在 hidden command，但缺少 host-visible subskill
- 并行 PRD 负责冻结 Beacon 自身的机器证据分层与噪音治理规则：
  - 哪些 machine evidence 应进入 git 并参与 gate
  - 哪些 `.beacon` runtime/cache/debug 状态必须保持本地
  - `status / qa / release` 如何在“有 runtime 用 runtime，无 runtime 重验”前提下降噪

如果后续需要继续展开实现切片，建议按以下方向补并行 PRD：

- workspace / multi-repo 建模与恢复合同
- requirement bootstrap / skill routing / optional toolkit host surface
- runtime evidence layering / status-release noise governance

当前已补充两份调研 Brainstorm：

- `research/beacon-v1.3.4-management-board-lifecycle-brainstorm.md`
  - 收口 CEO 总览视角
  - 收口项目负责人详情视角
  - 明确生命周期主轴与 runtime 下钻关系
  - 明确 Beacon 子 skill 生命周期映射展示
- `research/beacon-v1.3.4-one-person-company-ops-board-model.md`
  - 收口一人公司 CEO / 项目负责人双角色模型
  - 细化首页、项目详情、运行态中心三层页面
  - 约束 host session、git/worktree、runtime 细节的展示边界
  - 明确 `omc` / `omx` 不属于 Beacon 管理看板范围
- `research/beacon-v1.3.4-real-project-board-acceptance-brainstorm.md`
  - 收口四个真实项目并板验收
  - 冻结首页降噪、详情解释性、debug 三态、Beacon 自并板和断库重建场景

当前已补充正式需求闭环材料：

- `user-story/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
  - 将 CEO 汇总、项目负责人详情、runtime 下钻、恢复降级、边界治理拆成正式用户故事与 AC
- `qa/test-cases/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
  - 将 lifecycle-first board、team/ralph 下钻、git/worktree、session 边界、四项目真实并板、deterministic projection、degraded/rebuild、prototype 一致性拆成可执行场景
- `execution/real-project-validation-checklist-beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`
  - 将 `rolo / slow_uni_bmtop / shopxo_canada / beacon` 四项目并板验收冻结成执行清单
  - 约束首页总览、详情解释性、debug 三态、deterministic projection 与断库重建

当前已补充一套冻结 prototype 参考包：

- `prototype/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane/`
  - `index.html`
  - `design-prompt.md`
  - `ui-style-analysis.md`
  - `prototype-review.md`
  - `freeze.json`
  - `page-specs/`
  - `pages/`
  - `states/`

其原型 source envelope 位于：

- `user-story/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane.md`
  - 仅用于 `beacon prototype` 编译与冻结
  - 正式需求真相仍以主 PRD 为准
