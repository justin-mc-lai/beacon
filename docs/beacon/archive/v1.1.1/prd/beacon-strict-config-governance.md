# PRD: Beacon 严格配置治理、Research 编排与 AI Agent 工程化标准化（v1.1.1）

## 1. 目标

将 Beacon 从“可生成需求产物”的工具，升级为“可被 AI Agent 严格、稳定、可审计执行”的需求治理底座，确保：

1. **配置即契约**：workspace / project / implementation / git / docs / source_info 均可配置。
2. **严格阻断**：关键配置缺失、目标项目无法解析、Git 版本未对齐时，Beacon 必须阻断执行。
3. **执行可追溯**：每次执行都输出配置快照、来源元信息、Git 对齐结果。
4. **Agent 可落地**：项目初始化时自动注入 Beacon 生命周期说明，确保 LLM/Agent 默认遵循 Beacon 工作流。
5. **发散与收敛分层**：brainstorm / analysis / research 统一沉淀到 `docs/beacon/<version>/research/`，再收敛进 `user-story / prd / test-case` 主链。
6. **交付显式化**：多项目 / 多仓库需求变更必须以正式交付物 manifest 与 change-impact 形式记录受影响项目、Git 分支与收敛状态。

## 2. 背景

v1.1.1 已明确 `docs/beacon/<version>/` 为唯一维护源，`docs/product/<version>/` 仅作为兼容视图；同时，Beacon 在 AI Agent 场景中的核心价值应集中在 **结构化、可信、可交付**。

但当前工程化落地仍存在以下问题：

1. **多项目 / workspace 场景不清晰**：主目录下管理多个 Beacon 项目时，容易依赖 cwd 或 `--project` 猜测，存在跑错目录风险。
2. **实现目录边界不清晰**：需求文档与工程实现目录缺乏配置绑定，Agent 很难知道“允许在哪些目录执行实现/验证”。
3. **版本一致性不足**：Beacon 迭代版本、Git 分支/Tag/Commit、产物目录之间缺乏强一致校验，容易出现“文档版本正确、代码版本漂移”的问题。
4. **上下文注入不完整**：当前根目录初始化文件更多是基础上下文提示，缺少 Beacon 全生命周期、严格模式与故障修复入口的完整说明。
5. **执行证据不足**：需要把配置、来源、Git 对齐、审计日志作为标准产物输出，而不是依赖运行时隐式状态。
6. **research / analysis / brainstorm 与主链边界不清晰**：当前研究资料部分手工放在 `docs/beacon/<version>/research/`，部分分析命令仍输出到 `docs/product/...`，导致 research 与 PRD、测试主链关系不稳定。
7. **交付物缺少多项目/多仓库变更清单**：即使需求只影响部分项目、部分分支，当前也缺乏一个正式交付物来描述受影响项目、当前分支、目标分支、base branch、commit 与 worktree 路径。

## 3. 范围

### In Scope

1. Workspace 多项目配置与目标项目解析。
2. 实现目录（implementation root / include / exclude）配置。
3. Git 版本严格对齐策略与阻断校验。
4. Doctor 配置模板生成、校验、纠错与 agent 初始化注入。
5. Workflow 执行前 preflight 校验与严格阻断。
6. `execution/config.json`、`execution/source.json`、`execution/git-alignment.json` 等标准元信息产物。
7. `docs/beacon` 作为唯一人工维护源，`docs/product` 仅作为兼容镜像。
8. `brainstorm / analysis / research` 统一落盘到 `docs/beacon/<version>/research/`。
9. 从 `research -> user-story / prd -> test-case` 的可追踪收敛规则。
10. `execution/delivery-manifest.json` 记录多项目/多仓库交付范围与 Git refs。
11. `execution/change-impact.json` 记录本次需求变更涉及的层、待更新链路与闭环状态。
12. `execution/boundaries.md` 明确 research 层、主链层、交付层的消费边界。

### Out of Scope

1. 不实现业务代码本身。
2. 不替代 CI/CD、代码评审或发布平台。
3. 不在本版本内彻底移除 `docs/product` 兼容镜像。
4. 不扩展 Beacon 到“自动编写业务实现”的职责边界。
5. 不允许 research 直接进入 gate 或直接作为最终交付主源。

## 4. 功能需求

### FR-001 Workspace 多项目配置

