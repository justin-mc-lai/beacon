# Beacon v1.2.0 完整工作流使用指南

> 面向人类操作者的 `v1.2.0` 全流程说明。目标不是列出所有命令，而是告诉你 **什么时候该跑什么、为什么跑、会产出什么**。

---

## 1. 这份文档解决什么问题

`v1.2.0` 的主线已经收敛为：

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

但真正使用 Beacon 时，操作者通常会卡在这几个点：

1. 先用 `ask / help / status` 还是直接 `workflow start`
2. 项目什么时候需要 `skill discover`
3. `implement plan`、`implement run`、`qa run`、`review accept` 的先后顺序
4. 哪些 artifact 是正式交付物，哪些只是运行时状态
5. 什么时候算“真的可以 release”

这份指南就是把这些问题一次讲清楚。

---

## 2. 先记住 4 条总规则

### 2.1 默认入口优先级

如果你不知道下一步做什么，优先级是：

```text
help
→ ask
→ status
→ 再决定具体命令
```

不要盲猜下一步。

### 2.2 正式文档与运行时状态分层

- 正式交付文档：`docs/beacon/<version>/`
- 运行时状态：`.beacon/`

`docs/beacon/<version>/` 是 source of truth。  
`.beacon/` 是执行时证据与状态，不替代正式文档。

进一步拆分 execution surface：

- `docs/beacon/<version>/execution/`：**只放人类主读 Markdown**
- `docs/beacon/<version>/.machine/execution/`：**只放机器主读 JSON**

如果你在 `execution/` 里看到 `*.json`，那通常表示：

1. 历史版本包还没 repair
2. 某个命令面绕过了 machine-surface path helper

优先修命令，不要把混放当成正常现象。

### 2.3 `skill discover` 是项目绑定面，不是新产品中心

`beacon skill discover` 只负责：

```text
detect
→ recommend
→ preview
→ apply
```

它服务的是项目如何进入主链，而不是把 Beacon 变成泛化代码分析平台。

### 2.4 `release` 不是 workflow 内部阶段

主线到 `gate` 为止。  
`release` 是 **post-gate action**：

```text
workflow mainline complete
→ gate pass
→ release check / release create / git tag / GitHub release
```

---

## 3. 适合谁用这条完整流程

### 适合

- 想把需求、实现、QA、发布放到同一套版本包里的团队
- 想用 `v1.2.0` 主链做真实 feature delivery 的项目
- 想让 Beacon 在项目里做“要求 → 证据 → gate”闭环的人

### 不适合

- 只想临时写一份 markdown 模板
- 不关心 QA / gate / release evidence
- 想让 Beacon 直接接管项目私有部署/运维平台

---

## 4. 最短安全路径

如果你只想先安全跑通一轮，请用这条：

