# Boundaries: Beacon v1.1.1 研究层 + 主链层 + 交付层闭环

**版本**: v1.1.1
**日期**: 2026-03-13
**状态**: Draft
**Feature**: beacon-strict-config-governance

---

## 1. 分层边界

### 研究层（Research Layer）
- 目录：`docs/beacon/v1.1.1/research/`
- 内容：`brainstorm-*`、`analysis-*`、`research-*`、`architecture-*`、`compare-*`、`convergence-*`
- 角色：输入层 / 发散层 / 方案沉淀层
- 约束：
  - 不是最终交付主源
  - 不直接参与 gate
  - 必须通过 `user-story / prd` 收敛后才能进入测试主链

### 主链层（Main Chain Layer）
- 目录：
  - `docs/beacon/v1.1.1/user-story/`
  - `docs/beacon/v1.1.1/prd/`
  - `docs/beacon/v1.1.1/qa/test-cases/`
- 角色：正式需求与验证主源
- 约束：
  - workflow / gate 只消费主链层
  - `test-case` 只能从 `user-story / prd` 收敛而来
  - compat 镜像只允许自动同步

### 交付层（Delivery Layer）
- 目录：`docs/beacon/v1.1.1/execution/`
- 最低必备交付物：
  - `boundaries.md`
  - `delivery-manifest.json`
  - `change-impact.json`
  - `config.json`
  - `source.json`
  - `git-alignment.json`
  - `terminal.json`（完整闭环时）
- 角色：交付范围、变更影响、Git refs、终态证明

---

## 2. In Scope

| 范围 | 描述 | 优先级 |
|------|------|--------|
| 配置治理 | workspace/project/implementation/docs/source_info/git | Must |
| Research 编排 | brainstorm/analyze/research 统一进入 research 目录 | Must |
| 主链收敛 | research -> user-story / prd -> test-case | Must |
| 多项目交付清单 | 受影响项目、仓库、分支、commit、worktree 必须进入 delivery manifest | Must |
| 变更影响闭环 | changed_layers/tasks/main_chain_converged/delivery_manifest_ready | Must |
| Gate/CI 校验 | verify-config / verify-git-alignment / verify-agent-md / gate | Must |

## 3. Out of Scope

| 范围 | 原因 |
|------|------|
| research 直接参与 gate | 会污染正式交付主源 |
| compat 镜像人工维护 | 会造成 docs/beacon 与 docs/product 双写漂移 |
| 未记录 Git refs 的交付 | 无法在多仓库场景下证明交付边界 |
| 业务代码实现本身 | 本版本聚焦治理与交付链路，不扩展业务实现职责 |

## 4. 交付必备项

### 4.1 delivery-manifest.json 必填字段

每个 `affected_projects[]` 至少包含：
- `name`
- `project_root`
- `repo_url`
- `change_scope`
- `changed_layers`
- `base_branch`
- `target_branch`
- `current_branch`
- `commit`
- `tag`（可空）
- `worktree_path`

### 4.2 change-impact.json 必填字段
- `changed_layers`
- `doc_chain_update_required`
- `tasks[]`
- `research_converged`
- `main_chain_converged`
- `delivery_manifest_ready`

### 4.3 主链必备项
- `docs/beacon/v1.1.1/user-story/beacon-strict-config-governance.md`
- `docs/beacon/v1.1.1/prd/beacon-strict-config-governance.md`
- `docs/beacon/v1.1.1/qa/test-cases/beacon-strict-config-governance.md`
- `docs/beacon/v1.1.1/qa/test-cases/beacon-strict-config-governance.ac-test-matrix.json`
- `docs/beacon/v1.1.1/qa/test-cases/beacon-strict-config-governance.qa9-matrix.json`

---

## 5. Done Criteria

| 条件 | 验证方式 |
|------|----------|
| research 已统一归档 | `docs/beacon/v1.1.1/research/` 下存在 feature 相关文档 |
| research 已收敛到主链 | User Story / PRD / Test Case 都有对应 feature 产物 |
| delivery manifest 完整 | `affected_projects` 与 Git refs 字段完整 |
| change impact 完整 | `changed_layers`、`tasks`、收敛状态存在 |
| strict 交付可校验 | verify-config / verify-git-alignment / verify-agent-md / gate 有标准链路 |

## 6. Blocked Criteria

| 条件 | 状态 |
|------|------|
| `delivery-manifest.json` 缺失 | Blocked |
| `affected_projects` 为空 | Blocked |
| 任一受影响项目缺失 `base/current/target branch` 或 `commit/tag` | Blocked |
| `change-impact.json` 缺失 | Blocked |
| `change-impact.tasks` 存在未完成项 | Blocked |
| `research` 尚未收敛但已尝试进入 gate | Blocked |
| 主链文档缺失（US/PRD/TC） | Blocked |

## 7. Reason Codes（交付层）

| Code | 说明 | 阻断级别 |
|------|------|---------|
| delivery_manifest_missing | 交付清单缺失 | Blocked |
| delivery_manifest_schema_invalid | 交付清单字段不完整 | Blocked |
| affected_projects_empty | 未声明受影响项目 | Blocked |
| affected_project_git_ref_missing | 受影响项目缺失 Git refs | Blocked |
| change_impact_missing | 变更影响交付物缺失 | Blocked |
| change_impact_open_tasks | 文档链/交付链未闭环 | Blocked |
| research_not_converged | research 尚未收敛入主链 | Blocked |
| main_chain_incomplete | user-story / prd / test-case 缺失 | Blocked |

## 8. 当前 v1.1.1 交付范围（本稿）

- Source of Truth: `docs/beacon/v1.1.1/`
- Compat Mirror: `docs/product/v1.1.1/`
- Affected Project: `beacon`
- Current Branch: `main`
- Base Branch: `main`
- Target Branch: `beacon/v1.1.1`
- Commit: `d14bc014a5e91e0a547966d8421b0bdf745019b8`
- Repo: `https://github.com/justin-mc-lai/beacon.git`
- Worktree: `/Users/apple/Developer/Personal/my_skill/beacon`

---

**说明**：本边界文档用于定义 v1.1.1 的研究层 + 主链层 + 交付层闭环规则；只有在交付层三件套（`boundaries.md`、`delivery-manifest.json`、`change-impact.json`）齐备时，才可认为“交付物整理”进入可验收状态。
