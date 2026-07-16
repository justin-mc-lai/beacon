# 证据：Go TODO CRUD Smoke

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| research | support_advisory | docs/beacon/archive/v1.6.0/research/go-todo-crud-smoke.md | accepted | truth.research |
| feature-package | requirement_truth | docs/beacon/archive/v1.6.0/features/go-todo-crud-smoke/truth.md | **frozen R5** | truth.define |
| package-tests | test_truth | docs/beacon/archive/v1.6.0/features/go-todo-crud-smoke/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/archive/v1.6.0/features/go-todo-crud-smoke/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/archive/v1.6.0/features/go-todo-crud-smoke/evidence.md | evidence-indexed | evaluate |

## 决策记录

- 已接受：scope_mode=smoke — 最小 Go 标准库 CRUD，内存存储，无外部依赖。
- 已接受：AC-001..AC-008 覆盖编译、CRUD 端点、并发安全、测试覆盖。
- 已接受：测试使用 `httptest.Server` 进行端到端验证，无需外部端口。
- 已接受：非目标包括持久化、认证、路由库、分页、Docker。

## Implementation Candidate Evidence

- `examples/go-todo-crud/go.mod`：module `examples/go-todo-crud`，Go 1.21，零第三方依赖。
- `examples/go-todo-crud/todo.go`：`Store` + `sync.RWMutex`；`NewRouter(store)` 注册 `/todos` 与 `/todos/{id}`。
- `examples/go-todo-crud/main.go`：标准 `http.ListenAndServe`，`PORT` 环境变量覆盖。
- `examples/go-todo-crud/todo_test.go`：7 个测试函数（`TestListTodos`、`TestCreateTodo`、`TestGetTodo`、`TestUpdateTodo`、`TestDeleteTodo`、`TestConcurrentAccess`、`TestFullSuite`），全部使用 `httptest.Server`。
- `go build ./...` → exit 0（AC-001）
- `go test ./...` → 7/7 PASS（AC-008）
- `go test -race ./...` → PASS（AC-007）

## Verification Commands

```bash
cd examples/go-todo-crud && go build ./...
cd examples/go-todo-crud && go test ./... -v
cd examples/go-todo-crud && go test -race ./...
```

## 边界

`evidence.md` 是证据索引/read model，不是 final verdict。不得包含 release readiness、QA pass、implementation completion 或 source-of-truth override。
