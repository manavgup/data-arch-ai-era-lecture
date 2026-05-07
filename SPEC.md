# Half-Day Lecture: Data Architecture for the AI Era
## Claude Code Build Handoff

**Owner:** Manav Gupta, VP & CTO, Technical Sales, IBM Canada
**Audience:** Mixed IBM technical (sellers, ATLs, architects, SSRs)
**Format:** Half-day (4h contact + 30 min breaks)
**Anchor visual:** IBM Software Hub / Cloud Pak for Data Reference Architecture (provided separately)

---

## 0. Read this first

This document is the complete, frozen spec for a half-day lecture deliverable. It captures every decision made during scoping. Build everything in this document. Do not re-litigate decisions unless the user explicitly asks. When a choice was made between two options, the chosen option is described and the rejected option is noted in the **Decisions log** at the end.

The lecture is anchored on a single canonical IBM diagram — the **Cloud Pak for Data Platform Reference Architecture** (PDF in this repo as `reference/Software_Hub_5_2_-_Reference_Architecture.PDF`). Every block of the lecture returns to this diagram with a different swimlane highlighted. Treat this diagram as the spine of the entire deliverable.

### Build order (long pole first)

1. Synthetic BFSI dataset (`data/`)
2. Six Jupyter notebooks (`notebooks/`)
3. Facilitator guide (`facilitator-guide.md`)
4. PPTX deck (`deck/data-architecture-ai-era.pptx`)
5. Architecture critique handout (`handouts/critique.pdf` or `.md`)
6. Take-home study guide (`handouts/self-paced-guide.md`)

### Tone and style

- **Light theme PPTX** (light backgrounds, dark text). No dark theme. This is non-negotiable.
- **Humorous-yet-authoritative speaker notes.** Manav's standard register. Self-deprecating, occasionally barbed at industry hype, never cruel about clients. Examples: *"This is the slide everyone has seen 400 times. Today is the day someone explains it to you."* / *"Pure vector RAG is what consultants sell. Hybrid retrieval is what works."*
- **No IBM references in non-IBM-branded decks** is Manav's usual rule, but THIS deck is IBM-internal, so IBM branding is fine and expected.
- **BFSI lens.** Examples should reference Canadian banks (RBC, CIBC, Scotia, BMO, Desjardins) and SSC, anonymized where appropriate.

---

## 1. Lecture structure (final, approved)

### Total: 270 min (4h 30m), targeted at "half day"

| Segment | Time | Type |
|---|---|---|
| Opening | 10 min | Slides + diagram tour |
| Block 1 — Foundations | 45 min | Slides + 2 brief notebook cameos |
| Block 2 — AI-Era Architecture | 60 min | Slides + 1 notebook teaser |
| Break | 15 min | — |
| Block 3 — Governance, AI Governance, Agent Control Plane | 45 min | Slides |
| Block 4 — Hands-on Labs + Critique | 60 min | 2 notebooks live + critique |
| Block 5 — Close & Q&A | 15 min | Slides + discussion |
| Buffer / second short break | 20 min | — |

The "hybrid teaching model" was chosen: **slides drive the conceptual map, notebooks provide visceral evidence at key moments, deep notebook work happens in Block 4.**

### Opening (10 min)

- **Hook slide:** *"The data architecture you designed in 2019 is what's breaking your AI strategy in 2026."*
- **Anchor slide:** Full Cloud Pak for Data reference architecture diagram. Stated thesis: *"This is the slide. The whole half-day is teaching you how to read it."*
- 30,000-ft swimlane walk (3 min)
- Why each role cares (sellers / architects / SSRs)
- Ground rules: interrupt freely, two notebooks live in Block 4, two notebook cameos in Block 1, one critique exercise

### Block 1 — Foundations (45 min)

Teaches the **storage and access swimlanes** of the reference architecture.

#### 1.1 Why data architecture keeps getting reinvented (8 min)
- 30-year arc: OLTP → warehouse → lake → lakehouse → mesh → fabric
- Each generation solved scaling and created governance debt
- Pendulum: centralize → decentralize → federate

#### 1.2 The five primitives every architect must know cold (12 min)

Reframe from "four primitives" to **five** — observability is now first-class.

- **Storage:** object stores, columnar formats (Parquet, ORC), open table formats (Iceberg, Delta, Hudi)
- **Compute:** query engines (Presto/Trino, Spark, DuckDB), separation of storage and compute
- **Catalog:** Hive, Unity, Polaris, Nessie — catalog wars are the new format wars
- **Governance plane:** lineage, access, classification, lifecycle
- **Observability:** quality, freshness, schema drift, pipeline SLOs, lineage-driven impact analysis

