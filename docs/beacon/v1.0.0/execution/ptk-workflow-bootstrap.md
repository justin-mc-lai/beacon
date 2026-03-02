# Beacon v1.0.0：PTK Workflow 补充记录（三层防线）

## 1) 执行目的

按 PTK 工作流先补齐 Beacon v1.0.0 文档，并对齐三层防线：

1. Gate 门控  
2. 证据驱动  
3. 记忆体约束

## 2) 本次执行命令（已实跑）

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon

# PTK workflow dry-run（强制将 PTK root 指向 beacon 项目）
PTK_ROOT_OVERRIDE=$(pwd) python3 ../product-toolkit/scripts/ptk_cli.py --version v1.0.0 run workflow --mode dry-run

# PTK summary（human + machine）
PTK_ROOT_OVERRIDE=$(pwd) python3 ../product-toolkit/scripts/ptk_cli.py --version v1.0.0 report --human latest
PTK_ROOT_OVERRIDE=$(pwd) python3 ../product-toolkit/scripts/ptk_cli.py --version v1.0.0 report --machine latest
```

## 3) 执行结果快照

- PTK run_id: `run-20260302T081044842Z-9dd5`
- route: `workflow`
- mode: `dry-run`
- status: `completed`
- artifacts:
  - `.ptk/runs/run-20260302T081044842Z-9dd5/events.jsonl`
  - `.ptk/memory/scope/deviations.json`
  - `.ptk/memory/scope/confirmations.json`

## 4) 三层防线对齐状态（v1.0.0）

### A. Gate 门控

- `beacon gate` 严格模式对齐 `Pass/Blocked` 终态语义。
- 支持并覆盖 PTK 常用 reason code 校验（边界、终态、证据、一致性、scope guard）。
- `scope_guard_enabled` 配置开关生效（`gate-config.json`）。

### B. 证据驱动

- 新增强校验：
  - `raw_command_log_invalid`（JSONL/空文件无效）
  - `evidence_sha256_manifest_invalid/incomplete/mismatch`
  - `gate_consistency_report_invalid/mismatch/conflict`
- `evidence-manifest` 同时兼容 `entries` 与 `items`。
- 终态 traceability 补充 `ac_tc_mapping_gap` / `terminal_evidence_missing` 路径校验入口。

### C. 记忆体约束

- 新增 PTK 风格 memory envelope：
  - `.beacon/memory/project-insights.json`
  - `.beacon/memory/decisions.json`
  - `.beacon/memory/vocabulary.json`
- `remember` 支持 envelope 元数据：`type/source_session_id/source/evidence_ref/confidence/tags`
- `recall memory` 支持按 query/type 检索。
- `run workflow --mode strict` 支持：
  - `--proposal`
  - `--confirm A|B|C`
  - 高风险 proposal 未确认即 `Blocked(awaiting_human_confirmation)`
  - scope memory 落盘：`.beacon/memory/scope/{deviations,confirmations}.json`

## 5) 自动化补测（本次新增）

- `tests/test_memory_envelope.py`
- `tests/test_run_strict_scope_memory.py`
- `tests/test_gate_evidence_strict_contract.py`

执行结果：

```bash
cd /Users/apple/Developer/Personal/my_skill/beacon
python3 -m pytest -q
```

- 结果：`129 passed`

