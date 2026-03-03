# PRD: Beacon 命令口径统一与历史目录兼容改造（沿用原文件名）

**版本**: v1.0.0  
**状态**: Draft  
**对应用户故事**: `user-story/beacon-ptk-compat-alignment.md`

---

## 1. 背景

Beacon 源于历史 PTK 重构版本；当前需要把命令口径统一到 Beacon，并把历史 PTK 兼容收敛到目录层，主要问题为：

1. 历史命令迁移过程中出现层级不一致（如 `doctor diagnose` 与扁平入口并存）。
2. 核心命令（run/status/report/init/doctor）存在占位实现或输出契约不一致。
3. workflow auto 有“阶段失败但仍显示成功”的风险。
4. 文档/状态/Gate 路径策略不一致，出现写入目录与读取目录不匹配。

本 PRD 的目标是把 Beacon 收敛到“命令统一、目录兼容”的工程标准。

---

## 2. 目标与非目标

### 2.1 目标

- **G1**: Beacon 命令入口统一率 100%。
- **G2**: 核心行为（run/report/status/doctor/gate/init）契约对齐。
- **G3**: 目录与状态双兼容（`.beacon`/`.ptk`，`docs/beacon`/`docs/product`）。
- **G4**: 补齐回归用例，确保后续版本不回退。

### 2.2 非目标

- 不在本次改造中引入新业务功能。
- 不在本次改造中重构所有分析类子命令模板内容。

---

## 3. 完整改造点（兼容清单）

> 优先级定义：P0=必须先完成；P1=高优先；P2=增强。

| ID | 优先级 | 改造点 | 目标行为 |
|---|---|---|---|
| COMP-001 | P0 | 根命令统一层 | 统一 Beacon 扁平语法：`beacon status/doctor/report/debug/feedback/resume/init/gate/run/upgrade` |
| COMP-002 | P0 | doctor 命令扁平化 | `beacon doctor --json` 可直接执行，并保留 `doctor diagnose` 兼容 |
| COMP-003 | P0 | status 命令扁平化 | `beacon status --board` 可直接执行，并保留 `status show-status` |
| COMP-004 | P0 | report 命令扁平化 | `beacon report --human latest` / `--machine latest` |
| COMP-005 | P0 | init 命令扁平化 | `beacon init --apply|--dry-run` 与 Beacon 契约一致 |
| COMP-006 | P0 | resume 命令扁平化 | `beacon resume <run_id>` 直接读取 run state |
| COMP-007 | P0 | gate 双语法兼容 | 同时支持 `beacon gate think --json` 与 `beacon gate check think --json` |
| COMP-008 | P0 | run 契约对齐 | `run` 生成 run_id/events/state，且 exit code 满足 Beacon 契约 |
| COMP-009 | P0 | report 契约对齐 | 生成 human summary + machine summary，并写 execution 目录 |
| COMP-010 | P0 | doctor 契约对齐 | JSON 结构统一，PASS/WARN/BLOCKED/UPGRADE 与 exit code 一致 |
| COMP-011 | P0 | init 落盘能力 | `--apply` 真正创建基础目录与报告；`--dry-run` 不落盘 |
| COMP-012 | P0 | workflow auto 真实执行 | 修复子命令执行路径与 returncode 处理，禁止“假成功” |
| COMP-013 | P0 | workflow 错误传播 | 任一阶段失败，workflow 必须非 0 退出并输出失败阶段 |
| COMP-014 | P0 | 路径策略统一 | 明确主写路径与兼容镜像策略，所有命令统一实现 |
| COMP-015 | P0 | version 解析统一 | `latest`、`vX.Y.Z`、默认版本行为一致 |
| COMP-016 | P0 | Gate 路径修复 | Gate 检查路径与文档产物路径一致 |
| COMP-017 | P0 | `.ptk` 兼容 | 读 `.beacon` 优先，回退 `.ptk`；必要时双写或可配置镜像 |
| COMP-018 | P0 | 控制台入口统一 | `pyproject` 仅保留 `beacon` console script（`ptk` 入口下线） |
| COMP-019 | P1 | `beacon work` 别名 | `beacon work` 等价 `beacon workflow start` |
| COMP-020 | P1 | route alias 对齐 | `auto_test`/`auto-test`，`ralph_bridge`/`ralph-bridge` 对齐 |
| COMP-021 | P1 | `--version` 行为统一 | 支持全局版本输出和产品版本参数，避免语义冲突 |
| COMP-022 | P1 | README/Skill 对齐 | README、SKILL、--help 与真实命令一一对应 |
| COMP-023 | P1 | 升级链路兼容 | 保留 `upgrade` deprecated 入口，提示并转发至 doctor upgrade 逻辑 |
| COMP-024 | P1 | 证据链对齐 | raw log / evidence manifest / gate report 保持同级别可追溯 |
| COMP-025 | P2 | 数据迁移工具 | 提供 `.ptk -> .beacon` 显式迁移命令（可选） |

---

## 4. 关键实现策略

### 4.1 命令兼容层（P0）

- 在 `beacon.main` 统一 Beacon 风格扁平命令分发：
  - 若输入 `beacon doctor --json`，直接走 doctor handler（无需 `diagnose`）。
  - 若输入 `beacon gate think`，自动映射到 `gate check think`。
- 保留当前二级子命令，以减少破坏性。

### 4.2 行为复用（P0）

- 核心建议：继承历史成熟逻辑为共享模块或兼容适配层，避免重复造轮子。
- `run/report/status/doctor/init/gate` 优先按 Beacon 结果契约拉齐。

### 4.3 workflow 稳定性（P0）

- 修复 `python -m beacon` 执行路径问题（可改为 `python -m beacon.main` 或内部函数调用）。
- 强制检查每个 stage returncode，并在失败时中断。

### 4.4 路径与状态兼容（P0）

- 输出路径策略二选一并全局一致：
  1) 主写 `docs/beacon/{version}` + 镜像 `docs/product/{version}`；或
  2) 主写 `docs/product/{version}` + 镜像 `docs/beacon/{version}`。
- 状态目录同理：`.beacon` 为主，`.ptk` 兼容读取。

---

## 5. 交付验收标准（DoD）

1. 下列命令在 Beacon 中可直接执行且行为等价：
   - `status --board`
   - `run workflow --mode strict`
   - `debug watch`
   - `report --human latest`
   - `feedback sync latest`
   - `resume <run_id>`
   - `doctor --json`
   - `init --dry-run/--apply`
   - `gate think --json`
   - `upgrade`
2. 新增兼容回归测试全部通过。
3. README 与 SKILL 示例命令可实测通过。
4. workflow auto 不再出现“假成功”。

---

## 6. 风险与回滚

### 风险

- 兼容层与现有 Typer 子命令冲突。
- 路径双写导致产物覆盖顺序问题。
- 历史状态读写兼容可能引入脏数据。

### 回滚

- 通过 feature flag 或环境变量控制兼容层启用。
- 保留旧子命令路径，兼容失败时回退二级命令调用方式。

