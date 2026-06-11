package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	store := NewStore()
	mux := NewRouter(store)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	fmt.Printf("go-todo-crud listening on :%s\n", port)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		fmt.Fprintf(os.Stderr, "server error: %v\n", err)
		os.Exit(1)
	}
}
