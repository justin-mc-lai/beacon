# Planner Review — UI 全生命周期闭环 + Goal Design Stage + Google lint + 公司模板

Status: `support_advisory`（非 requirement truth）  
Version: `v1.6.7`  
Skill: `beacon-pln-review`  
Runtime evidence: `.beacon/state/planner-review/beacon-ui-design-ship-gate-v167/pln-review-20260717t034622z.json`  
Recommended route: **`beacon-gen-change`** → implement → qa → release  
User decision required: **YES**（进入 change/implement 前）

---

## Intent snapshot

用户确认此前 UI 思考，并要求加深：

1. 视觉工程交付必须遵循已吸收的 UI 原则（google design.md / awesome-design-md / impeccable / ui-ux-pro-max / vibe-to-ui）。
2. **`design baseline` 挂入 `beacon goal`**：当 truth `ux_required`（或等价视觉交付信号）时，自动插入 stage。
3. **接入 `google design.md lint` 作为 ship 证据**。
4. **增加多个专业公司模板**供自动选择；千篇一律可接受，先对齐商业大公司视觉再微调。
5. **Beacon 全生命周期**对 UI：**审阅 → 实现 → 验收**闭环。

成功标准：

- Goal 跑 UX 湖时，无人也可自动产出 DESIGN.md（公司模板 + surface）。
- Implement 不得 freestyle UI。
- QA/Release 必须看到 design baseline + design.md lint + ui-state-matrix 证据链。

---

## Scope mode

- **湖**：在 v1.6.7 内煮干一包（或扩展现有 `beacon-ui-design-ship-gate-v167` + `beacon-product-goal-runtime-v167`）。
- **不做**：重写全部 design skills、替代 ui-ux-dev 执行、把 awesome-design-md 升为 ship 权威。

---

## Current-state inventory（关键事实）

| 能力 | 现状 | 缺口 |
|------|------|------|
| Design routes | explore/system/review/polish/library 已映射上游 | 非 goal 强制 stage |
| `beacon design baseline` | 完整 DESIGN + surface auto + fine-tune | **未挂入 goal STAGE_ORDER** |
| Surface packs | pc-console/web/h5/client | **公司模板选择层不足** |
| UI ship gate | DESIGN 存在性 + ui-state-matrix↔FSM | **无 google design.md lint 证据** |
| Goal stages | plan→truth→implement→qa→release | **无 design stage**；`done_when` 无 design |
| Implement | 读 DESIGN.md；提示 baseline | **非自动执行 baseline** |
| Company templates | awesome-design-md 本地 70+ | **未进入 auto-select catalog** |

`PROGRESSIVE_SKILLS` 当前：

```text
plan → truth → implement → qa → release
```

目标态（UX 时）：

```text
plan → truth → design → implement → qa → release
                 ↑
         ux_required / visual signals
         design baseline + company template
         optional polish/review route
```

---

## Findings

### F1 — P0 — Goal 缺 design stage（intent fidelity / lifecycle）

- **Finding**: `ux_required` 时 goal 仍可 plan/truth 后直接 implement，视觉 OS 非强制。
- **Evidence**: `product_goal_runtime.STAGE_ORDER` 无 design；`PROGRESSIVE_SKILLS` 无 design skills。
- **Impact**: 自动驾驶下 UI 回落 LLM 直觉。
- **Recommendation**: 当 `scan_truth_for_ux` 或 feature `ux_required` 为真，插入 stage `design`：
  - skills: `beacon-gen-design`, progressive load
  - auto action: `synthesize_unattended_design_baseline(... surface=auto, company_template=auto)`
  - stage done 条件: DESIGN.md exists + surface decided + (optional) lint pass artifact

### F2 — P0 — Ship 缺 google design.md lint 证据

- **Finding**: UI ship 只查 baseline 存在与 matrix 绑定，不验证 DESIGN.md 结构/token/对比度。
- **Evidence**: `ui_design_ship.build_ui_design_ship_gate`；本机可用 `npx @google/design.md lint`。
- **Recommendation**:
  - 新增 `beacon design lint`（wrapper）→ 写 `.beacon/evidence/design-md-lint/<feature|project>.json`
  - `build_ui_design_ship_gate` / QA scorecard：`ux_required` 时 require lint status pass 或 findings 无 error
  - reason_code: `design_md_lint_failed` / `design_md_lint_missing`

### F3 — P1 — 公司模板自动选择不足

- **Finding**: 仅有 3 preset + 4 surface；商业对齐应优先“公司模板库自动 pick”。
- **Evidence**: awesome-design-md `design-md/{vercel,apple,stripe,linear.app,notion,figma,shopify,...}`
- **Recommendation**: catalog `COMPANY_DESIGN_TEMPLATES`（先 curated 8–12 个，不是 70 全量）：

