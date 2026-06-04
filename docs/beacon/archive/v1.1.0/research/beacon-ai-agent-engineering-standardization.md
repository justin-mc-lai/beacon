# 调研：Beacon AI Agent 工程化标准化落地（v1.1.0）

**日期**：2026-03-12  
**范围**：实现目录配置 / Git 版本对齐 / Agent 初始化注入 / 端到端工程化标准化  
**目标**：确保 Beacon 迭代版本与工程实现严格一致，AI Agent 在项目内可完整运用 Beacon 全生命周期能力。

---

## 1. 场景补充（实现目录 & Git 版本对齐）

### 场景 A：需求版本与实现分离导致漂移
- Beacon 版本：`v1.1.0`
- 工程实现：分支/Tag 未对齐（例如 `feature/foo`）
- 风险：交付证据与实际实现不一致，审计不可追溯

### 场景 B：多模块项目的“实现目录”不明确
- Beacon 产物在 docs/beacon
- 实际代码目录可能为 `apps/*` 或 `src/*`
- 风险：AI Agent 无法确定“工程实现范围”，执行不稳定

---

## 2. 需求目标（严格对齐）

1. **实现目录配置（implementation root）**
2. **Git 版本必须与 Beacon 版本一致**
3. **Agent 初始化文件注入 Beacon 生命周期说明**
4. **工程化标准化路径与校验**

---

## 3. 实现目录配置（建议）

```yaml
beacon:
  implementation:
    root: /abs/path/to/project
    include_paths:
      - src
      - apps/web
      - services/api
    exclude_paths:
      - node_modules
      - dist
      - .beacon
```

用途：
- AI Agent 在执行时明确“实现范围”
- auto-test / evidence / verify 时可限定目录
- doctor 可验证目录有效性

---

## 4. Git 版本严格对齐（建议）

### 4.1 配置字段（示意）
```yaml
beacon:
  git:
    version_policy: strict
    version_ref: v1.1.0
    enforce_branch_prefix: beacon/
    allowed_refs: [tag, branch]
```

### 4.2 校验逻辑（doctor + workflow preflight）
- 当前 Git HEAD 必须匹配 `version_ref`
- branch/tag 必须包含 Beacon 版本号
- 不匹配 → 阻断执行（strict=true）

### 4.3 可选扩展
- 自动写入 `execution/source.json` 的 git 元信息
- 生成 `execution/git-alignment.json` 校验报告

---

## 5. Agent 初始化文件注入（Claude.md / agent.md）

### 5.1 需求目标
- 项目根目录的 `claude.md` / `agent.md` 自动追加 Beacon 生命周期使用说明
- 确保 LLM 在项目内默认遵循 Beacon 工作流

### 5.2 建议命令
- `beacon doctor setup-agent-md`
- `beacon doctor verify-agent-md`

### 5.3 注入内容（示意）
```md
## Beacon Lifecycle (Required)
- 使用 Beacon 进行需求 → 用户故事 → PRD → 测试用例 的闭环
- 输出文档必须落在 docs/beacon/<version>/
- 执行前需通过 beacon gate
- 运行产物需包含 execution/source.json

### Recommended Commands
- beacon workflow start "<feature>" --version <version> --project <path>
- beacon gate check --version <version>
- beacon doctor verify-config --strict
```

---

## 6. 工程化标准化补充方向

### 6.1 强制规范
- `beacon config` 作为唯一入口（禁止隐式 cwd）
- strict 模式强制开启
- source_info 必须存在并严格写入

### 6.2 CI Gate 化
- CI 检查：
  - `beacon doctor verify-config --strict`
  - `beacon gate check --version <version>`
  - `execution/terminal.json` schema 校验

### 6.3 运行证据标准化
- `execution/config.json`：每次执行配置快照
- `execution/source.json`：来源与 git 信息
- `execution/git-alignment.json`：版本对齐报告

### 6.4 Agent 提示词模板化
- 在 `.beacon/agent/` 下存放标准 prompt
- doctor 支持一键生成

### 6.5 版本发布标准
- Beacon 版本发布必须包含：
  - PRD / User-story / Test-case
  - gate 通过
  - execution/terminal.json

---

## 7. 收敛优先级（建议）

**P0**
- 实现目录配置 + doctor 校验
- Git 版本对齐校验（strict）
- agent.md / claude.md 注入

**P1**
- CI Gate 标准化
- execution/config.json 快照

**P2**
- Prompt 模板库
- 多项目标准化脚手架

---

## 8. 结论

要实现 Beacon 在 AI Agent 项目中的工程化落地，必须同时满足：
1) **实现目录可配置**（避免执行范围不清）
2) **Git 版本严格对齐 Beacon 版本**（避免证据失真）
3) **Agent 初始化文件强制注入生命周期说明**（保证 LLM 默认遵循 Beacon 规范）
4) **CI + Gate 标准化**（让执行结果可验证、可审计）

---

**落盘位置**：`docs/beacon/archive/v1.1.0/research/`
