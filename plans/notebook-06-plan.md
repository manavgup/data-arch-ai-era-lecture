# Plan: Notebook 6 — MDM + RAG (Headline Artifact) — REVISED

## Context

Notebooks 1-5 each cover a data architecture pattern (warehouse, lake, lakehouse, virtualization, mesh). Every notebook defers Q2: "Find customers whose policy documents reference AML procedure X." NB5 ends with: "Next: Notebook 6 (RAG) — finally answering Q2 with AI." NB5 also exposes the identity resolution problem (different customer IDs across domains). NB6 is the capstone that combines MDM (entity resolution) + RAG (document intelligence) to finally answer Q2.

## Codex Review — Issues Addressed

| # | Codex Finding | Resolution |
|---|--------------|------------|
| 1,3,26 | Q2 is a bait-and-switch; no customer-to-document link in data | **Reframed honestly.** Q2 is now a two-step composition: (a) RAG discovers *which policy rules* reference AML procedure X, (b) MDM + structured query finds *which customers those rules apply to*. The notebook explicitly states this is policy-driven customer identification, not customer-to-document lookup. See Q2 design below. |
| 2 | NB5 already joins on customer_id, undermines identity premise | **Added bridging cell.** New markdown cell explicitly calls out NB5's join was a simulation (all domains shared customer_id). Real banks have different IDs per system. |
| 5 | Eval file has 30 rows, not 31 | **Fixed.** All references now say 30. |
| 7 | Q1 overengineered | **Simplified.** Q1 now just shows the entity-resolved customer_360 view. No forced branch-volume query through MDM. Quick demo of dedup across 176 entities / 500 links. |
| 8 | Lineage section partly fictional | **Made honest.** Q3 traces existing lineage graph edges to customer_360 (7 downstream edges exist). RAG pipeline lineage is presented as "what IBM Knowledge Catalog would track in production" — not pretending it's in the graph. |
| 9,10 | Eval is shallow; target metric arbitrary | **Improved.** Added per-category breakdown (single-doc vs multi-doc). 13 of 30 items are multi-doc. Report Recall@5 separately for each. No predetermined "acceptable range" — just report what we get. |
| 11 | Chunking is naive char-based | **Changed to section-aware.** Docling outputs markdown with headings. Chunk on `## ` / `### ` section boundaries first, fall back to char-split only for sections exceeding max size. |
| 12 | No OpenSearch health check | **Added.** Poll `os_client.cluster.health()` with retry loop (max 30s) before indexing. |
| 13 | Delete-and-recreate index unsafe | **Changed.** Use index name `nb6_policy_docs` (notebook-specific). Create-if-not-exists pattern. |
| 14 | docker compose starts everything | **Noted in setup markdown.** "Only OpenSearch is required for NB6. If other services aren't needed: `docker compose up -d opensearch`" |
| 15 | OpenSearch image unpinned | **Added risk note.** Pin suggestion in configuration cell comment. |
| 16-18 | No error handling for PDF/embedding/indexing | **Added try/except per PDF**, embedding batch validation, and bulk index error count check. |
| 19 | Break 2 hand-picked | **Validate first.** Run the query at implementation time. If MTB-POL-003 isn't actually the right doc, pick a different example based on real eval data. |
| 20 | Plan overstates MDM data | **Toned down.** Notebook says entity_links is pre-computed output. Adjudication/survivorship are described as what Match 360 adds, not what the notebook demonstrates. |
| 21 | Too markdown-heavy (21 md / 15 code) | **Rebalanced.** Merged adjacent markdown cells. Reduced to ~13 md / 16 code. |
| 22 | Plan A is noise unless executable | **Reduced.** Plan A is one line in config cell + one paragraph in S3 header. Not a separate cell. |
| 23 | Assumes internet for model download | **Added pre-flight check cell.** Verifies model is cached or downloadable before proceeding. |
| 24 | Backward link to NB1 is odd | **Changed.** Links to NB5 (predecessor) and a "series complete" note. |
| 25 | Eval multi-doc assumption unproven | **Proven.** 13 of 30 eval items have comma-separated source_docs. Report single-doc vs multi-doc recall separately. |

