# Data Architecture for the AI Era — Lecture Build Targets

.PHONY: setup generate-data run-notebooks smoke-test clean docker-up docker-down

setup:  ## Install Python deps and start Docker services
	@command -v uv >/dev/null 2>&1 && uv pip install -e ".[dev]" || pip install -e ".[dev]"
	docker compose up -d

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
