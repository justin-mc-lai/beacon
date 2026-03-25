# Beacon v1.1.7 使用文档

> 面向 Beacon 使用者、维护者、AI agent 操作者的 **v1.1.7 正式使用说明**。

---

## 1. 这份文档解决什么问题

如果你现在要真正使用 Beacon v1.1.7，而不是只看设计文档，这份文档回答 4 个核心问题：

1. **现在该从哪个命令开始**
2. **需求如何从草稿走到冻结、实现、验证、验收**
3. **native-single / native-team 该怎么用**
4. **卡住时如何用 `status / help / doctor advise` 找到下一步**

---

## 2. v1.1.7 的正式定位

Beacon v1.1.7 不是纯文档生成器，也不是只做 adapter 转发。

它现在提供的是一条 **正式、可闭环、可回写、可重开** 的需求交付主链：

```text
draft/refined
→ freeze
→ implement
→ verify/review
→ accept
→ release
```

同时支持：

- `freeze`：冻结当前 revision baseline
- `reopen`：需求变更时开启新 revision
- `implement run --runner native-single`
- `implement run --runner native-team`
- `profile create / skill bind`：为项目声明 profile 与 skill 绑定
- `verify run`：按项目 profile 执行项目特定验证
- `orchestrate run`：按 profile 预演或执行编排图
- `review accept`
- `help / doctor advise / status` 阶段导航

---

## 2.1 v1.1.7 新增的 project-aware 能力

如果 v1.1.6 解决的是“需求闭环”，那么 v1.1.7 新增的是：

- **multi-skill registry**
- **project-specific profile**
- **skill-backed orchestration**
- **required evidence gate**
- **contract drift diagnosis**

它解决的问题是：

> 在多服务项目里，Beacon 不再只会生成通用 QA，而是可以按项目真实工作流调用特定 skill 做 verify / delivery / debug，并在 accept 前阻断缺失证据。

例如：

- 项目可以声明 `rolo-uat` profile
- profile 可以把 `verify / delivery / debug` 绑定到 `rolo-dev`
- accept 前必须检查 `required_cases` 与 `required_evidence`

---

## 3. source of truth 约定

### 3.1 人类主阅读面

正式交付物在：

```text
docs/beacon/v1.1.7/
```

重点目录：

- `user-story/`
- `prd/`
- `qa/test-cases/`
- `execution/`
- `release/`

### 3.2 机器状态真相

机器状态在：

```text
docs/beacon/v1.1.7/.machine/
```

重点目录：

- `.machine/user-story/`
- `.machine/qa/`
- `.machine/execution/`

### 3.3 运行时状态

运行时与中间态在：

```text
.beacon/
```

注意：

- `docs/beacon/v1.1.7/` 是 **正式交付文档**
- `.machine/` 是 **正式 machine truth**
- `.beacon/` 是 **运行时状态**

`.beacon/` 不替代正式交付文档。

---

## 4. 安装与基础确认

### 4.1 安装

```bash
pip install beacon
```

开发态：

```bash
pip install -e ".[dev]"
```

### 4.2 确认版本

```bash
beacon --version
```

期望看到：

- Beacon CLI 版本为 `v1.1.7`

### 4.3 确认项目上下文

```bash
beacon doctor verify-context --project-root . --strict
```

如果上下文缺失：

```bash
beacon doctor setup-context --project-root .
```

---

## 5. 先建立正确心智模型

## 5.1 Feature

一个需求主题，例如：

```text
Beacon native lifecycle closure
```

## 5.2 Revision

同一个 feature 可以有多轮 revision：

- `R1`
- `R2`
- `R3`

每次 `reopen` 都不是污染旧需求，而是开启 **新 revision**。

## 5.3 Story / Item

Feature 下会落成 story 与稳定 item：

- `AC-*`
- `TASK-*`
- `TEST-*`

这些 item 会被 implement / verify / accept **直接回写状态**。

## 5.4 生命周期

### 文档 / 需求生命周期

```text
draft → refined → frozen → superseded → archived
```

### 交付生命周期

```text
idle → implementing → implemented → verifying → accepted → released
```

---

## 6. 最常用的 3 条路径

## 6.1 路径 A：从 0 到正式需求包

适合：

- 需求刚开始
- 还没建立 user-story / prd / test-case

命令：

```bash
beacon ask "<goal>" --project-root . --version v1.1.7 --plan-only --json
beacon workflow start "<feature>" --project . --version v1.1.7
beacon think start "<feature>" --project . --version v1.1.7
beacon user-story create "<feature>" --project . --version v1.1.7
beacon prd create "<feature>" --project . --version v1.1.7
beacon test-case create "<feature>" --project . --version v1.1.7
```

## 6.2 路径 B：从 frozen baseline 进入实现

适合：

- 需求已经稳定
- 要进入实现与回写

命令：

```bash
beacon freeze "<feature>" --project-root . --version v1.1.7
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-single --json
beacon review quality "<feature>" --project-root . --version v1.1.7 --json
beacon review accept "<feature>" --project-root . --version v1.1.7 --json
```

## 6.3 路径 C：需求变更后重新闭环