## Key Design Decisions

1. **No new deps needed.** All libraries in pyproject.toml. First-run needs internet for `all-MiniLM-L6-v2` (~80MB download). Pre-flight check cell added.
2. **RAG chain:** Docling (PDF parsing, section-aware markdown) -> sentence-transformers (`all-MiniLM-L6-v2`, 384-dim) -> OpenSearch (knn vector search).
3. **Filename:** `notebooks/06-rag-mdm.ipynb`
4. **Q2 reframing:** Two-step composition. RAG answers "what does the policy say about AML procedure X?" MDM answers "which customers match those criteria?" This is honest, useful, and demonstrably valuable. The notebook explicitly says we're inferring customer applicability from policy rules, not looking up customer-specific documents.

## Available Data (verified)

- `data/mdm/entity_links.parquet` — 500 rows, 176 unique entities, 4 source systems (115 with 3+ systems, 33 with all 4). All 176 customer_ids join to customers.parquet.
- `data/policies/MTB-POL-001..010.pdf` — 10 AML/KYC/compliance policy PDFs
- `data/eval/aml_qa_eval.jsonl` — **30** Q&A pairs (17 single-doc, 13 multi-doc). All 10 policy docs referenced.
- `data/lineage/lineage_graph.json` — 7 edges downstream from curated.customer_360
- Core parquets: customers (100K), accounts (200K), transactions (1M), branches (50)

## Infrastructure

- OpenSearch 2 on localhost:9200 (docker-compose, security disabled, knn plugin)
- DuckDB in-memory for structured queries
- Only OpenSearch needed for NB6: `docker compose up -d opensearch`

---

## Cell-by-Cell Plan

### Title + Sections 1-2

| Cell | Type | Content |
|------|------|---------|
| 0 | md | Title: "# Notebook 6: MDM + RAG — Document Intelligence with Entity Resolution". Pattern/stack/Maple Trust header. Framing: "Every previous notebook deferred Q2. This one answers it — by combining policy document intelligence (RAG) with entity resolution (MDM)." |
| 1 | md | **Section 1** — one paragraph. MDM solves identity (who): 176 entities resolved across 4 source systems. RAG solves knowledge (what): 10 policy PDFs made searchable. Together: "which policy rules mention AML procedure X, and which customers do those rules apply to?" Explicitly: "This is not a customer-to-document lookup. It is policy-driven customer identification." |
| 2 | md | **Section 2** — Use/Don't Use table (6 rows). |

### Section 3: The Setup (~9 cells)

| Cell | Type | Content |
|------|------|---------|
| 3 | md | Section 3 header. Three phases: (1) load MDM entity links, (2) parse policy PDFs + generate embeddings, (3) index into OpenSearch. One line: "Plan A: IBM Match 360 + Watson Discovery. Plan B (this notebook): pre-computed entity links + Docling + sentence-transformers + OpenSearch." Note: `docker compose up -d opensearch` is sufficient. |
| 4 | code | Configuration + imports. `PLAN = "B"`, OpenSearch host/port, index name `nb6_policy_docs`, embedding model, DATA_DIR. Imports: pandas, duckdb, json, Path, OpenSearch, SentenceTransformer. Comment noting pinned OpenSearch version recommendation. |
| 5 | code | **Pre-flight checks.** (a) Verify OpenSearch reachable with retry loop (max 30s, poll cluster.health). (b) Check if embedding model is cached, warn if download needed. (c) Connect DuckDB. |
| 6 | code | **Load MDM entity links + core data.** Register in DuckDB. Print: 500 links, 176 entities, source system distribution, confidence range. |
| 7 | code | **The identity problem (bridging from NB5).** Print explaining: "NB5's cross-domain join worked because the simulation used the same customer_id everywhere. Real banks don't. Retail: CUST-000001, CRM: CL-MTB-000001, AML: ENT-000001." Then show one entity resolved across 3-4 source systems. Swimlane ref. |
| 8 | code | **Parse 10 PDFs with Docling.** Try/except per PDF. Print per-file section count + char count. Warn about 30-60s runtime. |
| 9 | code | **Section-aware chunking.** Split Docling markdown on `## ` / `### ` heading boundaries. Chunks that exceed 1024 chars get sub-split at 512 with 64 overlap. Each chunk carries metadata: doc_name, section_heading, chunk_id. Print stats. |
| 10 | code | **Generate embeddings.** Encode all chunks. Validate shape matches chunk count. Print dimensions, dtype. |
| 11 | code | **Index into OpenSearch.** Create index `nb6_policy_docs` if not exists (knn mapping, hnsw/cosinesimil/lucene). Bulk index with error count check. Refresh. Print indexed count. |

