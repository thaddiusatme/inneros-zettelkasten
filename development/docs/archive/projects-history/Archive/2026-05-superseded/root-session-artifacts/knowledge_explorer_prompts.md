# Knowledge Explorer Prompt Kit (Windsurf/Cascade)

This file is a prompt toolkit for doing exploratory semantic analysis over a large vault without blowing the context window.

The workflow is:

1. Generate a vault census JSON with `knowledge_census.py`
2. Run **Phase 1** to get an overview (clusters, gaps, orphans)
3. Run **Phase 2** to deep-dive into selected clusters by selectively opening notes
4. Run **Phase 3** to generate concrete outputs (MOCs, refactors, backlog items)

---

## Phase 0 — Generate the Census

Command:

```bash
python knowledge_census.py ./knowledge ./knowledge_census.json
```

---

## Phase 1 — Whole-Vault Overview (Census-Only)

Paste this prompt into Windsurf and attach `knowledge_census.json` (or point the agent to it in the repo):

```text
You are helping me analyze an Obsidian/Zettelkasten vault.

Constraints:
- You must NOT read every note.
- First, read ONLY the census JSON file and reason over it.
- Only if needed, propose a small set of targeted notes to open next.

Task:
1) Read `knowledge_census.json`.
2) Summarize the vault into 5-12 thematic clusters (name each cluster).
3) For each cluster, list:
   - Representative notes (paths)
   - Common tags (from frontmatter + body tags)
   - Key terms from first_paragraphs
4) Identify structural gaps:
   - Orphan notes (no incoming/outgoing links)
   - Notes with many unresolved links
   - Sparse clusters (few notes, unclear purpose)
5) Recommend 5-10 candidate deep dives (specific note paths) that would confirm/refine the cluster map.

Output format:
- Clusters section
- Gaps/risks section
- Top deep-dive candidates section
```

---

## Phase 2 — Targeted Deep Dive (Selective Reads)

After Phase 1, run this prompt:

```text
Based on the Phase 1 cluster map, pick ONE cluster that seems:
- high-value OR
- confusing OR
- fragmented OR
- critical for project delivery.

Then:
1) Choose 8-15 note paths from that cluster to open.
2) For each note, extract:
   - What problem it solves / what decision it records
   - Key claims / assumptions
   - Links that imply dependencies (what it builds on)
   - Links that imply follow-ups (what should be created next)
3) Synthesize:
   - A refined cluster definition
   - A list of missing notes that should exist
   - 5-15 concrete next actions (create note / link notes / archive / rename / move)

Rules:
- Keep reads minimal: only open the chosen set.
- Prefer evidence from note content over speculation.

Output format:
- Cluster definition (refined)
- Evidence table (note -> key point)
- Missing notes
- Next actions
```

---

## Phase 3 — Generate MOCs / Roadmaps / Refactors

### Phase 3A — Generate a MOC Draft

```text
Create a MOC (Map of Content) draft for the chosen cluster.

Inputs:
- The cluster's refined definition
- The evidence table

Requirements:
- Use Obsidian wikilinks for key nodes.
- Include sections:
  - Purpose
  - Core concepts
  - Active projects / initiatives
  - Decisions & ADRs
  - Backlog / open questions
  - Related clusters

Output as Markdown.
```

### Phase 3B — Generate a Backlog (GitHub Issues style)

```text
Generate a backlog of 5-20 work items based on the deep dive.

Each item should have:
- Title
- Rationale
- Acceptance criteria
- Suggested location in vault (where note/file should live)

Output as Markdown.
```

---

## Utility Prompts

### Utility 1 — Find Candidate Notes for a Concept

```text
Using ONLY the census JSON, find notes related to this concept:
<CONCEPT>

Return:
- Top 10 note paths (with a short reason)
- The most common tags among them
- Any unresolved links that look related
```

### Utility 2 — Tag Audit (Messy / Duplicate Tags)

```text
Using ONLY the census JSON:
1) List the top 30 tags (frontmatter and body).
2) Identify tags that look synonymous (e.g., ai vs artificial-intelligence).
3) Identify tags that look malformed or low-signal.
4) Recommend a normalization mapping.

Output:
- Stats table
- Proposed merges
- Proposed deletions
- Proposed namespaces (if appropriate)
```

### Utility 3 — Link Integrity Spot Check

```text
Using ONLY the census JSON:
- List notes with the highest `unresolved_links` count.
- For each unresolved link target, propose 1-3 likely intended matches (by stem similarity) from existing notes.
- Recommend whether to create missing notes vs fix links.
```
