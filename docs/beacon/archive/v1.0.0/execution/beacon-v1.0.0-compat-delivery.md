# Beacon v1.0.0 兼容改造与交付验收（命令统一 + 目录兼容）

## 1. 交付结论

- 目标：完成 Beacon 命令统一与历史目录兼容的 v1.0.0 交付与补测自动化。
- 结果：已完成核心兼容改造；兼容回归用例全通过；全量测试通过。
- 当前状态：可完整交付使用。

## 2. 已完成的兼容改造点

### 2.1 CLI 语法统一（Beacon 扁平命令）
- 支持 `doctor --json`（保留 `doctor diagnose`）。
- 支持 `status --board`。
- 支持 `report --human latest` / `report --machine latest`。
- 支持 `init --dry-run` / `init --apply`。
- 支持 `resume <run_id>`（并兼容 `resume restore <run_id>`）。
- 支持 `gate think|user-story|prd|test-case|release --json`。
- 增加 `work` 别名（映射 `workflow start`）。
- 增加全局 `--version/-V` 输出。

### 2.2 行为契约兼容
- `run workflow` 生成 `.beacon/runs/<run_id>/state.json` 与 `events.jsonl`。
- `report` 自动写 execution summary（human + machine）。
- `debug watch` 支持真实事件 tail/follow。
- `feedback sync` 生成 requirement-feedback 产物。
- `doctor` 输出结构化 JSON，并按状态返回正确 exit code。
- `init --apply` 真正创建目录与初始化报告。

### 2.3 路径与 Gate 兼容
- Gate 路径支持：
  - `docs/<version>/execution`
  - `docs/product/<version>/execution`
  - `docs/beacon/<version>/execution`
- Gate stage alias 与 `check` 路径行为对齐。

### 2.4 Workflow 稳定性修复
- `workflow --auto` 修复为逐阶段真实执行并在失败时 fail-fast。
- 子进程入口统一为 `python -m beacon.main`。
- workflow status/gate 对 docs/beacon 与 docs/product 路径均可识别。

### 2.5 入口与兼容别名
- 新增 `beacon/__main__.py`，支持 `python -m beacon`。
- `pyproject.toml` 统一保留 `beacon` 入口；目录层继续兼容 `.ptk` / `docs/product`。

### 2.6 三层防线（继承历史规则）
- **Gate 门控**：`gate` strict 下完成边界/终态/证据/一致性/scope guard 联动校验，`scope_guard_enabled` 配置生效。
- **证据驱动**：补强 `raw-command-log`、`evidence-manifest(entries/items)`、`gate-report` 结构与 hash/一致性校验。
- **记忆体约束**：补齐统一 memory envelope（继承历史结构）；strict run 支持 `--proposal` + `--confirm A|B|C`，高风险未确认直接 Blocked，并落盘 scope memory。

### 2.7 `auto_test` UI 防假通过强校验（继承历史规则）
- 新增统一 UI guard 判定（`beacon/commands/auto_test.py`，继承历史规则）：
  - `expectation=success` 且 `origin != target` => `failed`（防错页误通过）
  - `expectation=error` 且重定向/错误关键词命中 => `passed`
  - `origin` 不可判定 => `blocked`（`ui_origin_target_unknown`）
  - strict 下无显式 UI assertion => `blocked`（`ui_assertion_missing_strict`）
- `auto-test create` 新增参数：
  - `--expectation`
  - `--target-url`
  - `--origin-url`
  - `--snapshot-file` / `--snapshot-text`
  - `--ui-assertion`（可重复）
  - `--strict-ui-assertion`
- 结果写入 `.beacon/auto-test-status.json` 的 `ui_guard` 字段，包含：
  - `status`
  - `reason_code`
  - `origin_vs_target`
  - `detail`
  - `assertion_count`

## 3. xfail 消灭与自动化补测

> 本轮兼容用例已去除 xfail，按真实通过标准执行。

### 3.1 新增自动化兼容测试文件
- `tests/test_compat_cli_flat_commands.py`
- `tests/test_compat_behavior_contract.py`
- `tests/test_compat_workflow_paths.py`
- `tests/test_compat_gate_evidence.py`
- `tests/test_compat_regression_docs_examples.py`
- `tests/test_auto_test_ui_false_positive_guard.py`
- `tests/test_memory_envelope.py`
- `tests/test_run_strict_scope_memory.py`
- `tests/test_gate_evidence_strict_contract.py`

### 3.2 结果
- 兼容专项（含 UI 防假通过）：`35 passed`
- 全量测试：`141 passed`

### 3.3 历史 workflow 补充文档
- 新增：`docs/beacon/archive/v1.0.0/execution/ptk-workflow-bootstrap.md`
- 记录历史 run/report 实跑结果（run_id：`run-20260302T081044842Z-9dd5`）及三层防线对齐状态。

## 4. 执行命令（可直接复现）

### 4.1 兼容专项回归
```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
python3 -m pytest -q \
  tests/test_compat_cli_flat_commands.py \
  tests/test_compat_behavior_contract.py \
  tests/test_compat_workflow_paths.py \
  tests/test_compat_gate_evidence.py \
  tests/test_compat_regression_docs_examples.py \
  tests/test_auto_test_ui_false_positive_guard.py
```

### 4.2 全量回归
```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
python3 -m pytest -q
```

### 4.3 历史团队工作流（本次执行方式）
```bash
cd /Users/apple/Developer/Personal/my_skill

# 1) 启动 team
./product-toolkit/scripts/team_runtime.sh start \
  --project-root beacon \
  --team beacon-v1-delivery \
  --runtime file \
  --workers 5 \
  --task "beacon v1.0.0 功能开发与 xfail 清零交付"

# 2) 审查 Gate（spec -> quality）
./product-toolkit/scripts/review_gate.sh --project-root beacon --team beacon-v1-delivery init
./product-toolkit/scripts/review_gate.sh --project-root beacon --team beacon-v1-delivery spec --status pass --reviewer pm
./product-toolkit/scripts/review_gate.sh --project-root beacon --team beacon-v1-delivery quality --status pass --reviewer qa
./product-toolkit/scripts/review_gate.sh --project-root beacon --team beacon-v1-delivery evaluate --critical-open 0 --high-open 0

# 3) 推进到 terminal
./product-toolkit/scripts/team_runtime.sh resume --project-root beacon --team beacon-v1-delivery
./product-toolkit/scripts/team_runtime.sh resume --project-root beacon --team beacon-v1-delivery
./product-toolkit/scripts/team_runtime.sh resume --project-root beacon --team beacon-v1-delivery
./product-toolkit/scripts/team_runtime.sh resume --project-root beacon --team beacon-v1-delivery

# 4) 查看最终状态
./product-toolkit/scripts/team_runtime.sh status --project-root beacon --team beacon-v1-delivery
```

## 5. 最终验收

- Team Runtime：`terminal / Pass`
- 兼容测试：`35 passed`
- 全量测试：`141 passed`
- Beacon v1.0.0：满足完整交付条件。
