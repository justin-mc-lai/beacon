# Spec Kit 多 Agent 安装机制与 Beacon / Trae 对齐说明

## 1. 背景问题

在 **Trae**（spec-kit 文档中的 key：`trae`）里，人类只能看到「一层」技能入口时，常见原因不是 Beacon「没有子技能」，而是 **Agent 产品只在仓库根读取约定目录下的 SKILL**，全局目录或未落盘的技能包 **不会出现在该项目的人类面**。

本文先还原 **GitHub Spec Kit（Specify CLI）** 如何实现多 Agent 兼容，再给 **Beacon** 的对齐方向（借鉴 ≠ 复制 `.specify/` 全流程）。

---

## 2. Spec Kit 如何实现「多 Agent + 可安装」

### 2.1 单一注册内核：`IntegrationRegistry` + `CommandRegistrar`

- **`INTEGRATION_REGISTRY`**：每种 Agent（`claude`、`codex`、`cursor-agent`、`trae`…）对应一个 **Integration** 类（见 `specify_cli/integrations/*`）。
- **`CommandRegistrar`**（`specify_cli/agents.py`）：把同一套命令模板渲染成 **各 Agent 所需的磁盘格式**（Markdown / TOML / 路径约定），写入 **项目根下该 Agent 专属目录**。
- **catalog**：`integrations/catalog.json` 列出官方支持的 integration key；文档 **`docs/reference/integrations.md`** 维护人类可读矩阵。

### 2.2 Skills 型 Agent：统一的「一命令一技能」目录规约

对 **Trae**，官方集成类 **`TraeIntegration`**（`SkillsIntegration` 子类）约定：

| 项 | 值 |
|----|-----|
| 技能根目录 | **`.trae/skills/`** |
| 单个技能路径 | **`.trae/skills/<prefix>-<name>/SKILL.md`**（Specify 侧为 `speckit-<name>`） |
| 项目规则上下文 | **`.trae/rules/project_rules.md`** |
| CLI | **不要求** Trae CLI（`requires_cli: False`） |
| 多 Agent 并存 | `multi_install_safe = True`（目录隔离） |

自 **v0.5.1** 起 Trae 集成 **默认走 skills**，独立「commands」路径被弱化：**安装逻辑就是把每条 speckit 命令落成 `.trae/skills/speckit-*/SKILL.md`**，而不是只写一个总索引。

### 2.3 人类可用的 CLI：`specify integration *`

- **`specify integration install <key>`**：向 **当前已 `specify init` 的项目** 写入该 Agent 的文件树。
- **`list` / `use` / `switch` / `upgrade` / `uninstall`**：默认 Agent、多集成并存、升级与回滚、修改文件的哈希跟踪（见集成文档）。
- **`.specify/integration.json`**：记录 `default_integration`、`installed_integrations` 等，便于 **可审计、可重复安装**。

### 2.4 小结：Speckit 「兼容多 Agent」的本质

1. **安装产物落在「项目根 + Agent 约定路径」**，而不是仅全局目录。  
2. **命令与技能一一映射到磁盘文件**，Trae 这类 **skills-only** 宿主才能枚举 UI。  
3. **显式 CLI** 管理安装/切换/升级，状态进 JSON，满足团队内 **可验证、可审计**。

---

## 3. 为何 Beacon 在 Trae「人类面无法展开子 skill」

结合上文，典型根因包括：

1. **Beacon 技能包默认存在于 Beacon 仓库的 `skills/beacon/<name>/`**，或用户 **全局 `~/.claude/skills`**；**Trae 默认只认项目内的 `.trae/skills/`**。  
2. **`skills/beacon/` 是层级包**（多子目录），若 Trae 侧 **只扫描扁平的 `<skillId>/SKILL.md`**，没有把每个 **子技能** 落成独立文件夹，则 UI **只会看到一个顶层包或什么也看不到**。  
3. **未运行「面向 Trae 的材质化」步骤**：没有像 `specify integration install trae` 那样，把「权威 SKILL」**拷贝/同步**到 `.trae/skills/beacon-*/`。

---

## 4. Beacon 借鉴后的「可交付」对齐策略（保持极简人类 CLI）

以下策略与 **`docs/beacon/global-boundaries.md`** 一致：**人类主面仍以 `beacon` 为主**；Agent 侧文件只是 **宿主可读投影**，不新增一层「Beacon 第二真相」。

### 4.1 目录契约（建议）

