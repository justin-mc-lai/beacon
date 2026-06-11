---
slug: go-todo-crud-smoke
version: v1.6.0
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/go-todo-crud-smoke/truth.md
  user_story: docs/beacon/v1.6.0/features/go-todo-crud-smoke/truth.md
  test_case: docs/beacon/v1.6.0/features/go-todo-crud-smoke/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parent_feature: null
---

# 需求真相：Go TODO CRUD Smoke

## 概述

`go-todo-crud-smoke` 是一个最小化 Go HTTP CRUD 示例应用，作为 Beacon 示例项目投放到 `examples/go-todo-crud/` 目录。

实现范围：纯标准库（无第三方依赖），内存 map 存储，RESTful `/todos` 端点，包含 `go test` 可验证的单元/集成测试。

## Scope Mode

`scope_mode` = `**smoke**`（最小可验证示例）：

- 仅包含 CRUD 四个操作
- 仅使用 Go 标准库（`net/http`、`encoding/json`、`sync`、`testing`）
- 内存存储，无持久化
- 包含 `go test` 可执行的测试覆盖
- 不引入路由库、ORM、数据库、认证

## 背景

### 问题

Beacon 示例目录需要一个独立、可编译、可测试的 Go CRUD 参考实现，用于验证 Beacon generate 阶段在 Go 项目中的实现能力。

### 目标

在 `examples/go-todo-crud/` 目录下交付：

- 一个 `main.go`：启动 HTTP 服务器，注册 `/todos` 路由
- 一个 `todo.go`：数据模型与内存存储逻辑
- 一个 `todo_test.go`：覆盖 CRUD 四个操作的测试
- `go.mod`：Go 模块定义
- 无需第三方依赖

## Requirements (AC-001..AC-008)

## 验收标准

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | go-mod-init | `examples/go-todo-crud/` 目录包含有效的 `go.mod`，模块路径为 `examples/go-todo-crud`，Go >= 1.21；`go build ./...` 成功。 |
| AC-002 | get-list | `GET /todos` 返回 HTTP 200 + JSON 数组；空列表返回 `[]`；每个元素含 `id`(int)、`title`(string)、`completed`(bool)。 |
| AC-003 | post-create | `POST /todos` 接受 `{"title": "..."}`，返回 HTTP 201 + 创建的 TODO（默认 `completed: false`）；空 title 返回 400。 |
| AC-004 | get-by-id | `GET /todos/{id}` 存在时返回 200 + JSON；不存在时返回 404。 |
| AC-005 | put-update | `PUT /todos/{id}` 接受 `{"title": "...", "completed": true/false}`，成功返回 200 + 更新后 JSON；不存在返回 404；空 title 返回 400。 |
| AC-006 | delete | `DELETE /todos/{id}` 成功返回 204 无 body；不存在返回 404；后续 GET 不应包含。 |
| AC-007 | concurrency | 使用 `sync.RWMutex` 保护内存存储；并发读写无 race（`go test -race` 通过）。 |
| AC-008 | test-coverage | `go test ./...` 通过，使用 `httptest.Server` 端到端验证，覆盖 happy path 和 error path。 |


### AC-001：Go 模块初始化

- **优先级**：P0
- **描述**：`examples/go-todo-crud/` 目录包含有效的 `go.mod`，模块路径为 `examples/go-todo-crud`，Go 版本 >= 1.21。
- **验收标准**：`cd examples/go-todo-crud && go build ./...` 成功。

### AC-002：GET /todos — 列出所有 TODO

- **优先级**：P0
- **描述**：`GET /todos` 返回 JSON 数组，包含所有 TODO 条目。空列表时返回 `[]`。
- **验收标准**：
  - 返回 HTTP 200
  - Content-Type 为 `application/json`
  - 响应体为 JSON 数组
  - 每个元素含 `id`（int）、`title`（string）、`completed`（bool）

### AC-003：POST /todos — 创建 TODO

- **优先级**：P0
- **描述**：`POST /todos` 接受 JSON body `{"title": "..."}`，创建新 TODO（默认 `completed: false`），分配自增 ID。
- **验收标准**：
  - 返回 HTTP 201
  - 响应体包含创建的 TODO（含 id、title、completed）
  - 后续 GET 可查到该条目
  - 空 title 返回 HTTP 400

### AC-004：GET /todos/{id} — 获取单个 TODO

- **优先级**：P0
- **描述**：`GET /todos/{id}` 返回指定 ID 的 TODO。
- **验收标准**：
  - 存在时返回 HTTP 200 + JSON
  - 不存在时返回 HTTP 404

### AC-005：PUT /todos/{id} — 更新 TODO

- **优先级**：P0
- **描述**：`PUT /todos/{id}` 接受 JSON body `{"title": "...", "completed": true/false}`，更新指定 TODO。
- **验收标准**：
  - 成功返回 HTTP 200 + 更新后的 JSON
  - 不存在时返回 HTTP 404
  - 空 title 返回 HTTP 400

### AC-006：DELETE /todos/{id} — 删除 TODO

- **优先级**：P0
- **描述**：`DELETE /todos/{id}` 删除指定 TODO。
- **验收标准**：
  - 成功返回 HTTP 204，无响应体
  - 不存在时返回 HTTP 404
  - 后续 GET 不应包含该条目

### AC-007：并发安全

- **优先级**：P1
- **描述**：内存存储使用 `sync.RWMutex` 保护，并发读写安全。
- **验收标准**：测试中包含并发写入/读取场景，无 race condition（`go test -race` 通过）。

### AC-008：go test 覆盖

- **优先级**：P0
- **描述**：`go test ./...` 必须通过，覆盖所有 CRUD 操作。
- **验收标准**：
  - `go test ./...` 退出码 0
  - 测试使用 `httptest.Server` 进行端到端验证
  - 覆盖 happy path 和 error path

## 非目标（Out of Scope）

- 持久化存储（数据库、文件）
- 认证/授权
- 分页、排序、过滤
- 中间件链
- 第三方路由库（gorilla/mux、chi 等）
- Docker 化
- 配置文件

## Success Criteria

1. `cd examples/go-todo-crud && go build ./...` 成功
2. `cd examples/go-todo-crud && go test ./...` 全部通过
3. `cd examples/go-todo-crud && go test -race ./...` 全部通过
4. 手动 `curl` 验证 CRUD 四个端点均可正常工作

## Deferral Ledger

无。本 feature 为 smoke 级别，不接受 defer。

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-06-11 | gnhf agent | Initial truth draft (AC-001..AC-008) |
| 2026-06-11 | beacon-gen-change R5 | Merge from worktree `examples-go-todo-cru-671ce1`；保留 draft；作为 orchestrator R5 E2E 夹具 |
| 2026-06-11 | beacon-gen-implement R5 | `examples/go-todo-crud/` 实现完成；go build + go test 7/7 + go test -race PASS；AC-001..AC-008 全部满足；truth 提升为 frozen |
