# Beacon v1.3.1 极简人类面使用指南

## 这份文档给谁看

给真实项目里需要推动交付的人看：

- 产品负责人
- 需求负责人
- 技术负责人
- 交付负责人

这份指南的目标不是解释 Beacon 的所有能力，而是告诉人类：

> **你真正只需要记住哪些命令，什么时候该做什么。**

---

## 人类只记 6 个主命令

在 `v1.3.1` 的极简人类面里，你长期只需要记住这 6 个：

1. `prd`
2. `user-story`
3. `test-case`
4. `implement`
5. `qa`
6. `release`

把它理解成一条稳定闭环：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

你不需要把下面这些当成人类长期心智负担：

- `implement-team`
- `qa-team`
- `team`
- learning / auto research
- 机器内部 agent lane

这些都是 Beacon 的内部执行面，不是人类主操作面。

---

## 只在卡住时使用 3 个辅助命令

辅助命令只有 3 个：

1. `help`
2. `status`
3. `doctor`

它们不是主流程，只在以下场景使用：

- 不知道下一步
- 想看整体状态
- 上下文、物料、环境需要修复

换句话说：

- **主流程靠 6 个命令**
- **卡住时才用 3 个辅助命令**

---

## 在 Codex / Claude 里对应的 skill 触发名

为了让 `v1.3.1` 的极简人类面不只停留在文档里，Beacon 还应把这套主面暴露成 host-visible skill names。

推荐只公开：

- umbrella:
  - `using-beacon`
- 6 个主技能：
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
  - `beacon-implement`
  - `beacon-qa`
  - `beacon-release`
- 3 个辅助技能：
  - `beacon-help`
  - `beacon-status`
  - `beacon-doctor`

用户在 host agent 中自然表达这些意图时，应该更容易触发对应 skill，而不是重新掉回 Beacon 的宽命令面。

---

## 你不需要主动操作的能力

以下能力对交付很重要，但不需要你长期记住为“人类主命令”：

### `brainstorm`

`brainstorm` 仍然存在，但在 `v1.3.1` 的人类面里，它不应成为一个长期独立阶段。

正确理解：

- 它嵌入在 `prd -> user-story` 的探索里
- 用来发现需求缺口、业务问号、未澄清点
- 最终必须回写到正式 `prd` / `user-story`

所以对人类来说：

- 你要关心“需求是否清晰”
- 不必关心“brainstorm 是不是单独命令”

### `implement-team` / `qa-team`

它们仍然可以继续存在，甚至非常重要，但属于 Beacon 内部执行面。

你只需要知道：

- `implement` 阶段 Beacon 可以自行组织 team 协作
- `qa` 阶段 Beacon 可以自行组织 team、learning、auto research

你不用把这些当成长期主入口记忆。

---

## 极简人类面下的真实工作方式

在 `v1.3.1` 里，一个版本可以同时承载多个并行 feature package。

你的人类心智不需要因为“并行”而增加新的阶段。

只需要记住：

- 主链还是 `prd -> user-story -> test-case -> implement -> qa -> release`
- 只是这条链每次聚焦一个具体 feature
- 一个 feature 的 `prd` 只对应它自己的 `user-story` 和 `test-case`
- release 时再汇总到版本级 `change` 文档

### 1. `prd`

你在这个阶段要关心的不是写得多快，而是：

- 需求是否完整
- 是否还有遗漏点
- 是否还有问号点
- 是否还有未澄清点

如果这些问题还存在，后面不能 freeze。

### 2. `user-story`

这里要把 PRD 收敛成可交付、可验收、可冻结的用户故事材料。

重点不是“写更多”，而是：

- story 是否清晰
- AC 是否明确
- 业务边界是否清楚

### 3. `test-case`

这里的重点是把验收覆盖准备完整。

你要关心：

- 是否覆盖主链
- 是否覆盖关键边界
- 是否覆盖异常与回归

### 4. `implement`

这不是“立刻开始写代码”的意思。

在 `v1.3.1` 下，`implement` 真正开始前有两个前置门：

- 需求清晰度已经通过
- 技术评审 contract 已经明确

所以你在这个阶段真正关心的是：

- 实现是否开始
- 实现边界是否确定
- Beacon 是否已经拿到 branch/worktree/service scope

### 5. `qa`

你在这个阶段只关心 4 件事：

- 有什么新发现
- 覆盖有没有增加
- 边界是否更清晰
- 当前能不能 release

如果一轮 QA 没有新增发现、覆盖或边界澄清，那不算有效进展。

### 6. `release`

这里只做最后的放行判断。

在 `v1.3.1` 下，release 不只看实现和 QA，还要看：

- requirement clarity 是否已闭合
- technical review 是否已批准
- 当前版本有哪些 feature package 真正 landed
- `change/v<version>.md` 是否已经能说明新增 / 删除 / 修复

---

## 极简人类面的 3 个关键 checkpoint

虽然你长期只记 6 个主命令，但在执行中要认识 3 个 checkpoint：

### Checkpoint A：需求清晰度

如果 PRD / user-story 里还有：

- 遗漏点
- 不清晰点
- 问号点
- 未澄清点

那么需求包不能冻结。

需要时，Beacon 会把你引到：

```bash
beacon doctor sync-requirement-clarity "<feature>" --project-root . --version <version> --json
```

### Checkpoint B：冻结

需求清晰后，再 freeze。

```bash
beacon freeze "<feature>" --project-root . --version <version> --json
```

注意：

- `freeze` 是 checkpoint
- 不是人类长期主流程中的“第 7 个主命令”

### Checkpoint C：技术评审 contract

进入 `implement` 之前，必须有 deterministic implementation contract。

需要时，Beacon 会把你引到：

```bash
beacon doctor sync-technical-review-contract "<feature>" --project-root . --version <version> --revision-id <revision> --json
```

再由人类把它补成已批准状态。

---

## 人类面推荐操作顺序

### 场景 A：从需求到交付

```bash
beacon prd ...
beacon user-story ...
beacon test-case ...
beacon implement ...
beacon qa ...
beacon release ...
```

### 场景 B：不知道下一步

```bash
beacon help --project-root . --version <version> --feature "<feature>" --json
```

### 场景 C：看整体状态

```bash
beacon status --board --project-root . --version <version> --feature "<feature>"
```

### 场景 D：修上下文或物料

```bash
beacon doctor ...
```

---

## 极简人类面的最小心智模型

你可以把 Beacon 理解成：

### 人类负责

- 正式需求文档
- 正式交付闭环
- 是否放行

### Beacon 负责

- 内部 team 协作
- learning / auto research 穿插
- 机器物料同步
- 执行面拆解
- 证据面汇总

所以最小心智模型只有一句话：

> **人类只管六段闭环，机器协作由 Beacon 自由制定。**

---

## 实际使用时不要犯的错

### 不要把所有命令都当成主命令

你不需要长期记住整个 CLI。

### 不要在需求未清晰时急着 freeze

先关掉问号，再进入实现。

### 不要在技术评审没定实现面时直接 implement

branch/worktree/service scope 不明确时，Beacon 不应盲目推进。

### 不要把 `qa` 理解成“重复跑测试”

每轮 QA 都必须带来新的交付价值。

---

## 一页版

### 长期只记

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

### 卡住才用

- `help`
- `status`
- `doctor`

### 机器内部负责

- `brainstorm`
- `implement-team`
- `qa-team`
- learning
- auto research

### 绝对前置门

- 需求不清，不得 freeze
- 技术评审未定，不得 implement
