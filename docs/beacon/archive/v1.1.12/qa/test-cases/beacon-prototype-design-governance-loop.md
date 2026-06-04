# beacon-prototype-design-governance-loop 测试用例

**版本**: v1.1.12
**Feature**: `beacon-prototype-design-governance-loop`
**状态**: Draft
**更新时间**: 2026-03-31

---

## 1. 目标

验证 Beacon 能将 design brief、design-system contract、web guideline audit、bounded autoresearch iteration，以及版本真相 / profile-aware execution routing / typed learning boundary 合并进 prototype 主链，而不是把设计质量和执行边界都留给人工补充。

---

## 2. 测试分组

| 组别 | 目标 |
|---|---|
| DG-TC-001 ~ 005 | Design brief / design-system contract compilation |
| DG-TC-101 ~ 106 | Guideline audit / design review outcome |
| DG-TC-201 ~ 204 | Iteration writeback / keep-discard governance |
| DG-TC-301 ~ 303 | Freeze / gate / backward compatibility |
| DG-TC-401 ~ 406 | Version truth / profile routing / learning-plane / takeover boundary |

---

## 3. Design brief / contract

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| DG-TC-001 | design brief 编译 | 从 story/prd/research 运行 prototype plan | 生成 `design-brief.json` | unit |
| DG-TC-002 | design-system contract 编译 | 启用 `frontend-design` generation contract | 生成 `design-system-contract.json` | unit |
| DG-TC-003 | anti-generic guard | 设计 brief 明确禁止 generic aesthetic | contract 中出现可审计限制项 | unit |
| DG-TC-004 | shared token discipline | render 多页面 reference pack | 页面消费共享 token，不靠 page-level 失控硬编码 | unit + snapshot |
| DG-TC-005 | unified directory + style analysis | 运行 `prototype create/directory` | 存在统一目录页与 `ui-style-analysis` 工件，可供二开读取 | integration |

---

## 4. Guideline audit / design review

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| DG-TC-101 | guideline 拉取与审查 | review design 时拉取最新 guideline | 生成 `web-guideline-review.json` | integration |
| DG-TC-102 | critical a11y finding | 人为去掉 skip link / focus replacement / aria label | review 输出 critical finding 并阻断 | integration |
| DG-TC-103 | URL state finding | tab/filter 仅本地 state 不入 URL | guideline audit 报出 state-sync finding | integration |
| DG-TC-104 | visual generic finding | 使用通用字体/弱视觉方向 | design review 输出 revise/block finding | review |
| DG-TC-105 | outcome synthesis | 同时存在 structure pass + design fail | `design_review_outcome` 不得误判为 pass | unit |
| DG-TC-106 | cso-inspired design security review | 运行 `review design` 审查 upload / privileged action / secret / integration surfaces | 输出结构化 security finding，并作为 review artifact 保留 | integration |

---

## 5. Iteration writeback / governance

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| DG-TC-201 | finding 回流 page/state | review 发现页面/状态缺口 | next iteration input 写回 page/state additions | unit |
| DG-TC-202 | finding 回流 design brief | review 发现风格方向过泛 | next iteration input 写回 design-brief edits | unit |
| DG-TC-203 | keep/discard 账本 | 进行一轮 design policy 迭代 | 账本记录 benchmark + keep/review/discard | integration |
| DG-TC-204 | bounded surface enforcement | 尝试将 autoresearch 扩展到任意 HTML/CSS 自改 | 系统阻止并给出 boundary reason | unit |

---

## 6. Freeze / gate / compatibility

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| DG-TC-301 | freeze 依赖 design truth | 存在 critical guideline finding 时运行 freeze | freeze 阻断 | integration |
| DG-TC-302 | gate 消费 design artifacts | 运行 prototype/release gate | gate 能识别 design brief / guideline audit / review outcome | integration |
| DG-TC-303 | backward compatibility | 对旧 prototype line 不启用 design governance | 旧流程不回归，但明确缺少 governed guarantee | regression |

---

## 7. Boundary stabilization / routing / learning plane

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| DG-TC-401 | version truth 单源 | 对比 skill/runtime/release/help current line | current line 一致；planning line 与 runtime fact 显式区分 | unit |
| DG-TC-402 | profile-aware next step | feature 已绑定 project profile，help/status 给下一步建议 | 优先命中 profile/stage-local execution surface，不盲推 native-single | integration |
| DG-TC-403 | capability-bounded orchestration | project skill 的 `supported_stages/capabilities/evidence_contract` 与 node 声明不匹配 | orchestration blocked，返回 boundary reason | integration |
| DG-TC-404 | typed learning surface | 查询或运行 learning plane mutation routing | 只允许 `qa_policy/design_policy/contract_policy/debug_policy/rewrite_policy/benchmark_policy` | unit |
| DG-TC-405 | learning out-of-scope enforcement | 尝试把 gateway/UAT/pipeline 命令或 project command template 纳入 learning surface | 系统拒绝并返回 out-of-scope reason | unit |
| DG-TC-406 | takeover baseline gate | `project_mode=takeover` 且缺 architecture/current-state/refactor-boundaries/freeze baseline | implement blocked，并给出先 freeze 的下一步 | integration |

---

## 8. 通过标准

- design brief 与 design-system contract 成为正式工件
- guideline audit 成为正式 review/gate 输入
- design findings 能回流 next iteration
- keep/discard 维持 bounded governance
- 版本真相、profile 路由、learning plane、takeover baseline 都成为正式 gate truth
- 旧 prototype 线不被破坏
