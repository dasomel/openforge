.PHONY: fmt lint test check

GOFUMPT ?= gofumpt

fmt:
	$(GOFUMPT) -w .

lint:
	go vet ./...

check:
	test -z "$$($(GOFUMPT) -l .)"
	go vet ./...
	go test ./...

test:
	go test ./...
