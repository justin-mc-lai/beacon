# Beacon v1.4.12 总览

## 状态

- Version line: `v1.4.12`
- Current status: `frozen`
- 调研主题：真相三件套格式规范统一、目录-文档规范地图、图示真相闭环
- 当前版本聚合范围：2 个 frozen requirement package

## 调研输入

- `docs/beacon/archive/v1.4.12/research/version-material-file-map-contract.md`
- `docs/beacon/archive/v1.4.12/research/unified-truth-template-cli-contract.md`
- `docs/beacon/archive/v1.4.12/research/diagram-truth-triptych-closure.md`
- `docs/beacon/archive/v1.4.12/research/doubt-register-truth-spec-in-skill.md`
- `docs/beacon/archive/v1.4.12/source-architecture/version-material-file-map-contract.md`
- `docs/beacon/archive/v1.4.12/source-architecture/unified-truth-template-cli-contract.md`
- `docs/beacon/archive/v1.4.12/source-architecture/diagram-truth-triptych-closure.md`

## Frozen Feature Packages

```text
version-material-file-map-contract
unified-truth-template-cli-contract
```

## 版本聚合证据

- Feature count: `2`
- PRD:
  - `docs/beacon/archive/v1.4.12/prd/version-material-file-map-contract.md`
  - `docs/beacon/archive/v1.4.12/prd/unified-truth-template-cli-contract.md`
- User Story:
  - `docs/beacon/archive/v1.4.12/user-story/version-material-file-map-contract.md`
  - `docs/beacon/archive/v1.4.12/user-story/unified-truth-template-cli-contract.md`
- Test Cases:
  - `docs/beacon/archive/v1.4.12/qa/test-cases/version-material-file-map-contract.md`
  - `docs/beacon/archive/v1.4.12/qa/test-cases/unified-truth-template-cli-contract.md`

## 冻结边界

- 真相三件套格式规范：Section 标题纯英文无编号，Outline mermaid 图示 mandatory，表格列名纯英文固定，Language 字段与正文语言一致
- 目 录-文档规范地图：`version-features.json` 为 canonical feature 列表，所有 glob 发现迁移至 manifest 读取，无 compat fallback
- 旧版本视为已 release，不设格式兼容跳过
- 格式升级走 `beacon change --refreeze-chain`，baseline hash 变更是合法结果
- Diagram Truth Layer 保留为 complex feature 的 optional section
- Skill 层需新增 `truth-format-spec.md` 规范引用

## 依赖关系

- `version-material-file-map-contract` 先行（manifest 是 truth init 的前置依赖）
- `unified-truth-template-cli-contract` 依赖 manifest 集成
- 旧入口适配（`beacon prd create`、`prd_bootstrap.py`）归入 unified-truth-template-cli-contract

## 下一步

完成 refreeze 闭环后可进入 `beacon-implement`：
```bash
beacon implement --project . --version v1.4.12 --feature version-material-file-map-contract
beacon implement --project . --version v1.4.12 --feature unified-truth-template-cli-contract
```