Beacon 必须支持 workspace 根目录下的多项目配置，至少包含：

- `workspace.root`
- `workspace.projects[].name`
- `workspace.projects[].root`
- `workspace.projects[].default`
- `workspace.projects[].docs.*`
- `workspace.projects[].source_info.*`

目标项目解析优先级：
1. CLI `--project <name|path>`
2. 环境变量 `BEACON_PROJECT`
3. cwd 最长路径匹配
4. workspace 默认项目
5. 无法解析时，在 strict 模式下阻断

### FR-002 实现目录配置

Beacon 必须支持实现目录配置，用于约束 implementation / verify 阶段可操作范围：

- `implementation.root`
- `implementation.include_paths[]`
- `implementation.exclude_paths[]`

要求：
- implementation root 必须落在目标项目根目录内。
- include / exclude 冲突时，以 exclude 优先。
- strict 模式下，超出实现范围的执行计划必须阻断。

### FR-003 Git 版本严格对齐

Beacon 必须支持 Git 对齐配置，并在 strict 模式下强制校验：

- `git.version_policy = strict`
- `git.version_ref`
- `git.allowed_refs = [tag, branch, commit]`
- `git.enforce_branch_prefix`（可选）

要求：
- 当前执行上下文的 Git branch/tag/commit 至少一项必须与 `version_ref` 对齐。
- 允许定义 `beacon/v1.1.1` 这类 branch 命名规范。
- 不对齐时阻断 workflow / doctor verify / gate 继续执行。

### FR-004 Doctor 配置治理入口

Doctor 必须成为配置治理的唯一入口，新增或扩展以下能力：

- `beacon doctor setup-workspace`
- `beacon doctor verify-workspace --strict`
- `beacon doctor setup-config`
- `beacon doctor verify-config --strict`
- `beacon doctor fix-config`
- `beacon doctor verify-git-alignment --strict`
- `beacon doctor setup-agent-md`
- `beacon doctor verify-agent-md`

要求：
- 可确定修复项允许自动修复。
- 不可确定修复项必须输出明确 reason code 与修复建议。
- strict 模式下，任何 P0 级配置问题都必须返回 BLOCKED。

### FR-005 Agent 初始化文件注入

Beacon 必须支持向项目初始化文件注入完整的 Beacon 生命周期说明。支持的目标文件至少包括：

- `CLAUDE.md`
- `AGENTS.md`
- 项目配置声明的其他 agent 初始化 md 文件（如 `agent.md`）

注入内容至少包含：
- Beacon 生命周期（think → user-story → prd → test-case → implementation → verify → gate）
- `docs/beacon/<version>/` 为唯一人工维护源
- strict 模式与 doctor 修复入口
- 建议命令模板与常见阻断原因说明

### FR-006 执行前 Preflight 校验

Workflow 在进入 think 阶段前，必须输出 preflight 摘要并完成以下校验：

1. 目标项目已解析。
2. 版本已解析且与 Git 对齐。
3. docs source root 合法。
4. implementation root 合法。
5. source_info 配置合法。
6. 必要的 agent 初始化文件存在且版本未漂移。

任何 P0 失败项在 strict 模式下必须阻断执行。

### FR-007 元信息与执行证据标准化

每次 workflow / doctor / gate 执行必须输出标准元信息：

- `docs/beacon/<version>/execution/config.json`：解析后的最终配置快照
- `docs/beacon/<version>/execution/source.json`：source_info 元信息
- `docs/beacon/<version>/execution/git-alignment.json`：Git 对齐结果
- `.beacon/evidence-manifest.json`：证据清单
- `.beacon/raw-command-log.jsonl`：原始命令日志
- 可选：`execution/audit.jsonl`

### FR-008 docs/beacon 单一维护源

本版本对外口径统一为：
- `docs/beacon/<version>/` 是唯一人工维护源
- `docs/product/<version>/` 是兼容镜像，不允许作为 source/meta 手工维护

要求：
- 所有新需求物料优先写入 `docs/beacon`
- 若仍保留 compat 镜像，必须由 Beacon/doctor 自动同步，而非人工双写

### FR-009 CI / Gate 标准化

CI 与 Gate 必须支持以下标准校验链路：