```bash
beacon ask "<goal>" --project-root . --version v1.2.0 --plan-only --json
beacon workflow start "<feature>" --project . --version v1.2.0
beacon think start "<feature>" --project . --version v1.2.0
beacon user-story create "<feature>" --project . --version v1.2.0
beacon prd create "<feature>" --project . --version v1.2.0
beacon test-case create "<feature>" --project . --version v1.2.0
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

这条路径会把你带到：

- 已启动 workflow
- 已生成主链 requirement artifacts
- 已能通过 `help` 获得下一步推荐

如果你想专门给最终用户一份“少记命令、多说意图”的版本，请同时阅读：

- `./natural-language-trigger-handbook.md`

如果你下一步要把 QA 做成 autoresearch 风格的受控演进，请继续阅读：

- `./qa-autoresearch-usage-guide.md`
- `./autoresearch-module-evolution.md`

---

## 5. 完整工作流：推荐顺序

下面是 `v1.2.0` 推荐的完整使用顺序。

### Step 0：确认版本与上下文

```bash
beacon --version
beacon status --board --project-root . --version v1.2.0
```

你要确认：

- 当前 CLI 版本是否是 `v1.2.0`
- 当前 docs / runtime / context 是否一致
- 项目是否已有正在进行的 feature

如果你已经在某个 feature 中途恢复，先跑：

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

---

### Step 1：从自然语言或阶段路由进入

#### 场景 A：你还没完全想清楚 feature

```bash
beacon ask "<goal>" --project-root . --version v1.2.0 --plan-only --json
```

#### 场景 B：你已经有 feature 名，但不知道下一步

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

#### 场景 C：你只想看当前全局状态

```bash
beacon status --board --project-root . --version v1.2.0
```

---

### Step 2：启动 workflow

```bash
beacon workflow start "<feature>" --project . --version v1.2.0
```

这一步会：

- 建立 workflow run
- 让后续 `help / gate / accept / release` 可以围绕同一条 run 做闭环

---

### Step 3：生成 requirement 主链

```bash
beacon think start "<feature>" --project . --version v1.2.0
beacon user-story create "<feature>" --project . --version v1.2.0
beacon prd create "<feature>" --project . --version v1.2.0
beacon test-case create "<feature>" --project . --version v1.2.0
```

标准产物：

- `docs/beacon/v1.2.0/think/...`
- `docs/beacon/v1.2.0/user-story/...`
- `docs/beacon/v1.2.0/prd/...`
- `docs/beacon/v1.2.0/qa/test-cases/...`
- `docs/beacon/v1.2.0/.machine/user-story/...`
- `docs/beacon/v1.2.0/.machine/qa/...`

---

### Step 4：按需要做项目绑定（可选但推荐）

如果这是一个真实项目而不是纯文档包，优先检查是否需要项目级 skill/profile。

#### 4.1 先看 Beacon 是否建议 discovery

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

如果返回中有：

```text
next_step.action = skill-discover
```

或者有 `skill_discovery_hint`，就继续下面这步。

#### 4.2 预览 discovery（默认推荐）

```bash
beacon skill discover --project-root . --dry-run --json
```

你会得到：

- `project_features`
- `recommended_templates`
- `recommended_skills`
- `recommended_profile_id`
- `config_diff`
- `.beacon/state/skill-discovery/<project>.json`

#### 4.3 明确 apply

```bash
beacon skill discover --project-root . --apply-recommended --no-dry-run --json
```

apply 后会把推荐绑定写回 `beacon.config.yaml`。

#### 4.4 查看 discovery 结果

```bash
beacon profile discovery --project-root . --json
beacon skill doctor --project-root . --json
```

---

### Step 5：冻结 / 规划实现

如果当前 revision 还未冻结，先冻结：

```bash
beacon freeze "<feature>" --project . --version v1.2.0 --json
```

然后编译 implementation plan：

```bash
beacon implement plan "<feature>" --project . --version v1.2.0 --json
```

你会得到：

- human plan：`docs/beacon/v1.2.0/execution/implementation-plan-*.md`
- machine plan：`docs/beacon/v1.2.0/.machine/execution/implementation-plan-*.json`
- progress ledger：`...progress.json`

---

### Step 6：执行实现

先看可用 runner：

```bash
beacon implement list-runners --json
```

再执行实现：

```bash
beacon implement run "<feature>" --project . --version v1.2.0 --runner native-single --json
```

如果项目配置了更适合的 runner，也可以换成：

- `native-team`
- `auto`
- 项目 skill 绑定出的 runner

实现后你应该能看到：

- technical archive
- implementation summary
- artifact update obligations

其中：

- human summary / archive markdown → `docs/beacon/<version>/execution/*.md`
- machine summary / archive json → `docs/beacon/<version>/.machine/execution/*.json`

---

### Step 7：运行 QA

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --json
```

`v1.2.0` 下，QA 要求围绕：

```text
story / AC order
→ scenario coverage
→ evidence pack
→ coverage_current / coverage_gap
→ continue_decision
```

重点检查：

- `status`
- `feature_scorecard.release_ready`
- `continue_decision`
- `coverage_gap`
- `repair_handoff`

如果 `continue_decision = stop_for_repair`，先修复，再重新跑 `qa run`。

---

### Step 8：质量评审

```bash
beacon review quality "<feature>" --project . --version v1.2.0 --json
```

通过标准：

- `status = pass`
- `gate_ready = true`

这一步会关闭 `review_quality` obligation。

---

### Step 9：正式 accept

```bash
beacon review accept "<feature>" --project . --version v1.2.0 --reviewer qa --json
```

通过后应看到：

- `status = accepted`
- `workflow_closure_complete = true`
- `workflow_gate_pass = true`

这一步会：

- 关闭 acceptance obligation
- 回填 workflow closure
- 刷新 terminal / gate / evidence / baseline / fingerprint

---

### Step 10：跑 release gate

```bash
beacon gate check release --project-root . --version v1.2.0 --json
```

通过标准：

- `status = Pass`
- `blocked_count = 0`
- `doc_impl_verdict.status = pass`

---

### Step 11：跑 release check

```bash
beacon release check v1.2.0 --project .
```

这一步检查的是：

- auto-test status
- gate report
- evidence manifest
- run_id/version 是否一致
- coverage artifact 是否 ready

看到 `Release conditions met` 才算真正可发版。

---

### Step 12：发布动作

Beacon 内：

```bash
beacon release create v1.2.0 --project .
```

Git / GitHub 层：

```bash
git checkout main
git pull --ff-only origin main
git merge --ff-only beacon/v1.2.0
git tag -a v1.2.0 -m "Release Beacon v1.2.0 runtime line"
git push origin main --follow-tags
```

---

## 6. 一张表看懂完整流程

| 阶段 | 推荐命令 | 通过标准 | 主要产物 |
| --- | --- | --- | --- |
| 路由/导航 | `beacon ask` / `beacon help` / `beacon status` | 能明确下一步 | 导航建议、状态板 |
| 启动 workflow | `beacon workflow start` | run 建立 | `.beacon/runs/...` |
| 需求主链 | `think` / `user-story` / `prd` / `test-case` | docs + `.machine` 完整 | `docs/beacon/v1.2.0/...` |
| 项目绑定 | `skill discover` / `profile discovery` | preview/apply 正常 | `.beacon/state/skill-discovery/...` |
| 计划 | `implement plan` | `status=planned` | plan md/json/progress |
| 实现 | `implement run` | `status=completed` | implementation summary / archive |
| QA | `qa run` | `status=passed` | QA evidence / scorecard |
| 质量评审 | `review quality` | `status=pass` | quality review artifact |
| 正式 accept | `review accept` | accepted + workflow closure | acceptance writeback |
| 放行 | `gate check release` | `Pass` | gate verdict |
| 发布确认 | `release check` | `Release conditions met` | release readiness |

---

## 7. 失败时怎么恢复

### 7.1 不知道下一步

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

### 7.2 requirement materials 有问题

```bash
beacon doctor verify-materials --project-root . --version v1.2.0 --strict --json
```

### 7.3 project binding 不清楚

```bash
beacon skill discover --project-root . --dry-run --json
beacon profile discovery --project-root . --json
beacon skill doctor --project-root . --json
```

### 7.4 QA 被 stop_for_repair

先看返回里的：

- `coverage_gap`
- `repair_handoff`
- `resume_command`

然后修复后再次执行：

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --json
```

### 7.5 release gate 不过

先跑：

```bash
beacon gate check release --project-root . --version v1.2.0 --json
```

如果想看最终是否已可发版，再跑：

```bash
beacon release check v1.2.0 --project .
```

---

## 8. 推荐阅读顺序

如果你要一边执行一边理解 `v1.2.0`，建议按这个顺序读：

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `./workflow-usage-guide.md`
4. `./command-surface-simplification-blueprint.md`
5. `./project-skill-qa-evolution-blueprint.md`
6. `../source-architecture/index.md`
7. `../release/v1.2.0.md`

---

## 9. 一句总结

`v1.2.0` 的正确打开方式不是“把所有命令都背下来”，而是：

```text
先 ask/help/status 拿路由
→ 再跑 workflow 主链
→ 需要项目绑定时用 skill discover
→ implement plan / run
→ qa
→ review quality
→ review accept
→ gate check release
→ release check
```

只有这样，Beacon 才会保持：

```text
requirements
→ evidence
→ gate
→ release
```

这条主链不漂移。
