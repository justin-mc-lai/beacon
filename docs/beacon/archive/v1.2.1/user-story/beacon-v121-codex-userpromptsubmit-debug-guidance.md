# User Story: Beacon v1.2.1 Codex UserPromptSubmit Debug Guidance

**Feature**: Beacon v1.2.1 - Codex UserPromptSubmit Debug Guidance  
**Version**: v1.2.1  
**Date**: 2026-04-10  
**Status**: Drafted supplement line

---

## Story 1: 作为 Codex 中的 Beacon 使用者，我希望系统能在我刚提交 prompt 时就识别 Beacon 意图

**验收标准**:

- `UserPromptSubmit` payload 必须可被 Beacon 读取
- payload 中的 `prompt/input/user_prompt/userPrompt/text` 候选字段必须兼容解析
- 解析后必须复用 Beacon 现有 intent router，而不是额外造一套路由规则

## Story 2: 作为模型协作者，我希望获得一段可以直接引导用户重写输入的上下文

**验收标准**:

- hook 输出必须包含 `hookSpecificOutput.additionalContext`
- 该上下文必须说明：
  - 当前推断意图
  - 边界状态
  - 推荐 Beacon 命令
  - 如何把输入改写成更规范的 Beacon 提示词
- 当请求混合了 Beacon 与非 Beacon 动作时，必须明确建议拆分输入

## Story 3: 作为 Beacon 维护者，我希望真实用户输入摩擦被记入 debug canonical 面

**验收标准**:

- hook 事件必须写入 prompt router history
- hook 事件必须写入 debug feedback canonical surface
- hook 事件必须生成 run-scoped snapshot，保留原始 prompt 与 adaptation 结果

## Story 4: 作为版本维护者，我希望这次增强仍然服从 `v1.2.0` 主链中心

**验收标准**:

- `v1.2.1` 只增强 prompt-ingress/debug 层
- 不新增新的产品中心
- 不改变 `PRD → user-story → QA` 作为唯一主链锚点的事实
