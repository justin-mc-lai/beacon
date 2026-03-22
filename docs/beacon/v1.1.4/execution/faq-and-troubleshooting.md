# Beacon v1.1.4 FAQ / Troubleshooting

> 目标：汇总 Beacon v1.1.4 在真实使用中最常见的问题、原因和排查路径。

---

## 1. 最常见的排查顺序

出现问题时，不要直接猜。先按这个顺序看：

```bash
beacon skill detect --json
beacon implement list-runners --json
beacon implement run "<feature>" --dry-run --json
beacon implement status "<feature>" --json
```

然后看这些文件：

```text
.beacon/implement/<run_id>/request.json
.beacon/implement/<run_id>/command.txt
.beacon/implement/<run_id>/stdout.log
.beacon/implement/<run_id>/stderr.log
.beacon/implement/<run_id>/result.json
```

---

## 2. FAQ：为什么 `beacon implement run` 被 blocked

### 现象

你执行：

```bash
beacon implement run "<feature>" ...
```

结果返回 blocked 或非 0 退出码。

### 常见原因

1. 没有 runner
2. runner 未检测到
3. feature 主链文档不完整
4. result 文件没有生成

### 优先检查

```bash
beacon implement list-runners --json
```

看：
- `preferred`
- `detected`
- `adapter_type`

---

## 3. `runner_not_configured`

### 含义

Beacon 没找到可用 runner。

### 常见场景

- 没传 `--runner`
- 没配置 `beacon.config.yaml`
- 没设 `skill.preferred`
- 没设 `implementation.default_runner`

### 修复方法

最小修复：

```yaml
skill:
  preferred: omx

implementation:
  default_runner: omx
```

然后再试：

```bash
beacon implement list-runners --json
```

---

## 4. `runner_command_not_found`

### 含义

Beacon 找到了 runner 配置，但系统里没有对应命令。

### 常见场景

- 配了 `command: omx`，但 PATH 里没有 `omx`
- 配了自定义脚本命令，但脚本不存在

### 修复方法

先手工验证：

```bash
omx --help
omc --help
```

或：

```bash
which omx
which omc
```

---

## 5. `runner_execution_timeout`

### 含义

runner 命令执行超时。

### 常见场景

- 任务太大
- runner 卡住
- 外部 CLI 等待交互

### 修复方法

1. 先用更小 slice 重试
2. 提高 `timeout_sec`
3. 确认 runner 是非交互模式

例如 OMX 当前推荐：

```yaml
args:
  - exec
  - --full-auto
  - --cd
  - "{project_root}"
  - --skip-git-repo-check
  - "{task_prompt}"
```

---

## 6. `runner_result_missing`

### 含义

runner 执行完了，但没有写出：

```text
.beacon/implement/<run_id>/result.json
```

### 常见场景

- 外部 runner 没按 contract 写文件
- task prompt 没明确要求写 result
- 路径写错

### 排查方式

先看：

```bash
cat .beacon/implement/<run_id>/command.txt
cat .beacon/implement/<run_id>/request.json
cat .beacon/implement/<run_id>/stdout.log
cat .beacon/implement/<run_id>/stderr.log
```

然后确认 task prompt 中是否有：

```text
Write structured result to .beacon/implement/<run_id>/result.json
```

---

## 7. `runner_result_invalid`

### 含义

runner 写了 result 文件，但结构不合法。

### 最小合法结构

```json
{
  "schema_version": "1.0",
  "run_id": "run-xxx",
  "status": "completed",
  "summary": "done",
  "changed_files": [],
  "verification": [],
  "artifact_updates": {}
}
```

### 常见场景

- result 不是合法 JSON
- 缺少 `status`
- 缺少 `summary`
- `changed_files` 不是数组

---

## 8. `implement_execution_failed`

### 含义

runner 返回了 result，但它自己报告没有完成实现。

### 常见场景

- result 中：

```json
{ "status": "failed" }
```

- runner 没完成目标，只输出了一些中间态

### 建议处理

先不要直接改 Beacon。先回看：

1. task prompt 是否太大
2. feature 是否没切 slice
3. runner 是否本身能力不适合该任务

---

## 9. FAQ：为什么 dry-run 看起来对，但正式执行失败

### 原因

dry-run 只验证三件事：

1. request 是否生成
2. task prompt 是否拼装
3. command 是否能构造

它**不保证**：
- runner 真能执行成功
- result 真能写出来
- review / quality 一定通过

### 正确认知

```text
dry-run = contract and assembly check
formal run = real execution check
```

---

## 10. FAQ：为什么 `implement status` 显示 `summary_exists=false`

### 含义

Beacon 还没有产出：

```text
docs/beacon/<version>/execution/implementation-summary-<feature>.json
```