#### 1.3 Pattern decoder ring (15 min)

Slide table — when to use, when each is actively wrong:

| Pattern | Best for | Anti-pattern |
|---|---|---|
| Data warehouse | Stable schemas, BI, regulatory reporting | Unstructured/AI workloads |
| Data lake | Cheap raw storage, ML training sets | Anything needing ACID or governance |
| Lakehouse | Unified analytics + ML on open formats | Sub-second OLTP |
| Data virtualization | Federated queries across heterogeneous sources without moving data; cases where data *cannot* move | High-volume analytical scans, latency-sensitive workloads |
| Data mesh | Large orgs with strong domain teams | Orgs without product thinking |
| Data fabric | Heterogeneous estates, federation | Greenfield single-cloud |

**Notebook cameo #1 (3 min):** open `notebooks/01-warehouse.ipynb`, run one canonical query against the synthetic BFSI star schema, show the output. Establishes "we have notebooks, they're real, you'll see more later."

**Notebook cameo #2 (3 min):** open `notebooks/04-virtualization.ipynb`, run one federated query joining two sources without moving data. Virtualization is the most-misunderstood pattern; seeing it run kills 80% of the confusion.

#### 1.4 Master data management — the unsexy foundation (7 min)
- Why MDM became cool again: agents need authoritative entities to reason over
- Four MDM patterns: registry, consolidation, coexistence, centralized
- IBM MDM / InfoSphere MDM / Match 360 positioning
- BFSI reality: every Canadian bank has a 10-year MDM program that's "almost done"; agentic AI just made it urgent again
- Graph + MDM: the entity resolution play (foreshadows Block 2.3 Graph RAG)

#### 1.5 IBM stack mapped to the reference architecture (3 min)
Annotated version of the canonical diagram with the storage + access swimlanes lit up, rest dimmed. Show: watsonx.data, Db2, Db2 Warehouse, Informix, EDB Postgres, Data Virtualization, Presto connector, Iceberg, Delta Lake, Milvus.

### Block 2 — AI-Era Data Architecture (60 min)

Teaches the **right side and AI extensions** of the reference architecture, with two explicit gap callouts: Docling (ingestion) and MCP/Context Forge (agent control plane).

#### 2.1 What changed when AI ate the stack (10 min)
- Read patterns flipped: from "scan tables" to "retrieve passages"
- Latency budgets collapsed: minutes (BI) → milliseconds (agent loops)
- New first-class citizens: embeddings, chunks, traces, prompts, tool-call logs
- Unstructured data tax: 80% of enterprise data was unusable for analytics, now it's primary fuel

#### 2.2 The RAG reference architecture (15 min)

Pipeline: **Docling → chunking → embedding → OpenSearch → retrieval → reranking → context assembly → watsonx.ai**

- Where each layer fails in production (chunking is where dreams die)
- **Docling** as the ingestion-side fix:
  - Open-source, Apache 2.0, IBM Research Zurich, now in Linux Foundation's Agentic AI Foundation
  - Replaces naive OCR with layout-aware extraction (~30× speedup, preserves structure)
  - Outputs `DoclingDocument` representation: bounding boxes, reading order, structure-aware chunking
  - Integrates with LangChain, LlamaIndex, spaCy
  - Granite-Docling-258M VLM under Apache 2.0
  - Docling OpenShift Operator with Red Hat — banks named as deployment segment
- **OpenSearch** as the hybrid retrieval workhorse: BM25 + vector + reranker in one engine
- Vector store decision tree: Milvus, Elastic/OpenSearch, Pinecone, Weaviate, Chroma, pgvector — picking based on scale, hybrid needs, ops maturity
- Pure vector is a myth — hybrid retrieval is the real baseline

**Notebook teaser #3 (3 min):** open `notebooks/06-rag-mdm.ipynb` to the Docling cell, parse a real PDF live, show the structured output with reading order preserved.

#### 2.3 Beyond RAG: context engineering and the agent data plane (15 min)
- "RAG vs fine-tuning" is the wrong question
- Context engineering: what goes in the window, in what order, with what provenance
- Agent data plane: tool registries, memory stores, trace logs, evaluation sets — *these are data architecture now*
- Graph RAG and when it beats vector (entity-heavy, multi-hop)
- **Open RAG positioning:** open standards, open formats, swappable components — why enterprise buyers are demanding it

#### 2.4 The integration contract: MCP and the agent control plane (15 min)
- Why MCP matters for data architects: integration contract between agents and enterprise data
- **MCP Context Forge** as the missing layer between AI agents and your enterprise — full pitch (Manav is a contributor; lean in)
  - NHI attribution, blast radius, HITL gate, DLP, immutable audit, anomaly detection
  - Plugin model and why it matters for governance
