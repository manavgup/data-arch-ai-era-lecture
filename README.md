# Data Architecture for the AI Era — A Field Guide for Sellers, Architects, and SSRs

**Owner:** Manav Gupta, VP and CTO, Technical Sales, IBM Canada

## Overview

This is a hands-on, half-day lecture anchored on the IBM Software Hub / Cloud Pak for Data reference architecture. Participants will work through a realistic BFSI (Banking, Financial Services, and Insurance) scenario—generating synthetic data, querying across federated engines, building governance pipelines, and exploring AI-powered document processing—all running on a single-node Docker stack that mirrors the production topology.

## Quick Start

```bash
make setup && make generate-data
```

## Prerequisites

- Python 3.11+
- Docker (with Docker Compose)
- [uv](https://github.com/astral-sh/uv) or conda (for dependency management)

## Repo Structure

```
├── README.md
├── pyproject.toml
├── docker-compose.yml
├── Makefile
├── data/
│   ├── eval/              # Evaluation datasets
│   ├── lineage/           # Data lineage artifacts
│   ├── mdm/               # Master data management
│   └── policies/          # Generated policy documents
├── notebooks/             # Jupyter notebooks (see below)
├── deck/
│   └── assets/            # Generated diagram overlays
├── handouts/              # Participant handouts
├── tools/                 # Utility scripts
├── tests/                 # pytest test suite
├── trino-config/          # Trino catalog configurations
└── reference/             # Reference architecture PDF
```

## Notebooks

| # | Notebook | Pattern |
|---|----------|---------|
| 1 | `01_data_generation.ipynb` | Synthetic data generation with Faker |
| 2 | `02_lakehouse_queries.ipynb` | Federated queries across Postgres, MinIO, and Trino |
| 3 | `03_governance_lineage.ipynb` | Data lineage and governance metadata |
| 4 | `04_document_processing.ipynb` | Document parsing with Docling and embeddings |
| 5 | `05_vector_search.ipynb` | Semantic search with OpenSearch |
| 6 | `06_mdm_entity_resolution.ipynb` | Master data management and entity linking |

## Links

- [MCP Context Forge](https://github.com/IBM/mcp-context-forge) — Model Context Protocol toolkit
- [Docling](https://github.com/DS4SD/docling) — Document parsing library from IBM Research

## License

TBD