1. `beacon doctor verify-config --strict`
2. `beacon doctor verify-git-alignment --strict`
3. `beacon doctor verify-agent-md --strict`
4. `beacon gate check --version <version>`
5. `execution/terminal.json` schema 校验（在完整闭环场景）

### FR-010 Research 目录统一编排

Beacon 必须支持把发散与研究类资料统一沉淀到：

- `docs/beacon/<version>/research/`

并明确分类：
- `brainstorm` 是 `research` 的一个子类型
- `analysis` 是 `research` 的一个子类型
- research 目录允许包含：`brainstorm-*`、`analysis-*`、`research-*`、`architecture-*`、`compare-*`、`convergence-*`

要求：
- research 不要求同步到 `docs/product`
- compat 镜像不作为 research 的人工维护位置
- research 输出路径应支持命令配置化覆盖

### FR-011 Research 元数据与状态模型

每份 research 文档应支持基础治理元信息，至少包括：

- `type`
- `status`
- `feature`
- `version`
- `convergence_targets`
- `source_of_truth=false`

推荐状态：
- `divergent`
- `triaged`
- `converged`
- `archived`

要求：
- brainstorm 结果支持直接落盘并持续追加
- 研究资料必须可区分“发散中”与“已收敛入主链”

### FR-012 Research 到主链的收敛规则

Beacon 必须明确：

```text
research -> user-story / prd -> test-case
```

要求：
- `workflow` 主链只消费：`user-story`、`prd`、`test-case`
- `research` 不直接参与 gate
- `test-case` 不得直接从 research 生成并跳过 user-story / prd
- 每次收敛都应能追溯来源 research 文档

### FR-013 多项目 / 多仓库交付物 Manifest

Beacon 必须支持在 `docs/beacon/<version>/execution/delivery-manifest.json` 中显式记录本次交付范围。

要求：
- 至少包含 `affected_projects[]`
- 每个项目至少记录：
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
- 若需求仅影响部分项目，也必须显式列出“只影响哪些项目”
- 该文件属于正式交付物，而不是仅存在于 `.beacon/state` 的内部状态

### FR-014 execution/change-impact.json

Beacon 必须支持在 `docs/beacon/<version>/execution/change-impact.json` 中输出变更影响结果。

要求：
- 记录 `changed_layers`
- 记录 `doc_chain_update_required`
- 记录 `tasks[]`
- 记录 `research_converged` / `main_chain_converged` / `delivery_manifest_ready` 等状态
- 若 PRD / User Story / Test Case / Execution 其中任一链路未收敛，应显式标记未完成

### FR-015 Delivery Readiness 边界与阻断

Beacon 必须在 `execution/boundaries.md` 中明确交付层边界：

- research 层：输入层，不直接 gate
- 主链层：`user-story / prd / test-case`
- 交付层：`boundaries.md / delivery-manifest.json / change-impact.json / terminal.json / execution 元信息`

严格模式下，以下情况必须阻断交付就绪：
- `delivery-manifest.json` 缺失
- `affected_projects` 为空或缺少 Git refs
- `change-impact.json` 缺失
- `change-impact.tasks` 未完成
- `research` 未收敛但主链已尝试 gate

## 5. 配置模型（建议稿）

```yaml
workspace:
  root: /abs/path/to/workspace
  projects:
    - name: beacon
      root: /abs/path/to/workspace/beacon
      default: true
      docs:
        source_root: docs/beacon
        compat_root: docs/product
        write_mode: source_only
      implementation:
        root: /abs/path/to/workspace/beacon
        include_paths: [beacon, tests]
        exclude_paths: [dist, node_modules, .beacon]
      source_info:
        enabled: true
        output: docs/beacon/archive/v1.1.1/execution/source.json
        include_git: true
        fields: [project_name, project_root, workspace_root, branch, commit, run_id, version, timestamp]
      git:
        version_policy: strict
        version_ref: v1.1.1
        allowed_refs: [tag, branch]
        enforce_branch_prefix: beacon/
      research:
        root: docs/beacon/archive/v1.1.1/research
        sync_to_compat: false
        allowed_types: [brainstorm, analysis, research, architecture, compare, convergence]
      delivery:
        manifest_output: docs/beacon/archive/v1.1.1/execution/delivery-manifest.json
        change_impact_output: docs/beacon/archive/v1.1.1/execution/change-impact.json
        require_git_refs: true
        require_affected_projects: true
```