- This is a **gap** in the canonical reference architecture diagram — call it out explicitly. Position Manav (and the audience) as ahead of the published material.
- Connects to Block 3 (governance) — preview, not deep-dive

### Break (15 min)

### Block 3 — Data Governance, AI Governance, Agent Control Plane (45 min)

Teaches the **bottom three bands** of the reference architecture: Information & Model Governance, Security, Deploy Anywhere.

#### 3.1 Three governance problems, not one (10 min)
- **Data governance:** table-stakes (lineage, quality, access, classification)
- **AI/model governance:** model-risk (E-23, SR 11-7, model cards, bias, drift)
- **Agent control plane:** the new problem (autonomous tool use, NHI, blast radius, prompt injection)
- Treating these as one thing is how enterprises get burned

#### 3.2 What "regulated" actually means (10 min)
- OSFI B-13, PIPEDA, residency, lineage-to-audit-trail, model risk management
- Why every reference architecture you see online is wrong for a Canadian bank
- Sovereignty vs. residency vs. operational sovereignty — three different things
- "Sovereignty, not solitude" — sovereignty doesn't mean isolation
- How RBC, CIBC, Scotia approach this differently (anonymized stories)

#### 3.3 Data observability — the fifth primitive in production (5 min)
- Data quality monitoring, freshness, schema drift, pipeline SLOs
- Tools: Monte Carlo, Bigeye, IBM Databand, OpenLineage
- The triad: data observability + model observability + agent trace observability
- Three layers, frequently confused, rarely all instrumented

#### 3.4 Governance as architecture, not afterthought (12 min)
- The 10-domain agentic governance framework (75 sub-capabilities) — overview only
- Mapping to a real bank's 80-domain questionnaire (anonymized RBC pattern)
- watsonx.governance + Orchestrate: where HITL and BPM integration fits
- Plugin-based governance: how Context Forge implements the framework
- AI Factsheets and model inventory in the reference architecture

#### 3.5 Why agents change the threat model (8 min)
- Autonomous tool use, lateral movement via tool chains, prompt injection as exfiltration vector
- Control plane requirements: identity, authorization, audit, kill switch, eval harness
- Where the named-partner ecosystem (AWS, Google, Microsoft, JPMC, Palo Alto, etc.) is converging
- Where IBM's POV is differentiated — and where we're catching up
- **Note:** Project Mantis was deliberately excluded from this lecture (decision below). Do not introduce it.

### Block 4 — Hands-on Labs + Critique (60 min)

#### 4.1 Setup and architecture map (5 min)
- Recap the reference architecture diagram one more time
- Show which notebooks light up which swimlanes
- Set the BFSI scenario: a Canadian bank's AML policy Q&A system with full lineage and audit

#### 4.2 Notebook 3 — Lakehouse pattern, run together (15 min)
File: `notebooks/03-lakehouse.ipynb`
- Connect to watsonx.data, query Iceberg tables of synthetic BFSI data
- Demonstrate schema evolution, time travel, partition pruning
- Trace a record from raw → curated → consumed; identify governance gaps
- **Outcome:** "lakehouse" is not a product, it's a contract between layers

#### 4.3 Notebook 6 — AI-era end-to-end, run together (25 min)
File: `notebooks/06-rag-mdm.ipynb`
- The full reference architecture in one notebook, traced explicitly
- Each section prints which swimlane is being exercised
- Sections:
  1. Foundation: Iceberg query on watsonx.data
  2. Virtualization: federated query joining watsonx.data + Db2
  3. Ingestion: Docling parses a PDF policy document
  4. Embedding + retrieval: OpenSearch hybrid (BM25 + vector + reranker), eval comparison
  5. Generation: watsonx.ai with retrieved context
  6. MDM: entity resolution on customer references in retrieved passages
  7. Governance: lineage probe, data quality checks, watsonx.governance hooks
  8. Agent control plane: wrap behind MCP Context Forge with NHI, blast radius, audit log, HITL
  9. Observability: traces across data, model, agent layers
  10. **The "break it" cell** — deliberately bad prompt or missing governance hook; watch the audit log catch it
- This is the most-discussed segment of the day. Do not cut.

#### 4.4 Architecture critique (15 min)
- Distribute the critique handout (`handouts/critique.md` / `.pdf`)
- Bad reference architecture pattern based on anonymized real-client engagement: simple RAG sold as "agentic," tightly coupled .NET/C#, vibes-based eval, PHI sent to a hyperscaler API with no guardrail, multi-tenancy "planned" at DB level, minimal logging, no fallback
- Small groups (3–4 people), 10 min to find failures, 5 min readout
- Facilitator surfaces failures groups miss

