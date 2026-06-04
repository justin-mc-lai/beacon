# Test Cases: Beacon 命令口径统一补测方案（沿用原文件名）

**版本**: v1.0.0  
**来源**: `user-story/beacon-ptk-compat-alignment.md`  
**用途**: 兼容改造完成后的补测与回归基线

---

## 1. 补测范围与分组

- A 组：命令语法兼容（CLI Grammar）
- B 组：行为契约兼容（Behavior Contract）
- C 组：工作流与路径兼容（Workflow + Path）
- D 组：Gate 与证据链兼容（Gate + Evidence）
- E 组：负向与回归（Negative + Regression）

**建议总数**: 52 条（可按 P0/P1 分批执行）

---

## 2. A 组：命令语法兼容（15 条）

| TC ID | 级别 | 用例 | 期望 |
|---|---|---|---|
| TC-A-001 | P0 | `beacon status --board` | exit=0，输出 board 字段 |
| TC-A-002 | P0 | `beacon doctor --json` | exit 与结果一致，输出 JSON |
| TC-A-003 | P0 | `beacon report --human latest` | exit=0，输出 human summary |
| TC-A-004 | P0 | `beacon report --machine latest` | exit=0，输出 machine JSON |
| TC-A-005 | P0 | `beacon debug watch` | exit=0，能 tail 最近事件 |
| TC-A-006 | P0 | `beacon feedback sync latest` | 写入 feedback 产物 |
| TC-A-007 | P0 | `beacon resume <run_id>` | 正确回显 run state |
| TC-A-008 | P0 | `beacon init --dry-run` | 不落盘，仅输出计划 |
| TC-A-009 | P0 | `beacon init --apply` | 正常落盘并写 init-report |
| TC-A-010 | P0 | `beacon gate think --json` | 可执行，结构化输出 |
| TC-A-011 | P0 | `beacon gate check think --json` | 与 TC-A-010 等价 |
| TC-A-012 | P1 | `beacon work <feature>` | 等价 workflow 入口 |
| TC-A-013 | P0 | `beacon status --board` | 状态面板输出完整 |
| TC-A-014 | P0 | `beacon doctor --json` | JSON 输出结构正确 |
| TC-A-015 | P1 | `beacon --version` | 版本输出符合约定 |

---

## 3. B 组：行为契约兼容（12 条）

| TC ID | 级别 | 用例 | 期望 |
|---|---|---|---|
| TC-B-001 | P0 | `run workflow --mode normal` | 生成 run_id/events/state |
| TC-B-002 | P0 | `run workflow --mode dry-run` | status=completed, exit=0 |
| TC-B-003 | P0 | `run workflow --mode strict` + 缺少前置 | status=blocked, exit=2 |
| TC-B-004 | P0 | `run workflow --mode replay` + 无历史 run | 明确报错，exit=2 |
| TC-B-005 | P0 | report human 产物 | 生成 summary.md |
| TC-B-006 | P0 | report machine 产物 | 生成 summary.json |
| TC-B-007 | P0 | status JSON 模式 | 字段含 team/gate/bridge/test |
| TC-B-008 | P1 | debug follow | 支持 idle_exit 自动退出 |
| TC-B-009 | P0 | feedback sync | 写入 requirement-feedback 文件 |
| TC-B-010 | P0 | resume 非法 run_id | 友好报错，exit=2 |
| TC-B-011 | P0 | doctor BLOCKED 场景 | exit=2，JSON overall=BLOCKED |
| TC-B-012 | P1 | doctor WARN 场景 | exit=0，JSON overall=WARN |

---

## 4. C 组：工作流与路径兼容（10 条）

| TC ID | 级别 | 用例 | 期望 |
|---|---|---|---|
| TC-C-001 | P0 | `workflow start <f> --auto` | 真实执行各阶段，不可假成功 |
| TC-C-002 | P0 | workflow 某阶段故障注入 | workflow 失败并返回非 0 |
| TC-C-003 | P0 | `workflow status` | 能识别已有 user-story/prd/test-case |
| TC-C-004 | P0 | `workflow gate` | 与 `gate` 判定一致 |
| TC-C-005 | P0 | docs 主写路径检查 | 产物进入约定主目录 |
| TC-C-006 | P0 | docs 兼容镜像路径检查 | 兼容目录可读取或镜像成功 |
| TC-C-007 | P0 | version=latest | 路径解析一致 |
| TC-C-008 | P0 | version=v1.0.0 | 路径解析一致 |
| TC-C-009 | P1 | `.beacon` 读取 | 新运行数据可读 |
| TC-C-010 | P1 | `.ptk` 回退读取 | 历史数据可读 |

---

## 5. D 组：Gate 与证据链兼容（9 条）

| TC ID | 级别 | 用例 | 期望 |
|---|---|---|---|
| TC-D-001 | P0 | 缺少 boundaries.md | reason_code=boundaries_missing |
| TC-D-002 | P0 | terminal schema 错误 | reason_code=terminal_schema_invalid |
| TC-D-003 | P0 | evidence-manifest 缺失 | reason_code=evidence_sha256_manifest_missing |
| TC-D-004 | P0 | manifest hash 不匹配 | reason_code=evidence_sha256_manifest_mismatch |
| TC-D-005 | P0 | raw-command-log 缺失 | reason_code=raw_command_log_missing |
| TC-D-006 | P0 | strict + scope violation | status=Blocked |
| TC-D-007 | P1 | `--force` | 结果可通过并写 risks 日志 |
| TC-D-008 | P1 | `--json` 输出 | 包含 stage/mode/status/issues/blocked_count |
| TC-D-009 | P1 | reason codes 列表完整性 | 与文档清单一致 |

---

## 6. E 组：负向与回归（6 条）

| TC ID | 级别 | 用例 | 期望 |
|---|---|---|---|
| TC-E-001 | P0 | 未知命令 | 明确错误与帮助提示 |
| TC-E-002 | P0 | 参数缺失 | 明确报错，exit=2 |
| TC-E-003 | P1 | 中英文路径/特性名 | 正常写文件，不乱码 |
| TC-E-004 | P1 | 并发两次 run | run_id 不冲突 |
| TC-E-005 | P1 | 回归：旧二级子命令 | 仍可用（向后兼容） |
| TC-E-006 | P1 | 回归：README 示例命令 | 全部可执行 |

---

## 7. 建议补充的自动化测试文件

- `tests/test_compat_cli_flat_commands.py`
- `tests/test_compat_behavior_contract.py`
- `tests/test_compat_workflow_paths.py`
- `tests/test_compat_gate_evidence.py`
- `tests/test_compat_regression_docs_examples.py`

---

## 8. 推荐执行顺序（Beacon 统一命令风格）

1. 先跑 P0 的 A/B/C/D 用例。
2. P0 全绿后再跑 E 组与 P1。
3. 最后跑全量回归与 README 示例验证。