### 常见原因

- 你跑的是 dry-run
- 正式执行失败
- result 无效

### 正常情况

#### dry-run

```json
{
  "status": "dry_run",
  "summary_exists": false
}
```

这是正常的。

---

## 11. FAQ：为什么 `review_spec_exists=false`

### 含义

还没有生成：

```text
docs/beacon/<version>/execution/review-spec-<feature>.json
```

### 常见原因

- 没有正式实现成功
- `auto_review_spec` 被关闭
- 还没手工跑：

```bash
beacon review spec <feature> --project . --version <version> --json
```

---

## 12. FAQ：为什么非 git 项目也能跑 implement

因为 Beacon v1.1.4 内置 OMX 走的是：

```bash
omx exec --full-auto --cd "{project_root}" --skip-git-repo-check "{task_prompt}"
```

其中：
- `--cd` 指定工作目录
- `--skip-git-repo-check` 允许非 git 项目

### 典型适用

- WordPress 主题目录
- 内容站点目录
- 非标准工程仓

---

## 13. FAQ：为什么多服务 workspace 不适合直接在根目录 implement

### 原因

Beacon 的 `implement run <feature>` 最擅长：

```text
一个 feature -> 一个明确实现面
```

而多服务 workspace 往往是：

```text
一个 feature -> 多个服务 repo
```

### 正确做法

先做：
- service-slice 拆分

例如：
- `sku-commission-marketing-sys`
- `sku-commission-marketing-primary-fe`
- `sku-commission-order-svr`

然后把真正实现放到目标服务 repo 里执行。

---

## 14. FAQ：为什么 root `SKILL.md` 还保留

因为 v1.1.4 采用的是双层模型：

### 标准 skill 包

```text
skills/beacon/
```

### 兼容入口

```text
SKILL.md
```

保留根 `SKILL.md` 的原因：

- doctor/runtime 版本检查依赖它
- 安装态 skill copy drift 检查依赖它
- 现有测试和兼容入口依赖它

---

## 15. FAQ：为什么标准 skill 包和根 skill 同时存在

这是为了同时满足：

1. **标准规范**
   - `skills/beacon/SKILL.md`
2. **兼容现有生态**
   - 根 `SKILL.md`

这不是重复，而是：

```text
skills/beacon/ = canonical standard package
SKILL.md       = compatibility mirror
```

---

## 16. FAQ：slow-wp 这类项目为什么要在 workspace 根放配置

因为有些项目希望：

- 配置源集中在 workspace 根
- 子项目只做引用

推荐方式：

```text
my_skill/
├── beacon.config.yaml
└── slow-wp/
    └── beacon.config.yaml -> ../beacon.config.yaml
```

### 为什么要用 symlink

因为 Beacon 当前默认读取：

```text
<project-root>/beacon.config.yaml
```

不会自动向父目录递归查找。

所以如果你只把配置放在 workspace 根，而不让项目根也能看到这个文件，project-root 下的 Beacon 是吃不到配置的。

---

## 17. FAQ：OMX / OMC / gstack 我该选哪个

### 推荐顺序

#### 1. OMX
当前最推荐，原因：
- Beacon 已内置并实战修正
- 支持 `omx exec`
- 对非 git 项目也友好

#### 2. gstack
更适合：
- handoff
- 人工接续

#### 3. OMC
建议先项目内显式定义 args，再正式用。

---

## 18. FAQ：什么时候应该先切 slice

出现任一情况就切：

1. feature 太大
2. 同时跨 UI/API/数据模型
3. 同时跨多个服务
4. 无法明确改哪个目录

### 错误示例

```text
ecommerce-template
v1.3.0-core-features
full-release
```

### 正确示例

```text
theme-shell-foundation
mega-menu-navigation
sku-commission-marketing-sys
health-report-guidance-download-marketing-primary-fe
```

---

## 19. FAQ：release / delivery 为什么还会 fail

即使你有：

- SUMMARY
- user-story
- prd
- test-case

也不代表 latest Beacon delivery 一定 pass。

还要补 execution / release 工件：

```text
execution/
├── boundaries.md
├── config.json
├── source.json
├── git-alignment.json
├── change-impact.json
├── delivery-manifest.json
└── terminal.json

release/
└── <version>.md
```

---

## 20. 最后一条 troubleshooting 原则

如果你发现 Beacon “好像不工作”，先不要急着改代码。

先确认这 4 件事：

1. 主链文档是否完整
2. runner 是否真实可用
3. feature 是否切到了正确粒度
4. 你是不是把 Beacon 当成了 scheduler，而不是 delivery kernel

这四步里，前 3 步出问题的概率，远高于 Beacon 本身有 bug。