### Block 5 — Close & Q&A (15 min)

**One-slide takeaway:**
> *Data architecture in 2026 is the integration contract between your enterprise and your agents. Get it wrong and nothing else matters.*

**Three things every role should do Monday morning:**
- **Sellers:** stop selling "AI"; start selling the data plane that makes AI work
- **Architects:** audit your context engineering and your control plane, not just your RAG pipeline
- **SSRs:** every incident is now a governance incident

**Pointers:**
- MCP Context Forge: github.com/IBM/mcp-context-forge
- factor10.ai 10 Principles of Enterprise AI
- Docling: github.com/DS4SD/docling
- OpenSearch hybrid retrieval guide
- Internal IBM governance framework doc

**Open Q&A**

---

## 2. Notebook specification

### Six notebooks, all following the same template

Each notebook follows this structure for comparability:

1. **The pattern in one paragraph** (markdown)
2. **When you'd use it, when you wouldn't** (markdown table)
3. **The setup** — load synthetic BFSI data into the pattern's representative stack
4. **Three canonical queries** — same business questions across all notebooks:
   - Q1: "Total transaction volume by branch for Q3"
   - Q2: "Find all customers whose policy documents reference AML procedure X"
   - Q3: "Trace the lineage of this aggregate back to source"
5. **Where this pattern breaks** — a deliberately failing query that exposes the weakness
6. **The IBM stack mapping** — which IBM product implements each piece, with reference to the canonical diagram swimlane
7. **BFSI reality check** — one paragraph on how a Canadian bank actually uses this pattern (anonymized)

Same scaffold, six implementations. Sellers get pattern recognition; architects get code; SSRs get failure modes.

### The set

| # | File | Pattern | Stack | Live or take-home |
|---|---|---|---|---|
| 1 | `01-warehouse.ipynb` | Data warehouse | Postgres (portable proxy for Db2) with star schema | Take-home (3-min cameo in Block 1) |
| 2 | `02-data-lake.ipynb` | Data lake | MinIO + DuckDB on raw Parquet | Take-home only |
| 3 | `03-lakehouse.ipynb` | Lakehouse | watsonx.data + Iceberg + Presto (or local Iceberg + DuckDB fallback) | **Live, Block 4** |
| 4 | `04-virtualization.ipynb` | Data virtualization | Trino with Postgres + MinIO connectors (or watsonx.data federation) | Take-home (3-min cameo in Block 1) |
| 5 | `05-data-mesh.ipynb` | Data mesh | Iceberg + per-domain catalogs (simulated) | Take-home only |
| 6 | `06-rag-mdm.ipynb` | AI-era full stack | Docling + OpenSearch + watsonx.ai + Context Forge | **Live, Block 4** |

### Environment strategy

**Plan A (live IBM environment):** watsonx.data + OpenSearch + watsonx.ai + Context Forge instance provisioned ahead of time. Whoever owns lab environment provisioning needs lead time. Manav to identify owner.

**Plan B (fallback):** Notebooks 3 and 6 ship with pre-recorded cell outputs already populated. Participants read along during the session and run locally afterward. Less interactive but bulletproof. **Build for Plan A but make every notebook runnable on a participant's laptop with Docker** (Postgres, MinIO, DuckDB, Trino are all containerized; OpenSearch has a single-node Docker image; watsonx.ai inference can be stubbed with a local Ollama model for offline notebook execution if needed).

### Notebook 6 deserves special attention

This is the headline artifact. It needs to:

- Tell a single coherent BFSI story (AML policy Q&A) end-to-end
- Print swimlane callouts at each section so participants connect code to diagram
- Have the **break-it cell** as the climax — a deliberately bad prompt or missing governance hook that the Context Forge audit log catches in real time
- Be ~60 cells total, runnable in 25 minutes when narrated
- Have a "skip" structure so the facilitator can fast-forward sections if running behind

### Notebook 5 (data mesh) caveat

Mesh is fundamentally an organizational pattern. The notebook simulates it: per-domain Iceberg catalogs, data product contracts (JSON schemas), a consumer notebook that pulls from multiple domains. Be honest in markdown that this is a *simulation* of the consumer experience, not a full mesh implementation.

### Synthetic BFSI dataset

Build in `data/`. Approximate size 50 MB total. Contents:

