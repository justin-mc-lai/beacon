# Brainstorm: `beacon-manager` 强文档链路同步工具

**日期**：2026-04-07  
**方法**：基于 `$brainstorm` 七维发散框架收敛  
**定位**：一个独立于 Beacon 核心版本演进的文档链路同步工具/skill  
**目标**：把多个项目中的 Beacon 需求物料统一绑定到一个 GitHub 个人知识库中，形成“人类思考、agent 实现、强一致不漂移”的文档同步工作流。

---

## 1. 一句话结论

这次要解决的问题，不该继续并入 Beacon 本体版本线，而应抽成一个独立工具面：

> `beacon-manager` 负责把各项目 Beacon 需求物料绑定到一个中心知识库中，提供有限、幂等、强约束的文档同步工作流，让人类主要在中心库思考，agent 负责收集、整理、同步、回写与校验。

它更像：

- `git` 对源码做强同步
- `beacon-manager` 对 requirement/docs/materials 做强同步

它不是新的 Beacon release line，也不是 Beacon 内核重构。

---

## 2. 核心问题

当前痛点不是“单个项目文档怎么写”，而是：

1. 多个项目各自有 Beacon 需求物料，但分散在不同仓库里
2. 人类在多个项目间思考时，缺少一个统一知识工作台
3. agent 能执行，但缺少统一的文档收集/回写/校验链路
4. 不同项目的文档更新很容易不同步、不同场景漂移
5. 一旦想统一梳理和迭代，容易误入 Beacon 核心版本系统，造成耦合

因此正确方向不是继续修改 Beacon 本体，而是新增一个独立的“文档同步与知识治理层”。

---

## 3. 七维发散

## 3.1 用户维度

### 核心用户

1. **多项目维护者**
   - 同时维护多个项目的需求、PRD、测试用例、执行物料
2. **研究/产品负责人**
   - 想在统一知识库中思考、比较、归纳、制定下一步
3. **执行型 agent**
   - 负责 pull / sync / reconcile / writeback / audit

### 潜在用户

- 个人产品工作室
- 同时维护多个私有项目的开发者
- 用 Beacon 管需求，但不想把所有逻辑塞回 Beacon 内核的人

### 不适合的用户

- 只维护一个项目、无需统一知识库的人
- 想让所有项目自动共享上下文、不在意边界的人

### 判断

`beacon-manager` 适合“多项目、重文档、重一致性”的用户，不适合轻量一次性任务。

---

## 3.2 场景维度

### 核心场景

#### 场景 A：项目下有各自 Beacon 文档

例如：

- `project-a/docs/beacon/...`
- `project-b/docs/beacon/...`
- `project-c/docs/beacon/...`

用户希望统一看、统一想、统一对比，但又不想把项目仓库本身揉成一个。

#### 场景 B：在一个个人知识库中做长期思考

用户希望：

- 在一个中心 GitHub repo 中沉淀跨项目研究
- 形成统一索引、主题页、比较页、迭代页
- 再把确定的结果同步回各项目

#### 场景 C：agent 执行同步，人类专注判断

用户不想自己手动：

- 到各仓库复制文件
- 比对差异
- 更新引用
- 确认哪些文件要回写

这些应该由 agent 走固定命令完成。

### 连续场景

1. 项目仓库发生文档变更
2. `beacon-manager pull` 收集到中心库
3. 人类在中心库思考、重写、聚合
4. agent 执行 `sync` 回写目标项目
5. `status` / `doctor` / `reconcile` 保证不漂移

---

## 3.3 业务维度

这个工具的价值不在变现，而在把“多项目文档治理”变成一个独立产品面。

### 核心价值

- 中心化思考
- 分布式项目物料同步
- 强绑定关系
- 可追溯的回写链路

### 差异化点

相对普通知识库：

- 它不是只存笔记
- 它还能回写项目文档并校验一致性

相对普通同步脚本：

