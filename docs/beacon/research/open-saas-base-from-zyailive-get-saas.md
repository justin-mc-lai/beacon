# Research: Open SaaS Base from `@zyailive` stack note + `ItusiAI/get-saas`

**Date**: 2026-07-21  
**Intent**: 把两份互补参考收敛成一套可复用的「自研产品开源底座」研究方向，并落到独立产品仓 `open-saas-base` 的规划资产（非实现）。  
**Status**: plan artifact only — **not frozen truth**, **not implementation**.

**Linked product project**:

- `/Users/apple/Developer/Personal/products/open-saas-base/`

**Primary sources**:

1. X Article（张禹 @zyailive）  
   - URL: https://x.com/zyailive/status/2058790586052903250  
   - Article id: `2057771121882415104`  
   - Title: 《一个人、零成本、赚美元：2026 独立开发者的 SaaS “印钞机”底座大公开》  
   - Local capture: `open-saas-base/references/zyailive-2026-saas-base-article.md`
2. GitHub SaaS template  
   - Upstream: https://github.com/ItusiAI/get-saas  
   - Demo: https://getsaas.co  
   - Docs/commercial: https://getmoney.wang/zh/article/get-saas-pro  
   - `oss-sync status`: **canonical** → `/Users/apple/Developer/Personal/oss-sync/saas/templates/get-saas`

**Beacon first principle reminder**:

> 底座的价值不在于堆功能，而在于把「能上线收钱的闭环」做成可验证、可插件扩展、可被 agent skill 稳定操作的证据链。

---

## 1. Executive summary

两份参考回答的是同一问题的不同切面：

| 参考 | 回答的问题 | 强项 | 缺口 |
|------|------------|------|------|
| `@zyailive` 2026 底座文 | **成本/所有权/Vibe Coding 约束** | 零/低基础设施成本；自持用户数据；AI 友好类型系统 | 不是完整产品模板；缺插件化与 agent skill 体系 |
| `ItusiAI/get-saas` | **SaaS 产品面能力清单** | Auth/Pay/i18n/Dashboard/Admin/Blog/SEO 开箱即用 | 传统 Vercel+Postgres 成本面更高；插件/多产品扩展不是一等公民；无 agent skill 运营面 |

**翻译结论（给自研底座）**：

> 做一套 **Kernel + Plugin Products** 的开源底座：  
> - Kernel 吸收 zyailive 的「省 / 快 / 稳 / 自持数据」约束；  
> - Product surface 吸收 get-saas 的「认证 / 支付 / 多语言 / 后台 / 增长面」能力清单；  
> - 用 **plugin contract + agent skills + docs/beacon 证据链** 作为长期扩展面，后续每个自研产品 = 一个 plugin / product capsule，而不是 fork 一份 monorepo。

这是 **海（ocean）级 program**：不宜一次 parity 全抄 get-saas，应拆湖交付。

---

## 2. Source A — `@zyailive` 文章要点（锚定）

文章核心口号：**省、快、稳**。选型摘录：

1. **基础设施成本打到接近 0**  
   - Cloudflare Pages + D1  
   - 全球边缘部署；起步免费额度优先  
2. **给 AI 写代码加「防呆」**  
   - TanStack + Drizzle  
   - 类型/查询边界约束，降低 Vibe Coding 隐性 bug  
3. **用户数据自持，拒绝被 Auth SaaS 割韭菜**  
   - Better Auth（开源、数据进自有库）  
4. **收钱与触达闭环**  
   - Stripe / Cremm（支付 + 订阅权限自动开通）  
   - Resend（验证码 / 收据高到达率）

**可抽取原则（不是必须锁定同一供应商）**：

- P1 冷启动成本优先：免费额度 / 边缘部署优先于「先上 heavy cloud」
- P2 AI-coding 友好：强类型 schema / route / ORM 边界
- P3 身份数据主权：Auth 逻辑可自托管，用户表在自有 DB
- P4 商业闭环一等公民：支付 webhook → 权益状态机 → 邮件通知
- P5 一人可运维：少运维面，少第三方锁死

---

## 3. Source B — `get-saas` 能力地图（锚定）

基于 README + 仓库树（2026-07-21 远端 `main` 观测）：

### 3.1 Tech stack（观测）

- Next.js App Router + TypeScript + Tailwind + Radix UI  
- next-intl 多语言（`app/[locale]` + `messages/{en,zh}.json`）  
- NextAuth + Drizzle + PostgreSQL  
- Stripe + Resend  
- 部署叙事：Vercel 友好

### 3.2 产品面能力清单（parity 候选）

| Domain | get-saas 现状 | 底座是否 P0 |
|--------|---------------|-------------|
| Email/password + OAuth (Google/GitHub) | 有 | P0 |
| Email verify / password reset | 有 | P0 |
| Stripe subscription + one-time / points | 有 | P0（points 可 P1） |
| Customer portal / webhook | 有 | P0 |
| User dashboard / profile | 有 | P0 |
| Admin（newsletter 等） | 有 | P1 |
| i18n + SEO multi-locale | 有 | P0 |
| Blog / marketing landing | 有 | P1 |
| Cookie / legal pages | 有 | P1 |
| Newsletter | 有 | P1 |
| S3-like asset storage | package 依赖可见 | P1 |