- `transactions.parquet` — 1M synthetic transactions across 50 branches over 2 years; columns: transaction_id, account_id, branch_id, amount, currency, timestamp, transaction_type, channel, counterparty_id
- `customers.parquet` — 100K synthetic customers; columns: customer_id, name, dob, residency, kyc_status, risk_score, opened_date, segment
- `branches.parquet` — 50 branches; columns: branch_id, name, address, region, manager_id
- `accounts.parquet` — 200K accounts linking customers to transactions
- `policies/` — 10 synthetic AML/KYC policy PDFs, ~5–20 pages each, with realistic structure (sections, tables, references). Use real policy *structure* (drawn from public OSFI/FINTRAC guidance) but invent the bank name ("Maple Trust Bank" or similar). These are what Docling parses in Notebook 6.
- `eval/aml_qa_eval.jsonl` — 30 question-answer pairs against the policy corpus for hybrid retrieval evaluation in Notebook 6
- `lineage/lineage_graph.json` — synthetic lineage records connecting raw → curated → consumed for the lineage probe in Notebook 3
- `mdm/entity_links.parquet` — synthetic match keys for the entity resolution exercise

Generate with a single script `data/generate.py` that's idempotent and seedable. Use Faker, Mimesis, or similar. Document the schema in `data/README.md`.

### MCP Context Forge integration

Manav is a contributor to the project (github.com/IBM/mcp-context-forge). Notebook 6 should genuinely use Context Forge, not stub it. If Context Forge has a Python SDK or HTTP API, wire to it. If not, ship a minimal local proxy (`tools/context_forge_local.py`) that implements the plugin interface (NHI attribution, blast radius check, HITL gate, audit log emission) so the notebook demonstrates the *contract* even when running offline. The audit log should be visibly inspected in the break-it cell.

---

## 3. Deck specification

### File: `deck/data-architecture-ai-era.pptx`

