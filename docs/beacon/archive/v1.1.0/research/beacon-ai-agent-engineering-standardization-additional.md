# 调研补充：Beacon AI Agent 工程化标准化（v1.1.0）

**日期**：2026-03-12  
**范围**：在既有“实现目录配置 / Git 版本对齐 / agent.md 注入”之外的工程化标准化补充  
**目标**：让 Beacon 在 AI Agent 项目中“稳定、可复现、可审计、可协作”。

---

## 1. 核心问题
除了已提出项（实现目录配置、Git 版本对齐、agent.md/claude.md 注入），还需要哪些工程化机制，才能确保 Beacon 的 AI Agent 使用可标准化落地？

---

## 2. 关键补充方向

### 2.1 配置治理（Config Governance）
- **全局配置注册中心**（workspace 统一管理）
- **path lint**：强制输出目录必须落在 source_root
- **execution/config.json**：每次运行生成配置快照

### 2.2 版本可信（Version Integrity）
- **git-alignment.json**：版本对齐校验报告
- **version gate**：执行前必须通过版本校验
- **evidence checksum**：证据文件清单 + hash

### 2.3 CI 标准化（Pipeline Gate）
- `beacon doctor verify-config --strict`
- `beacon gate check --version <version>`
- `execution/terminal.json` schema 强制校验

### 2.4 Agent 标准化（Lifecycle Control）
- `.beacon/agent/` 标准 Prompt 模板库
- **agent preflight**：执行前自动校验配置/版本
- **md 注入机制**：强制生命周期说明进入 agent.md/claude.md

### 2.5 审计与追踪（Auditability）
- `execution/audit.jsonl`：记录关键执行事件
- `execution/evidence-manifest.json`：证据清单
- `execution/source.json`：来源信息

---

## 3. Idea Pool（补充清单）

1. 全局配置注册中心（workspace root）
2. path lint（强制目录落在 source_root）
3. execution/config.json（配置快照）
4. git-alignment.json（版本对齐报告）
5. evidence checksum（证据 hash）
6. CI Gate（verify-config + gate check）
7. execution/terminal.json schema 校验
8. agent preflight（执行前校验）
9. prompt 模板库（.beacon/agent/）
10. audit.jsonl（执行审计日志）

---

## 4. 收敛优先级（建议）

**P0**
- config snapshot + path lint
- git 对齐 + version gate
- agent preflight + md 注入

**P1**
- evidence checksum + manifest
- CI Gate 标准化

**P2**
- audit.jsonl + 配置签名
- prompt 模板库标准化

---

## 5. 结论

为保证 Beacon 在 AI Agent 项目中“可复现、可审计、可协作”，除了已提出的实现目录、版本对齐、初始化注入，还需补齐：

> **配置治理 + 版本可信 + CI Gate + Agent Preflight + 证据校验 + 审计日志**。

---

**落盘位置**：`docs/beacon/archive/v1.1.0/research/`
