# 测试：Go TODO CRUD Smoke

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | unit | `cd examples/go-todo-crud && go build ./...` | 编译成功，退出码 0 |
| AC-002 | TC-002 | integration | `go test -run TestListTodos` | GET /todos 返回 200 + JSON 数组；空列表为 `[]` |
| AC-003 | TC-003 | integration | `go test -run TestCreateTodo` | POST /todos 返回 201 + 创建的 TODO（含 id/title/completed）；空 title 返回 400 |
| AC-004 | TC-004 | integration | `go test -run TestGetTodo` | GET /todos/1 返回 200（存在时）；不存在的 ID 返回 404 |
| AC-005 | TC-005 | integration | `go test -run TestUpdateTodo` | PUT /todos/1 返回 200 + 更新后 JSON；不存在返回 404；空 title 返回 400 |
| AC-006 | TC-006 | integration | `go test -run TestDeleteTodo` | DELETE /todos/1 返回 204；不存在返回 404；后续 GET 返回 404 |
| AC-007 | TC-007 | unit | `go test -race -run TestConcurrentAccess` | 并发读写无 race condition |
| AC-008 | TC-008 | unit | `go test ./...` | 所有测试通过，退出码 0 |

## 测试结构

测试文件 `examples/go-todo-crud/todo_test.go` 使用 Go 标准库 `testing` + `net/http/httptest`：

```go
package main

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "strings"
    "sync"
    "testing"
)
```

## 测试用例详情

### TC-002：TestListTodos

- **场景**：GET /todos，初始为空，返回 `[]`
- **步骤**：
  1. 启动 httptest.Server
  2. GET /todos
  3. 断言状态码 200
  4. 断言 Content-Type 含 `application/json`
  5. 断言 body 为 `[]`
- **场景 2**：先 POST 一条，再 GET /todos，断言返回数组含该条

### TC-003：TestCreateTodo

- **场景**：POST /todos `{"title": "buy milk"}`
- **步骤**：
  1. POST /todos，body `{"title": "buy milk"}`
  2. 断言状态码 201
  3. 断言返回 JSON 含 `id: 1, title: "buy milk", completed: false`
- **场景 2**：POST /todos `{"title": ""}` 断言 400

### TC-004：TestGetTodo

- **场景**：先创建，再获取
- **步骤**：
  1. POST /todos 创建一条
  2. GET /todos/1 断言 200 + 匹配 JSON
  3. GET /todos/999 断言 404

### TC-005：TestUpdateTodo

- **场景**：先创建，再更新
- **步骤**：
  1. POST /todos 创建 `{"title": "old title"}`
  2. PUT /todos/1 body `{"title": "new title", "completed": true}`
  3. 断言 200 + 返回 JSON 含 `title: "new title", completed: true`
- **场景 2**：PUT /todos/999 断言 404
- **场景 3**：PUT /todos/1 body `{"title": ""}` 断言 400

### TC-006：TestDeleteTodo

- **场景**：先创建，再删除
- **步骤**：
  1. POST /todos 创建一条
  2. DELETE /todos/1 断言 204
  3. GET /todos/1 断言 404
- **场景 2**：DELETE /todos/999 断言 404

### TC-007：TestConcurrentAccess

- **场景**：并发 POST + GET
- **步骤**：
  1. 启动 10 个 goroutine 并发 POST
  2. 启动 10 个 goroutine 并发 GET
  3. 使用 `sync.WaitGroup` 等待完成
  4. `go test -race` 无 race detection

### TC-008：Full Test Suite

- **命令**：`cd examples/go-todo-crud && go test ./... -v`
- **断言**：退出码 0，无失败

## 验证说明

- 所有测试使用 `httptest.NewServer`，无需外部 HTTP 端口
- 每个测试独立（使用独立的 store 实例或 test server）
- Error path 覆盖：404、400
- Race detection 作为 CI 一部分（`go test -race ./...`）
