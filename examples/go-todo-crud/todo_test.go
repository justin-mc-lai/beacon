package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
)

func newTestServer() (*httptest.Server, *Store) {
	store := NewStore()
	mux := NewRouter(store)
	srv := httptest.NewServer(mux)
	return srv, store
}

func TestListTodos(t *testing.T) {
	srv, _ := newTestServer()
	defer srv.Close()

	// Empty list returns []
	resp, err := http.Get(srv.URL + "/todos")
	if err != nil {
		t.Fatalf("GET /todos: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
	ct := resp.Header.Get("Content-Type")
	if ct != "application/json" {
		t.Fatalf("expected application/json, got %s", ct)
	}

	var todos []Todo
	if err := json.NewDecoder(resp.Body).Decode(&todos); err != nil {
		t.Fatalf("decode: %v", err)
	}
	if len(todos) != 0 {
		t.Fatalf("expected empty list, got %d items", len(todos))
	}

	// After creating one, list contains it
	body := bytes.NewBufferString(`{"title":"buy milk"}`)
	http.Post(srv.URL+"/todos", "application/json", body)

	resp2, _ := http.Get(srv.URL + "/todos")
	defer resp2.Body.Close()
	var todos2 []Todo
	json.NewDecoder(resp2.Body).Decode(&todos2)
	if len(todos2) != 1 {
		t.Fatalf("expected 1 item, got %d", len(todos2))
	}
	if todos2[0].Title != "buy milk" {
		t.Fatalf("expected 'buy milk', got '%s'", todos2[0].Title)
	}
}

func TestCreateTodo(t *testing.T) {
	srv, _ := newTestServer()
	defer srv.Close()

	// Successful create
	body := bytes.NewBufferString(`{"title":"buy milk"}`)
	resp, err := http.Post(srv.URL+"/todos", "application/json", body)
	if err != nil {
		t.Fatalf("POST /todos: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		t.Fatalf("expected 201, got %d", resp.StatusCode)
	}

	var todo Todo
	json.NewDecoder(resp.Body).Decode(&todo)
	if todo.ID != 1 {
		t.Fatalf("expected id 1, got %d", todo.ID)
	}
	if todo.Title != "buy milk" {
		t.Fatalf("expected title 'buy milk', got '%s'", todo.Title)
	}
	if todo.Completed != false {
		t.Fatal("expected completed=false")
	}

	// Empty title returns 400
	body2 := bytes.NewBufferString(`{"title":""}`)
	resp2, _ := http.Post(srv.URL+"/todos", "application/json", body2)
	defer resp2.Body.Close()
	if resp2.StatusCode != http.StatusBadRequest {
		t.Fatalf("expected 400 for empty title, got %d", resp2.StatusCode)
	}
}

func TestGetTodo(t *testing.T) {
	srv, store := newTestServer()
	defer srv.Close()

	store.Create("test item")

	// Existing
	resp, _ := http.Get(srv.URL + "/todos/1")
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
	var todo Todo
	json.NewDecoder(resp.Body).Decode(&todo)
	if todo.Title != "test item" {
		t.Fatalf("expected 'test item', got '%s'", todo.Title)
	}

	// Not found
	resp2, _ := http.Get(srv.URL + "/todos/999")
	defer resp2.Body.Close()
	if resp2.StatusCode != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", resp2.StatusCode)
	}
}

func TestUpdateTodo(t *testing.T) {
	srv, store := newTestServer()
	defer srv.Close()

	store.Create("old title")

	// Successful update
	body := bytes.NewBufferString(`{"title":"new title","completed":true}`)
	req, _ := http.NewRequest(http.MethodPut, srv.URL+"/todos/1", body)
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("PUT /todos/1: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
	var todo Todo
	json.NewDecoder(resp.Body).Decode(&todo)
	if todo.Title != "new title" {
		t.Fatalf("expected 'new title', got '%s'", todo.Title)
	}
	if !todo.Completed {
		t.Fatal("expected completed=true")
	}

	// Not found
	body2 := bytes.NewBufferString(`{"title":"x","completed":false}`)
	req2, _ := http.NewRequest(http.MethodPut, srv.URL+"/todos/999", body2)
	resp2, _ := http.DefaultClient.Do(req2)
	defer resp2.Body.Close()
	if resp2.StatusCode != http.StatusNotFound {
		t.Fatalf("expected 404 for unknown id, got %d", resp2.StatusCode)
	}

	// Empty title returns 400
	body3 := bytes.NewBufferString(`{"title":"","completed":false}`)
	req3, _ := http.NewRequest(http.MethodPut, srv.URL+"/todos/1", body3)
	resp3, _ := http.DefaultClient.Do(req3)
	defer resp3.Body.Close()
	if resp3.StatusCode != http.StatusBadRequest {
		t.Fatalf("expected 400 for empty title, got %d", resp3.StatusCode)
	}
}

func TestDeleteTodo(t *testing.T) {
	srv, store := newTestServer()
	defer srv.Close()

	store.Create("to delete")

	// Successful delete
	req, _ := http.NewRequest(http.MethodDelete, srv.URL+"/todos/1", nil)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("DELETE /todos/1: %v", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusNoContent {
		t.Fatalf("expected 204, got %d", resp.StatusCode)
	}

	// Verify deleted
	resp2, _ := http.Get(srv.URL + "/todos/1")
	defer resp2.Body.Close()
	if resp2.StatusCode != http.StatusNotFound {
		t.Fatalf("expected 404 after delete, got %d", resp2.StatusCode)
	}

	// Not found
	req2, _ := http.NewRequest(http.MethodDelete, srv.URL+"/todos/999", nil)
	resp3, _ := http.DefaultClient.Do(req2)
	defer resp3.Body.Close()
	if resp3.StatusCode != http.StatusNotFound {
		t.Fatalf("expected 404 for unknown id, got %d", resp3.StatusCode)
	}
}

func TestConcurrentAccess(t *testing.T) {
	srv, _ := newTestServer()
	defer srv.Close()

	var wg sync.WaitGroup
	// Concurrent POST
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			body := bytes.NewBufferString(`{"title":"concurrent item"}`)
			http.Post(srv.URL+"/todos", "application/json", body)
		}(i)
	}
	// Concurrent GET
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			http.Get(srv.URL + "/todos")
		}()
	}
	wg.Wait()

	// Verify all 10 created
	resp, _ := http.Get(srv.URL + "/todos")
	defer resp.Body.Close()
	var todos []Todo
	json.NewDecoder(resp.Body).Decode(&todos)
	if len(todos) != 10 {
		t.Fatalf("expected 10 todos, got %d", len(todos))
	}
}

