# Navigation Map

- `intent-router` -> `decision-surface-overview`: 点击核心 skill 卡片
- `intent-router` -> `guardrail-cutover-audit`: 点击需要改 truth 的推荐
- `decision-surface-overview` -> `skill-surface-detail`: 点击单个 skill
- `decision-surface-overview` -> `reasoning-contract-review`: 点击 reasoning input
- `decision-surface-overview` -> `learning-disclosure-center`: 点击 learning hint
- `skill-surface-detail` -> `decision-surface-overview`: 点击返回
- `learning-disclosure-center` -> `decision-surface-overview`: 点击返回
- `reasoning-contract-review` -> `decision-surface-overview`: 点击返回
- `guardrail-cutover-audit` -> `intent-router`: 点击返回
- `guardrail-cutover-audit` -> `decision-surface-overview`: 点击继续实现
