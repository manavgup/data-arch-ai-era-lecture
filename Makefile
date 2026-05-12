# Data Architecture for the AI Era — Lecture Build Targets

.DEFAULT_GOAL := help

.PHONY: help install-dev setup generate-data run-notebooks smoke-test validate clean docker-up docker-down lint pre-commit

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
# help: validate           Validate deck + notebook structure against SPEC.md
# help: run-notebooks      Run all notebooks headless
# help:
# help: 🔍 CODE QUALITY
# help: lint               Run ruff lint + format checks
# help: pre-commit         Run all pre-commit hooks
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
	@test -d .venv || (echo "Creating .venv..." && uv venv .venv)
	uv pip install -e ".[dev]" --python .venv/bin/python

docker-up:
	docker compose up -d

docker-down:
	docker compose down

smoke-test:
	python -m pytest tests/ -v

validate:
	python -m pytest tests/test_deck.py tests/test_notebook_structure.py -v

run-notebooks:
	source .venv/bin/activate && for nb in notebooks/*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$$nb"; done

lint:
	ruff check . && ruff format --check .

pre-commit:
	pre-commit run --all-files

clean:
	docker compose down -v
	rm -f data/transactions.parquet data/customers.parquet data/branches.parquet data/accounts.parquet
	rm -rf data/policies/ data/mdm/entity_links.parquet
