# Beacon v1.1.6 Doctor 修复范围

## Doctor 在 v1.1.6 的职责

### 1. 路径修复
- execution JSON -> `.machine/execution/`
- QA matrix JSON -> `.machine/qa/`

### 2. 索引修复
- 生成 / 修复 `execution/index.md`
- 生成 / 修复 `qa/test-cases/index.md`

### 3. 引用修复
- 更新 `SUMMARY.md`
- 更新 `release/<version>.md`
- 更新 execution / qa 主入口引用

### 4. 校验修复结果
- 人类主入口完整
- machine 面完整
- runtime / gate / report 依赖关系不丢失

## 明确不做
- 长期双写兼容
- v1.1.6 运行时代码以外的兜底迁移策略
