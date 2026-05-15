# CLAUDE.md — InnerOS Zettelkasten

This is Thaddius's personal Zettelkasten knowledge base, managed in Obsidian. The active working directory is `knowledge/`. All note paths below are relative to `knowledge/`.

## Who This Is For

Thaddius is building **AHS (AI Humble Servant)**, an AI automation business targeting small businesses with a $10K/month MRR goal. The knowledge base supports his:
- Business strategy and client acquisition (Upwork, freelancing)
- AI automation project development
- Content creation pipeline (Threads, Instagram)
- Personal knowledge management

## Directory Structure

```
knowledge/
├── Permanent Notes/        # Evergreen, atomic notes — the core knowledge base
├── Fleeting Notes/         # Quick captures, rough ideas, temporary
├── Content Pipeline/
│   ├── Idea Backlog/       # Raw content ideas (timestamped slugs)
│   ├── Pre-Production/     # Content being developed
│   └── mustaphas-harissa-campaign/  # Client campaign — Moroccan food brand
├── Projects/               # Active project documents
├── Reviews/                # Weekly and daily review notes
├── Archive/                # Deprecated notes, old projects, templates
│   ├── Projects-Archive/
│   └── Templates/
├── People/                 # Notes about people
└── [MOC files]             # Maps of Content at the root level
```

## MOC Navigation (Maps of Content)

Top-level MOCs link the knowledge graph together:
- `AHS MOC.md` — AI Humble Servant business hub (revenue, tools, scaling)
- `Projects MOC.md` — Active and archived projects
- `Career & Entrepreneurship MOC.md` — Freelancing, Upwork, financial planning
- `Concepts MOC.md` — Stub; not yet populated
- `Books MOC.md` — Stub; not yet populated
- `Permanent Notes/Zettelkasten MOC.md` — Knowledge system documentation

## Active Projects & Key Themes

- **AHS Business**: AI automation services for SMBs. Revenue model: $100–1000/month per client via recurring automation (missed-call systems, content pipelines, CRM tagging).
- **Pharmacy Scraper**: `Permanent Notes/Project - Pharmacy Scraper MOC.md` — Technical scraper using Perplexity AI.
- **Freelancing / Upwork**: Client acquisition strategy documented in `Career & Entrepreneurship MOC.md`.
- **Voice-to-Task Pipeline**: Whisper + Make.com + Notion for client async communication (`Async Task Clarity Through AI Voice Parsing.md`).
- **TDD / Vibe Coding**: Development workflow principles scattered across several permanent notes.

## Note Frontmatter Convention

```yaml
---
type: permanent | fleeting | MOC | weekly | daily
created: YYYY-MM-DD
modified: YYYY-MM-DD
status: inbox | draft | published | promoted | archived
visibility: private | public
tags: [tag1, tag2]
---
```

## Note Lifecycle

`Fleeting Notes/` (raw capture) → processed via triage prompt in `Fleeting Note Triage Workflow for Evergreen Note Promotion.md` → `Permanent Notes/` (evergreen) → `Archive/` (deprecated)

Triage criteria: strategic fit, uniqueness, concrete next actions, reusable reference value. Three of four = promote to permanent.

## Known Issues in the Knowledge Base

- Several notes in `Permanent Notes/` still have `status: inbox` — they haven't been fully processed.
- Some notes in `Permanent Notes/` are empty or near-empty (e.g., `TDD Ritual for AI Tools.md`).
- `Concepts MOC.md` and `Books MOC.md` are auto-generated stubs with no real content.
- `Questions about.md` at the root is unclear/junk.
- `Permanent Notes/qr link.md` appears to be a junk note.
- Internal `[[wiki-links]]` reference notes that don't always exist in the `knowledge/` directory (some were moved or renamed).
- **Repo root**: 8 loose `.sh` scripts (`inneros.sh`, `status.sh`, `archive_active_projects.sh`, etc.) have no designated home — candidates for `development/scripts/` or deletion.
- `knowledge/scripts/` — JS Templater helper scripts living inside the vault; should move to repo level.

## Content Pipeline File Naming

Idea Backlog uses: `YYYYMMDD-HHMM-slug.md`
Pre-Production uses: descriptive kebab-case filenames

## Common Tasks Claude May Be Asked to Help With

- Triaging fleeting notes into permanent notes (use the triage prompt in `Fleeting Note Triage Workflow...`)
- Drafting or expanding permanent notes
- Updating or creating MOC links
- Reviewing and improving content pipeline notes
- Identifying orphaned notes or broken wiki-links
- Processing weekly reviews
- Building content for the Mustapha's Harissa campaign or AHS business

## Key Reference Notes

- `Permanent Notes/inbox-processing-guidelines.md` — inbox triage process
- `Permanent Notes/Fleeting Note Triage Workflow for Evergreen Note Promotion.md` — triage prompt and criteria
- `Permanent Notes/bridge-ai-automation-patterns-for-small-business-revenue.md` — core business strategy synthesis
- `Permanent Notes/bridge-content-to-revenue-pipeline-strategy.md` — content-to-revenue strategy