### 3.3 结构观察

```
app/[locale]/{auth,dashboard,profile,admin,blog,...}
components/{auth,dashboard,blog,...}
lib/{auth,db,stripe,email,payments,points,schema,seo-config}
drizzle/ + messages/ + docs/
```

**启发**：功能边界清晰，但 **产品 = 仓库**。多产品时易变成 fork 扩散，不符合「插件化新增产品」。

---

## 4. Synthesis — 自研底座目标架构（规划）

### 4.1 定位

**Open SaaS Base** = 开源、可自托管/边缘部署的 **SaaS Kernel**，用于：

1. 快速启动单个出海/收款产品  
2. 以 plugin 形式叠加业务产品（工具站、CMS、AI 应用…）  
3. 用 agent skills 让 AI 在底座上稳定改需求、加插件、做 QA，而不是每次重新发明脚手架

### 4.2 分层（推荐）

```
┌─────────────────────────────────────────────┐
│  Product Plugins (业务产品)                  │
│  routes / UI / domain schema / skills       │
├─────────────────────────────────────────────┤
│  Extension Contracts                        │
│  plugin manifest / hooks / entitlements     │
├─────────────────────────────────────────────┤
│  SaaS Kernel (底座一等公民)                   │
│  auth · billing · i18n · email · admin shell│
│  entitlements · audit · feature flags       │
├─────────────────────────────────────────────┤
│  Platform adapters                          │
│  DB / host / mail / payment / storage       │
│  (CF D1 | Postgres) (Pages | Node) ...      │
├─────────────────────────────────────────────┤
│  Agent surface                              │
│  skills/ · AGENTS.md · docs/beacon · gates  │
└─────────────────────────────────────────────┘
```

### 4.3 与两份参考的映射

| 底座层 | 主要吸收 |
|--------|----------|
| Platform adapters | zyailive：CF Pages + D1 优先；保留 Postgres adapter 兼容 get-saas 路径 |
| Auth | zyailive：Better Auth 优先；对照 get-saas NextAuth 能力清单做 parity |
| Billing | 双方都有 Stripe；底座要抽象 provider + entitlement state machine |
| Product UX | get-saas 页面/后台/营销结构 |
| Multi-product | **双方都弱** → 自研 plugin contract 是差异化核心 |
| Agent skills | **双方都无** → 自研 agent surface 是差异化核心 |

### 4.4 Plugin 模型（草案）

每个产品插件最小清单：

```text
plugins/<product-slug>/
  plugin.manifest.json   # id, routes, nav, entitlements, deps
  schema/                # 插件自有表（隔离 namespace）
  routes/                # 业务路由挂载点
  ui/                    # 可选 UI 包
  skills/                # 插件专属 agent skills
  docs/                  # 产品说明 / story 入口
```

Kernel 提供 hooks（示意）：

- `onUserCreated` / `onSubscriptionActive` / `onEntitlementCheck`
- `registerNav` / `registerAdminSection` / `registerApiRoute`
- `registerI18nNamespace`

**硬约束（规划）**：

- 插件不得直连支付密钥；只消费 entitlement API  
- 插件 schema 迁移必须可独立版本化  
- 插件卸载不得破坏 kernel 用户/账单数据

---

## 5. Agent skill 体系（底座必须有的运营面）

目标：agent 打开仓库后 **知道怎么安全改底座 / 加插件 / 验证闭环**。

### 5.1 建议 skill 目录（产品仓内）

| Skill | 用途 |
|-------|------|
| `saas-base-orient` | 读架构边界、目录地图、禁止事项 |
| `saas-base-add-plugin` | 按 manifest scaffold 新插件 |
| `saas-base-auth-change` | 改登录提供方 / session / 角色 |
| `saas-base-billing-change` | 改 price/plan/webhook/权益 |
| `saas-base-i18n` | 加 locale / 补文案 / SEO meta |
| `saas-base-db-migrate` | schema 变更与迁移纪律 |
| `saas-base-smoke-qa` | 注册→登录→支付 sandbox→权益 冒烟 |
| `saas-base-release-checklist` | env / webhook / domain / 密钥检查 |

### 5.2 与 Beacon 协作

- 产品仓保留 `docs/beacon/`，用 Beacon 做 PRD→story→QA 证据链  
- Beacon research（本文）负责跨版本参考收敛  
- 实现期走 `beacon-goal` / implement 面，不在 plan 面写代码

---

## 6. Capability matrix — 底座 P0/P1/P2

### P0（能上线收一笔钱）

- Auth：邮箱密码 + 至少 1 个 OAuth  
- Session / 邮箱验证 / 重置密码  
- Billing：Stripe checkout + webhook + plan entitlement  
- Dashboard 最小面（账户 + 订阅状态）  
- i18n 双语言骨架（zh/en）  
- 邮件：验证 + 支付成功  
- Plugin contract v0 + 一个 example product plugin  
- Agent skills：orient / smoke-qa / add-plugin  
- Deploy path：至少 1 条（建议 CF 或 Node+Postgres 二选一作 primary，另一条 adapter stub）