- 它不是单向 copy
- 它有 binding、manifest、scene、reconcile、doctor、provenance

相对 Beacon 本体：

- 它不介入 release line
- 它只管文档链路和知识同步

---

## 3.4 技术维度

### 主要挑战

| 挑战类型 | 难度 | 应对 |
|---------|-----|------|
| 中心库与项目库绑定 | 高 | manifest + binding contract |
| 强一致不漂移 | 高 | pull/sync/reconcile/status/doctor |
| 多项目目录规范不统一 | 中 | registry + per-project path mapping |
| 幂等执行 | 高 | 每个命令只做固定状态转换 |
| 回写安全 | 高 | dry-run + explicit target + provenance |

### 最关键的技术原则

#### 原则 1：中心库是“思考面”，项目库是“交付面”

中心库负责：

- 聚合
- 比较
- 主题整理
- 跨项目洞察
- 中心化编辑

项目库负责：

- 项目正式 requirement materials
- 项目内执行链路消费

#### 原则 2：同步不是双向自由编辑，而是受约束链路

建议默认链路：

```text
project docs
→ pull into knowledge repo
→ human think / agent organize
→ sync back to project docs
→ reconcile status
```

而不是：

```text
both sides edit anything
→ hope they stay aligned
```

#### 原则 3：每个项目必须有 binding

没有 binding，就不能 sync。

binding 至少应定义：

- project id
- local repo path
- remote repo url
- docs root
- allowed categories
- central mirror path
- sync mode

#### 原则 4：只有有限命令，且尽量幂等

不要做一个“大而全平台”。
应该像 git 一样，只有少数固定动词。

---

## 3.5 体验维度

### 关键体验

| 体验点 | 重要度 | 目标体验 |
|-------|-------|---------|
| 命令少 | ★★★★★ | 像 git 一样只有少数核心命令 |
| 不漂移 | ★★★★★ | 一眼知道中心库和项目库是否一致 |
| 回写安全 | ★★★★★ | 不会误把中心库内容写错项目 |
| 思考集中 | ★★★★☆ | 人类只需要在一个地方看全局 |
| 执行自动 | ★★★★☆ | agent 可代替人工完成大部分同步步骤 |

### 理想用户感知

用户应感到：

- “我在中心知识库里想问题”
- “agent 帮我 pull、sync、对齐、校验”
- “每个项目都有绑定，不会串”
- “只要按固定命令跑，就不会漂”

---

## 3.6 价值维度

### 功能价值

- 统一管理多项目 Beacon 物料
- 支持集中思考与分散回写
- 建立跨项目文档强一致链路

### 认知价值

- 把“人类思考，agent 实现”从口号变成真正的工作面分层
- 把跨项目 knowledge work 从聊天和手工复制中解放出来

### 品牌价值

如果做对，`beacon-manager` 会成为：

> 一个面向 Beacon 物料的 Git-like 文档同步与思考工具。

---

## 3.7 风险维度

| 风险类型 | 概率 | 影响 | 应对 |
|---------|-----|-----|------|
| 工具过大，变成新平台 | 中 | 大 | 只保留有限命令 |
| 用户误以为中心库就是 source of truth | 中 | 中 | 明确中心库与项目交付面的角色 |
| 双向编辑导致冲突 | 高 | 大 | 强制 `reconcile` / provenance / scene 锁 |
| 回写错项目 | 中 | 大 | binding + explicit target + doctor |
| 场景粒度不清，导致覆盖不完整 | 中 | 中 | 引入 scene binding |

---

## 4. 聚类收敛：最合理的产品形态

## 4.1 它不该是什么

它不该是：

- Beacon 本体的一部分 release line
- 通用知识库平台
- 大一统多项目 agent runtime
- 一个自由度很高的“同步 anything”脚本集合

## 4.2 它最合理是什么

它应该是：

### 一个独立工具或 skill

名称候选：

