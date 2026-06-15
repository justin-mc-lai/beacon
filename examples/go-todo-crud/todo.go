package main

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"
	"sync"
)

// Todo represents a single TODO item.
type Todo struct {
	ID        int    `json:"id"`
	Title     string `json:"title"`
	Completed bool   `json:"completed"`
}

// Store is a thread-safe in-memory store for TODO items.
type Store struct {
	mu     sync.RWMutex
	todos  map[int]Todo
	nextID int
}

// NewStore creates a new empty Store.
func NewStore() *Store {
	return &Store{
		todos:  make(map[int]Todo),
		nextID: 1,
	}
}

// List returns all todos as a slice.
func (s *Store) List() []Todo {
	s.mu.RLock()
	defer s.mu.RUnlock()
	result := make([]Todo, 0, len(s.todos))
	for _, t := range s.todos {
		result = append(result, t)
	}
	return result
}

// Get returns a todo by ID. Returns false if not found.
func (s *Store) Get(id int) (Todo, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	t, ok := s.todos[id]
	return t, ok
}

// Create adds a new todo and returns it with an assigned ID.
func (s *Store) Create(title string) Todo {
	s.mu.Lock()
	defer s.mu.Unlock()
	t := Todo{
		ID:        s.nextID,
		Title:     title,
		Completed: false,
	}
	s.todos[s.nextID] = t
	s.nextID++
	return t
}

// Update modifies an existing todo. Returns false if not found.
func (s *Store) Update(id int, title string, completed bool) (Todo, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	t, ok := s.todos[id]
	if !ok {
		return Todo{}, false
	}
	t.Title = title
	t.Completed = completed
	s.todos[id] = t
	return t, true
}

// Delete removes a todo by ID. Returns false if not found.
func (s *Store) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.todos[id]; !ok {
		return false
	}
	delete(s.todos, id)
	return true
}

// NewRouter builds an http.ServeMux with /todos routes bound to the given store.
func NewRouter(store *Store) *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/todos", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			handleListTodos(w, r, store)
		case http.MethodPost:
			handleCreateTodo(w, r, store)
		default:
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		}
	})
	mux.HandleFunc("/todos/", func(w http.ResponseWriter, r *http.Request) {
		idStr := strings.TrimPrefix(r.URL.Path, "/todos/")
		if idStr == "" {
			http.Error(w, "missing id", http.StatusBadRequest)
			return
		}
		id, err := strconv.Atoi(idStr)
		if err != nil {
			http.Error(w, "invalid id", http.StatusBadRequest)
			return
		}
		switch r.Method {
		case http.MethodGet:
			handleGetTodo(w, r, store, id)
		case http.MethodPut:
			handleUpdateTodo(w, r, store, id)
		case http.MethodDelete:
			handleDeleteTodo(w, r, store, id)
		default:
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		}
	})
	return mux
}

func handleListTodos(w http.ResponseWriter, _ *http.Request, store *Store) {
	todos := store.List()
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(todos)
}

func handleCreateTodo(w http.ResponseWriter, r *http.Request, store *Store) {
	var input struct {
		Title string `json:"title"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "invalid json", http.StatusBadRequest)
		return
	}
	if strings.TrimSpace(input.Title) == "" {
		http.Error(w, "title is required", http.StatusBadRequest)
		return
	}
	t := store.Create(input.Title)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(t)
}

func handleGetTodo(w http.ResponseWriter, _ *http.Request, store *Store, id int) {
	t, ok := store.Get(id)
	if !ok {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(t)
}

func handleUpdateTodo(w http.ResponseWriter, r *http.Request, store *Store, id int) {
	var input struct {
		Title     string `json:"title"`
		Completed bool   `json:"completed"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "invalid json", http.StatusBadRequest)
		return
	}
	if strings.TrimSpace(input.Title) == "" {
		http.Error(w, "title is required", http.StatusBadRequest)
		return
	}
	t, ok := store.Update(id, input.Title, input.Completed)
	if !ok {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(t)
}

func handleDeleteTodo(w http.ResponseWriter, _ *http.Request, store *Store, id int) {
	if !store.Delete(id) {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

