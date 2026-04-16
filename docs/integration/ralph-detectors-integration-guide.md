# 集成指南：ExitDetector 和 CircuitBreaker 到 Beacon Implement

**目标**: 将 Ralph 风格的检测器集成到 `beacon implement` 的 Ralph 模式中

---

## 集成位置

**文件**: `beacon/commands/implement.py`  
**函数**: `_run_ralph_controller()` (第 367 行)

### 当前 Ralph 循环结构

```python
def _run_ralph_controller(...):
    # 初始化 Ralph 状态
    initialize_ralph_state(...)
    
    # 循环执行
    for round_index in range(1, max_rounds + 1):
        # 执行一轮实现
        exit_code, round_payload = run_implement_stage(...)
        
        # 记录轮次
        append_ralph_round(...)
        
        # 检查是否需要人工介入
        if round_payload.get("handoff_required"):
            mark_ralph_handoff_required(...)
            break
        
        # 更新状态
        last_payload = round_payload
        last_exit_code = exit_code
    
    # 完成 Ralph 状态
    finalize_ralph_state(...)
```

---

## 集成方案

### 1. 在循环开始前初始化检测器

```python
from beacon.utils.exit_detector import ExitDetector
from beacon.utils.circuit_breaker import CircuitBreaker

def _run_ralph_controller(...):
    # ... 现有初始化代码 ...
    
    # 初始化检测器
    exit_detector = ExitDetector(
        completion_threshold=2,
        completion_patterns=[
            r"implementation\s+complete",
            r"all\s+tests?\s+pass(?:ing|ed)",
            r"ready\s+for\s+(?:review|qa|release)",
            r"实现完成",
            r"所有测试通过",
        ],
    )
    
    circuit_breaker = CircuitBreaker(
        no_progress_threshold=3,
        same_error_threshold=3,
        output_decline_threshold=3,
        min_output_length=100,
    )
```

### 2. 在循环中检查熔断器

```python
    for round_index in range(1, max_rounds + 1):
        # 执行一轮实现
        exit_code, round_payload = run_implement_stage(...)
        
        # 记录轮次
        append_ralph_round(...)
        
        # === 新增：熔断器检查 ===
        result_for_breaker = {
            "output": round_payload.get("summary", ""),
            "error": round_payload.get("error_message", ""),
        }
        is_stuck, stuck_reason = circuit_breaker.detect_stuck(
            round_index, 
            result_for_breaker
        )
        
        if is_stuck:
            # 记录熔断原因
            round_payload["circuit_breaker_triggered"] = True
            round_payload["stuck_reason"] = stuck_reason
            
            # 标记需要人工介入
            mark_ralph_handoff_required(
                project_root,
                feature=feature,
                reason=f"Circuit breaker triggered: {stuck_reason}",
                action="review_and_adjust",
            )
            break
        
        # ... 现有 handoff 检查 ...
```

### 3. 在循环中检查退出条件

```python
        # === 新增：退出条件检查 ===
        result_for_exit = {
            "output": round_payload.get("summary", ""),
            "EXIT_SIGNAL": round_payload.get("implementation_complete", False),
        }
        should_exit, exit_reason = exit_detector.check_exit(result_for_exit)
        
        if should_exit:
            # 记录退出原因
            round_payload["exit_detector_triggered"] = True
            round_payload["exit_reason"] = exit_reason
            
            # 正常完成
            finalize_ralph_state(
                project_root,
                feature=feature,
                status="completed",
                reason=exit_reason,
            )
            break
```

---

## 完整集成示例

