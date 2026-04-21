# Implement 执行指南

**版本**: v1.3.6  
**命令**: `beacon implement`  
**职责**: 实现执行适配器 - 连接需求真相与代码实现

---

## 一、命令概览

### 1.1 核心职责

`beacon implement` 是实现阶段的执行适配器，负责：

1. **需求绑定**: 绑定到需求真相（PRD + User Story + Test Case + Prototype）
2. **执行编排**: 通过 Ralph runtime 或 Team surface 编排实现
3. **Git 工作流**: 管理分支守卫和实现计划门禁
4. **证据追踪**: 记录实现证据和交付契约

### 1.2 执行模式

| 模式 | 描述 | 适用场景 |
|------|------|---------|
| **Native** | 宿主原生实现 | 简单特性，单文件修改 |
| **Ralph** | 持久化循环 + architect 验证 | 复杂特性，需要多轮验证 |
| **Team** | 并行子 agent 编排 | 大型特性，可并行拆解 |

---

## 二、使用方式

### 2.1 基本用法

```bash
# 列出可用的 runner
beacon implement list-runners --json

# 运行实现（使用默认 runner）
beacon implement run "feature-name" --version v1.3.6

# 指定 runner
beacon implement run "feature-name" --version v1.3.6 --runner ralph

# 使用实现计划
beacon implement run "feature-name" --version v1.3.6 --plan-path docs/beacon/v1.3.6/execution/plan.md
```

### 2.2 高级用法

```bash
# Team 模式（并行子 agent）
beacon implement run "feature-name" --version v1.3.6 --runner team --team-size 3

# Ralph 模式（持久化循环）
beacon implement run "feature-name" --version v1.3.6 --runner ralph --max-rounds 5

# 指定 Git 分支
beacon implement run "feature-name" --version v1.3.6 --branch feature/my-branch

# 跳过 Git 工作流检查（不推荐）
beacon implement run "feature-name" --version v1.3.6 --skip-git-check
```

---

## 三、执行流程

### 3.1 完整执行流程

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 预检查 (Preflight)                                  │
│ - 检查需求材料完整性（PRD/User Story/Test Case/Prototype）  │
│ - 验证 Git 工作流契约                                        │
│ - 评估 takeover baseline gate                               │
│ - 检查实现计划（如果存在）                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 初始化 (Initialization)                             │
│ - 生成 run_id                                                │
│ - 创建实现工作目录 (.beacon/implement/{run_id})             │
│ - 初始化 Ralph state（如果使用 Ralph 模式）                 │
│ - 切换到目标分支（如果指定）                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: 执行 (Execution)                                    │
│ - Native: 直接调用 run_native_implementation()              │
│ - Ralph: 持久化循环，每轮 architect 验证                    │
│ - Team: 物化 team surface，并行子 agent 执行                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: 验证 (Verification)                                 │
│ - 检查实现计划进度（如果存在）                               │
│ - 验证交付契约                                               │
│ - 记录实现证据                                               │
│ - 写入 implement-to-qa handoff                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: 收尾 (Finalization)                                 │
│ - 更新证据清单                                               │
│ - 记录实现 writeback                                         │
│ - 保存 Ralph state（如果使用 Ralph 模式）                   │
│ - 输出实现摘要                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Ralph Runtime 流程

Ralph 是持久化循环模式，适用于复杂特性：

```python
# 初始化 Ralph state
ralph_state = {
    "run_id": "<uuid>",
    "feature": "feature-name",
    "version": "v1.3.6",
    "rounds": [],
    "status": "in_progress",
    "max_rounds": 5,
    "current_round": 0
}

# 每轮执行
for round in range(max_rounds):
    # 1. 执行实现
    result = execute_implementation(context)
    
    # 2. Architect 验证
    verification = architect_verify(result)
    
    # 3. 记录本轮
    append_ralph_round(ralph_state, {
        "round": round,
        "result": result,
        "verification": verification,
        "timestamp": now_iso()
    })
    
    # 4. 判断是否完成
    if verification["passed"]:
        finalize_ralph_state(ralph_state, "completed")
        break
    
    # 5. 判断是否需要 handoff
    if verification["requires_handoff"]:
        mark_ralph_handoff_required(ralph_state, verification["handoff_reason"])
        break
```

### 3.3 Team Surface 流程

Team 模式支持并行子 agent：

