# Beacon Doctor Orchestration Blueprint

## 1. 文档定位

本文件冻结 `beacon doctor` 在 `v1.3.4` 的完整职责重构结果。

目标不是改变 CLI surface，而是把 doctor 的执行职责全面收口为：

1. CLI 适配层
2. 内部 registry
3. 显式 orchestration

同时保持现有 CLI 命令名、JSON payload、exit code、测试契约不变。

## 2. 已实现判断

`doctor.py` 不再直接承载 doctor 的业务执行逻辑。

已下沉到 registry/orchestrator 的职责：

1. `doctor` 根入口 / `diagnose`
2. `setup` / `uninstall`
3. `setup-context`
4. `verify-context`
5. `sync-gitignore`
6. `verify-gitignore`
7. `sync-materials`
8. `verify-materials`
9. `sync-requirement-clarity`
10. `sync-technical-review-contract`
11. `verify-subagent-runtime`
12. `verify-subagent-delegation`
13. `verify-delivery`
14. `verify-config`
15. `verify-git-alignment`
16. `repair-package`
17. `upgrade-package`
18. `quiet-worktree`
19. `advise`
20. `setup-codex-hud-hook`
21. `verify-codex-hud-hook`
22. `verify-runtime-ledger`
23. `export-runtime-ledger`
24. `rebuild-runtime-ledger`
25. `doctor --fix`

其中复合编排最明确的仍是：

1. `setup-context`
2. `verify-context`
3. `verify-config`
4. `verify-git-alignment`
5. `doctor --fix`

保留在 `doctor.py` 的内容只剩：

1. `setup-context`
   - CLI 参数定义
   - 人类输出 renderer
   - `raise typer.Exit(...)`
2. alias 命令
   - `setup-agent-md`
   - `verify-agent-md`
3. 少量派生命令的人类输出格式拼装

## 3. 实现结构

### 3.1 CLI 适配层

文件：

- `beacon/commands/doctor.py`

职责只保留：

1. Typer 命令注册
2. CLI 参数解析
3. 人类输出渲染
4. `raise typer.Exit(code=...)`
5. 针对少量派生命令保留 doctor 层 JSON/human adapter

### 3.2 Registry

文件：

- `beacon/utils/doctor_registry.py`

核心对象：

- `DoctorHandlerSpec`

字段：

1. `key`
2. `domain`
3. `action`
4. `handler_id`
5. `description`
6. `handler`
7. `reads`
8. `writes`
9. `safe_by_default`
10. `supports_dry_run`
11. `supports_json`
12. `participates_in_parent_flows`

已注册的关键 handler 包括：

1. `diagnostics.run.payload`
2. `diagnostics.advise.next-step`
3. `launcher.setup.install`
4. `launcher.uninstall.remove`
1. `context.setup.managed-files`
2. `context.setup.onboarding-state`
3. `context.verify.managed-files`
4. `context.sync.gitignore`
5. `context.verify.gitignore`
6. `materials.sync.requirement-materials`
7. `materials.sync.requirement-clarity`
8. `materials.sync.technical-review-contract`
9. `materials.verify.material-audit`
10. `runtime.verify.subagent-runtime`
11. `runtime.verify.subagent-delegation`
12. `delivery.verify.audit`
13. `package.repair.v115-delivery`
14. `package.upgrade.version-package`
15. `package.verify.source-architecture-status`
16. `host.quiet-worktree.manage`
17. `host.setup.codex-hud-hook`
18. `host.verify.codex-hud-hook`
19. `projection.verify.runtime-ledger`
20. `projection.export.runtime-ledger`
21. `projection.rebuild.runtime-ledger`

### 3.3 Orchestrator

文件：

- `beacon/utils/doctor_orchestrator.py`

核心对象：

- `DoctorExecutionContext`
- `DoctorExecutionResult`

核心能力：

1. 统一构建 `project_root / runtime_info / runtime_version / version_context`
2. 统一执行 registry handler
3. 显式组合 parent flow
4. 统一 doctor domain exit code 决策
5. 保留单检查 payload 包装工具，供 `verify-*` 派生命令复用

## 4. 编排模型

### 4.1 `setup-context`

`setup-context` 不再被视为单个 handler，而是显式 orchestration：

1. `context.setup.managed-files`
2. 可选 `context.sync.gitignore`
3. `context.setup.onboarding-state`
4. 可选 `materials.sync.requirement-materials`

输出仍保持：

1. `action=setup-context`
2. `status=PASS`
3. `docs_version`
4. `runtime_version`
5. `version_context`
6. `version_semantics`
7. `result.actions`
8. `material_sync`

### 4.2 `verify-context`

`verify-context` 的内部流程：

1. `context.verify.managed-files`
2. 可选 `context.verify.gitignore`
3. 合并 checks 与整体状态

注意：

1. 合并逻辑发生在 orchestrator
2. `strict` 对最终 `WARN -> BLOCKED` 的处理仍保留原契约
3. `.gitignore` 检查只是新增一项 check，不改变既有 check 名

### 4.3 `sync-gitignore` / `verify-gitignore`

这两个命令现在只是 registry handler 的 CLI 包装。

它们依然保留原 JSON 外壳：

1. `schema_version`
2. `action`
3. `status`
4. `result`

### 4.4 `delivery` 派生命令

`verify-delivery`、`verify-config`、`verify-git-alignment` 都不再在 CLI 层直接执行 audit。

统一模式是：

1. 先执行 `delivery.verify.audit`
2. 再由 orchestrator 组装：
   - 直接透出 delivery audit
   - 或包装为单检查 payload

这样保留了现有外部 contract，同时把执行职责移出 `doctor.py`。

### 4.5 `sync-materials` / `verify-materials`

