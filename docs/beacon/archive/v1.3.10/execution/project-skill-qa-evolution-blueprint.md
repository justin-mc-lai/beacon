# Beacon v1.3.10 Project Skill QA Evolution Blueprint

## 目的

明确 Beacon 核心与项目内 skill 的分工，避免把复杂项目协作策略塞进核心 metadata schema。

## 核心分工

- Beacon 核心：
  - topology
  - repo binding
  - version-scoped allowed working branch
  - requirement package dual-write gate
- 项目内 skill / policy：
  - integration branch
  - testing / uat merge choreography
  - service-specific collaboration rules

## QA 关注点

- 核心 metadata 是否保持极简
- support skill 是否只消费 resolved metadata view
- 项目级复杂策略是否仍留在项目内 skill，而未倒灌进 Beacon 核心