### P1（可运营可扩展）

- Admin shell + newsletter  
- Points / credit ledger  
- Blog / marketing blocks  
- Feature flags  
- Multi-payment provider（Cremm 等）  
- Storage adapter  
- 第二宿主/数据库 adapter 完整可用  
- Skill 覆盖 auth/billing/i18n/migrate

### P2（平台化）

- Plugin marketplace / versioned install  
- Multi-tenant org  
- Audit log UI  
- Usage metering  
- 自动生成插件 skill 模板  
- 观测与告警包

---

## 7. 湖/海判断与拆分建议

**判定：海（ocean）**。建议拆湖：

| Lake | 范围 | Done when（规划口径） |
|------|------|------------------------|
| L0 Kernel skeleton | monorepo/layout + AGENTS + skill orient + plugin manifest schema | agent 能按 skill 定位边界 |
| L1 Identity | Better Auth + user/session/role | 注册登录重置可冒烟 |
| L2 Billing | Stripe + webhook + entitlement FSM | sandbox 支付改权益 |
| L3 Product shell | dashboard/admin/i18n/landing | 双语言壳可访问 |
| L4 Plugin v0 | example plugin 挂载导航与路由 | 新插件 30 分钟内可挂 |
| L5 Deploy adapters | CF Pages+D1 或 Postgres primary | 一键文档级部署路径 |
| L6 Agent QA pack | smoke-qa + release checklist | skill 可跑通主闭环 |

**Non-goals（本 program 初期）**：

- 完整复刻 get-saas 每一个页面与商业版差异  
- 立刻做多租户 org  
- 在 plan 面写生产代码 / freeze truth  
- 绑定单一云厂商到无法替换

---

## 8. High risks

1. **支付 / webhook / 权益状态机** — 错一次就资损或权益错乱  
2. **Auth 与会话安全** — OAuth、邮箱验证、CSRF、session 固定  
3. **插件数据隔离失败** — 卸载/迁移污染 kernel  
4. **双 runtime 适配（CF edge vs Node）** — 过早双实现会拖死  
5. **「抄模板」 vs 「底座」** — 直接 fork get-saas 会失去 plugin/agent 差异化  
6. **合规** — 隐私政策、退款、税务、营销邮件同意  

---

## 9. Options

| Option | 描述 | Tradeoff |
|--------|------|----------|
| A. Fork get-saas 再改 | 最快有页面 | 技术债与架构锁死；难插件化 |
| B. 绿场 Kernel + 能力对照表 | 干净边界 | 前期可见页面慢 |
| C. Hybrid（推荐） | 用 get-saas 作 **parity checklist**，绿场 Kernel 按 L0–L6 建；部署默认走 zyailive 低成本栈，Postgres 作兼容 adapter | 中等速度，长期正确 |

**Recommended**: **Option C**。

---

## 10. Recommended next (route)

1. **Stay in plan** until user acks ocean→lakes（本文 + 产品仓 docs）  
2. 用户确认 primary platform（CF+D1 vs Node+Postgres）  
3. 可选：把 `ItusiAI/get-saas` mirror 进 `oss-sync`，回填 source map  
4. Ack 后：`beacon-goal` 或 `beacon-truth` 按 L0→L2 顺序 freeze 首批湖  
5. **不要**在未 freeze 前大规模写业务代码

---

## 11. Evidence pointers

- X status: https://x.com/zyailive/status/2058790586052903250  
- get-saas: https://github.com/ItusiAI/get-saas  
- Product project plan root: `/Users/apple/Developer/Personal/products/open-saas-base/`  
- Local article capture: `open-saas-base/references/zyailive-2026-saas-base-article.md`

---

## 12. Change log

- 2026-07-21: initial research capture + synthesis + lake split + product project link


## 13. Decisions locked (2026-07-21)

1. Primary platform: **Cloudflare Pages + D1**
2. Public name: **open-saas-base**
3. get-saas mirror: `/Users/apple/Developer/Personal/oss-sync/saas/templates/get-saas` (`canonical`)
4. Delivery line: product **v0.0.1**, goal run `pgr-445fe60208ed`
5. Lakes L0–L6 implemented in monorepo (offline smoke green); live Stripe/CF secrets remain release checklist

## Plan authority (2026-07-21 reset)

Prior messy feature `truth.md` / goal stage claims under `open-saas-base` are **not** the planning authority.

**Current plan authority (advisory only)**:

- This research note
- Product program package: `open-saas-base/docs/beacon/v0.0.1/programs/open-saas-base-v001/`
- Local article capture: `open-saas-base/references/zyailive-2026-saas-base-article.md`
- Source mirror: `oss-sync/saas/templates/get-saas`

**Not authority**:

- Thin `features/*/truth.md` placeholders marked frozen without package (truth/tests/tasks/evidence)
- Prototype code under `apps/` / `packages/` until truth freeze + implement admission
- Goal runs that auto-advanced without journey package

**Recommended next harness**: after user acks program P4 → `beacon-gen-truth` per lake (feature package v2), not more plan-only code.