```python
def _run_ralph_controller(
    *,
    feature: str,
    project_root: Path,
    version: str,
    runner: str | None,
    skill: str | None,
    task_template: str | None,
    timeout_sec: int | None,
    auto_switch_branch: bool | None,
    team_runtime: str | None,
    host_runtime: str | None,
    max_rounds: int,
) -> tuple[int, dict[str, Any]]:
    resolved_version = resolve_target_version(project_root, version)
    requested_runner = None if str(runner or "").strip().lower() == "auto" else runner
    executor_mode = "single" if str(requested_runner or "").strip() == "native-single" else "team"
    controller_run_id = generate_run_id(project_root)
    detected_host_runtime = detect_host_runtime(host_runtime)
    
    # 初始化 Ralph 状态
    initialize_ralph_state(
        project_root,
        feature=feature,
        version=resolved_version,
        run_id=controller_run_id,
        host_runtime=detected_host_runtime,
        runner=str(requested_runner or _resolve_mode_runner(...) or ""),
    )
    
    # === 新增：初始化检测器 ===
    exit_detector = ExitDetector(completion_threshold=2)
    circuit_breaker = CircuitBreaker(
        no_progress_threshold=3,
        same_error_threshold=3,
        output_decline_threshold=3,
    )
    
    last_payload: dict[str, Any] = 
    last_exit_code = 0
    controller_state: dict[str, Any] = load_ralph_state(project_root, feature=feature)
    
    for round_index in range(1, max(1, int(max_rounds or 1)) + 1):
        child_run_id = generate_run_id(project_root)
        child_runner = _resolve_mode_runner(...)
        
        # 执行一轮实现
        exit_code, round_payload = run_implement_stage(
            feature=feature,
            project_root=project_root,
            version=resolved_version,
            mode=executor_mode,
            host_runtime=detected_host_runtime,
            run_id_override=child_run_id,
            runner=child_runner,
            skill=skill,
            task_template=task_template,
            dry_run=False,
            timeout_sec=timeout_sec,
            auto_review_spec=False,
            auto_review_quality=False,
            auto_qa=False,
            auto_qa_args=[],
            auto_qa_follow_handoff=False,
            auto_qa_max_rounds=0,
            auto_switch_branch=auto_switch_branch,
            team_runtime=team_runtime,
        )
        
        # 记录轮次
        append_ralph_round(
            project_root,
            feature=feature,
            round_index=round_index,
            run_id=child_run_id,
            exit_code=exit_code,
            payload=round_payload,
        )
        
        # === 新增：熔断器检查（优先级高）===
        result_for_breaker = {
            "output": round_payload.get("summary", ""),
            "error": round_payload.get("error_message", ""),
        }
        is_stuck, stuck_reason = circuit_breaker.detect_stuck(
            round_index,
            result_for_breaker,
        )
        
        if is_stuck:
            round_payload["circuit_breaker_triggered"] = True
            round_payload["stuck_reason"] = stuck_reason
            mark_ralph_handoff_required(
                project_root,
                feature=feature,
                reason=f"Circuit breaker: {stuck_reason}",
                action="review_and_adjust",
            )
            last_payload = round_payload
            last_exit_code = 1
            break
        
        # 现有 handoff 检查
        if round_payload.get("handoff_required"):
            mark_ralph_handoff_required(...)
            last_payload = round_payload
            last_exit_code = exit_code
            break
        
        # === 新增：退出条件检查 ===
        result_for_exit = {
            "output": round_payload.get("summary", ""),
            "EXIT_SIGNAL": round_payload.get("implementation_complete", False),
        }
        should_exit, exit_reason = exit_detector.check_exit(result_for_exit)
        
        if should_exit:
            round_payload["exit_detector_triggered"] = True
            round_payload["exit_reason"] = exit_reason
            finalize_ralph_state(
                project_root,
                feature=feature,
                status="completed",
                reason=exit_reason,
            )
            last_payload = round_payload
            last_exit_code = 0
            break
        
        # 更新状态
        last_payload = round_payload
        last_exit_code = exit_code
    
    # 完成 Ralph 状态
    if not round_payload.get("exit_detector_triggered"):
        finalize_ralph_state(
            project_root,
            feature=feature,
            status="max_rounds_reached" if round_index >= max_rounds else "incomplete",
        )
    
    return last_exit_code, {
        **last_payload,
        "ralph_controller": {
            "run_id": controller_run_id,
            "rounds_completed": round_index,
            "max_rounds": max_rounds,
            "exit_detector_triggered": round_payload.get("exit_detector_triggered", False),
            "circuit_breaker_triggered": round_payload.get("circuit_breaker_triggered", False),
        },
    }
```

---

## 配置选项

### beacon.config.yaml

```yaml
implementation:
  ralph:
    # 退出检测配置
    exit_detection:
      enabled: true
      completion_threshold: 2
      custom_patterns:
        - "deployment ready"
        - "production ready"
    
    # 熔断器配置
    circuit_breaker:
      enabled: true
      no_progress_threshold: 3
      same_error_threshold: 3
      output_decline_threshold: 3
      min_output_length: 100
```

---

## 测试验证

### 单元测试

```python
# tests/commands/test_implement_ralph_detectors.py

def test_ralph_controller_with_exit_detector(tmp_path):
    """Test Ralph controller exits when completion detected."""
    # Setup
    # ...
    
    # Run
    exit_code, payload = _run_ralph_controller(...)
    
    # Assert
    assert payload["ralph_controller"]["exit_detector_triggered"] is True
    assert payload["ralph_controller"]["rounds_completed"] < max_rounds


def test_ralph_controller_with_circuit_breaker(tmp_path):
    """Test Ralph controller breaks on stuck detection."""
    # Setup
    # ...
    
    # Run
    exit_code, payload = _run_ralph_controller(...)
    
    # Assert
    assert payload["ralph_controller"]["circuit_breaker_triggered"] is True
    assert "stuck_reason" in payload
```

### 集成测试

```bash
# 测试正常完成
beacon implement run "test-feature" --mode ralph --runner native-single

# 测试熔断器触发
# (模拟重复错误场景)

# 测试退出检测
# (模拟完成信号场景)
```

---

## 下一步

1. ✅ 实现 ExitDetector 和 CircuitBreaker
2. ✅ 编写单元测试
3. ✅ 创建集成示例
4. 📋 修改 `_run_ralph_controller()` 集成检测器
5. 📋 添加配置选项到 `beacon.config.yaml`
6. 📋 编写集成测试
7. 📋 更新文档

---

## 参考

- ExitDetector: `beacon/utils/exit_detector.py`
- CircuitBreaker: `beacon/utils/circuit_breaker.py`
- 集成示例: `examples/ralph_loop_integration.py`
- Ralph 状态管理: `beacon/utils/ralph_runtime.py`
