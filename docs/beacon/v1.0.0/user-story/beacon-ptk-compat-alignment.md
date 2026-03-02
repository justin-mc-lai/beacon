# User Story: Beacon 与 PTK 功能对齐改造

**版本**: v1.0.0  
**状态**: Draft  
**目标**: 让 Beacon 成为 PTK 的无缝重构版本（命令语法、行为、产物、状态一致）

---

## US-COMP-001: CLI 语法兼容

**作为** PTK 现有用户  
**我希望** 继续使用原有 PTK 命令语法  
**以便** 无迁移成本切换到 Beacon

### AC

| AC ID | 验收标准 |
|---|---|
| AC-001 | `beacon status --board` 可直接执行（无需 `show-status` 子命令） |
| AC-002 | `beacon doctor --json` 可直接执行（无需 `diagnose` 子命令） |
| AC-003 | `beacon report --human latest` / `--machine latest` 可直接执行 |
| AC-004 | `beacon debug watch` / `beacon feedback sync latest` / `beacon resume <run_id>` 与 PTK 语法一致 |
| AC-005 | 支持 `beacon gate think --json` 与 `beacon gate check think --json` 双语法 |
| AC-006 | 支持 `beacon work` 作为 `workflow` 别名 |
| AC-007 | 安装后同时提供 `beacon` 与 `ptk` 两个入口 |

---

## US-COMP-002: run/status/report/debug/resume/feedback 行为兼容

**作为** 研发与 QA  
**我希望** Beacon 的核心命令行为与 PTK 对齐  
**以便** 现有自动化脚本无需改写

### AC

| AC ID | 验收标准 |
|---|---|
| AC-001 | `run` 生成 run_id、events.jsonl、state.json，返回码遵循 completed=0/blocked=2/failed=1 |
| AC-002 | `status` 支持 board 与 JSON 两种输出 |
| AC-003 | `report` 生成 human summary 与 machine JSON |
| AC-004 | `debug watch` 支持 tail/follow/poll/idle_exit |
| AC-005 | `resume` 可按 run_id 读取完整运行状态 |
| AC-006 | `feedback sync` 会写入 requirement-feedback 产物 |

---

## US-COMP-003: init/doctor/upgrade 行为兼容

**作为** 项目维护者  
**我希望** 初始化、诊断与升级流程和 PTK 一致  
**以便** 新老项目都能统一治理

### AC

| AC ID | 验收标准 |
|---|---|
| AC-001 | `init --apply` 真实创建 docs/CLAUDE/AGENTS 与 init-report |
| AC-002 | `init --dry-run` 只输出计划，不落盘 |
| AC-003 | `doctor --json` 输出结构化 payload，并按结果返回正确 exit code |
| AC-004 | `doctor` 支持 external project 检查（project-root） |
| AC-005 | 保留 `upgrade` 兼容入口（deprecated 提示 + 可用迁移路径） |

---

## US-COMP-004: workflow 端到端兼容

**作为** 产品经理  
**我希望** workflow 主链可稳定串联 think→user-story→prd→test-case  
**以便** 一条命令完成核心产物链

### AC

| AC ID | 验收标准 |
|---|---|
| AC-001 | `workflow start <feature> --auto` 真正执行所有阶段，不允许“假成功” |
| AC-002 | 子阶段失败时 workflow 必须失败并返回非 0 |
| AC-003 | 支持 `--skip` / `--version` / `--project` |
| AC-004 | `workflow status` 能正确识别已生成产物 |
| AC-005 | `workflow gate` 与 `gate` 结果一致 |

---

## US-COMP-005: 目录与状态兼容（双读双写）

**作为** 运维与审计人员  
**我希望** Beacon 与 PTK 的目录/状态格式可兼容  
**以便** 历史数据可复用

### AC

| AC ID | 验收标准 |
|---|---|
| AC-001 | 文档主目录统一策略：`docs/beacon/{version}` 主写，`docs/product/{version}` 兼容镜像（或反向，需全局一致） |
| AC-002 | `latest` 与显式版本（如 `v1.0.0`）解析策略一致 |
| AC-003 | `.beacon/` 与 `.ptk/` 具备兼容读取能力 |
| AC-004 | Gate/Doctor/Workflow 对路径解析一致，不出现“写 A 读 B” |

---

## US-COMP-006: Gate 与证据链兼容

**作为** 交付负责人  
**我希望** Gate 规则、reason codes、证据链与 PTK 约束一致  
**以便** 交付判定可信可审计

### AC

| AC ID | 验收标准 |
|---|---|
| AC-001 | Gate 检查路径使用统一版本目录（不允许遗漏 `docs/product`/`docs/beacon` 前缀） |
| AC-002 | Gate 输出包含 stage/mode/status/issues/blocked_count |
| AC-003 | `--force` 产生风险日志 |
| AC-004 | evidence manifest hash 校验、raw-command-log、gate-report 检查可复现 |
| AC-005 | reason codes 与文档宣称保持一致 |

---

## US-COMP-007: 文档与实现一致性

**作为** 使用者  
**我希望** README / SKILL / CLI --help 与真实行为一致  
**以便** 降低误导成本

### AC

| AC ID | 验收标准 |
|---|---|
| AC-001 | README 示例命令可直接执行 |
| AC-002 | SKILL 中宣称的别名（如 `beacon work`、`ptk ...`）可执行 |
| AC-003 | `--json` 参数名、命令参数名与实际输出一致 |
| AC-004 | 版本信息（CLI/文档/skill）一致 |