- `beacon-manager`
- `beacon-docsync`
- `beacon-chain`

我更倾向：

**`beacon-manager`**

因为它表达的是：

- 管理 bindings
- 管理同步链路
- 管理中心知识库
- 管理场景级文档一致性

---

## 5. 推荐系统形态

## 5.1 三层结构

### Layer 1: Project Repos

每个项目保留自己的：

- `docs/beacon/...`
- 本地代码
- 本地执行物料

### Layer 2: Personal Knowledge Repo

单独一个 GitHub 个人知识库，负责：

- 多项目镜像目录
- 主题研究页
- 对比页
- scene 页
- 中央索引
- 同步日志

### Layer 3: `beacon-manager`

独立命令面，负责：

- 绑定
- 拉取
- 同步
- 状态
- 校验
- 对账

---

## 5.2 Scene 模型

为了做到“同场景同步更新”，建议引入 **scene** 概念。

scene 表示一组跨项目、跨文档但同一主题/任务的同步单元。

例如：

- `scene/release-governance`
- `scene/qa-closure`
- `scene/prototype-design`
- `scene/customer-x-onboarding`

每个 scene 可以绑定：

- 涉及的项目
- 涉及的文档类别
- 中央主题页
- 最近同步状态
- upstream/downstream 关系

这比单纯“同步整个 docs 目录”更稳，因为它允许按任务语义进行强一致。

---

## 6. 建议命令面

命令必须少，而且有清晰状态转换。

建议最小集合如下：

### 1. `bind`

用途：

- 把项目仓库与中心知识库建立绑定

效果：

- 创建/更新 binding manifest

### 2. `pull`

用途：

- 从项目仓库拉取 Beacon 物料到中心库镜像

效果：

- 更新中心镜像
- 记录 provenance
- 不回写项目

### 3. `sync`

用途：

- 把中心库中已确认内容回写到项目仓库

效果：

- 只同步绑定范围内文件
- 产生同步日志

### 4. `status`

用途：

- 查看项目库与中心库的对齐状态

效果：

- synced / drifted / unbound / conflict / dirty

### 5. `reconcile`

用途：

- 对账与冲突处理

效果：

- 找出哪些文件漂移
- 哪些 scene 未闭环
- 哪些回写来源不明

### 6. `doctor`

用途：

- 校验 binding、路径、scene、目录规范、同步契约

效果：

- 输出阻断项与修复建议

如果一定要进一步缩减，我建议最终公开面只保留：

```text
bind
pull
sync
status
reconcile
doctor
```

---

## 7. 幂等工作流定义

每个命令都应接近幂等。

## 7.1 `bind`

重复执行：

- 更新同一 binding，不应重复创建脏状态

## 7.2 `pull`

重复执行：

- 如果项目文档无变化，不应产生无意义 diff

## 7.3 `sync`

重复执行：

- 如果中心库与项目库已一致，不应重复写入

## 7.4 `status`

重复执行：

- 应稳定输出同一状态

## 7.5 `reconcile`

重复执行：

- 在无新冲突时应收敛到相同结果

## 7.6 `doctor`

重复执行：

- 应稳定给出同一诊断，不引入副作用

---

## 8. Binding Contract

建议每个项目有一个 binding manifest，例如：

```yaml
project_id: project-a
repo_root: /path/to/project-a
repo_url: git@github.com:me/project-a.git
docs_root: docs/beacon
central_repo: git@github.com:me/beacon-knowledge.git
central_path: projects/project-a
allowed_categories:
  - research
  - user-story
  - prd
  - qa/test-cases
  - execution
sync_mode: central-think-project-deliver
scenes:
  - release-governance
  - qa-closure
  - prototype-design
```

没有 manifest，就不能进入 `sync`。

---

## 9. 中心知识库应该长什么样

建议中心库结构如下：