| Template id | 对齐场景 | Surface 默认 |
|-------------|---------|--------------|
| `vercel` | 开发者控制台/中台密度 | pc-console |
| `stripe` | 金融/交易/信任密集 to-b | web / pc-console |
| `linear` | 工作台/issue 流 | pc-console / client |
| `notion` | 文档/知识工作面 | web / client |
| `figma` | 创意工具 chrome | client |
| `apple` | 克制消费级产品 web | web / h5 |
| `shopify` | 电商运营/商家后台 | pc-console |
| `airbnb` | 消费市场/预订流 | web / h5 |
| `slack` | 协作客户端 | client |
| `ibm` | 企业中台稳重 | pc-console |

选择序：`surface auto` → `company template auto`（关键词/行业）→ fallback surface pack。  
原则：**先千篇一律对齐大公司，再 fine-tune**（与用户一致）。

### F4 — P1 — 全生命周期 UI 闭环未串成 goal 证据链

目标闭环：

| Stage | UI 动作 | 证据 |
|-------|---------|------|
| truth | 标 `ux_required`；冻结 domain FSM | truth.md |
| **design** | baseline + company template + surface；可选 review/polish | DESIGN.md, surfaces/*, fine-tune-proposal, design-md-lint.json |
| implement | 强制读 DESIGN；禁止 freestyle | implementation marker refs DESIGN path |
| qa | ui_design_ship + matrix + lint | scorecard fields |
| release | design lint + ship gate green | release scorecard |

### F5 — P2 — 范围纪律

- awesome-design-md **永不**成为 ship 权威（仅 seed 模板）。
- google lint 失败 fail-closed 于 `ux_required`；`ux_deferred` 可跳过。
- 公司模板是 seed，不是品牌侵权复刻；输出须标注 `inspired-by` + Beacon-owned。

---

## State model（UI lifecycle FSM）

```text
NoVisualClaim
  → VisualClaimed (ux_required / UI signals)
  → DesignBaselineMissing | DesignBaselineReady
  → DesignLintPending → DesignLintPass | DesignLintFail
  → ImplementAligned | ImplementFreestyleBlocked
  → QaDesignPass | QaDesignBlocked
  → ReleaseDesignReady
```

Illegal:

- VisualClaimed → ImplementAligned without DesignBaselineReady  
- DesignLintFail → ReleaseDesignReady  
- ImplementFreestyle when DESIGN missing  

---

## Deferral ledger

| Item | Decision | Owner |
|------|----------|-------|
| Full 70 brand import | **defer** — curated 8–12 first | change package |
| Online brand scraping | **out of scope** | — |
| Replacing ui-ux-dev execution | **out of scope** | — |
| Auto pixel Figma sync | **defer** | later lake |

---

## Recommended route

1. **User GO** on this review（本消息即确认请求；若同意则下一跳执行）。  
2. `beacon-gen-change` 立项/扩湖（建议 feature slug）：  
   `beacon-ui-goal-design-lifecycle-v167`  
   或扩：`beacon-ui-design-ship-gate-v167` + `beacon-product-goal-runtime-v167`。  
3. Implement 切片：  
   - P0a goal design stage + auto baseline  
   - P0b google design.md lint evidence + ship gate  
   - P1 company template catalog auto-select + skill examples  
   - P1 implement/qa/release scorecard fields  
4. `beacon-eval-qa` / release check v1.6.7  

---

## Acceptance criteria draft（供 change 冻结）

| AC | 描述 |
|----|------|
| AC-UID-G01 | ux_required 时 goal stage 含 `design`，且 progressive load design skills |
| AC-UID-G02 | design stage 自动跑 baseline（surface auto + company template auto）写出 DESIGN.md |
| AC-UID-G03 | 已有 DESIGN 时不覆盖，写 fine-tune-proposal |
| AC-UID-L01 | `beacon design lint` 调用 google design.md lint 并落 JSON 证据 |
| AC-UID-L02 | ux_required 且 lint error → ui_design_ship blocked，`design_md_lint_failed` |
| AC-UID-T01 | ≥8 公司模板可被 catalog 选择；自动选择可解释（reason/hits） |
| AC-UID-I01 | implement prompt 在 DESIGN 缺失且 UX 时 fail-closed 指向 baseline |
| AC-UID-Q01 | QA scorecard 暴露 design_baseline、design_md_lint、ui_state_matrix |
| AC-UID-R01 | release 不允许 design ship blocked |

---

## Planner boundary

- 本文件 **不是** frozen truth。  
- 未改 package truth / 未写业务代码（planner-only）。  
- 进入 change/implement 需用户确认（recommended_route 已给出）。
