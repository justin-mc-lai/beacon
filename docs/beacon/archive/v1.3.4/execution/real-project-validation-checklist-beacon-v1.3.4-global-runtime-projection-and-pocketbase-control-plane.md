# Beacon v1.3.4 真实项目并板验收清单

- feature: `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`
- version: `v1.3.4`
- purpose: `把四个真实项目并板验收收口成可执行走查清单`
- status: `ready-for-implementation`

## 0. 执行入口

这份清单已正式接入 `beacon-real-project-validation` 路径：

- capture script:
  - `skills/beacon/beacon-real-project-validation/scripts/run_real_project_board_validation.sh`
- record template:
  - `skills/beacon/beacon-real-project-validation/references/board-acceptance-record-template.md`
- command matrix:
  - `skills/beacon/beacon-real-project-validation/references/command-matrix.md`

建议执行方式：

1. 先运行 capture script，生成只读验证产物包。
2. 把 `portfolio-board.txt / portfolio-board.json` 作为首页总览的唯一主页证据。
3. 再按本清单和 record template / 生成的 `acceptance-record.md` 填写真实项目验收记录。
3. 最后把结果分类为 `Beacon defect / project-state blocker / not-yet-implemented acceptance gap`。

## 1. 验收对象

必须同时覆盖以下 4 个真实项目：

1. `/Users/apple/Developer/Company/rolo`
2. `/Users/apple/Developer/Personal/products/slow_uni_bmtop`
3. `/Users/apple/Developer/Personal/products/shopxo_canada`
4. `/Users/apple/Developer/Personal/products/beacon`

## 2. 验收前提

1. Beacon 仍以 `docs/beacon + .beacon` 为 truth plane。
2. SQLite / PocketBase 仅为 projection / control plane。
3. `omc / omx` 不得出现在默认并板结果中。
4. 验收需要同时检查首页总览、项目详情、运行态下钻、降级/重建场景。

## 3. 首页总览验收

### 3.1 并板存在性

- [ ] 四个项目都出现在 `Beacon 管理看板`
- [ ] 每个项目都显示项目名、当前版本、生命周期阶段、总进度、blocker、下一步
- [ ] 首页默认不暴露 tmux pane、worker transcript、raw runtime event 洪流

### 3.2 首页差异性

- [ ] `rolo` 一眼可见 workspace 属性
- [ ] `slow_uni_bmtop` 一眼可见单仓属性
- [ ] `shopxo_canada` 一眼可见“有项目态但无 debug feed”
- [ ] `beacon` 一眼可见“自身 v1.3.4 自演进项目”

## 4. 项目详情验收

每个项目都必须下钻验证：

- [ ] 当前版本线
- [ ] 主 PRD / 并行 PRD
- [ ] requirement materials completeness
- [ ] runtime mode
- [ ] git / worktree 规范
- [ ] recommended next skill / next action
- [ ] 当前字段的解释性文案或来源说明

## 5. 真实项目差异校验

### 5.1 rolo

- [ ] 判定为 `multi_repo_workspace`
- [ ] debug 状态为 `runtime_feed_only`
- [ ] 不退化成单服务单仓
- [ ] branch / worktree 以高优先级 source 为准

### 5.2 slow_uni_bmtop

- [ ] 判定为 `single_repo`
- [ ] debug 状态为 `materialized_issue`
- [ ] 物化 issue 可以被详情页消费

### 5.3 shopxo_canada

- [ ] 判定为受管项目，而不是“无状态目录”
- [ ] debug 状态为 `no_debug_feed`
- [ ] 即使无 debug feed，仍显示 runtime / team/handoff / 项目推进摘要

### 5.4 beacon

- [ ] 判定为普通受管项目，而不是隐藏特殊对象
- [ ] 显示 `v1.3.4` 当前主线
- [ ] 自身 PRD / QA / release / doctor 信号可被详情页消费

## 6. Deterministic Projection 验收

- [ ] 每个项目目录都有 `projection-determinism.json`
- [ ] 同一 truth snapshot 重复投影得到同一 `projection envelope`
- [ ] SQLite / PocketBase 共享一致的 `source_hash / projection_seq`
- [ ] 如果 branch / worktree / session / lifecycle 推断冲突，只能进入 `reject / partial / conflicted`
- [ ] 不允许 heuristic 覆盖用户显式指定或 git worktree 实证

## 7. Debug 三态验收

- [ ] `materialized_issue` 有正式展示语义
- [ ] `runtime_feed_only` 有正式展示语义
- [ ] `no_debug_feed` 有正式展示语义
- [ ] 三态不会被压扁成“有 issue / 无 issue”二元逻辑

## 8. 降级与重建验收

- [ ] SQLite 缺失时，不阻断四项目继续推进
- [ ] PocketBase 缺失时，不阻断四项目继续推进
- [ ] 以每个项目 `status.json` 作为 truth-only baseline，对照隔离 ledger 的 `portfolio-board.json`
- [ ] 可从 `docs/beacon`、`.beacon` 与 git/worktree 恢复四项目最小并板能力
- [ ] 重建后首页与详情页仍可展示项目形态、生命周期、debug 三态与下一步

## 9. 验收记录

每次真实项目并板验收至少记录：

- 验收时间
- 执行人
- 项目路径
- 首页结果
- 详情页结果
- deterministic projection 结果
- debug 三态结果
- 降级 / 重建结果
- blocker / follow-up

## 10. 建议执行顺序

1. 先验证四项目发现与 project registry 建立。
2. 再验证首页卡片与 CEO 差异化展示。
3. 再验证四项目详情页解释性。
4. 再验证 deterministic projection 与 preflight 冲突处理。
5. 最后验证 SQLite / PocketBase 缺失时的降级与重建。
