# Beacon v1.1.10 QA, Implement, Release, And Feedback Loop

## 闭环核心

Beacon 当前真正复杂的不是“怎么跑一个命令”，而是：

```text
qa finding
→ release/gate judgement
→ implement follow-up
→ technical archive
→ requirement rewrite
→ next QA / next version
```

## QA 层

关键源码：

- `beacon/commands/qa.py`
- `beacon/utils/qa_feature.py`
- `beacon/utils/exhaustiveness.py`
- `beacon/utils/release_scorecard.py`
- `beacon/utils/qa_runtime.py`

关键责任：

- feature-aware QA
- story-scenario map
- browser evidence / replay
- session reuse
- release/gate input

## Implement 层

关键源码：

- `beacon/commands/implement.py`
- `beacon/utils/implement_native.py`
- `beacon/utils/learning_loop.py`

关键责任：

- 执行实现任务
- 写 runtime raw
- 生成 implementation summary
- 生成 technical implementation archive
- 生成 requirement rewrite input

## Release/Gate 层

关键源码：

- `beacon/commands/gate.py`
- `beacon/commands/release.py`
- `beacon/commands/report.py`
- `beacon/commands/status.py`

关键责任：

- 判断是否具备放行条件
- 汇总 QA、exhaustiveness、learning signals
- 对人类展示 release readiness

## Feedback/Learning 层

关键源码：

- `beacon/utils/learning_loop.py`
- `beacon/utils/debug_feedback.py`

关键责任：

- benchmark corpus
- keep/discard
- requirement rewrite input
- baseline uplift

## 这条闭环为什么要写进源码架构文档

因为很多真实问题不是出在单点模块，而是出在回流断裂：

- QA 发现缺陷，但 implement 没接住
- implement 修了，但技术归档没写
- 技术归档有了，但 requirement rewrite 不更新
- release 只看结果，不看 evidence chain

如果不把这条闭环显式画出来，后续变更很容易只修表层。
