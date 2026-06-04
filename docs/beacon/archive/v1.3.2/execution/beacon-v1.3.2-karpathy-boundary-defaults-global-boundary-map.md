# Beacon v1.3.2 Karpathy 边界默认规范映射

**Feature**: `beacon-v1.3.2-karpathy-boundary-defaults`  
**Version**: `v1.3.2`  
**Type**: `global-boundary map`

## 参考来源

- `https://github.com/forrestchang/andrej-karpathy-skills`
- 本次提炼基于该仓库的 `README.md`、`CLAUDE.md`、`skills/karpathy-guidelines/SKILL.md`

## 映射表

| Karpathy 原则 | Beacon 默认全局规范候选 |
|---------------|--------------------------|
| Think Before Coding | 显式假设、歧义、取舍；需求不清不得静默执行 |
| Simplicity First | 最小正确改动；禁止 speculative abstraction |
| Surgical Changes | 只改当前请求需要的范围；禁止 drive-by refactor |
| Goal-Driven Execution | 每个非平凡任务必须绑定成功标准与验证证据 |

## 建议写入 `docs/beacon/global-boundaries.md`

### 1. 假设与歧义边界

- 不清楚时必须命名不确定性。
- 多解释并存时必须记录取舍。
- 关键需求不明时回到 `prd/user-story`，不得直接进入实现。

### 2. 简单优先边界

- 不为单次需求新增抽象。
- 不为未请求的未来扩展新增配置。
- 不扩大 scope 追求“完整感”。

### 3. 外科手术式改动边界

- 每个 changed file 必须能追溯到当前请求。
- 不格式化、重构、删除无关代码。
- 只清理自己改动制造的 orphan。

### 4. 目标驱动验证边界

- bug fix 要有复现或验证证据。
- feature 要有 acceptance/test 映射。
- refactor 要有 before/after 验证。

### 5. 轻量例外边界

- typo、单行 copy、明显无风险改动可跳过完整重流程。
- 但仍不得触碰无关文件。

## 不写入全局规范的内容

- 外部插件安装命令。
- Claude-only plugin 细节。
- 对 `karpathy-guidelines` skill 的运行时调用。
- 任何新增 Beacon 公开主命令。

## 后续实现检查点

- 更新 `docs/beacon/global-boundaries.md`。
- 更新 AGENTS / CLAUDE context setup，使目标项目可继承这些规则。
- 更新 help/doctor 输出，只在阻断或诊断时展示详细边界。
- 添加 tests，防止外部参考变成默认 runtime dependency。
