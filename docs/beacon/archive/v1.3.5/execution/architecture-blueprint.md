# Beacon v1.3.5 Architecture Blueprint

## Blueprint Goal

`v1.3.5` 不是 Beacon 管理端产品成品线，而是 Beacon `prototype` 的 wireframe freeze 线。

## Frozen Boundary

```text
docs/beacon/<version>/prd + user-story + test-case
→ Beacon prototype wireframe package
→ freeze / review / status
→ downstream v1.3.6 visual management console
```

- 上游 requirement truth 仍然是 `prd / user-story / test-case`。
- 中游是 Beacon `prototype` 产出的 wireframe 包。
- 下游 `v1.3.6` 管理端产品线消费这些冻结产物来实现正式 UI。

## Wireframe Layers

1. Summary layer
   - 页面清单、页面职责、优先级、关联 requirement
2. Navigation layer
   - 路由、返回路径、状态切换、禁止跳转
3. Page wireframe layer
   - 单页布局草图、模块块、用户动作、状态说明
4. Freeze layer
   - review / freeze / status 对草图包完整度的判断
