# Beacon v1.2.0 完整使用文档（汇总版）

> 目标：把当前已接受发布线（`v1.2.0`）的使用方式收敛成一份可直接执行的单文档。  
> 定位：操作手册总入口；细节规范仍以各专题文档为准。

---

## 1. 版本与口径（先对齐）

- 当前运行时主发布线：`v1.2.0`
- 当前包版本：`1.2.0`
- 当前正式文档事实源：`docs/beacon/v1.2.0/`
- 运行时状态目录：`.beacon/`

补充：

- `v1.2.1` 在仓库中是 **partial runtime supplement line**（补充线），不替代 `v1.2.0` 主发布口径。

---

## 2. 先记住的主链

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

这条主链是 Beacon 的唯一中心。其它能力（如 `skill discover`、prototype、QA evolve）都必须服务这条链，不能另起产品中心。

---

## 3. 30 秒最短安全路径

```bash
beacon ask "<goal>" --project-root . --version v1.2.0 --plan-only --json
beacon workflow start "<feature>" --project . --version v1.2.0
beacon think start "<feature>" --project . --version v1.2.0
beacon user-story create "<feature>" --project . --version v1.2.0
beacon prd create "<feature>" --project . --version v1.2.0
beacon test-case create "<feature>" --project . --version v1.2.0
```

这条路径保证你先拿到路由，再进入可追踪的 workflow 主链。

---

## 4. 完整执行流程（推荐顺序）

### Step 0：确认上下文

```bash
beacon --version
beacon status --board --project-root . --version v1.2.0
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
```

### Step 1：启动 workflow

```bash
beacon workflow start "<feature>" --project . --version v1.2.0
```

### Step 2：生成 requirement 主链

```bash
beacon think start "<feature>" --project . --version v1.2.0
beacon user-story create "<feature>" --project . --version v1.2.0
beacon prd create "<feature>" --project . --version v1.2.0
beacon test-case create "<feature>" --project . --version v1.2.0
```

### Step 3：项目绑定（按需）

```bash
beacon skill discover --project-root . --dry-run --json
beacon skill discover --project-root . --apply-recommended --no-dry-run --json
beacon profile discovery --project-root . --json
beacon skill doctor --project-root . --json
```

说明：

- `skill discover` 采用固定合同：`detect → recommend → preview → apply`
- discovery 状态写入：`.beacon/state/skill-discovery/`
- 仅显式 apply 才会修改配置

### Step 4：冻结与实现

```bash
beacon freeze "<feature>" --project . --version v1.2.0 --json
beacon implement plan "<feature>" --project . --version v1.2.0 --json
beacon implement list-runners --json
beacon implement run "<feature>" --project . --version v1.2.0 --runner native-single --json
```

### Step 5：QA、评审、验收

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --json
beacon review quality "<feature>" --project . --version v1.2.0 --json
beacon review accept "<feature>" --project . --version v1.2.0 --reviewer qa --json
```

### Step 6：放行与发布

```bash
beacon gate check release --project-root . --version v1.2.0 --json
beacon release check v1.2.0 --project .
beacon release create v1.2.0 --project .
```

---

## 5. QA autoresearch 稳定闭环（四段式）

`v1.2.0` 中，autoresearch 不是单一“魔法命令”。稳定做法是：

```bash
beacon qa run "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
beacon qa evolve "<feature>" --project . --version v1.2.0 --mode story-exhaustive --json
beacon qa audit label <run_id> <scenario_id> --label <label> --project . --json
beacon version experiment "QA autoresearch for <feature>" --version v1.2.0 --project . --json
```

边界：

- 允许优化 bounded QA policy surfaces
- 不允许把它扩成“无限自治修复平台”
- 不允许覆盖 release verdict 或接管项目私有执行逻辑

---

## 6. 自然语言最小入口（三命令）

```bash
beacon ask "<自然语言目标>" --project-root . --version v1.2.0 --plan-only --json
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
beacon status --board --project-root . --version v1.2.0
```

推荐话术（高频）：

1. 帮我开始「<feature>」主链
2. 帮我继续「<feature>」，告诉我下一步
3. 帮我检查「<feature>」当前卡点
4. 帮我为当前项目推荐 Beacon skill/profile，先预览
5. 帮我对「<feature>」做 QA 验收
6. 帮我检查现在是否满足 release 条件

---

## 7. 产物落点（人机分层）

- 人类执行文档：`docs/beacon/v1.2.0/execution/*.md`
- 机器执行产物：`docs/beacon/v1.2.0/.machine/execution/*.json`
- 需求主链文档：`docs/beacon/v1.2.0/{think,user-story,prd,qa/test-cases}/`
- 运行时状态：`.beacon/`

注意：`execution/` 中出现机器 JSON 属于 surface drift，应修复回 `.machine/execution/`。

---

## 8. 失败恢复（最常用）

```bash
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
beacon doctor verify-materials --project-root . --version v1.2.0 --strict --json
beacon skill discover --project-root . --dry-run --json
beacon qa run "<feature>" --project . --version v1.2.0 --json
beacon gate check release --project-root . --version v1.2.0 --json
```

---

## 9. 深入阅读索引（按顺序）

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `./workflow-usage-guide.md`
4. `./natural-language-trigger-handbook.md`
5. `./qa-autoresearch-usage-guide.md`
6. `./boundaries.md`
7. `../release/v1.2.0.md`

---

## 10. v1.2.1 补充线如何使用

如果你需要 Codex prompt submit debug 能力，可单独使用：

```bash
beacon debug codex-user-prompt-submit --project-root . --version v1.2.1
```

但请保持认知：

- 主发布线仍是 `v1.2.0`
- `v1.2.1` 是补充能力，不是主线切换