适合：

- 已 frozen / implementing / verified / accepted
- 需求变化，需要重新介入

命令：

```bash
beacon reopen "<feature>" --project-root . --version v1.1.7 --reason change-request
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
beacon freeze "<feature>" --project-root . --version v1.1.7
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-team --json
```

## 6.4 路径 D：项目特定 skill 验收

适合：

- 多服务项目
- 需要 UAT / pipeline / gateway / SQL / 日志联合验收
- 需要让 Beacon 按项目真实流程执行验证

命令：

```bash
beacon profile create rolo rolo-uat --example rolo-uat --json
beacon skill bind "<feature>" --profile rolo-uat --version v1.1.7
beacon verify run "<feature>" --project-root . --version v1.1.7 --profile rolo-uat --json
beacon review quality "<feature>" --project-root . --version v1.1.7 --json
beacon review accept "<feature>" --project-root . --version v1.1.7 --json
```

---

## 7. 日常推荐命令顺序

如果你不确定下一步是什么，默认按这个顺序：

```bash
beacon status --board --project-root . --version v1.1.7 --feature "<feature>"
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
beacon doctor advise --project-root . --version v1.1.7 --feature "<feature>" --json
```

解释：

- `status`：给原始事实
- `help`：给下一步建议
- `doctor advise`：解释为什么 blocked、先修什么

不要跳过这三步直接猜命令。

---

## 8. 从 draft 到 release 的标准用法

## 8.1 Step 1：创建或补齐需求材料

```bash
beacon think start "<feature>" --project . --version v1.1.7
beacon user-story create "<feature>" --project . --version v1.1.7
beacon prd create "<feature>" --project . --version v1.1.7
beacon test-case create "<feature>" --project . --version v1.1.7
```

## 8.2 Step 2：检查是否 ready to freeze

```bash
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
```

如果输出：

```json
"next_step": { "action": "freeze", ... }
```

说明当前进入冻结阶段。

## 8.3 Step 3：冻结 revision

```bash
beacon freeze "<feature>" --project-root . --version v1.1.7
```

冻结后：

- active revision 进入 `frozen`
- 生成 baseline 语义
- 后续 implement 必须绑定该 revision

## 8.4 Step 4：执行实现

### 小需求：用 `native-single`

```bash
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-single --json
```

### 复杂需求：用 `native-team`

```bash
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-team --json
```

## 8.5 Step 5：检查 review / verify

```bash
beacon review spec "<feature>" --project-root . --version v1.1.7 --json
beacon review quality "<feature>" --project-root . --version v1.1.7 --json
```

## 8.6 Step 6：正式验收

```bash
beacon review accept "<feature>" --project-root . --version v1.1.7 --json
```

验收前必须满足：

- revision 已 `frozen`
- AC 已 verified
- TEST 已 passed / verified

## 8.7 Step 7：做 release readiness 检查

```bash
beacon gate check release --project-root . --version v1.1.7 --json
beacon release check v1.1.7 --project .
```

---

## 9. native-single 与 native-team 怎么选

## 9.1 native-single

适合：

- 小功能
- 单主线实现
- 低风险

特点：

- 单执行链
- 自动做 implementation writeback
- 最短路径快

命令：

```bash
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-single --json
```

## 9.2 native-team

适合：

- 多 story
- 高复杂度
- 要分角色交付

默认最小角色：

- `planner`
- `implementer`
- `reviewer`
- `tester`

特点：

- 会产出 team state
- 会产出角色级报告
- 会汇总 `implemented_items / verified_items / blocked_items`

命令：

```bash
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-team --json
```

### 说明

v1.1.7 当前的 `native-team` 是：

- **Beacon 原生**
- **deterministic**
- **file-backed multi-role orchestration**

它不是 tmux/OMX 外部并发 worker runtime，但已经是正式的多角色实现流。

---

## 10. status / help / doctor advise 怎么用

## 10.1 `status`

命令：

```bash
beacon status --board --project-root . --version v1.1.7 --feature "<feature>"
```

你会看到：

- current revision
- current delivery status
- coverage.story / coverage.ac / coverage.tc
- next_step
- scores

## 10.2 `help`

命令：

```bash
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
```

它回答：

- 现在在哪个阶段
- 当前 revision 是谁
- 为什么 blocked
- 下一步是什么
- 建议命令是什么

## 10.3 `doctor advise`

命令：

```bash
beacon doctor advise --project-root . --version v1.1.7 --feature "<feature>" --json
```

它回答：

- blocked 在哪一层
- 修复路径是什么
- 当前评分怎样
- 修复后建议执行什么

如果项目绑定了 profile，它还应该帮助你识别：

- 当前是否存在 `required_evidence_missing`
- 当前是否存在 `required_case_missing`
- 当前是否存在 `contract_drift`

也就是说，v1.1.7 的 `doctor advise` 不再只是“环境诊断”，还开始承担项目级验收阻断解释。

---

## 10.4 `verify run`

当项目需要走特定 skill 验收时，使用：

```bash
beacon verify run "<feature>" --project-root . --version v1.1.7 --profile "<profile>" --json
```

