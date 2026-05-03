# Maple Trust Bank — Synthetic BFSI Dataset

Synthetic data for the **"Data Architecture for the AI Era"** half-day lecture.
All data represents a fictional mid-size Canadian bank called **Maple Trust Bank**.

## Quick Start

```bash
pip install faker pandas pyarrow reportlab numpy
python data/generate.py              # default seed=42
python data/generate.py --seed 123   # custom seed
```

The script is **idempotent** — running it twice with the same seed produces identical output.

---

## Generated Files

### A. Tabular Data (Parquet)

#### `branches.parquet` — 50 rows

| Column | Type | Description |
|--------|------|-------------|
| `branch_id` | str | MTB-001 through MTB-050 |
| `name` | str | Descriptive branch name (e.g., "Downtown Toronto") |
| `address` | str | Realistic Canadian address |
| `region` | str | One of: Ontario, Quebec, BC, Alberta, Atlantic, Prairies |
| `manager_id` | str | MGR-001 through MGR-050 |

#### `customers.parquet` — 100,000 rows

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | str | CUST-000001 through CUST-100000 |
| `name` | str | Faker-generated full name |
| `dob` | date | Between 1940 and 2005 |
| `residency` | str | ~90% "Canada", rest: "US", "UK", "India", "China", "Other" |
| `kyc_status` | str | "verified" (80%), "pending" (10%), "expired" (5%), "flagged" (5%) |
| `risk_score` | int | 1-100, beta-distributed (skewed low) |
| `opened_date` | date | Between 2000 and 2025 |
| `segment` | str | "retail" (60%), "commercial" (20%), "wealth" (15%), "institutional" (5%) |

#### `accounts.parquet` — 200,000 rows

| Column | Type | Description |
|--------|------|-------------|
| `account_id` | str | ACCT-000001 through ACCT-200000 |
| `customer_id` | str | FK → customers (1-5 accounts per customer) |
| `branch_id` | str | FK → branches |
| `account_type` | str | "chequing", "savings", "investment", "mortgage", "credit" |
| `opened_date` | date | >= customer's opened_date |
| `status` | str | "active" (85%), "dormant" (10%), "closed" (5%) |
| `balance` | float | Realistic range by account type |

**Balance ranges by account type:**
- Chequing: $100 – $50,000
- Savings: $500 – $200,000
- Investment: $5,000 – $2,000,000
- Mortgage: -$500,000 – -$50,000 (liability)
- Credit: -$25,000 – $0 (liability)

#### `transactions.parquet` — 1,000,000 rows

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | str | TXN-0000001 through TXN-1000000 |
| `account_id` | str | FK → accounts |
| `branch_id` | str | FK → branches (same as account's branch) |
| `amount` | float | Log-normal distribution; mostly small, some large |
| `currency` | str | "CAD" (95%), "USD" (3%), "EUR" (1%), "GBP" (1%) |
| `timestamp` | datetime | 2023-01-01 to 2024-12-31, business-hour weighted |
| `transaction_type` | str | "deposit", "withdrawal", "transfer", "payment", "wire" |
| `channel` | str | "branch", "online", "mobile", "ATM", "phone" |
| `counterparty_id` | str | Another customer_id or "EXTERNAL-xxxx" |

**AML signals:** ~50 transactions are seeded with suspiciously high amounts ($50K–$500K) from accounts belonging to customers with "flagged" KYC status or risk scores >= 80. These are the signals Notebook 6 will detect.

---

### B. Policy PDFs — `policies/`

10 professional policy documents generated with ReportLab:

| File | Title | Version |
|------|-------|---------|
| MTB-POL-001.pdf | Anti-Money Laundering (AML) Program Policy | 3.1 |
| MTB-POL-002.pdf | Know Your Customer (KYC) Procedures | 2.4 |
| MTB-POL-003.pdf | Suspicious Transaction Reporting Guidelines | 2.2 |
| MTB-POL-004.pdf | Customer Due Diligence (CDD) Standards | 3.0 |
| MTB-POL-005.pdf | Enhanced Due Diligence (EDD) for High-Risk Customers | 2.1 |
| MTB-POL-006.pdf | Transaction Monitoring Program | 2.5 |
| MTB-POL-007.pdf | Sanctions Screening Procedures | 1.8 |
| MTB-POL-008.pdf | Politically Exposed Persons (PEP) Policy | 2.0 |
| MTB-POL-009.pdf | Record Retention and Data Management Policy | 2.3 |
| MTB-POL-010.pdf | Risk Assessment Methodology | 3.2 |

Each PDF includes:
- Header/footer on every page ("Maple Trust Bank — CONFIDENTIAL" + page numbers)
- Approval table and document metadata
- Table of contents
- Numbered sections and subsections
- Tables with grid lines (compatible with Docling parsing)
- Cross-references to other policy documents
- Realistic Canadian regulatory references (PCMLTFA, OSFI B-8, FINTRAC)

---

### C. Eval Set — `eval/aml_qa_eval.jsonl`

30 question-answer pairs against the policy corpus. Each line is JSON:

```json
{
  "question": "What is the reporting threshold for large cash transactions?",
  "answer": "$10,000 CAD...",
  "source_doc": "MTB-POL-003.pdf",
  "section": "3.1"
}
```

**Question distribution:**
- 15 factual lookups (thresholds, timeframes, definitions)
- 10 multi-document reasoning (cross-referencing policies)
- 5 procedural questions (what to do when X happens)

---

### D. Lineage Graph — `lineage/lineage_graph.json`

Synthetic data lineage showing data flow across three layers:

- **Raw** (7 nodes): Source system extracts (core banking, CRM, KYC platform, SWIFT, sanctions vendor)
- **Curated** (6 nodes): Cleaned and transformed datasets (dedup, enrichment, normalization)
- **Consumed** (6 nodes): Analytics and reporting outputs (AML alerts, risk scores, regulatory reports, dashboards)

25 edges showing realistic ETL transformations including dedup, schema enforcement, currency normalization, entity resolution, and ML scoring.

---

### E. MDM Entity Links — `mdm/entity_links.parquet`

~500 rows showing customer entity resolution across source systems.

| Column | Type | Description |
|--------|------|-------------|
| `entity_id` | str | ENT-0001 through ENT-0200 (~200 unique entities) |
| `source_system` | str | "core_banking", "crm", "aml_system", "branch_records" |
| `source_id` | str | System-specific IDs (e.g., CB-123456, CRM-789012) |
| `customer_id` | str | FK → customers (resolved link) |
| `match_confidence` | float | 0.0-1.0 (varies by method) |
| `match_method` | str | "exact_name_dob", "fuzzy_name_address", "ssn_match", "manual_review" |
| `last_updated` | datetime | Dates in 2024 |

---

## Entity Relationships

```
branches (50)
  └─< accounts (200K) — branch_id FK
        └─< transactions (1M) — account_id FK
              │
customers (100K)
  ├─< accounts (200K) — customer_id FK
  ├─< entity_links (500) — customer_id FK
  └── transactions.counterparty_id (some reference other customer_ids)
```

---

## Regeneration

To regenerate all data identically:

```bash
python data/generate.py --seed 42
```

To generate with a different seed (different but structurally identical data):

```bash
python data/generate.py --seed 99
```

Generated Parquet files and PDFs are excluded from version control via `.gitignore`.
Only the generator script, eval set, lineage graph, and this README are committed.
