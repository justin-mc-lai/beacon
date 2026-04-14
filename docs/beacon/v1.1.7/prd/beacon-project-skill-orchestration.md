# PRD: Beacon 项目级 skill profile、多 skill 编排与强证据验收（v1.1.7）

## 1. 背景

Beacon v1.1.7 已经完成：

- lifecycle closure
- native runner
- item writeback
- help / doctor advise / status / scoring
- formal accept

但在真实项目里，尤其是像 Rolo 这种：

- 多服务部署
- UAT gateway 存在统一入口规范
- 发布要走项目既有 CI/CD pipeline
- 验收需要查接口 / 页面 / 日志 / SQL / Redis / 工单证据

仅靠通用 QA 模板还不够。

问题不是 Beacon 不会生成需求，而是：

> Beacon 还不知道“某个项目的真实交付/验收路径是什么”。

典型漏测场景：

- 文档声明支持
- 前端控件允许上传
- 下游服务却不支持
- 但由于没有把真实验收链路固化成 must-run evidence，最终仍被误判为“通过”

## 2. 第一性原理结论

### 2.1 Beacon 应该负责什么

- 定义正式需求 / QA / accept gate
- 定义 required evidence contract
- 定义 skill/profile/orchestration 抽象
- 在 accept 前阻断缺失证据或合同漂移

### 2.2 Beacon 不应该负责什么

- 复制每个项目自己的全部运行时平台
- 把所有项目技能硬编码成 Beacon 内部实现
- 把 rolo-dev 这种项目 skill 的每个命令都直接内嵌进 Beacon Core

### 2.3 Beacon 需要新增的中间层

Beacon Core 与项目执行面之间，需要一层：

- `Skill Registry`
- `Project Profile`
- `Skill Adapter`
- `Orchestration Graph`
- `Required Evidence Gate`

## 3. 目标

1. **支持 Beacon 内置 multi-skill registry**
2. **支持 project-specific profile**
3. **支持 feature / stage 绑定 skill**
4. **支持 skill-backed orchestration**
5. **支持 required evidence gate**
6. **支持 contract drift diagnosis**
7. **以 Rolo 作为首个真实验证样板**

## 4. 核心设计

## 4.1 Skill Registry

Beacon 需要正式支持 skill registry，而不只是“外部命令字符串”。

### 建议对象字段
- `skill_id`
- `kind`（builtin / external / bridge）
- `entry`
- `capabilities[]`
- `requires_env[]`
- `supported_stages[]`
- `evidence_contract`

### 目标
- Beacon 知道有哪些 skills 可用
- Beacon 知道某个 stage 可以调用哪些 skills
- Beacon 知道这些 skill 会产出什么 evidence

## 4.2 Project Profile

每个项目可以定义自己的 profile，例如：

```yaml
project: rolo
profile_id: rolo-uat
skills:
  verify: rolo-dev
  delivery: rolo-dev
  debug: rolo-dev
  docs_sync: rolo-dev
required_evidence:
  - pipeline_run
  - gateway_smoke
  - interface_contract
  - required_business_case
```

### 目标
- Beacon 不再假设所有项目都走同一条 verify 路径
- 每个项目能声明自己的验收事实源

## 4.3 Feature/Stage Skill Binding

一个 feature 可以整体绑定 profile，一个 stage 也可以绑定 skill：

- implementation → `native-team`
- verify → `rolo-dev`
- debug → `rolo-dev`
- browser QA → `gstack` / `browser-use` / `playwright`

这样 Beacon 才能做到：

> 用统一生命周期管控，不同项目走不同执行面。

## 4.4 Orchestration Graph

Beacon 需要支持 skill-backed orchestration graph。

例如：

```text
freeze
→ implement
→ pipeline
→ deploy_wait
→ gateway_smoke
→ interface_verify
→ log_sql_verify
→ review quality
→ accept
```

### 编排节点需要有：
- node_id
- skill_id
- stage
- command / task template
- success criteria
- evidence outputs
- retry policy
- block policy

## 4.5 Required Evidence Gate

accept 不再只依赖：
- `auto-test-status = passed`

而要依赖：
- required test case evidence 是否存在
- required environment verification 是否存在
- required pipeline evidence 是否存在
- required negative-path verification 是否存在

### 示例
对于 Rolo 的 `KZFJ-1110`：

如果 `mp4 upload success` 是 required case，且没有对应 evidence：

- `review quality` = blocked
- `review accept` = blocked

## 4.6 Contract Drift Diagnosis

Beacon 需要能识别：

- 文档声明支持 `gif/mp4`
- FE 允许 `gif/mp4`
- downstream service 仅支持 `jpg/png/pdf`

并输出：
- `reason_code = contract_drift`
- drift layer
- candidate fix path

## 5. Rolo 作为首个真实样板

## 5.1 为什么选 Rolo

Rolo 具备 Beacon 最难覆盖的一类真实项目特征：

- 多服务
- 本地 / UAT / pipeline / gateway 多层环境
- skill 已经存在（`rolo-dev`）
- 验收不是单测，而是多阶段链路验证

## 5.2 Rolo 验收链路抽象

以 `KZFJ-1110` 为例，真正需要验证的是：

- `marketing_primary_fe`
- `marketing_sys`
- downstream STS/upload service
- OSS JSON publish
- UAT gateway
- optional client contract

### 真实链路应抽象为

```text
前端上传
→ /admin/oss/sts
→ marketing_sys
→ downstream sts service
→ oss upload
→ save task
→ publish oss json
→ uat verify
```

## 5.3 Rolo Profile 示例

```yaml
project: rolo
profile_id: rolo-uat
skills:
  verify: rolo-dev
  delivery: rolo-dev
  debug: rolo-dev
  pipeline: rolo-dev
required_cases:
  - upload_jpg_success
  - upload_gif_success
  - upload_mp4_success
  - invalid_type_rejected
  - oss_json_publish_success
required_evidence:
  - uat_pipeline_run
  - gateway_smoke
  - interface_response
  - optional_log_or_sql_snapshot
```

## 6. 建议命令面

### 6.1 Skill/Profile 管理
- `beacon skill registry list`
- `beacon skill bind <feature> --skill <skill>`
- `beacon profile create <project>`
- `beacon profile show <project>`

### 6.2 编排执行
- `beacon orchestrate run <feature> --profile <profile>`
- `beacon verify run <feature> --profile <profile>`
- `beacon evidence check <feature> --profile <profile>`

### 6.3 质量/验收门禁
- `beacon review quality <feature>` 读取 required evidence
- `beacon review accept <feature>` 读取 must-run case completion

## 7. 验收语义

### Pass
- profile 解析成功
- required skills 可执行
- required evidence 全部齐全
- review quality 不存在 critical blocker
- accept 允许进入 accepted

### Fail
- 编排执行失败
- required case 明确失败
- required pipeline/gateway/interface evidence 为 fail

### Blocked
- project profile 缺失
- skill 不可用
- required evidence 缺失
- contract drift 未解决

## 8. 风险

- 如果 skill registry 只做字符串映射，不做 evidence contract，仍然无法挡住漏测
- 如果 project profile 不可声明 required evidence，accept 仍会漂移
- 如果 orchestration 不支持 stage binding，Beacon 仍然只能做“外部命令提示器”
- 如果不把 Rolo 这种真实多服务项目作为首个样板，设计会继续停留在通用层
