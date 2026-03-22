# Test Cases: Beacon 人机协作分层与 `.machine` 迁移

**Feature**: beacon-human-machine-artifact-layering  
**Version**: v1.1.5

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | Human primary surface paths are defined | 人类主阅读面路径集合明确 |
| TC-002 | contract | Machine surface paths are defined | `.machine/` 路径集合明确 |
| TC-003 | contract | Runtime internal surface is separated | `.beacon/` 不被当成正式交付文档 |
| TC-004 | contract | Memory 4-layer model documented | store/lifecycle/feedback/consumption 四层明确 |
| TC-005 | contract | Doctor repair scope documented | 路径+索引+引用修复职责明确 |
| TC-006 | contract | Human entry paths exclude machine JSON from primary reading path | JSON 不再被列为 primary artifact |
| TC-007 | integration | Status/report/gate still depend on machine and memory surfaces | 依赖关系被明确记录 |
| TC-008 | integration | QA matrices are treated as machine artifacts | QA JSON 被归类为 machine surface |
| TC-009 | review | Summary/release only point to human-facing materials | 人类入口收口 |
| TC-010 | review | No compatibility-first language remains in PRD | 文档没有兼容性导向表述 |
