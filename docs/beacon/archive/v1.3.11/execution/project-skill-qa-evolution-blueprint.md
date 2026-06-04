# Beacon v1.3.11 Project Skill QA Evolution Blueprint

## 目的

明确 `v1.3.11` 中 Beacon 核心、project skill、doctor repair surface 的分工，避免把 PRD anti-drift 修复继续停留在人工脚本经验层。

## 核心分工

- Beacon 核心：
  - orchestration runtime 边界
  - PRD reconcile / audit / transaction pointer contract
  - stale mirror fail-closed gate
- project skill / project policy：
  - 具体项目的协作编排策略
  - 项目级 UX / workflow / release choreography
- doctor fallback：
  - machine sink 丢失
  - projection 损坏
  - 历史状态不可信时的 repair / rebuild

## QA 关注点

- PRD human truth 修订后，machine mirror 能否稳定重投影
- audit 是否能定位具体漂移 sink
- stale mirror 是否能阻断 implement / qa / release
- doctor fallback 是否只在 repair 场景暴露，而非挤占主链
