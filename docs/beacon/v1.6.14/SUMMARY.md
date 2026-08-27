# Beacon v1.6.14 — 批次1：FSM 升级 + FSM 测试生成 + Feature Map

## 定位

`v1.6.14` 是当前交付线。批次 1 把「功能地图方法论」与「状态机专业契约」落地：
L1 FSM 升级（mermaid 渲染 + 机器校验 + 行为 digest）、
L2 FSM 测试生成（GraphWalker 式 legal-walk 自动生成 + illegal 排除）、
L3 Feature Map（骨架 → 复现路由 → agent 自验证，单向投影）。

## Program

- 批次 1（3 个 lake）：
  - `beacon-v1614-fsm-mermaid-validate`（FSM mermaid + 校验 + digest + freeze 门禁）
  - `beacon-v1614-fsm-test-generation`（FSM legal-walk 测试生成 + illegal 排除）
  - `beacon-v1614-feature-map`（feature-map.md 骨架 + 复现路由 + agent 自验证）
- truth canonical: `main`（实现与验收在 worktree，验收后合并）

## 核心结果

1. truth 的 FSM 五元组自动附带 `stateDiagram-v2` mermaid 投影，文档可渲染。
2. FSM 机器校验进入 freeze 门禁：状态未定义 / 转移不合法 / illegal 未声明 → `truth_fsm_invalid` fail-closed。
3. 行为变化 digest vs 措辞变化 digest 分离（措辞改动不改变行为 digest）。
4. 从合法 FSM 自动生成 legal-walk 测试用例（vertex=断言、illegal 路径不生成），对接 v1.6.13 域湖 FSM 测试。
5. 每个 feature 派生 `feature-map.md`：入口 + 验证命令绑定 AC，复现路由 + agent 可自验证，单向投影不改 truth。

## 发布面

- runtime: `v1.6.12`（本批次以 docs/truth 面 + beacon 框架代码交付，runtime 语义未破坏）
- 正式版本面：SUMMARY / features truth 已冻结
