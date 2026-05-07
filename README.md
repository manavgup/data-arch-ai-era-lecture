# Data Architecture for the AI Era — A Field Guide for Sellers, Architects, and SSRs

**Owner:** Manav Gupta, VP & CTO, Technical Sales, IBM Canada

## Overview

A hands-on, half-day lecture (4h 30m) anchored on the IBM Software Hub / Cloud Pak for Data reference architecture. Participants work through a realistic BFSI (Banking, Financial Services, and Insurance) scenario — Maple Trust Bank — generating synthetic data, querying across federated engines, building governance pipelines, and exploring AI-powered document processing, all running on a single-node Docker stack that mirrors the production topology.

**Audience:** IBM sellers, ATLs, architects, and SSRs (technical sales)

**Anchor visual:** The Cloud Pak for Data Platform Reference Architecture diagram (`reference/Software_Hub_5_2_-_Reference_Architecture.PDF`). The entire lecture is organized around reading this diagram — each block lights up different swimlanes.

## Lecture Structure

| Block | Time | Topic |
|-------|------|-------|
| Opening | 10 min | Hook + full reference architecture diagram tour |
| Block 1 — Foundations | 45 min | 30-year arc, five primitives, pattern decoder ring (6 patterns incl. Data Fabric), MDM, annotated diagram #1 |
| Block 2 — AI-Era Architecture | 60 min | RAG reference architecture, Docling, OpenSearch hybrid retrieval, context engineering, MCP Context Forge, annotated diagram #2 |
| Break | 15 min | — |
| Block 3 — Governance | 45 min | Three governance problems (data, AI/model, agent), OSFI/PIPEDA, sovereignty, observability, agentic governance framework, annotated diagram #3 |
| Block 4 — Hands-on Labs + Critique | 60 min | Notebook 3 (Lakehouse) live, Notebook 6 (AI-era end-to-end) live, architecture critique exercise |
| Block 5 — Close & Q&A | 15 min | One-slide takeaway, Monday morning actions, pointers |

## Quick Start

```bash
make setup && make generate-data
```

## Prerequisites

- Python 3.11+
- Docker (with Docker Compose)
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## The Six Patterns

Each pattern has a notebook and corresponding deck slides. The same three business questions recur in every notebook — watch how each pattern handles them differently.

| # | Notebook | Pattern | Best for | Anti-pattern |
|---|----------|---------|----------|-------------|
| 1 | `01-warehouse.ipynb` | Data Warehouse | Stable schemas, BI, regulatory reporting | Unstructured / AI workloads |
| 2 | `02-data-lake.ipynb` | Data Lake | Cheap raw storage, ML training sets | Anything needing ACID or governance |
| 3 | `03-lakehouse.ipynb` | Lakehouse | Unified analytics + ML on open formats | Sub-second OLTP |
| 4 | `04-virtualization.ipynb` | Data Virtualization | Federated queries, data residency | High-volume scans, latency-sensitive |
| 5 | `05-data-mesh.ipynb` | Data Mesh | Large orgs with strong domain teams | Orgs without product thinking |
| 6 | `06-rag-mdm.ipynb` | MDM + RAG | Entity resolution + document intelligence | — (capstone, combines all patterns) |

**Data Fabric** appears in the Block 1 pattern decoder ring as the 6th architectural pattern (heterogeneous estates, federation) but does not have a standalone notebook — it is a meta-pattern that spans the other five.

### Three canonical queries (repeated in every notebook)

- **Q1:** Total transaction volume by branch for Q3 2024 *(structured, SQL-shaped)*
- **Q2:** Find all customers whose policy documents reference AML procedure X *(unstructured, document-shaped)*
- **Q3:** Trace the lineage of the Q3 branch summary back to source *(metadata, graph-shaped)*

### Notebook 7-section template

Every notebook follows the same structure: (1) The pattern in one paragraph, (2) When you'd use it / when you wouldn't, (3) The setup, (4) Three canonical queries, (5) Where this pattern breaks, (6) The IBM stack mapping, (7) BFSI reality check.

## Deliverables

| Deliverable | Location | Status |
|------------|----------|--------|
| Synthetic BFSI dataset | `data/` | Done |
| Six Jupyter notebooks | `notebooks/` | Done |
| PPTX deck (50–60+ slides) | `deck/data-architecture-ai-era.pptx` | In progress |
| Facilitator guide | `facilitator-guide.md` | Pending |
| Architecture critique handout | `handouts/critique.md` | Pending |
| Self-paced study guide | `handouts/self-paced-guide.md` | Pending |
| Smoke tests + CI | `tests/` + `.github/workflows/ci.yml` | Done |

## Repo Structure

```
├── SPEC.md                    # Frozen project spec (read this first)
├── CLAUDE.md                     # Claude Code project instructions
├── README.md                     # This file
├── pyproject.toml
├── docker-compose.yml            # Postgres, MinIO, Trino, OpenSearch
├── Makefile
├── reference/
│   └── Software_Hub_5_2_-_Reference_Architecture.PDF
├── deck/
│   ├── DECK-OUTLINE.md           # Slide-by-slide outline
│   ├── generate_deck.py          # python-pptx generator script
│   └── assets/                   # Annotated diagram overlays
├── notebooks/
│   ├── 01-warehouse.ipynb
│   ├── 02-data-lake.ipynb
│   ├── 03-lakehouse.ipynb
│   ├── 04-virtualization.ipynb
│   ├── 05-data-mesh.ipynb
│   └── 06-rag-mdm.ipynb
├── data/
│   ├── generate.py               # Idempotent, seedable data generator
│   ├── customers.parquet          # 100K synthetic customers
│   ├── accounts.parquet           # 200K accounts
│   ├── transactions.parquet       # 1M transactions
│   ├── branches.parquet           # 50 branches
│   ├── policies/                  # 10 AML/KYC policy PDFs
│   ├── eval/aml_qa_eval.jsonl     # 30 Q&A pairs for RAG eval
│   ├── lineage/lineage_graph.json # Lineage records
│   └── mdm/entity_links.parquet   # Entity resolution links
├── handouts/                      # Participant handouts
├── tools/                         # Utility scripts
├── tests/                         # pytest test suite
├── plans/                         # Implementation plans
└── trino-config/                  # Trino catalog configs
```

## Development

```bash
make install-dev        # Install Python dev deps
make docker-up          # Start Docker services
make generate-data      # Generate synthetic BFSI data
make lint               # Run ruff check + format
make smoke-test         # Run pytest
make pre-commit         # Run all pre-commit hooks
make run-notebooks      # Execute all notebooks headless
```

## Links

- [SPEC.md](SPEC.md) — Frozen project spec (the complete lecture specification)
- [MCP Context Forge](https://github.com/IBM/mcp-context-forge) — Model Context Protocol toolkit
- [Docling](https://github.com/DS4SD/docling) — Document parsing library from IBM Research
- [factor10.ai](https://factor10.ai) — 10 Principles of Enterprise AI

## License

TBD
