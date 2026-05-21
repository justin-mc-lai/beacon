# Change: markdown-first-freeze-truth-and-minimal-machine-state-contract

**Version**: `v1.4.8`
**Status**: `frozen`
**Revision**: `R3`
**Generated**: `2026-05-21`

## Why This Change Exists

v1.4.8 已经冻结“物料强 gate 与人类面子 skill 原子写回契约”，但该方案暴露出新的系统性问题：需求冻结阶段生成的 `.machine/*.json` 过多、过大、重复复制 Markdown truth，导致 token 成本高、运行慢，并制造新的 truth/cache 漂移风险。

本 change 冻结一个更小的材料架构：

- Markdown is truth
- JSON is cache/state
- No fulltext mirrors
- Runtime JSON only
- Gate reads Markdown first

## Delta

- 将需求冻结 truth 归还给 Markdown 三件套及相关人类材料。
- 将冻结阶段 JSON 收缩为最小状态缓存。
- 禁止机器 JSON 复制整篇 Markdown。
- 保留 implement / QA / release 运行时 JSON。
- 要求 gate 先解析 Markdown，再用最小 state cache 校验 hash / revision / refreeze status。

## Freeze Intent

本次只冻结 requirement truth，不执行代码实现、QA 或 release。

## Traceability

- `docs/beacon/v1.4.8/research/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/v1.4.8/source-architecture/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/v1.4.8/prd/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/v1.4.8/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- `docs/beacon/v1.4.8/qa/test-cases/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
