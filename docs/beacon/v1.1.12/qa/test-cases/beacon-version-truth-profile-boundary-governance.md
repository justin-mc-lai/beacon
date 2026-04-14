# beacon-version-truth-profile-boundary-governance 测试用例

**版本**: v1.1.12
**Feature**: `beacon-version-truth-profile-boundary-governance`
**状态**: Draft
**更新时间**: 2026-04-01

---

## 1. 目标

验证 Beacon 在 `v1.1.12` 能把版本真相、profile-aware 路由、project skill capability boundary、typed learning plane、requirement-anchor governance、adjacent-semantics drift blocker、transparent decision trace 与 takeover baseline gate 变成正式约束。

---

## 2. 测试分组

| 组别 | 目标 |
|---|---|
| VT-TC-001 ~ 004 | version truth 单源 |
| VT-TC-101 ~ 104 | profile-aware navigator |
| VT-TC-201 ~ 204 | project skill capability boundary |
| VT-TC-301 ~ 303 | typed learning plane |
| VT-TC-304 ~ 309 | requirement-anchor governance / RAS / drift blocker |
| VT-TC-401 ~ 403 | takeover baseline gate |
| VT-TC-501 ~ 503 | transparent decision trace / stable workflow order |

---

## 3. Version truth

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| VT-TC-001 | 当前版本单源一致 | 读取 runtime/package/skill/docs 当前版本 | 返回同一 machine-readable source 的派生值 | unit |
| VT-TC-002 | planning line with partial runtime supplement | 查询 `v1.1.12` release truth | 能同时表达 planning line 与 partial runtime supplement，不混淆 current runtime line | unit |
| VT-TC-003 | help/status 版本解析一致 | 分别执行 help/status/version context | docs/runtime/current release line 一致且来源可解释 | regression |
| VT-TC-004 | explicit version mismatch guard | 上下文已锚定 `vX.Y.Z`，显式输入 `--version vA.B.C` | 返回 `context_version_mismatch`，并给出推荐版本 | integration |

---

## 4. Profile-aware navigator

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| VT-TC-101 | profile 绑定 verify | feature 绑定 rolo/demo profile，调用 help | 优先推荐 profile verify surface，不回落 native-single | integration |
| VT-TC-102 | profile 绑定 implementation but verify blocked | profile gate 缺证据后调用 help | 推荐 verify / repair，而不是 generic review quality | integration |
| VT-TC-103 | 无 profile 绑定 | 在普通 Beacon 项目调用 help | 允许降级到通用 native / review 路径 | regression |
| VT-TC-104 | 输出 execution surface 解释 | help/status payload | 包含 execution surface / profile binding / blocked reason | regression |

---

## 5. Project skill capability boundary

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| VT-TC-201 | supported stage 不匹配 | orchestration node stage 与 skill.supported_stages 不一致 | blocked，不执行命令 | unit |
| VT-TC-202 | capability 不匹配 | node 请求 verify，但 skill.capabilities 不含 verify | blocked | unit |
| VT-TC-203 | evidence contract 不匹配 | node 产出未声明 evidence key | blocked | unit |
| VT-TC-204 | raw shell template 被拦截或受限 | 注入自由 command template | 被 adapter-boundary 校验拦截或降级为安全结构化执行 | integration |

---

## 6. Typed learning plane

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| VT-TC-301 | subject surface 分类完整 | 读取 learning plane contract | 至少包含 qa/design/contract/rewrite/debug/benchmark 六类 | unit |
| VT-TC-302 | design governance surfaces 对齐 | 读取 `v1.1.12` design policy contract | 包含 design brief extraction / guideline mapping / review thresholds | unit |
| VT-TC-303 | forbidden surfaces 拦截 | 尝试把 project skill command template 或 secrets 加入 learning plane | 返回 blocked reason | unit |

---

## 7. Requirement-anchor governance / RAS / drift blocker

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| VT-TC-304 | 发散场景携带锚定元数据 | 生成 QA scenario map 或 learning candidate | 每个场景包含 `anchor_ids` / `anchor_kinds` / `semantic_scope` / `divergence_budget` / `adjacent_capability_flags` | unit |
| VT-TC-305 | 需求内发散自动放行 | 对已明确 AC 的 happy/negative/boundary 场景计算 RAS | `RAS >= 85`，允许 auto 执行 | unit |
| VT-TC-306 | 中间带进入 review_required | 构造与需求相关但需要人工判断的边界场景 | `RAS` 落入 `70-84`，状态为 `review_required` | unit |
| VT-TC-307 | 低分段要求人工审批 | 构造 traceability 有限但非完全脱锚场景 | `RAS` 落入 `50-69`，状态为 manual approval required | unit |
| VT-TC-308 | 相邻产品语义漂移阻断 | requirement 仅为 `rolo` 开屏页视频上传/展示，注入 `500MB` 上传 + seek/fullscreen/buffering 场景 | `RAS < 50`，reason=`requirement_drift` 或等价 blocked reason | integration |
| VT-TC-309 | autoresearch 不得绕过 blocked band | 尝试通过 learning plane 调整权重/阈值来放行已被判定为相邻语义漂移的场景 | learning plane 可记录实验，但不得越过 blocked 决策 | regression |

---

## 8. Takeover baseline gate

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| VT-TC-401 | takeover baseline 缺失 | project_mode=takeover 且缺 architecture/service-map/refactor-boundaries | implement blocked，reason=`takeover_baseline_required` | integration |
| VT-TC-402 | takeover baseline 完整但未 freeze | baseline docs 存在但版本未冻结 | 仍 blocked | integration |
| VT-TC-403 | takeover baseline 完整且 frozen | current-state docs + frozen baseline 均满足 | 允许进入后续 feature / implement 流程 | integration |

---

## 9. Transparent decision trace / stable workflow order

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| VT-TC-501 | help/status 输出决策链 | 调用 help/status | 输出包含 `version_truth_source` / `project_mode` / `execution_surface` / `learning_surface` / `blocked_reason` | regression |
| VT-TC-502 | QA 发散输出锚定评分链 | 生成或评审 scenario candidates | 输出包含 `requirement_anchor_score`、anchor metadata 与决策结果 | integration |
| VT-TC-503 | 稳定工作流顺序被执行 | 在 version truth / project mode / execution surface 未决时直接请求 implement 或大范围 scenario expansion | 系统先要求补齐前置解析，不允许跳过顺序直接进入执行或发散 | integration |
