# Data Architecture for the AI Era — Lecture Build Targets

.DEFAULT_GOAL := help

.PHONY: help install-dev setup generate-data run-notebooks smoke-test clean docker-up docker-down

# help:
# help: 🎯 QUICK START
# help: setup              Install deps + start Docker services
# help: generate-data      Generate synthetic BFSI data
# help:
# help: 🐍 PYTHON
# help: install-dev        Install Python dev dependencies (no Docker)
# help:
# help: 🐳 DOCKER
# help: docker-up          Start Docker services (Postgres, MinIO, Trino, OpenSearch)
# help: docker-down        Stop Docker services
# help:
# help: 🧪 TESTING
# help: smoke-test         Run pytest smoke tests
# help: run-notebooks      Run all notebooks headless
# help:
# help: 🧹 CLEANUP
# help: clean              Tear down Docker + remove generated data
# help:

help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

setup: install-dev docker-up

generate-data:
	python data/generate.py

install-dev:
	@command -v uv >/dev/null 2>&1 && uv pip install -e ".[dev]" || pip install -e ".[dev]"

docker-up:
	docker compose up -d

docker-down:
	docker compose down

smoke-test:
	python -m pytest tests/ -v

run-notebooks:
	@echo "TODO: implement notebook runner"

clean:
	docker compose down -v
	rm -f data/transactions.parquet data/customers.parquet data/branches.parquet data/accounts.parquet
	rm -rf data/policies/ data/mdm/entity_links.parquet
