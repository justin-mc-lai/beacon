---
name: beacon-gov-automation
description: Beacon v1.6.0 governor retirement guidance for the old scheduled automation surface. Use when legacy automation assets or commands are encountered and must be routed away from queue/job/launchd mode.
---

# Beacon Governor Automation

The historical scheduled automation surface is retired for active delivery.

Do not initialize, validate, refresh, or maintain the old queue/job/launchd
automation assets. Do not recommend `beacon automation` commands. Do not route
long-running implementation through scheduler jobs.

Preferred route:

```bash
beacon-loop goal "<goal>"
```

Boundary:

- `beacon-loop` may produce implementation evidence candidates only.
- Beacon truth, QA, and release surfaces remain the only closure authorities.
- Runtime records under `.beacon/loop/runs/**` are process records, not
  requirement truth.

If a user asks for old automation setup, report:

```text
automation retired; use beacon-loop goal
```

## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。
