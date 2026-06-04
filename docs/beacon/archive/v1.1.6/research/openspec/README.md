# Research: OpenSpec — artifact-driven workflow 与多工具交付机制

> 来源：`oss-sync/automation/autoresearch/openspec/`
> 复核时间：2026-03-24
> 研究目标：为 Beacon v1.1.6 提供 **workflow artifact、profile、delivery** 三个维度的源码级借鉴

---

## 1. 先给结论

OpenSpec 的核心价值不在“仓库里有多少 skill 目录”，而在于三件事：

1. **用结构化 artifact 驱动变更生命周期**
2. **用 profile 控制启用哪些 workflows**
3. **用 delivery 决定把 workflows 生成为 skills、commands，还是两者同时生成**

因此，OpenSpec 更适合作为 Beacon 的：

- `implement` / `plan` 的 artifact 组织参考
- workflow profile 参考
- cross-tool workflow delivery 参考

而不是“直接照搬 skill 数量”的参考对象。

---

## 2. 从源码复核到的关键事实

### 2.1 workflow 并不是固定全集默认安装

`src/core/profiles.ts` 明确给出：

- **core profile**：`propose`, `explore`, `apply`, `archive`
- **all workflows**：
  `propose`, `explore`, `new`, `continue`, `apply`, `ff`, `sync`, `archive`, `bulk-archive`, `verify`, `onboard`

也就是说：

- OpenSpec 的默认体验是一个更小的核心 workflow 集合
- 扩展 workflow 是按 profile / custom selection 开启的
- 不能把它描述成“默认就有固定 N 个 skills 全量可用”

### 2.2 skills / commands 是生成出来的，不是仓库里固定摆好的最终形态

`src/core/init.ts` 显示：

- `profile` 决定当前启用哪些 workflows
- `delivery` 决定生成：
  - `skills`
  - `commands`
  - `both`
- 生成逻辑在 `init/update` 时写入目标工具目录

这说明 OpenSpec 的产品重点是：

> **workflow 的声明与分发机制**

而不是在源码仓库中长期维护一套固定的最终 skill 目录树。

### 2.3 OpenSpec 面向的是多工具交付，而非单一 IDE/CLI

`docs/supported-tools.md` 说明它支持多种 AI 工具的 skills / commands 安装目录。

这意味着 OpenSpec 在架构上天然考虑了：

- workflow 如何被映射到不同工具生态
- skills 和 slash commands 如何按不同工具约定落盘
- 交付方式如何随 profile/delivery 变化

这对 Beacon 的启发是：

- Beacon 可以借鉴“workflow 交付模型”
- 但不必在 v1.1.6 就承担 OpenSpec 这种跨工具分发复杂度

### 2.4 核心主轴是 artifact lifecycle

OpenSpec README 与 `docs/commands.md` 复核下来，最稳定的主轴是：

```text
propose / explore
      ↓
apply
      ↓
verify / sync / archive
```

其中 `propose` 创建的变更目录会包含类似：

- `proposal.md`
- `specs/`
- `design.md`
- `tasks.md`

也就是说，OpenSpec 最值得借鉴的是：

- 变更如何被结构化
- 变更产物如何成为后续执行的输入
- 变更结束后如何 verify / sync / archive

---

## 3. 本次修正了哪些旧口径

### 旧口径 1：OpenSpec = “22 个独立 SKILL.md”

**修正后：不成立。**

更准确的说法是：

- OpenSpec 有一组 workflow ids
- 是否启用这些 workflows 取决于 profile
- 最终安装为 skills / commands 取决于 delivery
- 目标工具目录也取决于所选 AI 工具

### 旧口径 2：仓库根目录长期维护固定 `SKILL.md` / `SKILL.md.tmpl` / `CLAUDE.md`

**修正后：不应作为研究结论继续使用。**

本地快照显示其核心逻辑在：

- `src/core/profiles.ts`
- `src/core/init.ts`
- `docs/commands.md`
- `docs/supported-tools.md`

研究重点应从“静态 skill 文件个数”切换到“workflow 生成机制”。

### 旧口径 3：OpenSpec 的关键差异化 = skill 数量多

**修正后：过于表面。**

更稳妥的判断是：

- 差异化在 artifact-guided workflow
- 差异化在 profile/delivery 机制
- 差异化在跨工具 workflow 分发

---

## 4. 与 Beacon 的真实可比维度

| 维度 | OpenSpec 的强项 | Beacon 可借鉴点 |
|------|------------------|-----------------|
| Artifact lifecycle | 强 | 结构化 `proposal/spec/design/tasks` |
| Workflow profile | 强 | 核心 workflow 与扩展 workflow 分层 |
| Delivery model | 强 | skill / command / mixed 的交付思路 |
| Verify / archive | 中强 | 实施后的验证、归档、同步机制 |
| Runtime control | 弱 | 不是其主战场 |
| QA 金字塔 | 弱 | 不应和 gstack 混为一类 |

---

## 5. 对 Beacon 的具体借鉴建议

### 适合吸收

1. **变更目录即工作流上下文**
2. **核心 workflow / 扩展 workflow 分层**
3. **verify / archive / sync 作为完整生命周期的一部分**

### 不适合现在就吸收

1. **面向多 AI 工具的完整分发系统**
2. **为了“看起来生态丰富”而人为扩增 workflow 数量**
3. **把 OpenSpec 理解为“skill 平台”而忽略 artifact 主轴**

---

## 6. 关键证据文件

- `oss-sync/automation/autoresearch/openspec/src/core/profiles.ts`
- `oss-sync/automation/autoresearch/openspec/src/core/init.ts`
- `oss-sync/automation/autoresearch/openspec/docs/commands.md`
- `oss-sync/automation/autoresearch/openspec/docs/supported-tools.md`
- `oss-sync/automation/autoresearch/openspec/README.md`

---

## 7. 一句话总结

OpenSpec 最值得 Beacon 学的，不是“它有多少 skill”，而是：

> **它把 workflow 定义、artifact 生命周期、以及面向不同 AI 工具的交付机制拆开了。**

这比“数 skill 个数”更接近 Beacon 真正需要的产品能力。

