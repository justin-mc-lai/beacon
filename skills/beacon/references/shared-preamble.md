# Beacon 共享守则（v1.6.0+）

> 单一来源。所有 beacon mode 文件引用本文件，不再逐字复制。

## 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

## HARD GATE

- Planner：只产 research/planning artifact，禁写 truth/实现/QA/release verdict。
- Generator：只在 resolver-selected truth 内写 truth/delivery artifact，不自证完成。
- Evaluator：只产 evidence verdict/finding/route，不改 truth 不修实现。
- Governor：只维护 context/metadata/archive/status，不成为主生命周期 stage。

## GIT_ADMISSION（truth 作者在 canonical 分支）

1. 解析 `truth_canonical`（默认 main/master）并核对当前 HEAD。
2. mismatch → `truth_canonical_branch_mismatch`，不写 requirement truth。
3. freeze/refreeze 产物提交在 `truth_canonical` 上。
