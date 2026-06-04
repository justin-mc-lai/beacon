# beacon-prototype-reference-pack-v2 测试用例

**版本**: v1.1.11
**Feature**: `beacon-prototype-reference-pack-v2`
**状态**: Draft
**更新时间**: 2026-03-31

---

## 1. 目标

验证 Prototype v2 能把 requirement materials 编译成可实现参考的高保真原型包，而不是 generic 单页 demo，并确保 review / freeze / gate 能阻断 coverage、state、route、baseline 与 artifact consistency 漂移。

---

## 2. 测试分组

| 组别 | 目标 |
|---|---|
| PT-TC-001 ~ 004 | Contract compiler / parsing / source ingestion |
| PT-TC-101 ~ 105 | Page inventory / page-spec / hi-fi output |
| PT-TC-201 ~ 204 | Route closure / implementation binding / baseline protection |
| PT-TC-301 ~ 305 | Review / freeze / status / gate consistency |
| PT-TC-401 ~ 403 | Backward compatibility / real fixture coverage |

---

## 3. Contract Compiler 与 Parsing

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PT-TC-001 | 结构化 block 输入 | 提供 story/prd 中的 structured prototype block + route source | `prototype plan` 输出规范化 `prototype-plan.json` | unit |
| PT-TC-002 | 中文标点健壮性 | 在 `jump_map`、`states`、`sections` 中使用 `；：，` 与换行列表 | 不发生字段吞并、截断或空列表 | unit |
| PT-TC-003 | route/code/baseline source ingestion | 同时提供 markdown、route 文件、baseline source | prototype plan 能合并多源输入并标记来源 | unit |
| PT-TC-004 | contract 缺失 fail-fast | 缺少 required page inventory / coverage mode / primary CTA 等关键字段 | `prototype plan/create` 直接 fail，并指出缺失项 | unit |

---

## 4. Page Inventory / Hi-fi Output

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PT-TC-101 | all-existing-routes 覆盖模式 | 使用 `coverage_mode=all-existing-routes` + route source | Beacon 解析出 required pages，而不是只按 archetype sections 渲染 | unit |
| PT-TC-102 | page-spec 生成 | 对 required pages 运行 `prototype create` | 每个 required page 生成 `page-specs/<page>.json` | unit |
| PT-TC-103 | 独立高保真页面输出 | 对 full-hi-fi feature 运行 create | required pages 全部产出 `pages/<page>.html` | unit + snapshot |
| PT-TC-104 | 关键状态输出 | contract 声明 required states | 关键页面至少产出默认态 + 关键状态态 | unit + snapshot |
| PT-TC-105 | 禁止 compact drift | feature 声明 `full-hi-fi` | 生成结果中不得出现 `compact coverage` 或结构补齐替代 required page | unit + review |

---

## 5. Route Closure / Baseline Protection

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PT-TC-201 | CTA/tab/page route closure | page-spec 含 CTA、tab、page jumps、params 与 fallback | route closure contract 能表达 target/context/fallback | unit |
| PT-TC-202 | implementation binding ingestion | 为 route closure cases 绑定真实代码路径和 runtime targets | `implementation-map.json` 与 route closure cases 一致 | unit |
| PT-TC-203 | baseline protection 不退化 | 声明 `baseline_protection` 并生成页面 | 受保护页面不退化为 generic shell 或摘要式卡片 | visual review + snapshot |
| PT-TC-204 | slow_uni_bmtop fixture 表达能力 | 对 `slow_uni_bmtop` 类 fixture 编译 prototype plan | 能表达 all-page hi-fi + baseline protection + route closure，不退回 13+25 模式 | fixture test |

---

## 6. Review / Freeze / Gate

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PT-TC-301 | review 检查 page coverage | 故意删除 required page artifact 后运行 review | review fail，reason code 指向 required page 缺失 | unit |
| PT-TC-302 | review 检查 state coverage | 删除关键状态态页面后运行 review | review fail，reason code 指向 required state 缺失 | unit |
| PT-TC-303 | review 检查 artifact consistency | 让 manifest/freeze/review/source fingerprint 不一致 | review 或 status 识别 inconsistent / stale | unit |
| PT-TC-304 | freeze 严格性 | review fail 或 stale=true 时运行 freeze | freeze 必须阻断 | unit |
| PT-TC-305 | gate 消费新 artifact pack | 对 feature 运行 prototype/release gate | gate 可消费 page-spec、coverage、route closure 和 review 工件 | integration |

---

## 7. Backward Compatibility

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| PT-TC-401 | minimal mode 旧 feature | 对旧 prototype feature 使用 minimal mode | 原有 prototype 工作流不回归 | regression |
| PT-TC-402 | minimal mode 语义显式降级 | 查看 minimal mode 产物和 status/review 输出 | 输出明确标记不具备 reference-pack-v2 强保证 | unit |
| PT-TC-403 | route-closure old-line compatibility | 未声明新 schema 的旧 feature 运行 review/gate | 旧 line 不被误拦截 | regression |

---

## 8. 通过标准

- contract compiler 能稳定解析结构化输入与中文标点
- required pages / states 全部生成独立 artifact
- review 能阻断 compact drift、baseline regression、artifact inconsistency
- freeze / status / gate 与新 contract 语义一致
- real fixture 可以 truthful 表达，而不是依赖手工 polish 绕过生成器