## Obsidian Templater — File Naming Rules

**Never include `.md` in `fname` when calling `tp.file.rename()` or `tp.file.move()`.**

Templater/Obsidian appends `.md` automatically. Passing a name that already ends in `.md` produces double-extension files (`.md.md`). This is invisible at write time — the bug only surfaces when a note is actually created.

```js
// WRONG — produces .md.md
const fname = `lit-${stamp}-${slug}.md`;

// CORRECT
const fname = `lit-${stamp}-${slug}`;
```

When auditing or writing templates, verify that `fname` is extension-free before any `rename` or `move` call. Reference `fleeting.md` and `chatgpt-prompt.md` as correct examples. Fixed in issue #124 (affected: `literature.md`, `permanent.md`, `idea.md`).

## Automation Scripts (Repo-Level)

Located in `../.automation/` and `../development/` (outside `knowledge/`):
- `validate_notes.py` — validates note frontmatter
- `migrate_templates.py` — template migration
- Backups stored in `.automation/backups/`

### Media Audit

Detect broken image embeds and orphaned files in `Media/`:

```bash
cd development && python -m src.utils.media_audit ../knowledge/
```

Output: broken `![[embed]]` refs grouped by folder severity (Permanent Notes → Content Pipeline → Archive), plus orphaned files in `Media/` with no referencing note. Run before any large migration. See issue #123 for the current known-broken list.

## Development Approach — Test Driven Development (TDD)

All code changes in this repo follow a strict TDD cycle. Claude must adhere to this when writing or modifying any Python in `development/`.

### The Cycle

1. **Red** — Write a failing test that defines the expected behavior. Do not write implementation code yet.
2. **Green** — Write the minimal implementation to make the test pass. No extras.
3. **Refactor** — Clean up the implementation without changing behavior. Tests must stay green.

### Rules

- Never write implementation code before a test exists for it.
- Test files live in `development/tests/` and mirror the source structure (e.g., `src/ai/tagger.py` → `tests/ai/test_tagger.py`).
- Each test should cover one behavior. Prefer many small tests over one large test.
- Run `pytest development/tests/` to verify before declaring a task done.
- If a module has no tests, write tests for the existing behavior before refactoring it (characterization tests).
- Mocks are acceptable for Ollama calls and file I/O at unit test boundaries. Integration tests use real fixtures.

### When Designing New Modules (e.g., #119 → #120)

- Draft the public interface (function signatures, class constructors) before writing any implementation.
- Write tests against that interface first.
- The test file is the spec — the implementation must conform to it.

## Active Refactor — Issue #116 (as of 2026-05-14)

A wide-sweeping architecture simplification is in progress. **Do not suggest edits to `development/src/ai/` or `development/src/cli/` outside of this sequence** — those files are being eliminated.

### Revised Direction (2026-05-14)

**Don't collapse dead code — delete it.** Audit found 11 src/ai/ files and 25 src/cli/ files with zero production wiring. Deleted in #133 (2026-05-15). After deletion, the live production chain is: 3 Makefile CLI targets → 4 CLI helpers → workflow_manager + workflow_manager_adapter → ~14 ai modules. Only these live modules get collapsed into the 10-module target.

### Sub-issue Sequence

| Issue | Scope | Status |
|---|---|---|
| #117 | Gitignore `.embedding_cache/` | Done — already in .gitignore, never tracked |
| #118 | Archive/delete `legacy/` | Done — deleted 2026-05-12, recovery at `pre-simplification-v1.0` tag |
| #119 | Design 10 target modules for `development/src/ai/` (no code) | Done — see `development/docs/issue-119-module-design.md` |
| #133 | Eliminate dead-code bloat in `src/ai/` and `src/cli/` before collapsing | **Done (2026-05-15)** — 11 ai + 25 cli + 16 tests deleted, commit `f164745` |
| #120 | Collapse `development/src/ai/` live files → 10 modules | **Next** — 3/10 done (`llm_client.py`, `analytics.py`, `enrichment.py`) |
| #121 | Reduce CLI from 34 entry points → 5 commands + subcommands | Open — blocked on #120 |
| #122 | Same-repo isolation for `development/` (Option A chosen) | Open — blocked on #120, #121 |

### #120 Module Progress

| Module | Status | Notes |
|---|---|---|
| `llm_client.py` | ✅ Done | commit `54208fd` |
| `analytics.py` | ✅ Done | commit `8385321` |
| `enrichment.py` | ✅ Done | commit `e47df7b` |
| `tags.py` | ⏭ Deferred | 8 files, 4681 lines — never wired to any pipeline. Skip until #133 decides fate. |
| `connections_discovery.py` | Pending | |
| `connections_insertion.py` | Pending | |
| `lifecycle.py` | Pending | |
| `batch.py` | Pending | |
| `automation.py` | Pending | |
| `media.py` | Pending | |

### Blocked Work

**#114 (wire LLM triage into CLI)** — do NOT start until #121 is closed. It targets `note_processing_coordinator.py` and `workflow_demo.py`, both of which will be eliminated by #120/#121.
