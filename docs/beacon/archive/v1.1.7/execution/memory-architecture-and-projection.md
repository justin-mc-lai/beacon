# Beacon Memory 架构与投影（v1.1.7）

## 四层模型

### 1. Store
- `memory-v1.json`
- canonical memory entries

### 2. Lifecycle
- `workflow-lifecycle.json`
- workflow stage event log

### 3. Feedback Assimilation
- `feedback extract/apply/sync`
- reason_code -> memory revision

### 4. Consumption / Projection
- `status`
- `report`
- `recall`
- gate strict memory closure checks
- governance metrics / memory metrics

## 原则
- raw memory JSON 是机器面；
- 人类默认读投影，不默认读 raw store。
