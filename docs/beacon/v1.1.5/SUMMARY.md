# Beacon v1.1.5 Summary

**主题**: 人机协作分层、memory 投影收口、`.machine` 机器面迁移  
**状态**: Requirement Materials Only  
**日期**: 2026-03-20

---

## 本版目标

v1.1.5 聚焦一个核心问题：

> Beacon 的正式交付物既服务人类，也服务机器，但当前两类受众被迫阅读同一层产物，导致人类认知负担过高。

因此，本版要正式冻结：

1. 人类主阅读面（human primary surface）
2. 机器读取面（machine secondary surface）
3. runtime 内部面（`.beacon/`）
4. memory 模块的四层模型
5. `doctor` 作为破坏性版本修复器的职责

## 当前结论

- v1.1.5 将 `.machine/` 设为机器工件的正式目标路径；
- 人类默认不再以 JSON 为主阅读路径；
- Beacon 不删除 machine artifacts，而是把 machine artifacts 从“人类主阅读路径”降级为“机器校验输入”；
- Beacon memory 应正式拆成：store / lifecycle / feedback assimilation / consumption-projection 四层；
- 不做兼容性长期设计；旧版本包需要通过 `doctor` 修复到 v1.1.5 规范。

## 本版新增物料

### 主链文档
- `docs/beacon/v1.1.5/user-story/beacon-human-machine-artifact-layering.md`
- `docs/beacon/v1.1.5/prd/beacon-human-machine-artifact-layering.md`
- `docs/beacon/v1.1.5/qa/test-cases/beacon-human-machine-artifact-layering.md`
- `docs/beacon/v1.1.5/qa/test-cases/beacon-human-machine-artifact-layering.ac-test-matrix.json`
- `docs/beacon/v1.1.5/qa/test-cases/beacon-human-machine-artifact-layering.qa9-matrix.json`

### 执行层文档
- `docs/beacon/v1.1.5/execution/boundaries.md`
- `docs/beacon/v1.1.5/execution/human-machine-collaboration-norm.md`
- `docs/beacon/v1.1.5/execution/memory-architecture-and-projection.md`
- `docs/beacon/v1.1.5/execution/doctor-repair-scope.md`
- `docs/beacon/v1.1.5/execution/safe-implementation-plan.md`

### 发布文档
- `docs/beacon/v1.1.5/release/v1.1.5.md`

## 版本说明

- 本稿是 v1.1.5 需求物料，不代表 Beacon 运行时已经完成 v1.1.5 实现；
- 本版允许破坏性版本演进；
- 本版不讨论长期兼容方案，只讨论 v1.1.5 规范与 `doctor` 的修复职责。

### LLM / Skill 提示词文档
- `docs/beacon/v1.1.5/user-story/beacon-llm-skill-prompt-first-principles.md`
- `docs/beacon/v1.1.5/prd/beacon-llm-skill-prompt-first-principles.md`
- `docs/beacon/v1.1.5/qa/test-cases/beacon-llm-skill-prompt-first-principles.md`
- `docs/beacon/v1.1.5/qa/test-cases/beacon-llm-skill-prompt-first-principles.ac-test-matrix.json`

### Autoresearch / Eval Lab 文档
- `docs/beacon/v1.1.5/user-story/beacon-autoresearch-eval-lab.md`
- `docs/beacon/v1.1.5/prd/beacon-autoresearch-eval-lab.md`
- `docs/beacon/v1.1.5/qa/test-cases/beacon-autoresearch-eval-lab.md`
- `docs/beacon/v1.1.5/qa/test-cases/beacon-autoresearch-eval-lab.ac-test-matrix.json`
- `docs/beacon/v1.1.5/execution/eval-lab-benchmark-surface.md`
- `docs/beacon/v1.1.5/execution/keep-discard-policy.md`
- `docs/beacon/v1.1.5/execution/drift-auditor-minimum-loop.md`

## 实现准备度判断

基于当前仓库状态，`v1.1.5` 的结论应明确为：

- **需求物料已经足够开工**
- **运行时代码尚未达到 v1.1.5**
- **可以实现，但不能直接视为可发布版本**

当前判断依据：

1. `v1.1.5` 已经是仓库里最大的版本目录，`auto` 会优先解析到它；
2. Beacon 当前 runtime 管理口径仍停在 `v1.1.4`；
3. `v1.1.5` 的 materials 已齐，但 delivery / gate 还没有闭环；
4. 因此 `v1.1.5` 现在应被视为 **requirements-ready, implementation-pending**。

## 安全实现结论

`v1.1.5` 可以实现，但必须保证不改变 Beacon 本质功能。

安全实现范围：

- 人机分层与 `.machine` 迁移
- human primary surface 收口
- `doctor` 破坏性修复职责
- LLM / skill prompt 合同

首轮不应扩张的范围：

- 新 orchestration 能力
- 新 runner 平台能力
- 全仓自动研究 / 自动修改
- 把 Beacon 演进为 agent lab

实现顺序与约束详见：

- `docs/beacon/v1.1.5/execution/safe-implementation-plan.md`
