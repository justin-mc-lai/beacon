# State Flow Map

- `route-preview`: 先解释 route 推荐与当前建议的 Beacon surface
- `change-required`: 若触及 frozen truth，必须从 route 面回到 change
- `learning-applied`: 说明本次 route 或说明消费了哪些 learning hint
- `learning-stale`: 旧 learning 被降级，不再继续误导
- `diagram-triggered`: 三件套进入 diagram / semantic 深度推理
- `dual-read-mismatch`: 新旧判断不一致，不能直接 cut over
- `guardrail-blocked`: Python guardrail 仍阻断 execution
- `implement-ready`: prototype freeze 已完成，且可进入 implement
