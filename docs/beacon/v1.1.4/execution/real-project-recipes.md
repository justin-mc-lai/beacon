# Beacon v1.1.4 Real Project Recipes

> 目标：把 Beacon v1.1.4 放进真实项目里时，给出**可直接照抄的使用配方**，而不是只讲抽象设计。

---

## 1. 这份文档适合谁

适合下面四类项目：

1. **单仓应用项目**
2. **非 git / 内容型项目**
3. **`slow-wp` 这类 WordPress 主题项目**
4. **`rolo` 这类多服务 workspace 项目**

如果你只想知道一句话：

> **Beacon 负责需求闭环与交付证据，真实实现面由你的 runner / 项目开发规范承接。**

---

## 2. Recipe 0：所有项目的统一前置动作

不管你是什么项目，先做这 4 步：

### 2.1 确认当前 Beacon 版本

```bash
beacon --version
```

### 2.2 确认主链物料是否存在

至少要有：

```text
docs/beacon/<version>/
├── user-story/<feature>.md
├── prd/<feature>.md
└── qa/test-cases/<feature>.md
```

### 2.3 确认 runner 是否可用

```bash
beacon skill detect --json
beacon implement list-runners --json
```

### 2.4 先 dry-run 再正式执行

```bash
beacon implement run "<feature>" \
  --project-root . \
  --version <version> \
  --runner omx \
  --dry-run \
  --json
```

---

## 3. Recipe 1：单仓应用项目

### 适用项目

- 一个 git repo
- 一个服务 / 一个应用
- feature 能直接对应一组 `user-story/prd/test-case`

### 典型结构

```text
my-app/
├── docs/beacon/vX.Y.Z/
├── src/
├── tests/
└── beacon.config.yaml
```

### 推荐配置

```yaml
skill:
  preferred: omx

implementation:
  default_runner: omx
  auto_review_spec: true
  auto_review_quality: false
```

### 推荐执行顺序

```bash
beacon skill list
beacon implement list-runners --json

beacon implement run "<feature>" \
  --project-root . \
  --version <version> \
  --runner omx \
  --dry-run \
  --json

beacon implement run "<feature>" \
  --project-root . \
  --version <version> \
  --runner omx \
  --json

beacon implement status "<feature>" --project-root . --version <version> --json
beacon review spec "<feature>" --project . --version <version> --json
beacon review quality "<feature>" --project . --version <version> --json
```

### 什么时候不要直接 implement

如果你的 feature 文档还是“大而全”的单文件，先切 slice，再 implement。

---

## 4. Recipe 2：非 git / 内容型项目

### 适用项目

- 没有 git repo
- 主题目录 / 站点目录 / 内容目录
- 需要 AI 帮你落地实现，但不走标准工程仓工作流

### 关键点

Beacon v1.1.4 内置 OMX 已经适配：

```bash
omx exec --full-auto --cd "{project_root}" --skip-git-repo-check "{task_prompt}"
```

所以这类项目也能进入 implement 闭环。

### 推荐动作

1. 先把 feature 切成 implement-ready slice
2. 给项目写 `beacon.config.yaml`
3. 用 `omx` 先 dry-run
4. 确认 request / command / task_prompt 正确后再正式执行

### 推荐配置

```yaml
skill:
  preferred: omx

implementation:
  default_runner: omx
  auto_review_spec: true
  auto_review_quality: false
```

### 注意

这类项目不要直接把一个超大 feature 扔给 implement。

正确做法：

> **先切 slice，再执行。**

---

## 5. Recipe 3：`slow-wp`（WordPress 主题项目）

### 项目特征

`slow-wp` 是一个：

- WordPress + WooCommerce 主题项目
- 当前根目录不是严格 git repo
- 主题实现应落在：
  - `wp-content/themes/slow-uni/`

### Beacon 最佳定位

Beacon 在 `slow-wp` 中不是“重新做需求”，而是：

> **把已有需求物料变成 implement-ready slices，并驱动 theme 开发闭环。**

### 推荐切片顺序

#### 第一批

1. `theme-shell-foundation`
2. `mega-menu-navigation`
3. `product-list-and-detail`

#### 第二批

4. `cart-and-inquiry`
5. `checkout-payment`
6. `responsive-mobile-polish`

### 推荐配置实践

`slow-wp` 当前推荐配置源可以放在 workspace 根，再由项目内 `beacon.config.yaml` 指向它。

#### 例子

```text
my_skill/
├── beacon.config.yaml
└── slow-wp/
    └── beacon.config.yaml -> ../beacon.config.yaml
```

### 推荐命令

```bash
beacon implement run theme-shell-foundation \
  --project-root /abs/path/to/slow-wp \
  --version v0.1.0 \
  --runner omx \
  --dry-run \
  --json
```

### 你应该检查什么

检查 dry-run 结果里：

- `request.json`
- `task_prompt`
- `command.txt`

重点确认：

