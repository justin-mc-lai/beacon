# Beacon v1.3.6 Architecture Blueprint

## Blueprint Goal

`v1.3.6` 是 Beacon 管理端看板与项目物料查看器的产品化实现线，但它必须建立在 `v1.3.5` 的 wireframe freeze artifact 之上。

如需查看 Beacon skill / host runtime / CLI 结构化执行内核本身的目标演进，请继续阅读：

- `./host-native-llm-and-skill-runtime-blueprint.md`

## Frozen Boundary

```text
docs/beacon + .beacon
→ normalized projection envelope
→ sqlite / pocketbase / pb_public
→ v1.3.5 wireframe package
→ Beacon UI console (v1.3.6)
```

- 上游 `docs/beacon + .beacon` 仍是正式真相。
- projection envelope / sqlite / pocketbase 仍是机器内部投影层。
- `v1.3.5` wireframe package 冻结页面结构、路由和状态说明。
- `v1.3.6` UI console 只负责展示、筛选、聚合、查看，不改写 truth。

## UI Product Layers

1. Portfolio layer
   - 面向 CEO / 一人公司经营者
   - 看多项目进度、阻塞、交付与介入点
2. Project layer
   - 面向项目负责人
   - 看版本、物料闭环、Git / worktree、当前阶段与下一步
3. Runtime layer
   - 面向实现治理者
   - 看 single / team / ralph 是否有效推进
4. Material viewer layer
   - 面向人类阅读者
   - 只读查看版本化 Markdown 物料
