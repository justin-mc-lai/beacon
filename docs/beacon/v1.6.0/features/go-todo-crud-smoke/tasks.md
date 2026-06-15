# 任务：Go TODO CRUD Smoke

## Phase A — 项目骨架与数据模型（AC-001, AC-002, AC-007）

- [x] TASK-001 创建 `examples/go-todo-crud/` 目录与 `go.mod`（module `examples/go-todo-crud`，Go >= 1.21）。evidence: `go.mod` exists, `go build ./...` PASS
- [x] TASK-002 创建 `examples/go-todo-crud/todo.go`：定义 `Todo` struct（ID int, Title string, Completed bool）+ `TodoStore`（map[int]Todo + sync.RWMutex + 自增 ID）。evidence: `todo.go` exists, struct fields match spec
- [x] TASK-003 实现 `TodoStore` CRUD 方法：`List()`, `Create(title)`, `Get(id)`, `Update(id, title, completed)`, `Delete(id)`。evidence: `todo.go` methods present, `go test ./...` PASS
- [x] TASK-004 实现 `GET /todos` handler（AC-002）。evidence: `main.go` GET /todos route registered, TC-002 PASS

## Phase B — HTTP handlers（AC-003..AC-006）

- [x] TASK-005 实现 `POST /todos` handler：JSON 解析，title 校验，创建并返回 201（AC-003）。evidence: `main.go` POST /todos route registered, TC-003 PASS
- [x] TASK-006 实现 `GET /todos/{id}` handler：路径解析 ID，存在返回 200，不存在返回 404（AC-004）。evidence: `main.go` GET /todos/{id} route, TC-004 PASS
- [x] TASK-007 实现 `PUT /todos/{id}` handler：JSON 解析，存在则更新返回 200，不存在返回 404（AC-005）。evidence: `main.go` PUT /todos/{id} route, TC-005 PASS
- [x] TASK-008 实现 `DELETE /todos/{id}` handler：存在返回 204，不存在返回 404（AC-006）。evidence: `main.go` DELETE /todos/{id} route, TC-006 PASS
- [x] TASK-009 创建 `examples/go-todo-crud/main.go`：注册路由，启动 HTTP 服务器（默认 `:8080`）。evidence: `main.go` exists with ServeMux + :8080

## Phase C — 测试（AC-007, AC-008）

- [x] TASK-010 创建 `examples/go-todo-crud/todo_test.go`：实现 TC-002..TC-008。evidence: `todo_test.go` exists, 7 test functions
- [x] TASK-011 运行 `go test ./...` 和 `go test -race ./...` 验证通过。evidence: `go test ./...` PASS, `go test -race ./...` PASS (2026-06-15)
- [x] TASK-012 `go build ./...` 编译验证。evidence: `go build ./...` PASS (2026-06-15)

## 边界

- 任务台账不是 implementation completion。
- 所有实现必须仅使用 Go 标准库。
- `go test -race ./...` 通过是 AC-007 的必要条件。
- feature 状态从 `draft` 升为 `frozen` 需要 generate 阶段完成后 refreeze。

## 证据摘要

验证日期：2026-06-15
- `go build ./...` → PASS
- `go test ./...` → ok (0.835s)
- `go test -race ./...` → ok (1.68s)