这两个命令继续保持对外 contract 不改：

1. `sync-materials`
   - 仍返回 `.machine/user-story`、`.machine/qa` 投影结果
2. `verify-materials`
   - 仍直接暴露 `result.checks`
   - `strict` 下 `WARN -> BLOCKED`

### 4.6 `runtime` / `package` / `host`

这三组也已进入统一执行面：

1. `runtime.verify.subagent-runtime`
2. `runtime.verify.subagent-delegation`
3. `package.repair.v115-delivery`
4. `package.upgrade.version-package`
5. `package.verify.source-architecture-status`
6. `host.quiet-worktree.manage`
7. `host.setup.codex-hud-hook`
8. `host.verify.codex-hud-hook`

### 4.7 `projection`

`v1.3.4` 新增的运行态账本治理，也收敛到同一套 registry + orchestrator 模式：

1. `projection.verify.runtime-ledger`
   - 负责验证 deterministic projection、preflight、SQLite 可用性、PocketBase control-plane scaffold
2. `projection.export.runtime-ledger`
   - 负责导出 SQLite / projection envelope / PocketBase scaffold 作为备份包
3. `projection.rebuild.runtime-ledger`
   - 负责从 `docs/beacon + .beacon` 重新投影并恢复最小可用 ledger 状态

对外 CLI surface 仍收敛在：

1. `beacon doctor verify-runtime-ledger`
2. `beacon doctor export-runtime-ledger`
3. `beacon doctor rebuild-runtime-ledger`

这样保持了 `status / doctor` 承担观测与修复入口的产品边界，不新增新的一级主命令。

1. `runtime`
   - `verify-subagent-runtime`
   - `verify-subagent-delegation`
2. `package`
   - `repair-package`
   - `upgrade-package`
3. `host`
   - `quiet-worktree`
   - `setup-codex-hud-hook`
   - `verify-codex-hud-hook`

注意：

1. `verify-codex-hud-hook` 仍保留 `WARN -> exit 0`
2. `quiet-worktree` 仍保留真实 git side-effect contract
3. `repair-package` / `upgrade-package` 仍保留真实迁移行为，不是空包装

### 4.7 `doctor --fix`

`doctor --fix` 现在不再手写：

1. context 文件修复
2. gitignore 修复
3. onboarding 写回

而是直接复用 `run_context_setup(...)`，再保留既有：

4. `upgrade-package`

这意味着后续 doctor repair 逻辑可以继续往 orchestrator 接，而不是继续回到 callback 里堆分支。

## 5. 领域边界

为避免 doctor 再次膨胀，`v1.3.4` 冻结以下 domain 判断：

1. `diagnostics`
   - 诊断、建议、解释
2. `context`
   - `CLAUDE.md`、`AGENTS.md`、`.gitignore`、onboarding、global boundaries
3. `materials`
   - requirement main-chain 与 machine projection
4. `runtime`
   - subagent/runtime readiness
5. `package`
   - package repair / upgrade / delivery migration
6. `host`
   - quiet worktree、HUD hook、本机集成

新增 doctor 职责时，先确定 domain，再决定是：

1. 直接注册为 atomic handler
2. 接入已有 orchestration
3. 新增父级 orchestration

而不是先想 CLI 名字。

## 6. 接入规范

新增 doctor 职责时，要求满足：

1. 必须先注册 `DoctorHandlerSpec`
2. 必须声明 `reads/writes`
3. 必须声明 `participates_in_parent_flows`
4. 如果属于复合流，不允许把编排直接写回 `doctor.py`
5. CLI 适配层只能做：
   - 参数解析
   - renderer
   - exit code 透传

## 7. 验收标准

本次重构以“外部契约不回归”为第一优先级。

必须通过的验收集：

1. `tests/test_doctor_v2_contract.py`
2. `tests/test_doctor_context_commands.py`
3. `tests/test_doctor_gitignore_commands.py`
4. `tests/test_doctor_alias_and_subagent_commands.py`
5. `tests/test_doctor_material_delivery_commands.py`
6. `tests/test_doctor_config_contract.py`
7. `tests/test_doctor_git_alignment_contract.py`
8. `tests/test_doctor_quiet_worktree.py`
9. `tests/test_doctor_codex_hud_hook.py`
10. `tests/test_v115_doctor_repair_package.py`
11. `tests/test_v112_doctor_upgrade_package.py`
12. `tests/test_v130_material_sync.py`
13. `tests/test_doctor_orchestrator.py`

必须保持的行为：

1. `doctor --json` 仍可直接执行
2. `setup-context --dry-run` 不写文件
3. `verify-context --strict` 在 marker 损坏时 exit `2`
4. `setup-context` 动作列表包含 `.gitignore` 与 onboarding state
5. `verify-context` 保留既有 check 名，并额外合并 `beacon_gitignore_policy`
6. `sync-materials` 仍投影 `.machine/user-story` 与 `.machine/qa`
7. `doctor --fix` 仍保留 context + package 补齐语义

## 8. 后续阶段

`v1.3.4` 已完成 doctor 执行职责的整体收口，后续不再是“迁命令”，而是两类持续工作：

1. 补 contract 测试空洞
   - `--fix`
   - alias 命令
   - subagent verify
2. 增量接入新职责
   - 先注册 handler
   - 再决定是否需要 orchestration

后续仍遵循当前方向：

1. 不轻易改 CLI surface
2. 先注册 handler，再做 orchestration
3. 先冻结 contract，再扩职责

## 9. 一句话结论

`v1.3.4` 对 doctor 的重构，不是换一层名字，而是把诊断、context、materials、runtime、delivery、package、host 这些职责全部从平面命令堆叠收束成一个可注册、可编排、可验收的内部控制面。