**Format requirements:**
- Light theme (light background, dark text). Always.
- IBM-branded (IBM-internal audience)
- 16:9 widescreen
- Speaker notes on every content slide
- Speaker notes tone: humorous-yet-authoritative; Manav voice
- Use IBM color palette: Signal Blue (#2D4ADE), neutral grays, accent colors sparingly
- Use Plex font family if licensed/available; fallback Helvetica/Arial

### Slide count target: ~50–60 slides total

Density rule: text-light, diagram-heavy. Sellers in the audience read fast and skim.

### Required slides (skeleton)

**Opening (3 slides):**
1. Title: *Data Architecture for the AI Era — A Field Guide for Sellers, Architects, and SSRs*
2. The hook quote slide
3. **The Diagram** — full Cloud Pak for Data reference architecture, full slide

**Block 1 (8–10 slides):**
4. *"Why we keep reinventing data architecture"* — the 30-year arc as a timeline
5. Five primitives (storage / compute / catalog / governance / observability)
6. Pattern decoder ring table (full slide)
7. MDM — the unsexy foundation
8. **Annotated diagram #1:** storage + access swimlanes lit, rest dimmed
9. Notebook cameo callout (warehouse)
10. Notebook cameo callout (virtualization)

**Block 2 (10–12 slides):**
11. *"What changed when AI ate the stack"* — old vs. new read patterns
12. The RAG reference architecture (Docling → ... → watsonx.ai) — full pipeline diagram
13. Docling deep-dive: structure-aware extraction, OpenShift Operator
14. OpenSearch hybrid retrieval (BM25 + vector + reranker)
15. Vector store decision tree
16. Beyond RAG: context engineering
17. Agent data plane components
18. Open RAG positioning
19. MCP — the integration contract
20. MCP Context Forge — the missing layer
21. **Annotated diagram #2:** AI/ingestion swimlanes lit, with Docling + Context Forge gap callouts

**Block 3 (10–12 slides):**
22. Three governance problems, not one
23. Regulated reality (OSFI B-13, PIPEDA, E-23, SR 11-7)
24. Sovereignty vs. residency vs. operational sovereignty
25. "Sovereignty, not solitude"
26. Data observability — the third leg of the triad
27. The 10-domain agentic governance framework
28. Mapping to a bank's 80-domain questionnaire
29. AI Factsheets and model inventory
30. Why agents change the threat model
31. **Annotated diagram #3:** governance + security + deploy bands lit
32. Where IBM's POV is differentiated

**Block 4 (4–5 slides):**
33. Block 4 setup and BFSI scenario
34. Notebook map — which notebook lights which swimlane
35. (notebooks run from this point — slides minimal)
36. Critique handout slide

**Block 5 (3–4 slides):**
37. The one-slide takeaway
38. Three Monday morning actions
39. Pointers and links
40. Q&A

### Annotated diagram slides

**Approach: SVG generation with Python** (`deck/generate_diagrams.py`)

Recreate the reference architecture diagram programmatically as SVG, then render 4 variants from a single data model. This gives pixel-perfect control, reproducibility, and matches the deck's blueprint aesthetic.

**Script:** `deck/generate_diagrams.py`
**Dependencies:** `svgwrite` (SVG generation), `cairosvg` (SVG → PNG conversion for PPTX embedding)
**Source data:** The diagram structure from `reference/Software Hub 5.2 - Reference Architecture.PDF` (pages 2-3)

**Diagram data model** (derived from the PDF):

The diagram has these swimlanes (left to right, top to bottom):

| Swimlane | Products / Boxes |
|----------|-----------------|
| Data Sources | Machine & Sensor Data, Images & Video, Content Services, Social Data, Internet Data Sets, Weather Data, Commercial Data Sets, Third-Party Data, Transactional Data, Application Data, System of Record Data |
| Data Acquisition & Application Access | (vertical bar, no sub-boxes) |
| Ingestion & Integration | Data Replication, Data Integration, Data Intelligence, Presto (connector), Connectivity |
| Analytical Data Management & Storage — On Software Hub | watsonx.data, Db2, Db2 Warehouse (SMP, MPP), MongoDB, EDB PostgreSQL, Informix |
| Analytical Data Management & Storage — Outside Software Hub | Db2 for z/OS & i, DataStax, Denodo, Dremio, Oracle (& RDS), Teradata, MS SQL Server, MongoDB, PostgreSQL/Netezza, SingleStore, Cloud Object Storage |
| Data Access | Data Virtualization, Apache Spark SQL, Hadoop Execution Engine, Apache Iceberg / Delta Lake / Milvus (connectors), Connectivity |
| Analytics In-Motion | Apache Spark (Streaming), Apache Kafka |
| Discovery & Exploration | IBM Knowledge Catalog (Enterprise Search, Data Catalog, Data Refinery), Watson Studio |
| Actionable Insight | Watson Studio, Watson OpenScale, Watson Machine Learning, Orchestration Pipelines, SPSS Modeler, Decision Optimization, watsonx.ai, Watson AI Services, Cognos Dashboards, Cognos Analytics, Planning Analytics |
| Business Process & Applications | Customer Insights, New Business Models, Planning & Analysis, Compliance & Fraud, Security, Operations |
| Information and Model Management & Governance | Business Glossary, Data Lineage, Metadata Enrichment, Governance Catalog, Data Quality, Model Inventory, Regulatory Accelerators, MDM/Match 360, Data Privacy, Product Master, AI Factsheets, watsonx.ai |
| Security | Pre-integrated stack, user roles, monitoring, industry certifications; IBM Security, Guardium Data Protection |
| Platform | IBM Software Hub (Cloud Pak for Data Platform) |
| Deploy Anywhere | IBM Cloud, AWS, Azure, Google Cloud, On-Premise, Hyper-converged system, Red Hat OpenShift |

**4 output variants:**

1. **Full diagram** (`deck/assets/refarch-full.svg` / `.png`) — all swimlanes at full opacity
2. **Block 1 highlight** (`deck/assets/refarch-block1.svg` / `.png`) — Storage + Access swimlanes lit (Data Sources, Ingestion & Integration, Analytical Data Management & Storage, Data Access). Rest dimmed to 30% opacity.
3. **Block 2 highlight** (`deck/assets/refarch-block2.svg` / `.png`) — AI/ingestion swimlanes lit (Discovery & Exploration, Actionable Insight, Analytics In-Motion). Docling + Context Forge gap callouts added as annotations.
4. **Block 3 highlight** (`deck/assets/refarch-block3.svg` / `.png`) — Governance + Security + Deploy bands lit (Information and Model Management & Governance, Security, Platform, Deploy Anywhere). Rest dimmed.

**Styling** (matches deck design system):
- Background: `#F4F2EC` (paper)
- Swimlane fills: graduated blues (`#0F62FE` IBM Blue for active, `#E8F0FE` for light)
- Text: Calibri/Helvetica for labels, Consolas for product names
- Active lanes: full saturation. Dimmed lanes: 30% opacity overlay.
- Blueprint grid: faint `#E1DCCB` grid lines behind the diagram
- Annotations: `#2D4ADE` accent blue callout boxes for gap callouts (Block 2)

**Integration with PPTX:**
- `generate_diagrams.py` outputs PNGs at 1920×1080 (full slide size)
- `generate_deck.py` places each PNG as a full-bleed slide background image
- Slide chrome (header, footer) overlaid by python-pptx on top of the image

---

## 4. Facilitator guide specification

### File: `facilitator-guide.md`

A separate document for Manav to use while delivering. Sections:

1. **Pre-session checklist** (T-7 days, T-1 day, T-30 min)
   - Lab environment health check
   - Notebook smoke tests
   - Backup recordings ready
   - Critique handouts printed
2. **Block-by-block facilitation notes**
   - For each block: timing markers, what to say, what to skip if running behind
   - Specific lines to deliver verbatim where the punchline matters
   - Anticipated questions and prepared responses
3. **Notebook execution choreography**
   - Which cells to narrate, which to run silently
   - Where to pause for questions
   - What to do if a cell fails live (skip to recorded output)
4. **Critique facilitation script**
   - The bad architecture, with the failures intentionally seeded
   - The list of failures the groups *should* find
   - The list of failures groups usually *miss* — facilitator surfaces these in readout
5. **Q&A bank**
   - 20 anticipated questions with pre-thought answers
   - Three "I don't know, let me come back to you" gracious deflections
6. **Time management cheat sheet**
   - One-page printable: what to cut if 15 min behind, 30 min behind
   - Always-cut-first: Block 1.4 IBM stack mapping; Block 3.5 last 3 min
   - Never-cut: Notebook 6 break-it cell; Block 5 takeaway

---

## 5. Critique handout specification

### File: `handouts/critique.md` (also produce `.pdf`)

One-page handout for the architecture critique exercise. Contents:

- **The scenario:** *"You've been brought in to review the data and AI architecture for HealthFirst Insights, a healthcare analytics startup serving long-term care providers. They're proud of their 'agentic AI platform.' They have one signed customer and are pitching for two more. Read the architecture below. In 10 minutes with your group, identify everything wrong with it. We'll regroup and compare lists."*
- **The architecture (anonymized NaviOwl pattern):**
  - Cosmos DB + Qdrant + SQL Server (three databases, no clear tier separation)
  - Azure OpenAI for ingestion (PHI sent to hyperscaler API directly)
  - Cohere reranker (no eval framework — vendor calls it "vibes-based")
  - Tightly coupled .NET / C# (founder's preference)
  - 80–100 page documents ingested whole, no chunking strategy described
  - Multi-tenancy "planned at DB level" — no tenant isolation today
  - SharePoint integration uses source permissions only
  - Minimal logging, no fallback, hallucination control via prompt only
  - LlamaGuard is "on the roadmap" for PHI protection
  - Sold as "agentic" but is single-shot RAG with no tool use, no planning, no memory
- **Group worksheet** — empty grid for findings: severity (critical / high / medium), category (data, AI, governance, security, ops)
- **Footer:** *"Names and details are anonymized. The pattern is real. Welcome to enterprise AI."*

---

## 6. Take-home self-paced guide

### File: `handouts/self-paced-guide.md`

- Map of all six notebooks and which to run in which order
- Estimated time per notebook (30–45 min each)
- Prerequisites (Docker, Python 3.11+, conda or uv recommended)
- One-liner setup: `make setup` runs the data generator and starts the docker-compose stack
- "If you only have 30 minutes" path: just Notebook 6
- "If you only have 2 hours" path: Notebook 3 + Notebook 6
- Discussion prompts for each notebook (so people can run them as a team study)

---

## 7. Repository structure

```
data-arch-ai-era-lecture/
├── SPEC.md                              # this document
├── README.md                               # for participants and Manav
├── Makefile                                # setup / run / clean / smoke-test
├── docker-compose.yml                      # MinIO, Postgres, Trino, OpenSearch
├── pyproject.toml                          # python deps (use uv or poetry)
├── reference/
│   └── Software_Hub_5_2_-_Reference_Architecture.PDF
├── deck/
│   ├── data-architecture-ai-era.pptx
│   └── assets/
│       ├── annotated-diagram-block1.png
│       ├── annotated-diagram-block2.png
│       └── annotated-diagram-block3.png
├── notebooks/
│   ├── 01-warehouse.ipynb
│   ├── 02-data-lake.ipynb
│   ├── 03-lakehouse.ipynb
│   ├── 04-virtualization.ipynb
│   ├── 05-data-mesh.ipynb
│   └── 06-rag-mdm.ipynb
├── data/
│   ├── README.md
│   ├── generate.py
│   ├── transactions.parquet                # generated, gitignored
│   ├── customers.parquet                   # generated, gitignored
│   ├── branches.parquet                    # generated, gitignored
│   ├── accounts.parquet                    # generated, gitignored
│   ├── policies/                           # generated, gitignored
│   ├── eval/aml_qa_eval.jsonl
│   ├── lineage/lineage_graph.json
│   └── mdm/entity_links.parquet
├── tools/
│   ├── context_forge_local.py              # local proxy for offline Notebook 6
│   └── ollama_stub.py                      # local watsonx.ai stand-in
├── handouts/
│   ├── critique.md
│   ├── critique.pdf
│   └── self-paced-guide.md
├── facilitator-guide.md
└── tests/
    ├── smoke_test.py                       # runs every notebook headless
    └── README.md
```

---

## 8. Key constraints and standing rules (do not violate)

These are persistent rules from Manav's working preferences. They apply across all artifacts.

1. **Light theme PPTX always.** Never dark theme.
2. **No IBM references in non-IBM-branded decks.** This deck IS IBM-branded, so IBM is fine. But do not assume this rule is generally relaxed.
3. **Manav is the sole host of Ship AI podcast** (formerly "Two Guys with AI"). Do not attribute it to anyone else.
4. **Manav's surname is Gupta.** Not Mistry or anything else.
5. **NaviOwl-derived critique example:** anonymize fully. Do not name NaviOwl, Closing the Gap Healthcare, Extendicare, or any real client. The scenario name "HealthFirst Insights" is fictional and intended for the handout.
6. **Project Mantis is excluded** from this lecture. Do not introduce it.
7. **Glasswing/Mythos** can be referenced obliquely as "what Anthropic announced and why it matters" but is not the focus. Do not deep-dive.
8. **IBM is not a Glasswing launch partner.** Do not state or imply otherwise.
9. **Speaker notes:** humorous-yet-authoritative. Manav voice. No corporate-speak.
10. **All quoted statistics must be sourced.** If a stat is in the deck, the source belongs in the speaker notes for that slide.

---

## 9. Decisions log (rejected options noted for context)

- **Audience:** mixed IBM technical (sellers, architects, SSRs). Rejected: ATL-only; consulting-only; new-hire-only.
- **Angle:** mix of foundations → AI-era → enterprise patterns. Rejected: pure foundations; pure AI-era; pure regulated.
- **Format:** lecture + whiteboard + 1–2 hands-on labs + Q&A. Final: lecture + 2 live notebooks + 4 take-home notebooks + critique. The whiteboard exercise was cut because Block 4's critique provides the same engagement function.
- **Examples:** BFSI/Canadian banks. Rejected: vendor-neutral; mixed BFSI+government; generic.
- **Lab level:** lakehouse (Notebook 3) + critique + AI-era (Notebook 6). The original "RAG pipeline" lab was absorbed into Notebook 6.
- **Notebooks:** six total, two live, four take-home. Rejected: three notebooks; one mega-notebook only; no notebooks.
- **Pattern decoder:** five patterns + virtualization added. Rejected: four patterns; three patterns.
- **Five primitives reframe** (storage / compute / catalog / governance / observability). Rejected: four primitives.
- **MDM placement:** dedicated section in Block 1. Originally proposed for Block 3; moved to Block 1 because MDM is foundational.
- **Data observability placement:** Block 3.3 plus mention as fifth primitive in Block 1.2.
- **Docling spelling and identity:** confirmed via web search. Open-source IBM Research toolkit, now in Linux Foundation AAIF, OpenShift Operator targets banks.
- **Context Forge depth:** full lean-in. Manav is a contributor.
- **OpenSearch and Open RAG:** included as Manav requested.
- **Mantis:** excluded per Manav's request.
- **Whiteboard exercise (Block 2.5):** cut to make room for MDM + observability content without exceeding 4h 30m.
- **Reference architecture diagram:** chosen as the anchor for the entire lecture. Three annotated versions used as section dividers.
- **Deliverable format for handoff:** markdown (this file), so it lives in the repo as `SPEC.md` and Claude Code reads it natively. Word doc was rejected because it would need conversion.

---

## 10. Suggested first session prompts for Claude Code

When picking this up in Claude Code, suggested first steps:

1. *"Read SPEC.md and reference/Software_Hub_5_2_-_Reference_Architecture.PDF. Confirm you understand the scope. Then propose a build order with rough effort estimates."*
2. *"Set up the repo skeleton per section 7 of SPEC.md. Initialize git, write the README, the Makefile, the docker-compose.yml, and the pyproject.toml. Stop and show me before generating data or notebooks."*
3. *"Build data/generate.py per section 2 of SPEC.md. Generate the synthetic dataset. Show me a sample of each table and one of the policy PDFs before moving on."*
4. *"Build Notebook 1 (warehouse) per the template in section 2. Show me the full notebook. We'll iterate on the template here, then apply it to the other five."*
5. *"Build Notebook 6 (AI-era end-to-end). This is the headline. Take your time. Use Plan B (local fallback) so it runs without an IBM environment, but structure cells so swapping in real watsonx.data / OpenSearch / Context Forge is a config change."*

---

**End of handoff.**