- 输入文档是对应 slice
- 输出目标是 `wp-content/themes/slow-uni/`
- 没有误把整个 WordPress 站点都当成实现目标

### 不推荐的做法

```text
直接对 ecommerce-template.md 这种大而全单文档执行 implement
```

正确做法是：

```text
先按 theme shell / menu / product / cart / checkout / mobile 分 slice
```

---

## 6. Recipe 4：`rolo`（多服务 workspace 项目）

### 项目特征

`rolo` 是典型的：

- 多服务 workspace
- 根目录不是单一服务 repo
- 子目录服务各自有自己的 git / 分支 / UAT 交付规则
- 有强约束的仓内治理（尤其 `rolo-dev`）

### Beacon 最佳定位

在 `rolo` 里，Beacon 最适合做：

- version 包治理
- feature map / story / PRD / QA / architecture
- delivery evidence
- service-slice 拆解

而不是：

> 直接在 workspace 根目录做一把梭代码实现

### 最新推荐模式

#### 第一步：升级到 latest Beacon delivery standard

至少补齐：

```text
docs/beacon/v1.3.0/execution/
├── boundaries.md
├── config.json
├── source.json
├── git-alignment.json
├── change-impact.json
├── delivery-manifest.json
└── terminal.json
```

以及：

```text
docs/beacon/v1.3.0/release/v1.3.0.md
```

#### 第二步：把 feature 拆成 service-slice

例如：

### F1 / KZFJ-1111
- `sku-commission-marketing-sys`
- `sku-commission-marketing-primary-fe`
- `sku-commission-order-svr`

### F2 / KZFJ-1110
- `splash-marketing-content-marketing-sys`
- `splash-marketing-content-marketing-primary-fe`
- `splash-marketing-content-client-contract`

### F3 / KZFJ-1108
- `health-report-guidance-download-marketing-primary-fe`
- `health-report-guidance-download-report-contract`

#### 第三步：真正的实现交给服务 repo + `rolo-dev`

心智模型：

```text
Beacon = docs / slice / review / delivery
rolo-dev = service impl / gateway / swagger / sql / uat
```

### 特别注意

在 `rolo` 里，Beacon 不应替代：

- 分支治理
- UAT 流程
- gateway / swagger / deploy rules

这些必须继续遵守 `rolo-dev` 和仓内 `AGENTS.md`。

### 当前边界示例

对于 F1：

- `marketing_sys`：配置与 API 聚合
- `marketing_primary_fe`：后台页面 / 表单 / 列表
- `order-svr`：SKU/订单分成落库与订单详情输出
- `marketing_distributor_fe`：只读消费端参考，不属于本次交付项目
- 外部佣金服务：通过订单详情接口同步读取

### 在 rolo 中不推荐的做法

```text
在 rolo workspace 根目录直接跑 implement 去改多个服务代码
```

正确做法：

1. 用 Beacon 把 requirement package 和 service-slice 准备好
2. 进入目标服务 repo
3. 用服务自己的分支规则和 `rolo-dev` 去执行

---

## 7. 什么时候要切 slice

出现下面任一情况，就先切 slice：

1. 一个 feature 横跨多个服务
2. 一个 feature 同时包含 UI + API + data contract
3. QA 文档是 release-level 总览，而不是具体实现点
4. 你无法明确“这次 implement 应该落在哪个目录”

### Beacon 推荐切片粒度

```text
一个 slice = 一个明确实现面
```

例如：

- `theme-shell-foundation`
- `sku-commission-marketing-sys`
- `health-report-guidance-download-marketing-primary-fe`

而不是：

- `v1.3.0-core-features`
- `ecommerce-template`
- `full-release`

---

## 8. 项目选择表

| 项目类型 | Beacon 应该做什么 | 不该做什么 |
| --- | --- | --- |
| 单仓应用 | 直接 implement + review + gate | 把所有 feature 挤成一个超大实现任务 |
| 非 git 内容项目 | 切 slice 后 implement | 直接拿大 PRD 整包跑实现 |
| `slow-wp` | 主题 slice + omx implement | 直接实现整个 WooCommerce 站点 |
| `rolo` | delivery standard + service-slice + review | 在 workspace 根目录直接跨服务改代码 |

---

## 9. 最常见实战顺序

### 通用版

```bash
beacon skill detect --json
beacon implement list-runners --json
beacon implement run "<feature>" --dry-run --json
beacon implement run "<feature>" --json
beacon implement status "<feature>" --json
beacon review spec "<feature>" --json
beacon review quality "<feature>" --json
beacon gate check release --json
```

### Skill wrapper 版

```bash
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json
bash skills/beacon/scripts/run_beacon.sh implement run "<feature>" --dry-run --json
```

---

## 10. 最后一条建议

Beacon v1.1.4 在实战里最好用的方式，不是“让它包办一切”，而是：

> **让它负责闭环，让 runner / 项目开发规范负责实现。**

这样才最稳定，也最符合 v1.1.4 的设计边界。

