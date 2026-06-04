# PRD: Beacon autoresearch-inspired Eval Lab（v1.1.5）

## 1. 背景

`autoresearch` 的启发不在于“AI 自动做研究”，而在于它把自动研究收缩成一个严格小闭环：

1. 固定评估面
2. 极小可编辑面
3. keep/discard
4. 实验账本

Beacon 当前的问题不是没有验证，而是缺少一种**面向自身规则层**的稳定迭代机制。我们需要验证：
- skill 是否稳定
- 置信度是否可靠
- 需求到实现是否漂移
- DB 字段到 API / UI 是否漂移
- doctor / review / gate 是否发现真实问题而不是假通过

## 2. 第一性原理结论

如果目标是“让 Beacon 学习像 autoresearch 一样思考”，最短路径不是自改整仓代码，而是：

> 先把 Beacon 的规则层、提示词层和漂移审计层纳入固定 benchmark 面下的 keep/discard 循环。

## 3. 目标

1. 定义 Beacon 固定 benchmark 面
2. 定义允许自动研究的最小可编辑面
3. 定义 keep/discard 硬门槛与软评分
4. 定义最小 drift auditor 闭环
5. 定义研究账本与证据格式

## 4. 固定 Benchmark 面

v1.1.5 应冻结 4 类 benchmark：

### 4.1 Delivery Closure Benchmark
- `doctor verify-materials`
- `doctor verify-delivery`
- `gate check release`
- `status` / `report` 基本可读性与指标稳定性

### 4.2 Human-Machine Layering Benchmark
- human primary surface 是否仍为 Markdown-first
- `.machine` 是否为正式机器面
- README / SUMMARY / release 是否未把 machine JSON 当 primary reading path

### 4.3 Drift Audit Benchmark
- requirement -> db
- db -> api
- api -> ui
- feature -> test-case
- implementation summary -> review spec

### 4.4 Confidence Benchmark
- confidence 与实际结果的一致性
- 高置信度错误率
- review/doctor 的误报与漏报风险

## 5. 最小可编辑面

Beacon 自动研究阶段仅允许编辑：

### 5.1 Prompt Policy Layer
- human/machine reading order
- progressive disclosure policy
- clarification gate policy
- doctor role policy

### 5.2 Rule Policy Layer
- doctor repair rules
- review/gate strictness rules
- memory projection rules
- human primary surface rules

### 5.3 Drift Extractor Layer
- db field extractor rules
- api field extractor rules
- ui field extractor rules
- comparator / scoring rules

### 明确不在可编辑面内
- 整个 Beacon 业务代码树
- CLI 框架整体
- runtime orchestration 能力
- 外部 runner 本体实现

## 6. Keep / Discard 规则

## 6.1 Hard Gates（任何一项失败即 discard）
1. `verify-materials` 不通过
2. `verify-delivery` 不通过
3. `status/report/gate` 被破坏
4. machine artifacts 丢失或不可读
5. human primary surface 被 machine artifacts 重新污染

## 6.2 Soft Scores（用于比较优劣）
1. Human Cognitive Load Score
2. Drift Detection Score
3. Confidence Calibration Score
4. Doctor Repair Success Score
5. Cost / Complexity Score

## 7. Drift Auditor 最小闭环

## 7.1 Step 1：需求结构化
从：
- user-story
- prd
- qa/test-case

提取：
- fields
- actions
- constraints
- permissions

## 7.2 Step 2：实现结构化
从代码中提取：
- db schema / migration / model
- api schema / handler / dto
- ui field / form / table / detail display

## 7.3 Step 3：图谱对齐
对齐：
- 需求字段是否落库
- 落库字段是否暴露 API
- API 字段是否被 UI 消费
- UI 字段是否有需求来源

## 7.4 Step 4：输出结论
输出：
- drift report
- missing coverage
- orphan fields
- confidence
- evidence refs

## 8. 研究账本

每次实验/规则迭代都必须落盘：
- 改动对象
- benchmark 结果
- keep/discard 结论
- 原因
- evidence

推荐目标路径（需求层冻结，不代表已实现）：

```text
.beacon/state/eval-lab/
├── experiments/
├── scores/
├── keep-discard-log.jsonl
└── drift-audit/
```

## 9. 非目标

- 不做模型训练平台
- 不做大规模 agent swarm 编排
- 不先允许整仓自修改
- 不在本版实现所有自动研究功能

## 10. 成功标准

- Beacon 具备固定 benchmark 面定义
- keep/discard 规则可审计
- drift auditor 最小闭环定义清晰
- 自动研究目标限定在规则层 / 提示词层 / 漂移审计层
- Beacon 仍保持 delivery kernel 定位