它适合：

- 多服务项目
- UAT / pipeline / gateway / logs / SQL 联动验证
- 希望把外部项目 skill 纳入 Beacon 验收链路

对像 Rolo 这样的项目，`verify run` 是 v1.1.7 最关键的新入口之一。

---

## 11. reopen 的正确用法

当你遇到这些情况时应该 `reopen`：

- frozen 后需求变更
- implementing 中途 scope 变化
- accepted 后又发现必须重做

命令：

```bash
beacon reopen "<feature>" --project-root . --version v1.1.7 --reason change-request
```

效果：

- 当前 revision 变成 `superseded`
- 新 revision 变成 active revision
- 后续重新 `freeze → implement → verify → accept`

不要手工覆盖旧 revision。

---

## 12. 评分怎么看

`help` / `doctor advise` / `status` 会给 4 个核心评分：

## 12.1 `test_score`

代表测试充分性。

低分意味着：

- AC 覆盖不足
- TC 执行不足
- verify 没过

## 12.2 `closure_score`

代表闭环完成度。

低分意味着：

- revision / writeback / verify / accept 还没完整落地

## 12.3 `readiness_score`

代表是否适合进入下一阶段。

低分意味着：

- 当前还没 ready
- 先别继续往下走

## 12.4 `quality_score`

代表质量风险。

低分意味着：

- 有 review / verify 风险
- 先修问题再 accept / release

---

## 13. 常见输出物

## 13.1 需求文档

```text
docs/beacon/v1.1.7/user-story/<feature>.md
docs/beacon/v1.1.7/prd/<feature>.md
docs/beacon/v1.1.7/qa/test-cases/<feature>.md
```

## 13.2 机器状态

```text
docs/beacon/v1.1.7/.machine/user-story/<feature>.json
docs/beacon/v1.1.7/.machine/qa/
docs/beacon/v1.1.7/.machine/execution/
```

## 13.3 review / execution 证据

```text
docs/beacon/v1.1.7/execution/review-spec-<feature>.json
docs/beacon/v1.1.7/execution/review-quality-<feature>.json
docs/beacon/v1.1.7/execution/implementation-summary-<feature>.json
docs/beacon/v1.1.7/execution/native-team/<feature>/<run_id>/
```

## 13.4 运行时状态

```text
.beacon/implement/<run_id>/
.beacon/state/implementation-<feature>.json
.beacon/auto-test-status.json
.beacon/gate-report.json
```

---

## 14. 常见问题

## 14.1 为什么 implement 被拒绝

典型原因：

- `revision_not_frozen`

先执行：

```bash
beacon freeze "<feature>" --project-root . --version v1.1.7
```

## 14.2 为什么 accept 被拒绝

典型原因：

- AC 没 verified
- TEST 没 passed
- revision 不是 frozen

先执行：

```bash
beacon review quality "<feature>" --project-root . --version v1.1.7 --json
beacon doctor advise --project-root . --version v1.1.7 --feature "<feature>" --json
```

## 14.3 为什么 help 一直建议 freeze

说明当前仍处于：

- `draft`
- `refined`
- 或 active revision 还没冻结

## 14.4 为什么 reopen 后不能直接继续 verify

因为 reopen 会开启 **新 revision**。

正确路径是：

```text
reopen → freeze → implement → verify → accept
```

---

## 15. 推荐的最小实战脚本

### 15.1 小需求闭环

```bash
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
beacon freeze "<feature>" --project-root . --version v1.1.7
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-single --json
beacon review quality "<feature>" --project-root . --version v1.1.7 --json
beacon review accept "<feature>" --project-root . --version v1.1.7 --json
```

### 15.2 复杂需求闭环

```bash
beacon status --board --project-root . --version v1.1.7 --feature "<feature>"
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
beacon freeze "<feature>" --project-root . --version v1.1.7
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-team --json
beacon review spec "<feature>" --project-root . --version v1.1.7 --json
beacon review quality "<feature>" --project-root . --version v1.1.7 --json
beacon review accept "<feature>" --project-root . --version v1.1.7 --json
beacon gate check release --project-root . --version v1.1.7 --json
```

### 15.3 变更重开闭环

```bash
beacon reopen "<feature>" --project-root . --version v1.1.7 --reason change-request
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
beacon freeze "<feature>" --project-root . --version v1.1.7
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-team --json
```

---

## 16. 推荐继续阅读

先读：

- `SUMMARY.md`
- `COMMANDS.md`
- `getting-started-10-minutes.md`

再按需深入：

- `execution/scenario-quick-reference.md`
- `execution/command-reference.md`
- `execution/help-doctor-navigator-contract.md`
- `execution/revision-reopen-writeback-contract.md`
- `execution/native-runner-and-agent-roles.md`

---

## 17. 一句话总结

Beacon v1.1.7 的正确用法，不是“记命令树”，而是：

```text
先看 status / help / doctor advise
再 freeze / implement / review / accept
需求变化时用 reopen 开启新 revision
```

只要沿这条线走，v1.1.7 就能形成正式、可追踪、可重开的闭环。