```python
# 1. 构建上下文隔离
context_isolation = build_context_isolation(
    feature="feature-name",
    version="v1.3.6",
    requirements={
        "prd": "docs/beacon/v1.3.6/prd/feature-name.md",
        "user_story": "docs/beacon/v1.3.6/user-story/feature-name.md",
        "test_case": "docs/beacon/v1.3.6/qa/test-cases/feature-name.md"
    }
)

# 2. 物化 team surface
team_contract = {
    "team_id": "<uuid>",
    "feature": "feature-name",
    "workers": [
        {"worker_id": "w1", "task": "实现核心逻辑"},
        {"worker_id": "w2", "task": "编写单元测试"},
        {"worker_id": "w3", "task": "更新文档"}
    ],
    "context_isolation": context_isolation
}

# 3. 生成 worker spec
for worker in team_contract["workers"]:
    write_worker_spec(worker["worker_id"], {
        "task": worker["task"],
        "context": context_isolation,
        "output_path": worker_result_path(worker["worker_id"])
    })

# 4. 启动 tmux workers
spawn_tmux_workers(team_contract["workers"])

# 5. 等待结果
results = wait_for_worker_results(team_contract["workers"])

# 6. 写入 implement-to-qa handoff
write_implement_to_qa_handoff({
    "team_id": team_contract["team_id"],
    "feature": "feature-name",
    "results": results,
    "timestamp": now_iso()
})
```

---

## 四、关键概念

### 4.1 实现计划 (Implementation Plan)

实现计划是可选的，但推荐用于复杂特性：

```markdown
# Implementation Plan: feature-name

## Phases

### Phase 1: 核心逻辑
- [ ] 实现 `core_function()` in `beacon/utils/core.py`
- [ ] 添加单元测试 `tests/test_core.py`

### Phase 2: 集成
- [ ] 集成到 `beacon/commands/implement.py`
- [ ] 更新 CLI 参数

### Phase 3: 文档
- [ ] 更新 SKILL.md
- [ ] 添加执行指南
```

**实现计划的好处**:
- 清晰的阶段划分
- 进度追踪
- 失败恢复点

### 4.2 Git 工作流契约 (Git Workflow Contract)

Git 工作流契约确保分支管理的一致性：

```json
{
  "feature": "feature-name",
  "version": "v1.3.6",
  "expected_branch": "beacon/v1.3.6",
  "implementation_plan_required": true,
  "branch_guard": {
    "enforce": true,
    "allowed_branches": ["beacon/v1.3.6", "feature/*"]
  }
}
```

**分支守卫规则**:
1. 实现必须在正确的分支上进行
2. 如果实现计划存在，必须先通过计划门禁
3. 禁止在 `main` 分支直接实现

### 4.3 Implement-to-QA Handoff

实现完成后，写入 handoff 文件供 QA 阶段使用：

```json
{
  "feature": "feature-name",
  "version": "v1.3.6",
  "run_id": "<uuid>",
  "implementation_mode": "ralph",
  "evidence": {
    "files_changed": ["beacon/commands/implement.py", "tests/test_implement.py"],
    "commits": ["abc123", "def456"],
    "test_coverage": 85.5
  },
  "delivery_contract": {
    "functional_complete": true,
    "tests_passing": true,
    "documentation_updated": true
  },
  "timestamp": "2026-04-21T16:30:00Z"
}
```

---

## 五、适配器系统

### 5.1 Skill Adapter

Beacon 通过适配器集成外部 skill：

```python
# 发现可用的 skill adapters
adapters = discover_skill_adapters(project_root)

# 解析适配器
adapter = resolve_adapter(
    feature="feature-name",
    adapters=adapters,
    default_runner="ralph"
)

# 执行适配器
result = adapter.execute(context={
    "feature": "feature-name",
    "version": "v1.3.6",
    "requirements": {...}
})
```

**适配器配置** (`.beacon/config.json`):

```json
{
  "implement": {
    "default_runner": "ralph",
    "adapters": [
      {
        "name": "ralph",
        "skill": "oh-my-claudecode:ralph",
        "template": "Implement {{feature}} according to requirements"
      },
      {
        "name": "team",
        "skill": "oh-my-claudecode:team",
        "template": "Team implementation for {{feature}}"
      }
    ]
  }
}
```

### 5.2 Native Implementation

Native 模式直接调用宿主实现：

```python
def run_native_implementation(
    feature: str,
    version: str,
    project_root: Path,
    requirements: dict
) -> dict:
    """
    宿主原生实现，适用于简单特性。
    
    Args:
        feature: 特性名称
        version: 版本号
        project_root: 项目根目录
        requirements: 需求材料
    
    Returns:
        实现结果
    """
    # 1. 构建实现上下文
    context = {
        "feature": feature,
        "version": version,
        "prd": requirements["prd"],
        "user_story": requirements["user_story"],
        "test_case": requirements["test_case"],
        "prototype": requirements.get("prototype")
    }
    
    # 2. 调用宿主 LLM
    result = host_llm_implement(context)
    
    # 3. 记录证据
    record_implementation_writeback(result)
    
    return result
```

---

## 六、故障排查

### 6.1 常见错误

#### 错误 1: 需求材料不完整

```
Error: Missing requirement materials
- PRD not found: docs/beacon/v1.3.6/prd/feature-name.md
```

