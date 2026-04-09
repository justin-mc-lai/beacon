# Beacon v1.2.0 自然语言触发手册

> 目标：让用户**少记命令、多说意图**。  
> 这份手册只收录 **最稳定、最短、最不容易误触发** 的自然语言模板。

---

## 1. 先记一个总原则

如果你想用自然语言触发 Beacon，**默认只记一个子命令就够了**：

```bash
beacon ask "<自然语言目标>" --project-root . --version v1.2.0 --plan-only --json
```

为什么是它：

- `ask` 是自然语言总入口
- 默认 `--plan-only`，更安全
- 会先给出路由结果和下一步，不会直接乱执行

如果你只想恢复某个已知 feature 的下一步，再记第二个：

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

---

## 2. 最稳定的触发写法

为了让 router 更稳定，建议所有自然语言都尽量符合这 4 条：

1. **一句话只表达一个主意图**
2. **直接使用 Beacon 的核心关键词**
3. **写出 feature 名或项目对象**
4. **默认先预览，不直接执行**

推荐结构：

```text
帮我【动作】「对象」，目标是【结果】。
```

例如：

```text
帮我继续「支付重构」，告诉我下一步。
```

---

## 3. 只需要记住的 3 个入口

### 入口 1：自然语言总入口

```bash
beacon ask "<自然语言目标>" --project-root . --version v1.2.0 --plan-only --json
```

适合：

- 我还不确定下一步
- 我只知道我想完成什么
- 我想先看推荐路线

---

### 入口 2：恢复某个 feature

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

适合：

- 我已经有 feature 名
- 我只想看当前阶段、阻塞点、下一步

---

### 入口 3：全局状态看板

```bash
beacon status --board --project-root . --version v1.2.0
```

适合：

- 我不确定现在整体卡在哪
- 我想看 release / coverage / memory closure

---

## 4. 最新 v1.2.0 推荐的通用短句

下面这些短句，是**最适合被普通用户记住**的版本。

---

### 4.1 开始一个需求

#### 最稳短句

> 帮我开始「\<feature\>」主链

#### 推荐调用

```bash
beacon ask "帮我开始「<feature>」主链" --project-root . --version v1.2.0 --plan-only --json
```

#### 常见变体

- 帮我开始这个功能的工作流
- 帮我把这个需求走成 Beacon 主链
- 帮我从 0 开始推进这个 feature

#### 预期路由

通常会导向：

- `workflow`
- `think`
- `user-story`
- `prd`
- `test-case`

---

### 4.2 继续当前 feature

#### 最稳短句

> 帮我继续「\<feature\>」，告诉我下一步

#### 推荐调用

```bash
beacon ask "帮我继续「<feature>」，告诉我下一步" --project-root . --version v1.2.0 --plan-only --json
```

或者更直接：

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

#### 常见变体

- 帮我恢复「\<feature\>」
- 帮我接着跑这个工作流
- 这个 feature 下一步做什么

#### 最稳关键词

- `继续`
- `恢复`
- `下一步`

---

### 4.3 看当前卡点

#### 最稳短句

> 帮我检查「\<feature\>」当前卡点

#### 推荐调用

```bash
beacon ask "帮我检查「<feature>」当前卡点" --project-root . --version v1.2.0 --plan-only --json
```

#### 常见变体

- 帮我看这个 feature 卡在哪
- 当前阻塞点是什么
- 为什么现在不能继续

#### 最稳关键词

- `检查`
- `卡点`
- `阻塞`

---

### 4.4 生成 user-story

#### 最稳短句

> 帮我为「\<feature\>」生成用户故事

#### 推荐调用

```bash
beacon ask "帮我为「<feature>」生成用户故事" --project-root . --version v1.2.0 --plan-only --json
```

#### 最稳关键词

- `用户故事`
- `验收标准`

---

### 4.5 生成 PRD

#### 最稳短句

> 帮我为「\<feature\>」生成 PRD

#### 推荐调用

```bash
beacon ask "帮我为「<feature>」生成 PRD" --project-root . --version v1.2.0 --plan-only --json
```

#### 最稳关键词

- `PRD`
- `需求文档`
- `规格说明`

---

### 4.6 生成测试用例

#### 最稳短句

> 帮我为「\<feature\>」生成测试用例

#### 推荐调用

```bash
beacon ask "帮我为「<feature>」生成测试用例" --project-root . --version v1.2.0 --plan-only --json
```

#### 最稳关键词

- `测试用例`
- `测试矩阵`
- `验收测试`

---

### 4.7 给项目推荐 skill/profile

这是 `v1.2.0` 的新重点能力。

#### 最稳短句

> 帮我为当前项目推荐 Beacon skill/profile，先预览

#### 推荐调用

```bash
beacon ask "帮我为当前项目推荐 Beacon skill/profile，先预览" --project-root . --version v1.2.0 --plan-only --json
```

如果你已经明确知道要跑 discovery：

```bash
beacon skill discover --project-root . --dry-run --json
```

#### 最稳关键词

- `推荐`
- `skill`
- `profile`
- `预览`

---

### 4.8 进入实现阶段

#### 最稳短句

> 帮我为「\<feature\>」生成实现计划

#### 推荐调用

