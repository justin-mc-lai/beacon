# Beacon v1.3.12 Machine Contract

本目录承载 `v1.3.12` requirement package 的最小 machine-readable 合同。

当前版本针对 `beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure` 至少包含：

- `requirement/*.freeze-contract.json`
- `requirement/*.completeness.json`
- `user-story/*.json`
- `qa/*.ac-test-matrix.json`
- `qa/*.qa9-matrix.json`
- `qa/*.story-scenario-map.json`

这些文件的职责不是宣称实现完成，而是把以下语义固定下来：

- requirement freeze 的 blocking / downgrade / pass 规则
- `accepted / rejected / deferred` 的补齐决策语义
- `user-story / test-case / delivery completeness` 的可消费结构
- 后续 `prototype / implement / qa / release` 必须读取的 requirement completeness 口径
