# 调研：Beacon 工作区多项目配置与 doctor 纠错（v1.1.0）

**日期**：2026-03-12  
**范围**：多项目（workspace）+ 配置化执行 + doctor 纠错 + source_info 严格输出  
**目标**：在主目录统一管理多个 Beacon 项目，确保按配置精准路由与严格执行，避免“跑错目录/输出不清晰”。

---

## 1. 调研场景（Workspace 多项目）

### 场景 A：主目录执行，自动路由到目标项目
- **示例**：在 `/Users/apple/Developer/Personal/my_skill` 执行 `beacon prd create ...`
- **期望**：根据 workspace 配置，自动识别目标子项目（如 `my_skill/beacon`）并执行
- **痛点**：当前依赖 `cwd` 或 `--project`，容易写错目录

### 场景 B：多项目并行维护
- **示例**：同一 workspace 下有 `beacon`、`product-toolkit` 等子项目
- **期望**：支持 `--project <name|path>` 明确选择；默认项目可配置
- **痛点**：多个项目输出混在一起，缺少统一路由与严格校验

### 场景 C：CI / 自动化运行
- **示例**：脚本在固定 workspace 路径运行
- **期望**：无需依赖 cwd 变化，严格按照配置执行并产出 source_info
- **痛点**：默认策略不稳定，难以复现产物

---

## 2. 需求目标（Strict + Clear）

1. **Workspace 配置支持多项目清单**
2. **严格按配置路由执行（strict 模式）**
3. **doctor 提供配置纠错与模板生成**
4. **source_info 严格按配置输出元信息**

---

## 3. 多项目配置草案（示意）

```yaml
workspace:
  root: /Users/apple/Developer/Personal/my_skill
  projects:
    - name: beacon
      root: /Users/apple/Developer/Personal/my_skill/beacon
      default: true
      docs:
        source_root: docs/beacon
        compat_root: docs/product
        write_mode: source_only
      source_info:
        enabled: true
        output: docs/beacon/{version}/execution/source.json
        include_git: true
        fields: [repo_url, branch, commit, worktree, run_id, version, timestamp]
    - name: product-toolkit
      root: /Users/apple/Developer/Personal/my_skill/product-toolkit
      docs:
        source_root: docs/beacon
        write_mode: source_only
```

---

## 4. 路由与解析策略（优先级）

1. CLI：`--project <name|path>`
2. 环境变量：`BEACON_PROJECT`
3. cwd 匹配（最长路径匹配）
4. workspace default 项目
5. 无匹配 → **阻断执行（strict=true）**

---

## 5. doctor 纠错能力（配置治理）

### 新增建议子命令
- `beacon doctor setup-workspace` → 生成 workspace 配置模板
- `beacon doctor verify-workspace --strict` → 校验配置并阻断错误
- `beacon doctor fix-workspace` → 自动修复可确定项

### 纠错规则（示例）
- `project.root` 不存在 → 报错 + 建议修复
- `default` 多个 → 报错
- `source_root` 不在 project.root 下 → 报错
- `write_mode` 非法 → 修复为 `source_only`
- strict=true 且未解析目标项目 → **阻断**

---

## 6. 元信息（source_info）严格执行

- `source_info.enabled=false` → 不生成
- `output` 路径严格按配置
- `fields` 严格过滤（禁止额外字段）
- strict=true 且 source_info 缺失 → **阻断**

推荐写入字段：
- project_name
- project_root
- workspace_root
- version
- run_id
- git 元信息（可选）

---

## 7. UX 体验建议（执行前提示）

执行前打印清晰上下文：
```
Resolved Project: beacon
Project Root: /Users/apple/Developer/Personal/my_skill/beacon
Docs Source: docs/beacon
Write Mode: source_only
Strict Mode: true
```

---

## 8. 收敛优先级建议

**P0**
- workspace 配置结构
- 严格路由 + 阻断机制
- doctor verify-workspace

**P1**
- source_info 自动生成
- 执行配置快照（execution/config.json）

**P2**
- 交互式选择 / LLM 辅助配置

---

## 9. 结论

Workspace 多项目管理的关键是：
**配置即契约、路由即治理、执行即证据**。  
通过 doctor 纠错 + strict 执行，可显著降低“输出不清晰/跑错目录”的风险。

---

**落盘位置**：`docs/beacon/archive/v1.1.0/research/`