```bash
beacon ask "帮我为「<feature>」生成实现计划" --project-root . --version v1.2.0 --plan-only --json
```

#### 最稳关键词

- `实现计划`
- `implement`

---

### 4.9 做 QA 验收

#### 最稳短句

> 帮我对「\<feature\>」做 QA 验收

#### 推荐调用

```bash
beacon ask "帮我对「<feature>」做 QA 验收" --project-root . --version v1.2.0 --plan-only --json
```

如果你已经知道要直接执行 QA：

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --json
```

#### 最稳关键词

- `QA`
- `验收`
- `测试验收`

---

### 4.10 检查能不能发版

#### 最稳短句

> 帮我检查现在是否满足 release 条件

#### 推荐调用

```bash
beacon ask "帮我检查现在是否满足 release 条件" --project-root . --version v1.2.0 --plan-only --json
```

如果你已经知道要跑放行：

```bash
beacon gate check release --project-root . --version v1.2.0 --json
beacon release check v1.2.0 --project .
```

#### 最稳关键词

- `release`
- `发布`
- `放行`
- `门禁`

---

### 4.11 生成发布说明

#### 最稳短句

> 帮我生成 v1.2.0 发布说明

#### 推荐调用

```bash
beacon ask "帮我生成 v1.2.0 发布说明" --project-root . --version v1.2.0 --plan-only --json
```

#### 最稳关键词

- `发布说明`
- `release summary`
- `变更总结`

---

## 5. 最适合给用户记忆的“万能短句”

如果你做的是对外文档、CLI onboarding、产品提示文案，建议直接让用户记下面这 6 句：

1. **帮我开始「\<feature\>」主链**
2. **帮我继续「\<feature\>」，告诉我下一步**
3. **帮我检查「\<feature\>」当前卡点**
4. **帮我为当前项目推荐 Beacon skill/profile，先预览**
5. **帮我对「\<feature\>」做 QA 验收**
6. **帮我检查现在是否满足 release 条件**

这 6 句基本覆盖 `v1.2.0` 主链的 90% 高频场景。

---

## 6. 哪些写法不稳定，尽量避免

### 6.1 一句话混多个意图

不推荐：

```text
帮我生成 PRD、顺便跑 QA、然后告诉我能不能发版
```

问题：

- router 可能只能稳定选中一个主意图
- 结果不够可预测

### 6.2 只说“做一下这个”

不推荐：

```text
帮我做一下这个
```

问题：

- 缺少 feature
- 缺少动作
- 缺少阶段

### 6.3 不写对象

不推荐：

```text
帮我继续
```

推荐：

```text
帮我继续「支付重构」，告诉我下一步
```

### 6.4 又想自然语言，又想立即执行

默认建议先：

```bash
beacon ask "..." --plan-only --json
```

先看路由，再决定是否显式执行。

---

## 7. 给产品/文档作者的建议

如果你的目标是让用户**尽量不记命令**，建议所有教程统一收口成这三句：

### 只记 3 个命令

```bash
beacon ask "<自然语言目标>" --project-root . --version v1.2.0 --plan-only --json
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
beacon status --board --project-root . --version v1.2.0
```

### 用户只记 6 种话术

- 帮我开始……
- 帮我继续……
- 帮我检查……
- 帮我推荐……
- 帮我验收……
- 帮我发版……

---

## 8. 一页速查

| 目标 | 最稳短句 | 推荐命令 |
| --- | --- | --- |
| 开始需求 | 帮我开始「\<feature\>」主链 | `beacon ask "..." --plan-only --json` |
| 继续 feature | 帮我继续「\<feature\>」，告诉我下一步 | `beacon help ... --feature "<feature>" --json` |
| 看卡点 | 帮我检查「\<feature\>」当前卡点 | `beacon ask "..." --plan-only --json` |
| 生成 user-story | 帮我为「\<feature\>」生成用户故事 | `beacon ask "..." --plan-only --json` |
| 生成 PRD | 帮我为「\<feature\>」生成 PRD | `beacon ask "..." --plan-only --json` |
| 生成测试用例 | 帮我为「\<feature\>」生成测试用例 | `beacon ask "..." --plan-only --json` |
| 推荐项目绑定 | 帮我为当前项目推荐 Beacon skill/profile，先预览 | `beacon ask "..." --plan-only --json` |
| 进入实现 | 帮我为「\<feature\>」生成实现计划 | `beacon ask "..." --plan-only --json` |
| QA 验收 | 帮我对「\<feature\>」做 QA 验收 | `beacon ask "..." --plan-only --json` |
| 检查发版 | 帮我检查现在是否满足 release 条件 | `beacon ask "..." --plan-only --json` |
| 生成发布说明 | 帮我生成 v1.2.0 发布说明 | `beacon ask "..." --plan-only --json` |

---

## 9. 最后的建议

如果你希望自然语言调用 **稳定可靠**，就遵守下面这条：

```text
一个 prompt 只表达一个目标，
而且尽量包含 Beacon 已知的核心关键词。
```

所以最稳的形式永远是：

```bash
beacon ask "帮我【动作】「对象」" --project-root . --version v1.2.0 --plan-only --json
```

这比“长段描述 + 多个目标 + 模糊对象”稳定得多。
