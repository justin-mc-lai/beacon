# Beacon Brainstorm: v1.4.11 Aggregate Projection Lifecycle Binding Gap

- version: `v1.4.11`
- mode: `requirement-convergence`
- status: `analysis-only`
- date: `2026-05-27`

## 结论

这次版本级 aggregate 对齐不是新 feature，也不是 release，更不应该是新生命周期。

更准确的名字不是 `aggregate truth`，而是 `version aggregate projection`：它是版本总账投影 / read model，用来汇总已经冻结、实现、QA 通过的 feature。

大白话说：单个 feature 已经做完了，但版本总表还不知道它做完了。release check 查的是版本总账，所以总账漏了，它就会挡住发布。

## 发现的问题

`beacon-design-human-subskills-closure-contract` 已经完成：

- change / PRD / user-story / test-case 已冻结。
- implement evidence 已写入。
- QA acceptance 已通过。
- 12 个 AC / 12 个场景都 accepted。

但版本聚合层一开始仍然只有 8 条 feature：

- `docs/beacon/v1.4.11/SUMMARY.md`
- `docs/beacon/v1.4.11/change/v1.4.11.md`
- `docs/beacon/v1.4.11/.machine/change/v1.4.11.json`

直接原因是缺少：

```text
docs/beacon/v1.4.11/.machine/change/beacon-design-human-subskills-closure-contract.json
```

`release create` 的聚合生成器主要读取每个 feature 的 `.machine/change/<feature>.json`。只有 refreeze transaction、revision、QA acceptance 不够；没有 feature change machine payload，版本 change 聚合器就看不见这条 feature。

这里的关键点是：`.machine/change/<feature>.json` 不是需求真相，它只是 release-facing 版本聚合投影的输入。

## 为什么它会像“跳出生命周期”

当前 lifecycle 是：

```text
change/refreeze -> implement -> qa -> release check
```

但版本 aggregate truth 实际上在两处被动发生：

```text
release create -> 生成版本 change
release check -> 检查版本 change 是否包含当前 feature
```

这导致一个空档：

```text
QA 通过
但版本聚合输入未生成
release check 才发现漏账
```

所以它看起来像“生命周期外单独补账”。

但正确判断是：不应该新增一个 `aggregate-sync` 生命周期节点，而应该把这个动作收回现有 lifecycle surface 的内部职责里。

生命周期仍然应该保持：

```text
change/refreeze -> implement -> qa -> release check
```

aggregate projection 只是这条链上的内部投影维护和 gate 输入校验：

- QA 通过时，应该同步 feature-level release projection。
- release create 时，应该重建 version-level aggregate projection。
- release check 时，应该 fail-closed 校验 version aggregate 是否包含当前 QA accepted feature。

也就是说，它是 existing lifecycle 的写回/校验副作用，不是一个让人手动进入的新阶段。

## 本次对齐做了什么

本次补齐了：

- `docs/beacon/v1.4.11/.machine/change/beacon-design-human-subskills-closure-contract.json`
- `docs/beacon/v1.4.11/change/v1.4.11.md`
- `docs/beacon/v1.4.11/.machine/change/v1.4.11.json`
- `docs/beacon/v1.4.11/SUMMARY.md`
- `docs/beacon/v1.4.11/.machine/testing/test-contract-index.json`

并重新校验：

```bash
rtk python3 -m beacon.main release check v1.4.11 --project . --json
```

结果：

- `status=pass`
- `release_ready=true`
- `feature_count=9`
- current feature included
- 仍有 `ceo challenge coverage current` warning，但不是 blocker。

## 是否能补回生命周期内

可以，但不是通过新增 lifecycle step。

正确做法是把 aggregate projection 绑定到现有 QA / release surface 的内部 invariant：

1. QA acceptance 通过后，自动生成或校验 `.machine/change/<feature>.json`。
2. 自动重建 `change/<version>.md` 和 `.machine/change/<version>.json`。
3. 自动校验 SUMMARY 的 feature count、feature list、QA evidence refs。
4. 自动刷新 test-contract-index。
5. release check 前 fail-closed 校验 current feature 已进入版本聚合。

用户看到的主链仍然是：

```text
change/refreeze -> implement -> qa -> release check
```

内部执行可以是：

```text
qa acceptance writeback
  -> feature change projection writeback
  -> version aggregate projection refresh
  -> test-contract-index refresh/verify
release check
  -> aggregate inclusion gate
```

这叫 projection writeback / release preflight，不叫 lifecycle。

## 建议的 runtime 改法

最小改法：

```text
beacon qa run 成功后提示并可执行：
beacon release create <version> --project .
beacon doctor build-test-contract-index "<feature>" --project-root . --version <version> --json
beacon doctor verify-test-contract-index "<feature>" --project-root . --version <version> --strict --json
```

更正确的改法：

```text
新增内部函数或 doctor repair：version aggregate projection refresh
```

它做固定动作，不靠 skill 临场解释：

- 输入：`project_root`、`version`、`feature`
- 读取：feature change markdown、revision、QA acceptance、implementation evidence
- 生成：feature machine change payload
- 重建：version change markdown / machine payload
- 校验：SUMMARY / version change / test-contract-index / current feature inclusion
- 输出：machine-readable aggregate sync verdict

但它不应该成为：

- 新 stage
- 新 human-facing lifecycle surface
- 新 release 前人工必跑命令
- 新 truth source

更合适的落点：

- `beacon qa run` 的 acceptance writeback 后置动作。
- `beacon release create` 的确定性重建逻辑。
- `beacon release check` 的 fail-closed 校验逻辑。
- `beacon doctor` 的 repair-only 命令。

## 不建议的做法

- 不建议每次 release 前靠人工手补 SUMMARY。
- 不建议把 `release create` 当成隐式修复器，因为它只读已有 feature payload，缺 payload 时不会知道漏了什么。
- 不建议让 QA pass 直接等于版本 release ready；中间必须有版本聚合账本。
- 不建议把版本聚合账本做成新的 lifecycle stage。
- 不建议让用户在 `qa` 和 `release` 之间多记一个人工步骤。
- 不建议把 brainstorm 输出当 truth。这个分析只说明缺口，正式规则要通过后续 change/refreeze 冻结。

## 推荐下一跳

如果要把这个问题彻底补进 Beacon lifecycle，下一条 feature 可以冻结为：

```text
version-aggregate-projection-guard-contract
```

目标不是做新产品能力，也不是新增生命周期，而是让现有 `qa` / `release` surface 自动维护版本聚合投影，并在 release check 里 fail-closed。
