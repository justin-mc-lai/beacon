# 执行索引（v1.3.0）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `./artifact-language-contract.md`
4. `./version-semantics-contract.md`
5. `./codex-native-subagent-implementation-blueprint.md`
6. `../research/beacon-v1.3.0-codex-native-subagent-direction.md`
7. `../think/beacon-v1.3.0-simplified-codex-native-subagents.md`
8. `../user-story/beacon-v1.3.0-simplified-codex-native-subagents.md`
9. `../prd/beacon-v1.3.0-simplified-codex-native-subagents.md`
10. `../qa/test-cases/beacon-v1.3.0-simplified-codex-native-subagents.md`
11. `../release/v1.3.0.md`

## 说明

- `v1.3.0` 仍是规划线，不是当前 runtime release line。
- 这条线的重点是：在保持 Beacon 主链与 release truth 不变的前提下，引入受约束的 Codex 原生子代理能力。
- `implement run` 是第一条需要真正验证多代理闭环的执行面。
- “下一版本 + 子代理演进”类 prompt 应优先进入 `version` 规划面，再收敛到阶段实现。
- `./artifact-language-contract.md` 定义未来所有 artifact 类型的“中人 / 英机”统一规范。
- `./version-semantics-contract.md` 是 `beacon/version-semantics.json` 的中文镜像；两者必须视为同步的一体两面契约。
- `team` 在 `v1.3.0` 应作为稳定显性 surface 看待，而不仅是实现细节里的隐式模式。