## 6. 验收标准（AC）

| AC ID | 验收项 |
|------|--------|
| AC-001 | strict 模式下，workspace 未配置或目标项目无法解析时，workflow / doctor 必须 BLOCKED |
| AC-002 | implementation root/include/exclude 配置可生效，超出允许范围的执行计划被阻断 |
| AC-003 | Git branch/tag/commit 与 Beacon 版本未对齐时，`verify-git-alignment --strict` 返回 BLOCKED |
| AC-004 | doctor 可生成 workspace/config 模板，并对可确定问题执行自动纠错 |
| AC-005 | `setup-agent-md` 可向初始化 md 文件注入完整 Beacon 生命周期说明 |
| AC-006 | workflow 执行前输出 preflight 摘要，展示目标项目、版本、docs source、strict 状态 |
| AC-007 | 每次执行生成 `execution/config.json`、`execution/source.json`、`execution/git-alignment.json` |
| AC-008 | `docs/beacon/<version>/` 作为唯一人工维护源，compat 镜像不要求人工双写 |
| AC-009 | CI 可串联 verify-config / verify-git-alignment / verify-agent-md / gate check |
| AC-010 | strict 模式下所有 P0 问题均带明确 reason code 与修复命令建议 |
| AC-011 | brainstorm / analysis / research 统一落盘到 `docs/beacon/<version>/research/`，且不要求同步到 compat 镜像 |
| AC-012 | research 文档具备 type/status/feature/version/convergence_targets/source_of_truth 等治理元信息 |
| AC-013 | workflow / gate 只消费 `user-story / prd / test-case`，research 不直接作为最终交付主源 |
| AC-014 | research 进入测试主链前，必须先收敛到 `user-story / prd`，并可追溯来源 research 文档 |
| AC-015 | `execution/delivery-manifest.json` 必须列出受影响项目、repo、project_root、base/current/target branch、commit/tag、worktree_path |
| AC-016 | `execution/change-impact.json` 必须记录 changed_layers、tasks 与链路收敛状态 |
| AC-017 | strict 模式下 affected_projects 缺失、Git refs 缺失或 change-impact 未闭环时，交付就绪必须 BLOCKED |
| AC-018 | 多项目场景下，只影响哪些项目必须成为正式交付物的一部分，而不是隐含在聊天或内部状态中 |

## 7. 风险与缓解

| 风险 | 级别 | 缓解 |
|------|------|------|
| strict 模式导致初期阻断较多 | 高 | 提供 doctor setup/fix 路径，先自动修复可确定项 |
| workspace 多项目配置冲突 | 高 | 限制 default 唯一，输出冲突报告 |
| Git 对齐规则过严影响研发效率 | 中 | 允许配置 `allowed_refs` 与分支前缀策略 |
| docs/beacon 与 docs/product 双树长期并存导致认知混乱 | 中 | 明确单一人工维护源，compat 仅自动同步 |
| agent 初始化文件种类不一 | 中 | 支持配置化声明注入目标文件列表 |
| research 无限膨胀 | 中 | 引入状态模型、triage、命名规范与 convergence 追踪 |
| analysis / research 被误当正式需求 | 高 | 强制 `source_of_truth=false`，workflow 不直接消费 research |
| 多项目交付范围记录不完整 | 高 | 把 manifest / change-impact 升级为正式 execution 交付物 |

## 8. 关联文档

- `docs/beacon/archive/v1.1.1/research/brainstorm-ai-agent-ux.md`
- `docs/beacon/archive/v1.1.1/research/brainstorm-research-convergence-orchestration.md`
- `docs/beacon/archive/v1.1.1/execution/v1.1.1-beacon-functional-architecture-directory-map.md`
- `docs/beacon/v1.1.0/research/beacon-workspace-multiproject-config-research.md`
- `docs/beacon/v1.1.0/research/beacon-ai-agent-engineering-standardization.md`
- `docs/beacon/v1.1.0/research/beacon-ai-agent-engineering-standardization-additional.md`

---

**Created**: 2026-03-13
**Version**: v1.1.1
**Status**: Draft
**Memory Context**: /Users/apple/Developer/Personal/my_skill/beacon/.beacon/state/workflow-memory/run-20260313T014417Z-b758/prd-context.json
