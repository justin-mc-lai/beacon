# Beacon v1.0.0 对齐 PTK `auto_test` UI 防假通过强校验

## 1. 核验结论（2026-03-02）

已核验 PTK 项目 `auto_test` 的 UI 防假通过加固，并将核心能力补齐到 Beacon v1.0.0。

## 2. PTK 核验来源

在以下文件中确认了本轮 PTK 侧新增/约束：

- `product-toolkit/scripts/auto_test.sh`
  - 新增 `evaluate_ui_assertion`（基于 expectation + origin/target + snapshot 关键词）
  - UI 分支不再“打开页面即通过”
- `product-toolkit/docs/implementation/ptk-auto-test-ui-false-positive-regression-suite-20260302.md`
- `product-toolkit/docs/product/v3.8.1/qa/test-cases/ptk-auto-test-ui-false-positive-guard.md`
- `product-toolkit/docs/qa-standards-playbook.md`

## 3. Beacon v1.0.0 改造点

代码文件：`beacon/commands/auto_test.py`

### 3.1 新增 UI guard 判定函数

- `evaluate_ui_false_positive_guard(...)`
- 核心判定：
  1. `expectation=success` + `origin!=target` => `failed`
  2. `expectation=error` + redirect/错误关键词 => `passed`
  3. `origin` 缺失 => `blocked`
  4. strict 且无断言 => `blocked`

### 3.2 `auto-test create` 参数扩展

- `--expectation`
- `--target-url`
- `--origin-url`
- `--snapshot-file`
- `--snapshot-text`
- `--ui-assertion`（可重复）
- `--strict-ui-assertion`

### 3.3 状态产物增强

`.beacon/auto-test-status.json` 新增 `ui_guard`：

- `status`
- `reason_code`
- `detail`
- `origin_vs_target`
- `assertion_count`

## 4. 对齐的 reason codes（Beacon）

- `ui_expectation_success_matched`
- `ui_expectation_success_mismatch`
- `ui_expectation_error_redirect`
- `ui_expectation_error_keyword`
- `ui_expectation_error_not_observed`
- `ui_origin_target_unknown`
- `ui_assertion_missing_strict`
- `ui_expectation_unknown_strict`
- `ui_expectation_unknown_skipped`
- `ui_expectation_invalid`

## 5. 自动化补测（已落地）

新增测试文件：`tests/test_auto_test_ui_false_positive_guard.py`

覆盖点：

1. success 场景 origin/target 不一致 -> fail
2. error 场景重定向登录 -> pass
3. strict 下无断言 -> blocked
4. origin 缺失 -> blocked
5. CLI `auto-test create` 产出状态与 reason code

## 6. 执行命令（PTK workflow 风格）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon

# 1) UI 防假通过专项
python3 -m pytest -q tests/test_auto_test_ui_false_positive_guard.py

# 2) 兼容专项（含 UI guard）
python3 -m pytest -q \
  tests/test_compat_cli_flat_commands.py \
  tests/test_compat_behavior_contract.py \
  tests/test_compat_workflow_paths.py \
  tests/test_compat_gate_evidence.py \
  tests/test_compat_regression_docs_examples.py \
  tests/test_auto_test_ui_false_positive_guard.py

# 3) 全量回归
python3 -m pytest -q
```

## 7. 快速手动验证命令

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon

beacon auto-test create ui \
  --project . \
  --expectation success \
  --target-url /admin/dashboard \
  --origin-url /admin/login \
  --ui-assertion "url_contains:/admin/dashboard"

beacon auto-test status --project . --json
```

预期：`status=failed`，`reason_code=ui_expectation_success_mismatch`。
