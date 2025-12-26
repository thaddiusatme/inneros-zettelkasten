# Project Manifest: InnerOS RAG Layer v1

## Team Announcement

New Project: RAG Layer for InnerOS PKM

Team,

We are adding a new project to InnerOS that will introduce a lightweight Retrieval Augmented Generation (RAG) layer. This will allow the system to pull relevant older notes into our daily content pipeline and future deep dives. This is a strategic upgrade that strengthens the long term value of the PKM system.

This will not be a heavy lift. The scope is intentionally small and fits neatly into the architecture we already have.

### Why We Are Adding RAG

As the InnerOS vault grows, we want to:
- Connect new notes with older relevant notes automatically
- Improve content idea generation by giving the model richer context
- Prevent the 20B model from needing to read hundreds of notes at once
- Enable future features like:
  - "What do I already know about X"
  - "Find similar ideas across my vault"
  - "Link old WFM notes to new ones"
  - Longitudinal insight threads

RAG achieves this by using embeddings to retrieve the top 3 to 10 relevant notes, then passing those to the LLM as context.

This is standard best practice for modern knowledge systems and aligns with our direction.

---

## New Project Manifest

Project: InnerOS RAG Layer v1
Status: Proposed
Owner: Thaddius
Start: 2025 11 29
Goal: Add a minimal Retrieval Augmented Generation layer to InnerOS to support cross note linking and richer content synthesis.

### Problem

The daily content pull pipeline can only see the notes created that day. As the vault grows, important older notes will be left out of idea generation. We need a first pass retrieval system that surfaces older relevant notes without expanding the LLM token budget.

### Outcome

- Each new notes seed summary is embedded.
- Embeddings are stored in a small local index (SQLite or JSON vector store).
- Daily content pull will retrieve 3 to 5 older notes per new note.
- Blender stage will combine todays notes and retrieved notes into better content ideas.

### Success Criteria

- Generated ideas show meaningful cross connections between past and current notes
- Daily jobs remain within 20B token limits
- Retrieval is fast on local hardware
- No impact on the stability of the existing pipeline

### Non Goals (for v1)

- No chunking of long notes
- No hybrid search
- No cross project retrieval modes
- No full RAG agentic workflows

---

## TODO List (v1 Scope)

1. Infrastructure

Choose embedding model
- Default: sentence transformers all MiniLM L6 V2, or a local embedding model

Create vector index storage
- SQLite table: note_id, embedding, metadata (title, tags)

Write EmbeddingsStore module
- Methods:
  - upsert_note_embedding(note_id, embedding, metadata)
  - search_similar(embedding, top_k)

2. Integration with Notes

Add embedding generation to seed_summary pipeline
- Whenever we update a seed summary, embed it

Add metadata fields to notes:
- embedding_last_updated_at

3. Retrieval Integration

Write helper:
- related_notes_for(note_id, top_k=5)

Add retrieval step to Stage 3 of Daily Content Pull
- For each new note:
  - Fetch 3 to 5 older related notes
  - Add to blender input

4. Synthesis and Output

Modify blender call to accept:
- New notes summaries
- Retrieved notes summaries

Guarantee that source_notes field includes both sets

5. Observability

- Log retrieval hits per note
- Log token size of blender call
- Add fallback if embeddings index is empty

6. Documentation

- Write ADR 11: Embeddings and Retrieval Strategy
- Add RAG layer description to InnerOS README
- Add testing plan for embeddings store

---

## Notes for the Team

This RAG v1 is intentionally small and safe:

- No major refactors
- No breaking changes
- No heavy memory requirements
- Easy to expand later

The key goal is to improve the quality and depth of the daily ideas without violating the 20B token constraints. It also gives InnerOS the foundation for more powerful PKM features.

If the team wants, I can also prepare:

- Initial schema for the SQLite embeddings store
- A design sketch for EmbeddingsStore in Python
- CLI commands for rebuilding, searching, and inspecting embeddings

Just let me know.