### Section 4: Three Canonical Queries (~8 cells)

| Cell | Type | Content |
|------|------|---------|
| 12 | md | Section 4 header + swimlane refs. |
| 13 | code | **Q1: Entity-resolved customer_360 view.** Cameo cell. Show: (a) entity count by source_system count (33 with all 4, 115 with 3+), (b) sample entity with all its source-system identities. Key insight print: "Without MDM, this customer appears as 4 different records. Regulatory reports (OSFI, FINTRAC) require consolidated identity." |
| 14 | md | Q2 intro. "This is the question every previous notebook deferred: *Find customers whose policy documents reference AML procedure X.* Here's how we answer it. Step 1: RAG retrieves the policy sections that define AML procedures. Step 2: We extract the customer criteria from those sections. Step 3: MDM + structured query finds matching customers across all source systems." Cameo cell notation. |
| 15 | code | **Q2 Step 1 — RAG retrieval.** Query: "Enhanced Due Diligence procedures for high-risk customers under AML policy". knn search top-5 chunks. Print scores, source docs, section headings, text previews. Show that MTB-POL-005 (EDD) and MTB-POL-001 (AML) surface. |
| 16 | code | **Q2 Step 2 — Extract criteria + find customers.** "The retrieved policy text says: EDD applies to customers with risk_score >= 71 (MTB-POL-005 Section 4)." Query entity_links + customers for matching customers. Print: N unique entities across M source-system records. Show top results with entity_id, name, risk_score, source_systems. |
| 17 | md | Q2 explanation. **Honest framing:** "What just happened: RAG discovered the *rule* (risk_score >= 71 triggers EDD). MDM found the *people* that rule applies to, across all source systems. This is policy-driven customer identification — the bank's compliance policies become queryable knowledge that drives structured-data actions. NB1-NB5 could query the structured data but couldn't read the policies. NB6 closes the loop." |
| 18 | code | **Q3: Lineage.** Trace lineage graph edges into and out of curated.customer_360 (7 downstream edges). Print the real graph. Then: "The RAG pipeline (PDF -> embeddings -> OpenSearch) is not yet in this lineage graph. In production, IBM Knowledge Catalog would track it. Here's what that lineage would look like:" followed by a printed representation. |
| 19 | code | **Q3 continued: RAG provenance.** For the Q2 answer, show which chunks contributed (doc_name, section_heading, score). "This audit trail is what OSFI requires: the bank must prove which policy section drove the compliance action." |

### Section 5: Where This Pattern Breaks (~5 cells)