func TestFullSuite(t *testing.T) {
	srv, _ := newTestServer()
	defer srv.Close()

	// Create
	body := bytes.NewBufferString(`{"title":"full suite"}`)
	resp, _ := http.Post(srv.URL+"/todos", "application/json", body)
	resp.Body.Close()
	if resp.StatusCode != http.StatusCreated {
		t.Fatalf("create: expected 201, got %d", resp.StatusCode)
	}

	// Read
	resp2, _ := http.Get(srv.URL + "/todos/1")
	var todo Todo
	json.NewDecoder(resp2.Body).Decode(&todo)
	resp2.Body.Close()
	if todo.Title != "full suite" {
		t.Fatalf("read: expected 'full suite', got '%s'", todo.Title)
	}

	// Update
	body2 := bytes.NewBufferString(`{"title":"updated","completed":true}`)
	req, _ := http.NewRequest(http.MethodPut, srv.URL+"/todos/1", body2)
	resp3, _ := http.DefaultClient.Do(req)
	resp3.Body.Close()
	if resp3.StatusCode != http.StatusOK {
		t.Fatalf("update: expected 200, got %d", resp3.StatusCode)
	}

	// Delete
	req2, _ := http.NewRequest(http.MethodDelete, srv.URL+"/todos/1", nil)
	resp4, _ := http.DefaultClient.Do(req2)
	resp4.Body.Close()
	if resp4.StatusCode != http.StatusNoContent {
		t.Fatalf("delete: expected 204, got %d", resp4.StatusCode)
	}
}
