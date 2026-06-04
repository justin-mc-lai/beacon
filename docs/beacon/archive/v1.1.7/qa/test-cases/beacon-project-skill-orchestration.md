# Test Cases: Beacon 项目级 skill profile、多 skill 编排与强证据验收（v1.1.7）

**Feature**: beacon-project-skill-orchestration  
**Version**: v1.1.7

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已具备 Beacon v1.1.7 现状、Rolo 真实问题与目标设计）
- Gate1 冲突未决判定：Pass（目标明确，问题来自真实多服务漏测）
- Gate2 AC→TC 映射：目标覆盖 project profile / multi-skill / orchestration / evidence gate / Rolo example

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | 注册 builtin + external skill | Beacon 可列出 builtin skill 与 external skill |
| TC-002 | contract | 一个项目绑定多个 skills | profile 中可同时声明 verify/delivery/debug/pipeline skills |
| TC-003 | contract | feature 绑定 profile | feature 能解析到 project profile |
| TC-004 | contract | stage 绑定 skill | implementation / verify / debug 可解析到不同 skill |
| TC-005 | contract | orchestration node 声明 evidence outputs | 编排节点存在稳定 evidence contract |
| TC-006 | contract | required evidence 缺失 | `review quality` / `review accept` 进入 blocked |
| TC-007 | contract | must-run case 未执行 | accept 被阻断 |
| TC-008 | diagnosis | 文档/前端/后端合同不一致 | `doctor advise` 输出 `contract_drift` |
| TC-009 | navigation | profile-aware help | `help` 输出项目特定 next step |
| TC-010 | integration | `verify run --profile <profile>` 调用 skill-backed 编排 | Beacon 按 profile 运行编排链 |
| TC-011 | integration | orchestration graph 中 pipeline → smoke → evidence → review | 执行顺序、状态与证据均可追踪 |
| TC-012 | integration | Rolo profile 绑定 `rolo-dev` | Beacon 能表达 Rolo 的 verify/delivery/debug skill binding |
| TC-013 | integration | Rolo UAT 验证链 | Beacon 能表达 pipeline、gateway smoke、interface verify、log/sql verify |
| TC-014 | regression | 通用项目不使用 rolo-dev | 非 rolo 项目仍可使用默认/其它 profile，不被写死 |
| TC-015 | security | evidence 缺失时不能 accept | formal accept gate 保持强阻断 |
| TC-016 | recovery | profile 调整后重新 verify | Beacon 可重新编排并重建证据闭环 |
| TC-017 | rolo-case | `jpg/gif/mp4` 上传成功为 must-run | 若任一缺失/失败，Rolo 场景不能 accept |
| TC-018 | rolo-case | 非法类型上传失败 | 必须有负向验证证据 |
| TC-019 | rolo-case | pipeline 成功但关键业务 case 未过 | 仍然 blocked，不得以“流水线绿了”替代验收 |
| TC-020 | scoring | readiness/quality 与 required evidence 一致 | score 与 gate 结论一致 |

## Rolo 验收样板场景

### 场景 A：上传合同漂移
- 需求 / FE 声明支持 GIF / 视频
- downstream STS 仅支持 JPG/PNG/PDF
- 预期：Beacon 识别 `contract_drift`，并阻断 accept

### 场景 B：流水线成功但关键业务场景未验证
- pipeline = success
- `upload_mp4_success` 无证据
- 预期：quality blocked，accept blocked

### 场景 C：项目特定 skill 验证链
- 通过 `rolo-dev` 运行：pipeline / uat-smoke / gateway / debuglab
- 预期：evidence 写回 Beacon，accept 依赖这些证据

## 执行语义

- `Pass`：profile、skill、编排、evidence gate 与 Rolo 样板都能成立
- `Fail`：编排链不能执行，或 required evidence/gate 逻辑错误
- `Blocked`：项目 profile / external skill / required evidence contract 未落地
