# Project Instructions

## Spec

**Read `SPEC.md` before starting any new deliverable.** It is the frozen, complete spec for the entire project. Do not re-litigate decisions unless the user explicitly asks.

## Key rules (from SPEC.md §8)

1. Light theme PPTX always. Never dark theme.
2. IBM branding is fine (this is IBM-internal). But do not assume this rule is relaxed for non-IBM decks.
3. Speaker notes: humorous-yet-authoritative, Manav voice. No corporate-speak.
4. All quoted statistics must be sourced in speaker notes.
5. Project Mantis is excluded. Do not introduce it.
6. NaviOwl critique example must be fully anonymized as "HealthFirst Insights."
7. Manav's surname is Gupta. He is the sole host of Ship AI podcast.

Full constraints list: SPEC.md §8.

## Workflow

- Always create a branch + PR for changes. Never commit directly to main.
- Run `ruff check .` and `ruff format --check .` before committing.
- Run `pre-commit run --all-files` to verify all hooks pass.
- Notebooks must follow the 7-section template (see SPEC.md §2).

## Architecture

- Anchor visual: `reference/Software_Hub_5_2_-_Reference_Architecture.PDF`
- Six patterns: Warehouse, Data Lake, Lakehouse, Virtualization, Data Mesh, AI-Era (MDM+RAG)
- Notebook 6 is the headline artifact — most effort there.
- Data Fabric appears in the pattern decoder ring (Block 1.3) but does not have its own notebook.