| 宿主 | 建议技能根（项目内） | 单技能形态 |
|------|----------------------|------------|
| **Trae** | `.trae/skills/` | `beacon-<subskill>/SKILL.md`（与 speckit-* 同级扁平） |
| **Claude Code** | `.claude/skills/` | `beacon-<subskill>/`（现有惯例可对齐） |
| **Codex** | `.agents/skills/` 或文档约定路径 | 同上 |

说明：**`<subskill>`** 对应现有包名，如 `beacon-qa`、`beacon-release`、`using-beacon`。

### 4.2 一条「材质化」命令（对齐 `specify integration install`）

建议新增或并入 **`beacon doctor`** 子命令（命名示例）：

```text
beacon doctor setup-agent-surface --project-root . --agent trae [--sync-skills] [--dry-run] [--json]
```

语义：

1. 解析 **Beacon 权威技能源**：优先 **当前 Beacon 安装/仓库中的 `skills/beacon/`**，或 **环境变量/配置指定的 BEACON_SKILL_ROOT**。  
2. 将每个 **公开子技能** 投影为 **扁平目录**：`.trae/skills/beacon-<name>/SKILL.md`。  
3. **合并或追加** `.trae/rules/project_rules.md` 中与 Beacon 相关的 **托管块**（类比 Spec Kit 写入 `project_rules` / `CLAUDE.md` 托管段）：仅包含「优先 `beacon` CLI、`docs/beacon` 真相路径」，避免全文替代用户规则。  
4. **可选**：写入 **`.beacon/agent-surfaces.json`**（或并入现有 machine 状态），记录 **surface 版本、源路径哈希、安装时间**，便于 **审计与幂等升级**（对齐 `.specify/integration.json` 的职责，体量保持极小）。

### 4.3 「子 skill」在人类面的展开方式

- **Speckit 做法**：每个 slash/技能对应 **独立 SKILL 目录**，不在 UI 里做「树状无限层级」。  
- **Beacon 建议**：  
  - **默认**：与 Speckit 一致 — **每个 `beacon-*` 一个文件夹**，Trae 列表即「子技能全集」。  
  - **`using-beacon`**：仍可作为 **总路由器 SKILL**（说明何时用 `beacon help` / `beacon-status`），但 **不能替代** 各子目录，否则 Trae 仍无法枚举。

### 4.4 与现有 Beacon 能力的关系

- **`beacon doctor setup-context`**：继续负责 **CLAUDE.md / AGENTS.md** 托管块；**Trae 规则文件**可作为 **同一托管逻辑的另一目标路径**（可选实现）。  
- **`beacon skill list` / `skill drift`**：可在 payload 中增加 **`trae_skills_materialized`** 计数，用于 **可验证**「项目内是否已投影」。  
- **不要求**用户记住多套 slash：**宿主侧 SKILL 内仍写「优先执行 `beacon …`」**，与当前 skills 文档策略一致。

---

## 5. 实施优先级（建议）

| 优先级 | 项 |
|--------|-----|
| P0 | **Trae 扁平材质化**：`skills/beacon/*/SKILL.md` → `.trae/skills/beacon-*/SKILL.md` + `.trae/rules` 托管段 |
| P1 | **幂等与审计**：`.beacon/agent-surfaces.json`（或等价）记录版本与校验 |
| P2 | **多 Agent**：同一套「材质化」函数，参数化目标根目录（`.claude/skills` / `.agents/skills`） |
| P3 | **CI 校验**：`beacon doctor verify-context` 扩展一项「Trae skill 目录与注册表一致」 |

---

## 6. 参考（上游）

- Spec Kit：`docs/reference/integrations.md`（Trae 行、`specify integration` 命令）  
- Spec Kit 源码：`src/specify_cli/integrations/trae/__init__.py`、`src/specify_cli/agents.py`、`src/specify_cli/integrations/base.py`（`SkillsIntegration`）  
- Beacon：`beacon doctor …`、`beacon/utils/context_files.py`（托管块模式可复用）

---

## 7. 与对比文档的关系

与 OpenSpec / Spec Kit 的产品边界对比见：  
[`beacon-openspec-speckit-comparison-and-deliverable-design.md`](./beacon-openspec-speckit-comparison-and-deliverable-design.md)。

本文只解决 **「宿主 Agent 侧技能如何落盘才能被 Trae 枚举」** 的工程对齐，不扩展 Beacon **7 段主流程** 的人类命令数量。