**解决方案**:
```bash
# 先生成 PRD
beacon prd create "feature-name" --version v1.3.6

# 再生成 User Story
beacon user-story create "feature-name" --version v1.3.6

# 再生成 Test Case
beacon test-case create "feature-name" --version v1.3.6
```

#### 错误 2: Git 分支不匹配

```
Error: Branch guard violation
- Current branch: main
- Expected branch: beacon/v1.3.6
```

**解决方案**:
```bash
# 切换到正确的分支
git checkout beacon/v1.3.6

# 或者在命令中指定分支
beacon implement run "feature-name" --version v1.3.6 --branch beacon/v1.3.6
```

#### 错误 3: Ralph 循环超过最大轮数

```
Error: Ralph max rounds exceeded (5 rounds)
- Last verification: Failed (reason: test coverage too low)
```

**解决方案**:
```bash
# 增加最大轮数
beacon implement run "feature-name" --version v1.3.6 --runner ralph --max-rounds 10

# 或者手动修复后恢复
beacon implement resume --run-id <run_id>
```

### 6.2 调试技巧

#### 查看 Ralph state

```bash
# Ralph state 保存在
cat .beacon/implement/<run_id>/ralph-state.json
```

#### 查看实现证据

```bash
# 实现证据保存在
cat .beacon/implement/<run_id>/evidence.json
```

#### 查看 implement-to-qa handoff

```bash
# Handoff 文件保存在
cat .beacon/implement/<run_id>/implement-to-qa-handoff.json
```

---

## 七、最佳实践

### 7.1 选择合适的执行模式

| 特性复杂度 | 推荐模式 | 理由 |
|-----------|---------|------|
| 简单（单文件修改） | Native | 快速，无需额外编排 |
| 中等（多文件，需验证） | Ralph | 持久化循环，architect 验证 |
| 复杂（可并行拆解） | Team | 并行执行，提高效率 |

### 7.2 使用实现计划

对于复杂特性，建议先生成实现计划：

```bash
# 生成实现计划
beacon implement plan "feature-name" --version v1.3.6

# 查看计划
cat docs/beacon/v1.3.6/execution/implementation-plan-feature-name.md

# 使用计划执行
beacon implement run "feature-name" --version v1.3.6 --plan-path docs/beacon/v1.3.6/execution/implementation-plan-feature-name.md
```

### 7.3 增量实现

对于大型特性，建议分阶段实现：

```bash
# Phase 1: 核心逻辑
beacon implement run "feature-name-phase1" --version v1.3.6

# Phase 2: 集成
beacon implement run "feature-name-phase2" --version v1.3.6

# Phase 3: 文档
beacon implement run "feature-name-phase3" --version v1.3.6
```

### 7.4 验证交付契约

实现完成后，验证交付契约：

```bash
# 查看交付契约
beacon implement status --feature "feature-name" --version v1.3.6

# 验证契约
beacon implement verify --feature "feature-name" --version v1.3.6
```

---

## 八、与其他命令的集成

### 8.1 与 QA 的集成

```bash
# 实现完成后，自动写入 implement-to-qa handoff
beacon implement run "feature-name" --version v1.3.6

# QA 阶段读取 handoff
beacon qa run "feature-name" --version v1.3.6
```

### 8.2 与 Prototype 的集成

```bash
# 如果存在 prototype，自动绑定
beacon implement run "feature-name" --version v1.3.6

# 手动指定 prototype
beacon implement run "feature-name" --version v1.3.6 --prototype-dir docs/beacon/v1.3.6/prototype/feature-name
```

### 8.3 与 Release 的集成

```bash
# 实现完成后，更新证据清单
beacon implement run "feature-name" --version v1.3.6

# Release 阶段读取证据
beacon release check --version v1.3.6
```

---

## 九、参考

### 9.1 相关文件

- `beacon/commands/implement.py`: 实现命令主文件
- `beacon/utils/ralph_runtime.py`: Ralph runtime 实现
- `beacon/utils/team_surface.py`: Team surface 实现
- `beacon/utils/implementation_plan.py`: 实现计划工具
- `beacon/utils/git_alignment.py`: Git 工作流契约

### 9.2 相关命令

- `beacon prd`: 生成 PRD
- `beacon user-story`: 生成 User Story
- `beacon test-case`: 生成 Test Case
- `beacon prototype`: 生成 Prototype
- `beacon qa`: QA 验证
- `beacon release`: 发布管理

### 9.3 相关文档

- `docs/beacon/global-boundaries.md`: 全局边界约束
- `docs/beacon/v1.3.6/execution/architecture-blueprint.md`: 架构蓝图
- `docs/beacon/v1.3.6/execution/boundaries.md`: 执行边界

---

**文档版本**: v1.3.6  
**最后更新**: 2026-04-21  
**维护者**: Beacon Team
