# Data Architecture for the AI Era — Deck Outline

**Format:** 16:9, 1920×1080 | **Slides:** 33 | **Duration:** ~4 hours (half-day)
**Design:** Paper (#F4F2EC) background, signal blue (#2D4ADE) accent, Source Serif 4 / Inter / JetBrains Mono

---

## Framing Slides (01–06)

### Slide 01 — Cover

**Layout:** Cover (no header/footer)

| Element | Content |
|---------|---------|
| Top bar left | A Field Guide · v1.0 · 2026 |
| Top bar right | Half-day · Lecture + Hands-on |
| Kicker | Volume One — Foundations |
| Title | Data Architecture for the AI Era. |
| Rule | 2pt × 3.6" horizontal line |
| Subtitle (italic) | A field guide for sellers, architects, and SSRs — six patterns, one BFSI scenario, six runnable notebooks. |
| Bottom left | Maple Trust Bank · Case Study |
| Bottom center | Manav Gupta |
| Bottom right | VP & CTO, Technical Sales |

**Speaker notes:**
Welcome everyone. This is a working session, not a PowerPoint marathon. You have six Jupyter notebooks in front of you. By the end of today, you'll know which data architecture pattern to propose for any customer conversation — and you'll have run the code to prove it.

---

### Slide 02 — How to Read This Deck

**Layout:** Field Guide Header + 3×2 grid

| Header | Front Matter | ii. |
|--------|-------------|-----|
| Section | §00 — How to read this deck |
| Title | Six patterns. One scenario. Three questions repeated everywhere. |

**Grid (3×2):**

| # | Section Title | Description |
|---|--------------|-------------|
| §01 | The pattern, in one paragraph | Plain-language definition. No marketing. |
| §02 | When to use, when not to | A two-column rule of thumb you can quote in a meeting. |
| §03 | The setup | What you stand up. Plan A on Software Hub, Plan B on the laptop. |
| §04 | Three canonical queries | Same three business questions, every notebook. Watch them get easier — or harder. |
| §05 | Where it breaks | The cell that fails. The point of the exercise. |
| §06 | The IBM stack mapping | Where this pattern lives in the reference architecture. |

**Speaker notes:**
Every pattern gets the same six sections. This parallel structure is deliberate — by pattern three, you'll stop reading the slide and start anticipating the answer. That's the goal. When you're in a customer meeting and they describe their problem, you should be able to mentally pull up the right column from the "when to use" table.

---

### Slide 03 — Agenda

**Layout:** Field Guide Header + table

| Header | Front Matter | iii. |
|--------|-------------|------|
| Section | §00 — Agenda |
| Title | A half-day, in ten parts. |

| Time | Min | Topic | Mode |
|------|-----|-------|------|
| 0:00 | 15 | Welcome & the question we are here to answer | Talk |
| 0:15 | 20 | The reference architecture in one diagram | Talk |
| 0:35 | 30 | 01 — Warehouse | Lecture + Notebook |
| 1:05 | 30 | 02 — Data Lake | Lecture + Notebook |
| 1:35 | 15 | Break | — |
| 1:50 | 30 | 03 — Lakehouse | Lecture + Notebook |
| 2:20 | 25 | 04 — Virtualization | Lecture + Notebook |
| 2:45 | 30 | 05 — Data Mesh | Lecture + Notebook |
| 3:15 | 25 | Synthesis: choosing between the six | Discussion |
| 3:40 | 20 | Sales motion & next steps | Talk |

**Speaker notes:**
We have four hours. Each pattern gets 25–30 minutes: I talk for 10, you run the notebook for 15, we discuss for 5. The break is real — take it. The synthesis at the end is the most important part. That's where you build the muscle memory for customer conversations.

---

### Slide 04 — Opening Quote

**Layout:** Big Quote

| Element | Content |
|---------|---------|
| Quote mark | " (display font, huge, accent blue) |
| Quote | Every bank we walk into has a warehouse that works and an AI roadmap that doesn't. The question isn't which to keep. It's how they fit together. |
| Attribution | — The conversation, every Tuesday, at every customer |

**Speaker notes:**
This is the question. Not "warehouse or lakehouse?" Not "should we do AI?" The question is: how do these six patterns compose into one architecture that serves both the regulatory reporting team and the fraud modelling team? That's what today is about.

---

### Slide 05 — Reference Architecture

**Layout:** Field Guide Header + swimlane diagram

| Header | Prologue | 02. |
|--------|----------|-----|
| Section | §00 — The reference architecture |
| Title | Five swimlanes. Every pattern lives in one or two of them. |

**Swimlane diagram (5 lanes × 4 boxes each):**

| Lane | Box 1 | Box 2 | Box 3 | Box 4 |
|------|-------|-------|-------|-------|
| Sources | Core Banking | CRM | Policy PDFs | Card Stream |
| Ingest & Integration | CDC | Batch ETL | Streaming | API / Files |
| Analytical Storage | Warehouse | Object Lake | Lakehouse | Vector Store |
| Query & Compute | SQL Engine | Federation | ML / Notebook | RAG / LLM |
| Governance | Catalog | Lineage | Policy | MDM |

**Footnote:** Adapted from Software Hub 5.2 reference architecture · for teaching purposes

**Speaker notes:**
This is the reference architecture diagram you've seen a hundred times — but simplified to five lanes. Every pattern we cover today lives in one or two of these lanes. When we get to the IBM stack mapping slide for each pattern, I'll point to exactly where it sits. By the end, you'll have the whole diagram populated.

---

### Slide 06 — Three Canonical Queries

**Layout:** Field Guide Header + 3 query blocks

| Header | Prologue | 03. |
|--------|----------|-----|
| Section | §00 — Three canonical queries |
| Title | Same three questions in every notebook. Watch them get easier — or harder. |

| Query | Text | Tag |
|-------|------|-----|
| Q1 | Total transaction volume by branch for Q3 2024. | Structured · SQL-shaped |
| Q2 | Find all customers whose policy documents reference AML procedure X. | Unstructured · Document-shaped |
| Q3 | Trace the lineage of the Q3 branch summary back to source. | Metadata · Graph-shaped |

**Speaker notes:**
These three questions are the spine of the entire lecture. Q1 is easy — every pattern can answer it. Q2 is hard — only one pattern can answer it fully, and you won't see that until Notebook 6. Q3 is subtle — it tests whether the pattern knows where its own data came from. Watch how each pattern handles these three. That's where the insight lives.

---

## Pattern 1: Warehouse (Slides 07–12)

### Slide 07 — Section Divider: Warehouse

**Layout:** Section Divider (dark bg — INK background, PAPER text)

| Element | Content |
|---------|---------|
| Top label | Pattern 1 of 06 |
| Large number | 01 |
| Rule | 2pt × 2.2" |
| Title | Warehouse. |
| Blurb (italic) | The boring pattern that actually works. Star schemas, audit trails, regulatory reporting. |
| Bottom left | —— Lecture · Notebook 01 |
| Bottom right | 30 min |

**Speaker notes:**
The warehouse. The one pattern every bank already has, the one nobody wants to talk about at conferences, and the one that actually works for regulatory reporting. Let's see why it works, and where it stops working.

---

### Slide 08 — Warehouse: The Pattern in One Paragraph

**Layout:** Field Guide Header + paragraph + sidebar

| Header | Pattern 01 · Warehouse | § 01 |
|--------|----------------------|------|
| Section | §01 — The pattern, in one paragraph |
| Title | The warehouse. |

**Paragraph:**
A centralized, schema-on-write analytical store. Data is modelled into star or snowflake schemas — dimension tables surrounding fact tables — and optimised for analytical SQL. The backbone of regulatory reporting and BI at every major bank. Stable schemas, strong consistency, audit trails, and fast aggregations over historical data.

**Sidebar:**
Reference Architecture · Lane
**Analytical Data Management & Storage**

**Speaker notes:**
Schema-on-write means you decide the shape of the data before you load it. That's a feature, not a bug — it means every query runs against a known, validated structure. The tradeoff is rigidity: if the business wants a new column, that's a change request, a sprint, and a deployment.

---

### Slide 09 — Warehouse: When to Use / When Not To

**Layout:** Field Guide Header + Two-Column Compare

| Header | Pattern 01 · Warehouse | § 02 |
|--------|----------------------|------|
| Section | §02 — When to use, when not to |
| Title | Two columns. Memorise both. |

| # | Use when | Don't use when |
|---|----------|----------------|
| 01 | Stable, known schemas | Schema evolves rapidly |
| 02 | BI and regulatory reporting | Unstructured / AI workloads |
| 03 | Strong consistency | Cheap raw storage at scale |
| 04 | SQL-heavy analytics | Sub-second OLTP |
| 05 | Historical trend analysis | Real-time streaming |

**Speaker notes:**
The left column is where the warehouse earns its keep. The right column is where customers start looking for something else. When you hear "we need to store PDFs" or "we want to train a model" — that's your cue. The warehouse is not the answer. But don't take it away either.

---

### Slide 10 — Warehouse: Where It Breaks

**Layout:** Field Guide Header + code block + takeaway

| Header | Pattern 01 · Warehouse | § 05 |
|--------|----------------------|------|
| Section | §05 — Where this pattern breaks |
| Title | Storing a policy PDF as a BLOB. |

**Code block (SQL):**
```sql
-- Try to search inside an unstructured doc
INSERT INTO policy_documents (id, pdf_content)
VALUES ('MTB-POL-001', :pdf_bytes);

SELECT * FROM policy_documents
 WHERE pdf_content CONTAINS 'AML procedure X';
        ^^^^^^^^^^
        ERROR — no full-text over BYTEA
```
**Comment:** The bytes are stored. They are not understood.

**Takeaway:** The warehouse stores the bytes. It cannot read them.

**Speaker notes:**
This is the cell that fails. You can INSERT a PDF into a BYTEA column. Congratulations, you have a very expensive file server. You cannot search inside it, you cannot extract entities, you cannot embed it for RAG. This is why Q2 — "find customers whose policy documents reference AML procedure X" — cannot be answered by a warehouse alone.

---

### Slide 11 — Warehouse: IBM Stack Mapping

**Layout:** Field Guide Header + table

| Header | Pattern 01 · Warehouse | § 06 |
|--------|----------------------|------|
| Section | §06 — The IBM stack mapping |
| Title | Where this pattern lives in the reference architecture. |

| Layer | IBM product or component | Notebook ref |
|-------|-------------------------|--------------|
| Storage | Db2 Warehouse (SMP/MPP), Db2 z/OS, Netezza | NB 01 |
| Query Engine | Db2 optimiser, Presto via watsonx.data | NB 01 |
| Catalog | Knowledge Catalog | NB 03 |
| Governance | Lineage, Quality, Business Glossary | NB 03 |

**Speaker notes:**
When you're positioning this with a customer, point at the Analytical Data Management & Storage lane in the reference architecture. Db2 Warehouse is the anchor product. If they're on z/OS, it's Db2 for z/OS. If they want modern, it's watsonx.data with Presto querying the same data.

---

### Slide 12 — Warehouse: BFSI Reality Check

**Layout:** Big Stat (PAPER_ALT background)

| Element | Content |
|---------|---------|
| Kicker | § 07 — BFSI Reality Check |
| Stat | 15-20 |
| Unit | YR |
| Caption | How old most Canadian banks' warehouse investments are. They work for BI dashboards. They cannot serve a fraud model. |
| Footnote | Source: customer interviews, Maple Trust composite |

**Speaker notes:**
This is a real number. When you walk into RBC, TD, or Scotiabank, their core warehouse is 15–20 years old. It runs the regulatory reports. It serves the BI dashboards. It is not going anywhere. But it also cannot serve a fraud model that needs real-time features, unstructured data, and embeddings. That's the gap we're here to fill — not by replacing the warehouse, but by layering the right patterns around it.

---

## Pattern 2: Data Lake (Slides 13–18)

### Slide 13 — Section Divider: Data Lake

**Layout:** Section Divider (dark bg)

| Element | Content |
|---------|---------|
| Top label | Pattern 2 of 06 |
| Large number | 02 |
| Title | Data Lake. |
| Blurb (italic) | Cheap object storage holding everything raw. Schema-on-read, when (and if) someone reads it. |

**Speaker notes:**
The data lake. Born from the promise that you could store everything cheaply and figure out the schema later. Some teams did figure it out. Most didn't. Let's see both sides.

---

### Slide 14 — Data Lake: The Pattern in One Paragraph

**Paragraph:** Raw files on cheap object storage — Parquet, JSON, CSV, PDFs — organised as bronze/silver/gold zones. Schema is applied at read time. Excellent for ML feature engineering and unstructured data. Without governance, easily becomes a data swamp.

**Sidebar:** Raw Storage & Curated Zones

**Speaker notes:**
Schema-on-read is the opposite of the warehouse. You dump the data first, ask questions later. The bronze/silver/gold zoning pattern is how teams impose order — raw, cleaned, curated. But zoning is a convention, not a constraint. Nothing enforces it.

---

### Slide 15 — Data Lake: When to Use / When Not To

| # | Use when | Don't use when |
|---|----------|----------------|
| 01 | Cheap raw storage at scale | Need ACID across the lake |
| 02 | Mixed structured & unstructured | Sub-second BI |
| 03 | ML / feature engineering | Strict regulatory schema |
| 04 | Schema may evolve | Concurrent writers without coordination |
| 05 | Long-tail audit retention | Naïve users running ad-hoc SQL |

**Speaker notes:**
The "don't" column is where 60% of data lake projects went wrong. "Concurrent writers without coordination" — that's the killer. Two Spark jobs appending to the same prefix at the same time. No ACID. No rollback. Partial files. This is exactly what the lakehouse pattern fixes.

---

### Slide 16 — Data Lake: Where It Breaks

**Title:** Concurrent writers, no transactions.

**Code (Python):**
```python
# Two ETL jobs writing to the same prefix
job_a.write_parquet('s3://gold/txns/', mode='append')
job_b.write_parquet('s3://gold/txns/', mode='overwrite')
# Race: partial files, no rollback
# downstream readers see half-written partition
```

**Takeaway:** Files alone are not a database. Concurrency requires a table format.

**Speaker notes:**
This happens at every bank that built a lake without Iceberg or Delta. Job A appends. Job B overwrites. The downstream reader gets a corrupted view. No rollback, no isolation, no history. This is why the next pattern — the lakehouse — exists.

---

### Slide 17 — Data Lake: IBM Stack Mapping

| Layer | IBM product or component | Notebook ref |
|-------|-------------------------|--------------|
| Storage | IBM Storage Ceph, MinIO, S3-compatible | NB 02 |
| Format | Parquet, ORC, Avro, JSON | NB 02 |
| Compute | Spark on watsonx.data, Presto | NB 02 |
| Governance | Knowledge Catalog (zone tagging) | NB 03 |

**Speaker notes:**
The storage layer is commodity S3-compatible — MinIO in the lab, Ceph or IBM Cloud Object Storage in production. The key IBM differentiator here is Knowledge Catalog for zone tagging and classification. Without it, your lake becomes a swamp on day 90.

---

### Slide 18 — Data Lake: BFSI Reality Check

| Stat | 60 | % |
|------|----|---|
| Caption | Of bank-built data lakes that became swamps within three years. The pattern requires governance from day one. |
| Footnote | Source: composite of customer engagements 2019–2024 |

**Speaker notes:**
Sixty percent. That's not a conference stat — that's what we see in customer engagements. The pattern works beautifully when you have a dedicated platform team and Knowledge Catalog from day one. It fails when someone says "just dump it in S3 and we'll figure it out."

---

## Pattern 3: Lakehouse (Slides 19–24)

### Slide 19 — Section Divider: Lakehouse

| Title | Lakehouse. |
|-------|-----------|
| Blurb | The lake, with transactions bolted on. ACID over Parquet. Iceberg, Delta, Hudi. |

**Speaker notes:**
The lakehouse is the pragmatic answer. Take the cheap storage from the lake, add ACID transactions from the warehouse, and you get the best of both. Iceberg is the default table format in watsonx.data — that's the product tie-in.

---

### Slide 20 — Lakehouse: The Pattern in One Paragraph

**Paragraph:** A table format — Iceberg, Delta, Hudi — layered over the lake. Adds ACID transactions, schema evolution, time travel, and partition pruning to cheap object storage. You get warehouse semantics on lake economics. The pragmatic answer for most new analytical workloads.

**Sidebar:** Analytical Data Management & Storage

**Speaker notes:**
Time travel is the sleeper feature. When a regulator asks "what did the data look like on March 15th?" — with Iceberg, you answer in one query. With a traditional lake, you answer with a three-week data recovery project.

---

### Slide 21 — Lakehouse: When to Use / When Not To

| # | Use when | Don't use when |
|---|----------|----------------|
| 01 | One source of truth for BI + ML | Sub-millisecond point lookups |
| 02 | Schema evolution required | Existing warehouse satisfies BI alone |
| 03 | Time travel / audit replay | Team has no Spark/Iceberg skill |
| 04 | Mixed batch + streaming writers | Tiny datasets |
| 05 | Open formats, no vendor lock-in | No object storage available |

**Speaker notes:**
"Existing warehouse satisfies BI alone" — this is the conversation you need to have with the customer. If their warehouse works fine and they don't need ML or unstructured data, don't sell them a lakehouse. Sell them governance. The lakehouse is for the team that needs both BI and ML from the same data.

---

### Slide 22 — Lakehouse: Where It Breaks

**Title:** A schema migration mid-flight.

**Code (SQL):**
```sql
-- Iceberg makes this safe.
ALTER TABLE bronze.transactions
  ADD COLUMN merchant_category STRING;

ALTER TABLE bronze.transactions
  RENAME COLUMN amt TO amount;

-- Time travel back if downstream breaks
SELECT * FROM bronze.transactions
  FOR VERSION AS OF 142;
```

**Takeaway:** Schema evolution is a feature, not a project plan.

**Speaker notes:**
This slide is actually showing where the lakehouse works — schema evolution that would be a two-week project on a traditional warehouse is a one-line DDL with Iceberg. The "break" here is subtle: if your team doesn't understand Iceberg metadata, they'll miss partition pruning and wonder why queries are slow. The tool works. The skill gap is the real break point.

---

### Slide 23 — Lakehouse: IBM Stack Mapping

| Layer | IBM product or component | Notebook ref |
|-------|-------------------------|--------------|
| Table Format | Apache Iceberg (default in watsonx.data) | NB 03 |
| Storage | S3 / Ceph / MinIO buckets | NB 03 |
| Query Engine | Presto, Spark, Db2 (via watsonx.data) | NB 03 |
| Catalog | Iceberg REST catalog + Knowledge Catalog | NB 03 |

**Speaker notes:**
watsonx.data is the product. Iceberg is the default table format. The pitch: "You get warehouse governance on lake economics, with time travel for regulatory replay." That's the one-liner for the customer conversation.

---

### Slide 24 — Lakehouse: BFSI Reality Check

| Stat | 3 | × |
|------|---|---|
| Caption | Faster point queries on a lakehouse with Iceberg metadata pruning vs. raw Parquet on the same lake. |
| Footnote | Maple Trust benchmark, Q3 2024 |

**Speaker notes:**
Three times faster. Same data, same hardware. The difference is Iceberg metadata — it knows which files contain the rows you need, so it skips the rest. This is not a vendor benchmark. This is what you get on the lab setup you're running right now.

---

## Pattern 4: Virtualization (Slides 25–30)

### Slide 25 — Section Divider: Virtualization

| Title | Virtualization. |
|-------|----------------|
| Blurb | No movement. Federated queries across engines, in place. |

**Speaker notes:**
Virtualization is the pattern that makes compliance teams happy: no data movement means no data residency violations. But it's also the pattern that makes performance engineers nervous. Let's see both sides.

---

### Slide 26 — Virtualization: The Pattern in One Paragraph

**Paragraph:** A federation engine — Presto, Db2 Big SQL, Starburst — that issues queries to source systems in place. No data movement, no copies. The warehouse, the lake, and the operational store all look like one SQL surface. Pays for itself in egress fees and copy-pipeline maintenance.

**Sidebar:** Query Federation

**Speaker notes:**
"No data movement" is the key phrase. In a world of data residency regulations, PIPEDA, and OSFI guidelines on cross-border data flows, the ability to query without copying is a compliance feature, not just a performance one.

---

### Slide 27 — Virtualization: When to Use / When Not To

| # | Use when | Don't use when |
|---|----------|----------------|
| 01 | Data cannot move (regulatory, residency) | Latency-sensitive transactional workloads |
| 02 | Many sources, one consumer | Source systems already overloaded |
| 03 | Prototype before you copy | Heavy aggregations on cold data |
| 04 | Recently-acquired subsidiary data | Same query 10,000× per hour |
| 05 | Cross-region analytical joins | Full historical scans |

**Speaker notes:**
"Same query 10,000 times per hour" — at that point, materialize it. Virtualization is for the query you run once a day across three systems, not for the dashboard that refreshes every 10 seconds. Know the boundary.

---

### Slide 28 — Virtualization: Where It Breaks

**Title:** Pushdown that did not push down.

**Code (SQL):**
```sql
-- Looks fine. Reads 240M rows across the wire.
SELECT c.segment, SUM(t.amount)
FROM   pg.bfsi.dim_customers c
JOIN   iceberg.gold.fact_transactions t
       ON c.customer_id = t.customer_id
WHERE  c.kyc_status = 'review'
GROUP BY c.segment;

-- The Postgres predicate did not push.
-- The join happened in the federation engine.
```

**Takeaway:** Virtualization is not magic. It is a placement decision dressed as SQL.

**Speaker notes:**
This is the most common failure mode. The developer writes SQL, the optimizer sends it to the federation engine, and the federation engine pulls 240 million rows across the network because it couldn't push the WHERE clause down to Postgres. Always EXPLAIN first. Always check the query plan.

---

### Slide 29 — Virtualization: IBM Stack Mapping

| Layer | IBM product or component | Notebook ref |
|-------|-------------------------|--------------|
| Engine | Presto / watsonx.data SQL, Db2 Big SQL | NB 04 |
| Connectors | JDBC, Iceberg, Kafka, MongoDB, S3 | NB 04 |
| Optimisation | Cost-based optimizer, materialized views | NB 04 |
| Governance | Row/column policies, query audit | NB 04 |

**Speaker notes:**
watsonx.data's Presto engine is the federation layer. The differentiator vs. open-source Presto is the governance integration — row-level and column-level policies enforced at query time, not at the application layer. That's the compliance story.

---

### Slide 30 — Virtualization: BFSI Reality Check

| Stat | 0 | COPIES |
|------|---|--------|
| Caption | Of customer transaction data leaves the originating jurisdiction in the federated reference design. |
| Footnote | Pattern requires query-time policy enforcement |

**Speaker notes:**
Zero copies. That's the pitch for any customer with data residency concerns. Canadian transaction data stays in Canada. European data stays in Europe. The federation engine queries it in place. The policy engine enforces column-level access at query time. This is the compliance architecture slide you bring to the CISO.

---

## Pattern 5: Data Mesh (Slides 31–36)

### Slide 31 — Section Divider: Data Mesh

| Title | Data Mesh. |
|-------|-----------|
| Blurb | Domain-owned data products. The org chart, expressed in storage. |

**Speaker notes:**
Data mesh. The most over-hyped and under-implemented pattern in the industry. But also the right answer for large organizations with 500+ data engineers and strong product culture. Let's be honest about when it works and when it doesn't.

---

### Slide 32 — Data Mesh: The Pattern in One Paragraph

**Paragraph:** A socio-technical pattern. Domains — Cards, Mortgages, Wealth — own their data as products with SLAs, contracts, and lifecycle. A central platform team provides the runway: catalog, discovery, governance, observability. Federated computational governance, not anarchy.

**Sidebar:** Data Products + Federated Governance

**Speaker notes:**
The key phrase is "socio-technical." This is not a technology decision. This is an org design decision expressed in technology. If the customer doesn't have domain teams with engineering ownership, mesh will fail — not because the tech is wrong, but because the org isn't ready.

---

### Slide 33 — Data Mesh: When to Use / When Not To

| # | Use when | Don't use when |
|---|----------|----------------|
| 01 | Large org with clear domains | Org < 200 people |
| 02 | Central data team is the bottleneck | No platform team |
| 03 | Data products have real consumers | "Self-serve" means "no service" |
| 04 | Strong platform engineering | Domains have no engineering |
| 05 | Long-term commitment | Quarterly priorities only |

**Speaker notes:**
Read the right column carefully. "Self-serve means no service" — that's the single biggest failure mode. The CTO says "we're doing self-serve data" and what they mean is "we fired the data team and gave everyone S3 access." That is not mesh. That is chaos.

---

### Slide 34 — Data Mesh: Where It Breaks

**Title:** The product without an owner.

**Code (YAML):**
```yaml
# data-product.yaml
name: cards.transactions.gold
owner: ???
sla:
  freshness: P1D
  availability: 99.5%
consumers:
  - fraud-modelling
  - finance-reporting
  - customer-360

# Status: orphaned. Last update 14 months ago.
# Three downstream teams are blocked on it.
```

**Takeaway:** Mesh is an org change, expressed in YAML.

**Speaker notes:**
This YAML file is real — the names are changed, but I've seen this exact situation at three different banks. A data product with three downstream consumers and no owner. The SLA says 99.5% availability, but nobody's been updating it for 14 months. This is what happens when you adopt mesh without investing in data product management.

---

### Slide 35 — Data Mesh: IBM Stack Mapping

| Layer | IBM product or component | Notebook ref |
|-------|-------------------------|--------------|
| Product Catalog | Knowledge Catalog (data products + contracts) | NB 05 |
| Storage | Lakehouse (NB 03) per domain | NB 05 |
| Governance | Federated policies, contract tests | NB 05 |
| Observability | Lineage, freshness SLOs, schema drift | NB 05 |

**Speaker notes:**
IBM doesn't sell "data mesh." IBM sells the platform that makes mesh possible — if the org is ready. Knowledge Catalog is the federated product catalog. watsonx.data is the storage layer each domain gets. The pitch is: "We give your domains the runway. You provide the product owners."

---

### Slide 36 — Data Mesh: BFSI Reality Check

| Stat | 18 | MO |
|------|----|----|
| Caption | Realistic minimum to a working mesh — and that is with a sponsoring exec, a platform team, and a clear first domain. |
| Footnote | Honest answer when a customer asks "how long" |

**Speaker notes:**
Eighteen months. That's the honest answer when a customer asks "how long does mesh take?" And that's the optimistic case — with executive sponsorship, a dedicated platform team, and a clear first domain. Tell the customer this. They'll trust you more for being honest than for promising six months.

---

## Closing Slides (37–39)

### Slide 37 — Exercise

**Layout:** Field Guide Header + Exercise Card

| Header | Hands-on | EX. |
|--------|----------|-----|
| Section | §EX — Exercise · choose your pattern |
| Title | Maple Trust just bought a regional credit union. Which pattern do you propose, and why? |

| Element | Content |
|---------|---------|
| Duration | 20 minutes |
| Prompt | The acquired credit union has Db2 on z/OS, a small Hadoop lake, and a folder of 14,000 PDF policy documents. Fraud Modelling needs everything in one queryable surface within six weeks. Regulator needs lineage from day one. Pick one or two patterns from the six. Defend your choice. |
| Step 01 | In pairs: pick the pattern. Sketch the data flow on a single sheet. |
| Step 02 | Identify the cell that breaks — what would be in your "Section 5" slide? |
| Step 03 | Name the IBM components, by reference-architecture lane. |
| Step 04 | Be ready to defend it for two minutes when called. |
| Deliverable | One slide, one diagram, two minutes |

**Speaker notes:**
This is the real test. No right answer — but there are wrong answers. If someone says "just warehouse everything," push back: what about the 14,000 PDFs? If someone says "data mesh," push back: in six weeks? The interesting answers are the compositions — virtualization + lakehouse, or lakehouse + RAG. Let them argue.

---

### Slide 38 — Synthesis Matrix

**Layout:** Field Guide Header + matrix table

| Header | Synthesis | 07. |
|--------|-----------|-----|
| Section | §07 — Choosing between the six |
| Title | The matrix you can draw on a napkin. |

| Workload | WH | DL | LH | V | M |
|----------|----|----|----|----|---|
| Regulatory BI | ● | ○ | ● | ◐ | ◐ |
| Ad-hoc ML feature eng. | ○ | ◐ | ● | ◐ | ● |
| Unstructured / RAG | ○ | ● | ● | ◐ | ● |
| Cross-system join | ◐ | ○ | ◐ | ● | ● |
| Schema evolves weekly | ○ | ◐ | ● | ◐ | ● |
| Data residency hard-line | ○ | ○ | ○ | ● | ● |

**Legend:** ● Strong fit · ◐ Possible · ○ Wrong tool

**Speaker notes:**
This is the slide you photograph and keep on your phone. When a customer describes their problem, you look at which row it sits on, and the filled circles tell you which pattern to propose. If they have three rows filled, they need a composition — and that's where the architecture conversation starts.

---

### Slide 39 — Closing

**Layout:** Dark background (INK bg, PAPER text)

| Element | Content |
|---------|---------|
| Top label | End of Volume One |
| Title | Six patterns. One conversation. |
| Subtitle (italic) | Walk into the next customer with the matrix on the previous slide. Listen for which row their problem sits on. Propose the pattern, not the product. |
| Bottom left | Questions? |
| Bottom center | manav.gupta@... |
| Bottom right | Notebooks · github.com/... |

**Speaker notes:**
Thank you. The notebooks are on GitHub — run them again at home, break them deliberately, build intuition. The matrix on the previous slide is your cheat sheet. When the customer says "we need to query across three systems without moving data," you know the answer is virtualization. When they say "we need ACID on the lake," it's lakehouse. When they say "our domains need autonomy," it's mesh — but only if they have the org maturity. Propose the pattern. Then back it with the product.
