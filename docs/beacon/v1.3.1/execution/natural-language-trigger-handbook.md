# Beacon v1.3.1 Natural Language Trigger Handbook

`v1.3.1` 在 Codex / Claude 中推荐通过 host-visible skill pack 触发，而不是要求人类记住完整 CLI catalog。

## Preferred public intents

- requirements / ambiguity closure:
  - `beacon-prd`
- user stories / acceptance:
  - `beacon-user-story`
- test and acceptance design:
  - `beacon-test-case`
- implementation:
  - `beacon-implement`
- verification / release confidence:
  - `beacon-qa`
  - `beacon-release`
- blocked / next step:
  - `beacon-help`
  - `beacon-status`
  - `beacon-doctor`

## Compatibility note

旧的自然语言入口说明可参考 `v1.3.0`，
但本地 Codex / Claude skill 使用应优先遵循 `v1.3.1` 的 6+3 surface。
