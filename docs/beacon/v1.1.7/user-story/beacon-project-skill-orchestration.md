# User Story: Beacon 项目级 skill profile、多 skill 编排与强证据验收（v1.1.7）

**Feature**: beacon-project-skill-orchestration  
**Version**: v1.1.7

**As a** Beacon 使用者 / 维护者 / 多服务项目交付负责人  
**I want** Beacon 支持内置 multi-skill、项目级 skill profile、可编排 verify runner 与 required evidence gate  
**So that** Beacon 能兼容像 Rolo 这样的真实项目工作流，并在 accept 前阻断“文档通过但真实链路未验证”的场景。

## Story Slices

### US-001: Beacon 支持内置 multi-skill registry
作为 Beacon 维护者，我希望系统内建正式 skill registry，以便 Beacon 知道可用 skills、能力边界与证据输出。

### US-002: Beacon 支持 project-specific profile
作为 Beacon 使用者，我希望为某个项目声明 profile，以便 Beacon 用项目真实工作流做 verify / accept。

### US-003: Beacon 支持 feature / stage 绑定特定 skill
作为 Beacon 使用者，我希望 implementation / verify / debug 等阶段可绑定特定 skill，以便不同项目走不同执行面。

### US-004: Beacon 支持编排式 verify runner
作为 Beacon 使用者，我希望 Beacon 能把 pipeline、gateway、接口、日志、SQL 等验证步骤编排成一条正式链路，以便复杂项目不再靠手工串流程。

### US-005: Beacon 支持 required evidence gate
作为 Beacon 使用者，我希望 accept 前必须检查 required evidence 与 must-run case，以便没有跑过关键场景时不能误判验收通过。

### US-006: Beacon 能识别 contract drift
作为 Beacon 使用者，我希望 Beacon 识别“文档/前端/下游服务合同不一致”，以便尽早阻断发布与验收。

### US-007: Beacon 以 Rolo 为样板验证通用性
作为 Beacon 维护者，我希望用真实的 Rolo 项目作为首个样板，但能力设计保持通用，以便后续扩展到更多项目。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Skill Registry | Beacon 存在正式的 skill registry，而不是仅靠外部命令字符串 |
| AC-002 | Multi Skill | 一个项目可同时声明多个 skills |
| AC-003 | Project Profile | Beacon 支持 project-specific profile |
| AC-004 | Stage Binding | implementation / verify / debug / delivery 可绑定不同 skill |
| AC-005 | Builtin Skill | Beacon 支持 builtin skill 与 external project skill 共存 |
| AC-006 | Orchestration | Beacon 支持 skill-backed orchestration graph |
| AC-007 | Evidence Contract | 每个 skill / orchestration node 可声明 evidence outputs |
| AC-008 | Required Evidence | accept 前可检查 required evidence 是否齐全 |
| AC-009 | Must-run Cases | 关键测试场景可声明为 must-run，否则不能 accept |
| AC-010 | Quality Gate | `review quality` 可读取 project profile 的 required cases/evidence |
| AC-011 | Accept Gate | `review accept` 不得忽略 required case 缺失 |
| AC-012 | Contract Drift | Beacon 可识别文档/前端/后端合同漂移 |
| AC-013 | Drift Output | drift 需输出清晰 reason_code 与 drift layer |
| AC-014 | Project Example | Rolo 可作为 profile example 被 Beacon 表达 |
| AC-015 | Rolo Skill | Rolo 示例中能明确绑定 `rolo-dev` 作为 verify/delivery/debug skill |
| AC-016 | Rolo UAT | Rolo 示例中能表达 pipeline + UAT gateway + interface smoke 的编排链 |
| AC-017 | Upload Contract | Rolo 示例中可表达 `jpg/gif/mp4` 正向成功与非法类型失败的 required cases |
| AC-018 | Generality | 设计不能写死为只服务 rolo，一个新项目也可声明自己的 skill/profile |
| AC-019 | Navigator | `help / doctor advise` 能输出 profile-aware next step |
| AC-020 | Determinism | project profile 变更后，required evidence 与 accept 规则仍可确定追踪 |

## Warn 风险

- 若只引入 skill registry，不引入 required evidence gate，漏测仍会发生
- 若只把 rolo-dev 当示例文档，不进入 Beacon profile 能力，无法自动化验收
- 若 orchestration 不把 pipeline / gateway / interface / logs / SQL 串起来，多服务项目仍要手工验收
