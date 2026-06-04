# Beacon v1.3.0 需求文档与功能对齐审计

**日期**: 2026-04-12  
**审计范围**: `docs/beacon/archive/v1.3.0/` 文档承诺、CLI 命令面、核心实现、测试覆盖、外部项目实测  
**结论摘要**: `v1.3.0` 在 Beacon 核心 runtime 层面已基本对齐；`implement-team` / `qa-team`、角色外置、上下文隔离、HUD、git workflow contract 都有命令、代码、测试和实测支撑。当前主要风险不在“功能不存在”，而在“外部项目的 machine 需求包未同步刷新时，qa-team 会消费过期工件并给出失真的 release-ready 结论”。

---

## 1. 审计基线

本次对齐审计按 Beacon 管理块要求，优先读取并核对以下 `v1.3.0` 文档面：

1. `docs/beacon/archive/v1.3.0/SUMMARY.md`
2. `docs/beacon/archive/v1.3.0/execution/index.md`
3. `docs/beacon/archive/v1.3.0/execution/architecture-blueprint.md`
4. `docs/beacon/archive/v1.3.0/prd/beacon-v1.3.0-simplified-codex-native-subagents.md`
5. `docs/beacon/archive/v1.3.0/qa/test-cases/beacon-v1.3.0-simplified-codex-native-subagents.md`
6. `docs/beacon/archive/v1.3.0/release/v1.3.0.md`

同时核对以下实现面：

- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/utils/team_surface.py`
- `beacon/utils/subagent_runtime.py`
- `beacon/team_roles/implement-team.json`
- `beacon/team_roles/qa-team.json`
- `tests/test_v130_implement_team_surface.py`

外部项目实测目标：

- 项目：`/Users/apple/Developer/Personal/products/slow_uni_bmtop`
- 特性：`friend-match`
- 文档线：`docs/beacon/v1.0.0/`

---

## 2. 文档承诺 vs 实现证据

### 2.1 已对齐项

| 文档承诺 | 审计结论 | 证据 |
|---|---|---|
| `team` 为稳定显性 surface，且 `implement-team` / `qa-team` 有明确入口 | 对齐 | `python3 -m beacon.main implement --help`、`python3 -m beacon.main qa --help` 均已暴露 `team-plan` / `team-run` |
| `implement-team` 支持 planner / implementation-architect / implementer / reviewer / tester | 对齐 | `beacon/team_roles/implement-team.json` 已外置 5 个角色；`implementation-architect` 已显式入列 |
| `qa-team` 支持 verifier / repair-handoff-writer | 对齐 | `beacon/team_roles/qa-team.json` 已外置 2 个角色 |
| `implement-team` 与 `qa-team` 保持上下文隔离 | 对齐 | `beacon/utils/team_surface.py` 的 contract + handoff 写入；两份 role config 都带 `qa_must_not_inherit_implement_private_context` |
| `runtime=file|tmux|auto` 与 HUD 页面存在 | 对齐 | `beacon/utils/subagent_runtime.py` 提供 runtime resolver、tmux worker spawn、HUD JSON/HTML 写入 |
| `implement dev-run` / `sync-git-workflow` / versioned git workflow contract 已纳入实现 | 对齐 | `implement --help` 暴露命令；`tests/test_v130_implement_team_surface.py` 覆盖 `git_workflow_ref` 和 `dev-run` |
| `v1.3.0` team surface 有测试背书 | 对齐 | `python3 -m pytest -q tests/test_v130_implement_team_surface.py` 结果 `11 passed in 10.19s` |
| 外部项目可实际跑通 implement-team | 对齐 | `friend-match` 的 `implement team-plan` / `team-run` 成功；生成 run 目录、role reports、HUD、implement→qa handoff |
| 外部项目可实际跑通 qa-team | 对齐 | `friend-match` 的 `qa team-plan` / `team-run` 成功 materialize `qa-team` 角色报告和 HUD |

### 2.2 部分对齐项

| 文档承诺 | 审计结论 | 说明 |
|---|---|---|
| `qa-team` 能代表当前需求包做 feature-aware 验证 | 部分对齐 | Beacon 核心命令存在且能运行，但它依赖目标项目的 `.machine/user-story` 与 `.machine/qa` 工件质量；如果外部项目 machine 面过期，`qa-team` 会复用失真输入 |
| `release_ready` 可作为对当前需求包的可信结论 | 部分对齐 | 在外部项目实测中，`qa team-run` 给出 `release_ready=true`，但 `coverage_current.executed_scenarios=1`、`required_scenarios=76`、`coverage_rate=0.0132`，因此“可发布”在 package drift 场景下并不可靠 |

---

## 3. 外部项目实测

### 3.1 目标项目上下文修复

初始执行：

```bash
python3 -m beacon.main doctor verify-context --project-root /Users/apple/Developer/Personal/products/slow_uni_bmtop --strict
```

结果：

- `docs_version: v1.0.0`
- `runtime_version: v1.3.0`
- `BLOCKED: managed_block_version_drift`

修复执行：

```bash
python3 -m beacon.main doctor setup-context --project-root /Users/apple/Developer/Personal/products/slow_uni_bmtop
python3 -m beacon.main doctor verify-context --project-root /Users/apple/Developer/Personal/products/slow_uni_bmtop --strict
```

修复后结果：

- `CLAUDE.md` 与 `AGENTS.md` 已升级到 `runtime_version: v1.3.0`
- `verify-context --strict` 通过

### 3.2 implement-team 实测

执行：

```bash
python3 -m beacon.main implement team-plan "friend-match" --project /Users/apple/Developer/Personal/products/slow_uni_bmtop --version v1.0.0 --json
python3 -m beacon.main implement team-run "friend-match" --project /Users/apple/Developer/Personal/products/slow_uni_bmtop --version v1.0.0 --runtime file --json
```

结果摘要：

- `team_surface=implement-team`
- `runner=codex-subagents`
- `run_id=run-20260412T132050Z-7317`
- `terminal_status=Pass`
- 生成 implement-team 工件目录：
  - `docs/beacon/v1.0.0/execution/codex-subagents/friend-match/run-20260412T132050Z-7317/`
- 生成角色报告：
  - `planner`
  - `implementation-architect`
  - `implementer`
  - `reviewer`
  - `tester`
- 生成 HUD：
  - `.beacon/state/team-hud/implement-team-run-20260412T132050Z-7317.json`
  - `docs/beacon/v1.0.0/execution/codex-subagents/friend-match/run-20260412T132050Z-7317/index.html`

### 3.3 qa-team 实测

执行：

```bash
python3 -m beacon.main qa team-plan "friend-match" --project /Users/apple/Developer/Personal/products/slow_uni_bmtop --version v1.0.0 --json
python3 -m beacon.main qa team-run "friend-match" --project /Users/apple/Developer/Personal/products/slow_uni_bmtop --version v1.0.0 --runtime file --json
```

结果摘要：

- `team_surface=qa-team`
- 角色报告与 HUD 已存在：
  - `docs/beacon/v1.0.0/execution/qa-team/friend-match/run-20260409T171723630898/`
- `verifier` 状态为 `passed`
- `repair-handoff-writer` 状态为 `completed`

但该 run 同时暴露关键问题：

- `story_sequence` 只有一条泛化记录：`AC-001 / TC-001 / Acceptance criteria TBD`
- `feature_scorecard.coverage_current.required_scenarios=76`
- `feature_scorecard.coverage_current.executed_scenarios=1`
- `feature_scorecard.coverage_current.coverage_rate=0.0132`
- `feature_scorecard.continue_decision=ready_for_release`

这说明：

1. qa-team runtime 本身可用
2. 但目标项目当前被消费的是**过期 machine 工件**
3. `ready_for_release` 在 package drift 场景下会误导操作者

---

## 4. 当前未对齐风险

### 风险 R1：外部项目 machine 需求包与人类文档未同步

`slow_uni_bmtop` 当前真实的人类文档：

- `docs/beacon/v1.0.0/user-story/friend-match.md`
- `docs/beacon/v1.0.0/qa/test-cases/friend-match.md`

都已经是完整的好友局闭环定义。

但被 qa-team 消费的 machine 面仍是：

- `docs/beacon/v1.0.0/.machine/user-story/friend-match.json`
- `docs/beacon/v1.0.0/.machine/qa/friend-match.ac-test-matrix.json`

其内容只保留了泛化 `AC-001 / TEST-001 / TC-001`。  
因此这不是 Beacon `v1.3.0` 核心功能缺失，而是**交付包同步机制没有保证 human/machine 双面同时刷新**。

### 风险 R2：qa scorecard 的 release-ready 语义过宽

在本次外部项目实测中，`coverage_rate=0.0132` 仍能得出 `ready_for_release`。  
这会让操作者误以为“qa-team 已对齐当前 friend-match 全量需求”，实际并没有。

建议后续约束：

- 当 `executed_scenarios < required_scenarios` 且差距明显时，不得输出 `ready_for_release`
- 或至少在 scorecard 中追加 `release_ready_reason=historical_evidence_only`

### 风险 R3：implement-team 的 changed_files 不区分本次 run 与既有脏工作区

本次 `implement team-run` 的 `changed_files` 基本等于目标仓库已有 dirty worktree 清单，而不是 run 本次差异。  
这让 reviewer/tester 报告难以作为“本次实现变更范围”的可信证据。

---

## 5. 审计结论

### 5.1 对 Beacon v1.3.0 核心功能的结论

`v1.3.0` 文档关于以下核心能力的承诺，已经有足够实现证据支撑：

- 显性 `implement-team` / `qa-team` surface
- 角色配置外置
- `implementation-architect` 执行角色
- implement/qa 上下文隔离
- file/tmux/HUD runtime contract
- versioned git workflow contract
- team surface 自动引导与帮助路由
- 仓内测试覆盖与外部项目实测

因此，**若问题是“Beacon v1.3.0 文档里写的 team runtime 能力，代码里有没有”**，结论是：**基本对齐，且已落地**。

### 5.2 对“需求文档是否真正被 team runtime 消费”的结论

若问题是“只要运行 `qa team-run`，就一定在验证当前最新 PRD / user-story / test-case” ，结论是：**不一定**。

当前真实前提是：

```text
Beacon 核心 runtime 对齐
!=
目标项目 delivery package 自动对齐
```

只有当目标项目的 human/machine 双面需求包都同步刷新后，`qa-team` 的输出才可被当成当前需求文档的可信验证结论。

---

## 6. 后续动作建议

1. 在目标项目中，把 `friend-match` 的 `.machine/user-story` 与 `.machine/qa` 从当前人类文档重新生成或重写。
2. 在 Beacon 核心中收紧 QA scorecard 对 `ready_for_release` 的判定条件，避免低覆盖率误报。
3. 在 implement-team 中把 `changed_files` 从“工作区全量脏文件”收敛为“本次 run 真实变更集”。
4. 在后续发布文档中，明确声明：
   - team runtime 成功 != feature package 已与当前人类需求面完全同步

