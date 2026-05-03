# Data Architecture for the AI Era — Lecture Build Targets

.DEFAULT_GOAL := help

.PHONY: help install-dev setup generate-data run-notebooks smoke-test clean docker-up docker-down

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install-dev:  ## Install Python dev dependencies (no Docker)
	@command -v uv >/dev/null 2>&1 && uv pip install -e ".[dev]" || pip install -e ".[dev]"

setup: install-dev docker-up  ## Install deps + start Docker services

generate-data:  ## Generate synthetic BFSI data
	python data/generate.py

run-notebooks:  ## Run all notebooks (placeholder)
	@echo "TODO: implement notebook runner"

smoke-test:  ## Run pytest smoke tests
	python -m pytest tests/ -v

clean:  ## Tear down Docker and remove generated data
	docker compose down -v
	rm -f data/transactions.parquet data/customers.parquet data/branches.parquet data/accounts.parquet
	rm -rf data/policies/ data/mdm/entity_links.parquet

docker-up:  ## Start Docker services
	docker compose up -d

docker-down:  ## Stop Docker services
	docker compose down
