# Change: design-craft-absorption-v1611

## Intent

把 `ui-skills` 的 4 个高价值 craft 能力吸收进 `beacon-design` support layer，不重做 design lifecycle，不扩展 1+6 public surface。

## Before

- beacon-design 有 system/explore/polish/prototype 治理与上游（impeccable / ui-ux-pro-max）
- 缺代码级 anti-slop / a11y / motion / read-only improve 手术刀
- UI craft 能力不足时容易靠通用模型自由发挥

## After

- `beacon-design/references/craft/` 承载 4 module
- `design route craft` + router 选择最小集合
- 输出严格 support-only，绑定路径显式
- metadata 与 registry 长尾 defer

## Impact

- skills/beacon/beacon-design/**（渐进引用与 route）
- 可能的 CLI `beacon design route craft`
- 测试：craft router/schema/write-guard
- **不改** goal/plan/truth/implement/qa/release 主状态机

## Migration

- 无旧包兼容读取要求
- 旧 polish/system 路由保留
- craft 为增量能力

## Status

draft requirement package R0 — not formally frozen
