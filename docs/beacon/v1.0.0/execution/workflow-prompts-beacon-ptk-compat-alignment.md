# Workflow Prompts: Beacon↔PTK 兼容改造执行命令（按 PTK 工作流）

> 项目根目录：`/Users/apple/Developer/Personal/my_skill/beacon`

---

## 1) Think（需求澄清）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
./beacon-cli think start "Beacon 与 PTK 功能对齐改造"
./beacon-cli think confirm "Beacon 是 PTK 的重构版本"
./beacon-cli think question "是否要求 ptk 二进制别名安装后可直接使用?" --priority high --blocking
./beacon-cli think summarize
```

---

## 2) User Story（用户故事）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
./beacon-cli user-story create "Beacon PTK 兼容改造" \
  --output docs/beacon/v1.0.0/user-story/beacon-ptk-compat-alignment.md
```

---

## 3) PRD（需求文档）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
./beacon-cli prd create "Beacon PTK 兼容改造" \
  --output docs/beacon/v1.0.0/prd/beacon-ptk-compat-alignment.md
```

---

## 4) Test Case（测试用例）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
./beacon-cli test-case create "Beacon PTK 兼容改造" --type all \
  --output docs/beacon/v1.0.0/qa/test-cases/beacon-ptk-compat-alignment.md
```

---

## 5) Gate（门控检查）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
./beacon-cli gate check think --json
./beacon-cli gate check user-story --json
./beacon-cli gate check prd --json
./beacon-cli gate check test-case --json
```

> 兼容目标（改造后）应支持：
>
> ```bash
> ./beacon-cli gate think --json
> ```

---

## 6) 回归测试（建议命令）

### 6.1 当前测试集

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
python3 -m pytest -q tests/test_beacon.py tests/test_gate_team.py
```

### 6.2 兼容补测（新增后）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
python3 -m pytest -q \
  tests/test_compat_cli_flat_commands.py \
  tests/test_compat_behavior_contract.py \
  tests/test_compat_workflow_paths.py \
  tests/test_compat_gate_evidence.py \
  tests/test_compat_regression_docs_examples.py
```

---

## 7) 目标验收命令集（PTK 核心 10 命令）

> 改造完成后，以下命令均应通过：

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
./beacon-cli status --board
./beacon-cli run workflow --mode strict
./beacon-cli debug watch
./beacon-cli report --human latest
./beacon-cli feedback sync latest
./beacon-cli resume <run_id>
./beacon-cli doctor --json
./beacon-cli init --dry-run
./beacon-cli gate think --json
./beacon-cli upgrade
```