| Cell | Type | Content |
|------|------|---------|
| 20 | md | Section 5 header. |
| 21 | code | **Break 1: Low-confidence entity matches.** Confidence distribution by match_method. Show links below 0.80. Count how many entities have at least one low-confidence link. Print: "In production, IBM Match 360 queues these for human review. This notebook uses pre-computed links — it cannot demonstrate adjudication or survivorship rules." |
| 22 | code | **Break 2: RAG retrieval quality — full eval.** Run all 30 eval Q&A pairs against the index. For each, check if ANY expected source_doc appears in top-5. Compute Recall@5 separately for single-doc items (17) and multi-doc items (13). Print per-category results + overall. Show the 5 worst failures with question, expected docs, retrieved docs. No predetermined acceptable range — just the numbers. |
| 23 | code | **Break 3: Section-boundary chunking still loses cross-section context.** Pick a multi-doc eval question that spans 3+ policies. Show that top-5 retrieval finds chunks from 1-2 of the expected docs but misses the rest. Print: "Single-vector retrieval finds one relevant section, not all four. Production RAG needs query decomposition, multi-hop retrieval, and re-ranking. Watson Discovery handles this with domain-adapted models." |
| 24 | md | Summary of breaks: "Entity resolution quality depends on match method and confidence thresholds. RAG retrieval degrades on multi-document reasoning and domain-specific jargon. Both need human oversight in production." |

### Sections 6-7 + Cleanup (~4 cells)

| Cell | Type | Content |
|------|------|---------|
| 25 | md | **Section 6:** IBM Stack Mapping table. Note: spans 3 swimlanes. One paragraph: "Our Plan B demo stitched 6 open-source tools together in Python. Plan A (IBM) provides this as a managed, governed, auditable platform. The compliance team cares about the latter. The data scientist loves the former. The architect bridges both." |
| 26 | code | IBM stack mapping print with swimlane refs. |
| 27 | md | **Section 7: BFSI Reality Check.** OSFI B-8 consolidated customer view. FINTRAC all-relationship STRs. Structuring detection needs cross-system identity. RAG over policy docs is the next frontier but needs governance. AI as assistant, not replacement. "OSFI will not accept 'the AI told us' as a defence in a supervisory review." |
| 28 | code | Cleanup: close DuckDB. Summary print. Link: `*Previous: [Notebook 5 — Data Mesh](05-data-mesh.ipynb)* | Series complete.` |

**Total: 29 cells (16 code, 13 markdown)**

---

## Implementation Phases

1. **Create notebook** — write full .ipynb in one pass
2. **Pre-flight** — `docker compose up -d opensearch`, wait for health
3. **Test run** — `jupyter nbconvert --to notebook --execute --inplace notebooks/06-rag-mdm.ipynb`
4. **Fix issues** — likely: chunking edge cases, eval scoring, OpenSearch knn config
5. **Validate Break 2 example** — verify the hand-picked Break 2/3 examples against actual retrieval results

## Verification

1. `docker compose up -d opensearch` + health check passes
2. `jupyter nbconvert --to notebook --execute --inplace notebooks/06-rag-mdm.ipynb` completes without errors
3. Entity links loaded (500 rows, 176 entities)
4. All 10 PDFs parsed (check for empty-text failures)
5. Embeddings generated (shape matches chunk count)
6. Bulk index: indexed count == chunk count, 0 errors
7. Q2 Step 1 retrieves relevant AML/EDD policy chunks
8. Q2 Step 2 returns customers with entity resolution
9. Eval: Recall@5 reported separately for single-doc and multi-doc items
10. No hardcoded counts that could be wrong (30 rows read dynamically, not asserted)

## Risks

- **Docling parsing time:** 30-90s for 10 PDFs. Comment warns about this.
- **Embedding model download:** ~80MB first-run. Pre-flight check cell detects this.
- **OpenSearch knn:** lucene engine should work out of box. Fallback: script_score with cosineSimilarity.
- **Section-aware chunking:** Docling markdown heading format may vary. Test with actual output, fall back to char-split if needed.

## Files to Create/Modify

- **Create:** `notebooks/06-rag-mdm.ipynb`
- **No modifications** to existing files or pyproject.toml
