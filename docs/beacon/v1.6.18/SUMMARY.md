# Beacon v1.6.18 — truth FSM 门禁收口

## 定位

`v1.6.18` 接续 `v1.6.17` 交付线，修复 Beacon 自身 truth 需求物料门禁的自锁与误判：生成出来的 truth 骨架通不过自己的冻结门，`truth review` 与 `freeze` 对终态各判一套，非法转移段里的自然语言句子被当成机器边。

## Program

- 单 lake：
  - `beacon-truth-fsm-terminal-unification`（terimal 结构性定义 + review/freeze 单一规则 + 非法转移结构化语法）
- truth canonical: `main`（实现与验收在 worktree，验收后合并）

## 核心结果

1. 生成器对自己的门禁封闭：`render_truth_package` 与 `render_intent_first_truth` 产出的骨架经 `validate_truth_fsm` 判定 `blocked=False`。
2. `truth review` Check B 与 `freeze` 共用同一校验函数，对同一包判定一致（domain 缺 FSM 双拦，非 domain 双跳过）。
3. 终态按结构判定：无转出边的目标状态不再硬拦（仅告警）；转移缺目标（空 To）硬拦。
4. 非法转移仅认 `- illegal: a -> b` 前缀与 `from|to` 表格行；含箭头的散文不再触发 `illegal_declared_as_legal`。
5. `attach_fsm_mermaid` 对过期投影重算，且不改写 FSM 标题之前的无关 mermaid 块；被拦的 `freeze` 不改写 truth.md。

## 发布面

- release notes: `docs/beacon/v1.6.18/release/v1.6.18.md`
- execution: `docs/beacon/v1.6.18/execution/`
- source architecture: `docs/beacon/v1.6.18/source-architecture/`
- feature package: `docs/beacon/v1.6.18/features/beacon-truth-fsm-terminal-unification/`