```text
beacon-knowledge/
  index.md
  log.md
  projects/
    project-a/
      mirror/
      scenes/
      notes/
      sync-log/
    project-b/
      mirror/
      scenes/
      notes/
      sync-log/
  scenes/
    release-governance/
    qa-closure/
    prototype-design/
  distilled/
    templates/
    patterns/
    checklists/
  bindings/
    project-a.yaml
    project-b.yaml
```

关键点：

- `projects/*/mirror/` 是项目文档镜像
- `scenes/` 是跨项目思考面
- `distilled/` 是抽象后的可复用资产
- `bindings/` 是强绑定关系

---

## 10. 人类与 Agent 的职责分工

## 10.1 人类负责

- 决定要思考什么 scene
- 决定哪些文档改动应该成为正式内容
- 决定哪些内容可以同步回项目
- 决定哪些总结可以进入 `distilled/`

## 10.2 Agent 负责

- 执行 `pull`
- 整理镜像
- 维护索引和同步日志
- 检查 drift
- 执行 `sync`
- 运行 `doctor`
- 给出 `reconcile` 建议

这才真正符合：

> 人类在思考，agent 在实现。

---

## 11. 强一致策略

真正做到“不漂移”，需要四条强约束。

### 11.1 单 binding 单来源

一个项目文档路径只能绑定到一个中心镜像路径。

### 11.2 同步必须带 provenance

每次 `pull` / `sync` 都要记录：

- source
- target
- scene
- timestamp
- commit
- operator

### 11.3 scene 级别闭环

不是只看文件是否同步，而要看 scene 是否闭环：

- 是否 pull 过
- 是否中心库更新过
- 是否 sync 回项目
- 是否 reconcile 过

### 11.4 doctor 作为 gate

在 `sync` 前默认执行 doctor：

- binding 是否存在
- 路径是否匹配
- 中心库是否干净
- scene 是否明确
- 目标项目是否可写

---

## 12. 与 Beacon 本体的关系

这点必须非常明确。

`beacon-manager`：

- 不进入 Beacon release line
- 不直接改 Beacon 核心命令语义
- 不改变 Beacon 本体的 docs contract
- 只消费 Beacon 物料，并建立更高一层的跨项目同步治理

它更像：

- 一个 `skill`
- 一个 companion CLI
- 一个 docs orchestrator

而不是 Beacon 本身。

---

## 13. 推荐最终方案

收敛后，我认为最稳的最终方案是：

## 名称

**`beacon-manager`**

## 形态

一个独立 skill/CLI，围绕一个中心 GitHub 知识库，对多个项目的 `docs/beacon` 物料做绑定、拉取、同步、对账、校验。

## 最小命令面

```text
beacon-manager bind
beacon-manager pull
beacon-manager sync
beacon-manager status
beacon-manager reconcile
beacon-manager doctor
```

## 工作流

```text
bind project
→ pull project docs
→ human think in central repo
→ sync approved changes back
→ reconcile drift
→ doctor before next sync
```

## 本质

这不是让 Beacon 变复杂，而是把“多项目文档思考与同步”从 Beacon 本体里抽离成独立工具。

---

## 14. 下一步建议

如果要继续推进，建议按以下顺序：

1. 先写 `beacon-manager` 的 PRD
2. 再定义 binding manifest schema
3. 再定义 scene schema
4. 再定义六个命令的状态机
5. 最后才实现 skill 或 CLI

不要先写同步脚本。
先把 contract 说清，才能保证这个工具真的像 git 一样稳定、有限、强一致。

---

## 15. 最终结论

这轮 brainstorm 最终得到的不是“把 Beacon 再做大”，而是一个更清晰的拆分：

> Beacon 继续做项目内 requirement/workflow/gate；`beacon-manager` 单独负责跨项目文档知识库绑定、同步、对账与强一致治理。

这样才能同时做到：

- 中心化思考
- 分布式项目交付
- 有限命令面
- agent 执行同步
- 人类掌握判断
- 强一致不漂移

