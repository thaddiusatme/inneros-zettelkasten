# START HERE — InnerOS Zettelkasten

**Status**: Simplified to maintained Zettelkasten (May 2026)
**Recovery anchor**: git tag `pre-simplification-v1.0` on `main` holds the previous full-featured system

---

## What this project is

A personal Zettelkasten in `knowledge/` (Obsidian vault), with a small Python toolkit in `development/` for AI-assisted inbox triage and weekly review.

**It is not**: a RAG system, an agent runtime, a YouTube transcript pipeline, a screenshot processor, a multi-user platform, or a web dashboard. All of that lives in `legacy/` and is preserved but not maintained.

---

## Daily loop

1. **Read** — Open `knowledge/` in Obsidian. Browse, link, think.
2. **Capture** — Drop new notes in `knowledge/Inbox/` with frontmatter `type: fleeting`, `status: inbox`.
3. **Review weekly** — Run `python3 development/src/cli/workflow_demo.py knowledge --weekly-review` to get promotion candidates.
4. **Promote** — Move ready notes to `Permanent Notes/` (the directory organizer can help if `type:` and folder are mismatched).
5. **Maintain** — Use the maintenance CLIs (below) sparingly.

---

## Maintenance toolkit (the surviving CLIs)

All paths run from repo root with `PYTHONPATH=development`:

```bash
# Vault overview / analytics
python3 development/src/cli/analytics_demo.py knowledge --interactive

# Generate weekly review (promotion candidates)
python3 development/src/cli/workflow_demo.py knowledge --weekly-review

# Process inbox with AI (auto-tag, quality, link suggestions)
python3 development/src/cli/workflow_demo.py knowledge --process-inbox

# Find semantic connections between notes
python3 development/src/cli/connections_demo.py knowledge

# Summarize a long note
python3 development/src/cli/summarizer_demo.py knowledge

# Fix type/folder mismatches (the "stranded promoted notes" bug)
# See development/src/utils/directory_organizer.py
```

The repo also has a `Makefile` with `make review`, etc. — but verify each target works against current code (some still reference legacy/ paths and will be slimmed in the Phase 6 final sweep).

---

## Vault structure

See `knowledge/CLAUDE.md` for the full assistant-facing guide. Quick version:

| Folder | What lives there |
|---|---|
| `Inbox/` | Staging only. Should stay small (< 30). |
| `Fleeting Notes/` | Quick captures, in-progress thoughts. |
| `Literature Notes/` | Notes ON a source (book, article, video). |
| `Permanent Notes/` | Atomic, evergreen, your own words. |
| `Content Pipeline/` | Drafts and campaign content. |
| `Reviews/` | Daily / weekly / sprint reviews. Includes `Reviews/Daily-Screenshots/`. |
| `Projects/` | Active work and the sprint board. |
| `Archive/` | Retired content. |
| `Media/` | Images, transcripts. |
| `Templates/` | Obsidian Templater templates. |

The invariant: a note's `type:` frontmatter field must match its folder. Anything else is drift.

---

## Repo structure

```
inneros-zettelkasten/
├── knowledge/             # the vault (gitignored except CLAUDE.md)
├── development/           # surviving Python toolkit
│   ├── src/ai/            # tagger, summarizer, connections, enhancer, workflow_manager
│   ├── src/cli/           # 33 CLIs (only ~5 are used regularly; rest to be slimmed)
│   └── src/utils/         # directory_organizer, frontmatter helpers
├── legacy/                # frozen, deprecated subsystems (see legacy/README.md)
├── Projects/
│   ├── ACTIVE/            # current sprint only
│   ├── REFERENCE/         # this file and a few essentials
│   └── Archive/           # everything else
└── README.md              # repo intro
```

---

## Active work

See `Projects/ACTIVE/SIMPLIFICATION-PLAN.md` for the in-flight refactor and `Projects/ACTIVE/SIMPLIFICATION-PHASE-LOG.md` for what's been done.

When the refactor merges, this file becomes the steady-state guide. Any new "what's next" doc should be named `PROJECT-STATUS-<MONTH>.md` and live in `ACTIVE/`. There should never be more than one.

---

## Open questions / known issues

- **Fleeting triage CLI** (`--fleeting-triage`) uses a word-count heuristic that is unreliable for atomic notes. Filed as **#110**.
- **Dead CLI flags** still in `workflow_demo.py` (`--screenshots`, `--evening-screenshots`, `--process-youtube-*`, `--*-safe`, `--*-session`) will fail at runtime — to be removed in Phase 6.
- **Pre-commit pytest** breaks on `legacy/` tests — full test sweep deferred to Phase 6.

---

## Recovery

If you need anything from the pre-simplification era:

```bash
git checkout pre-simplification-v1.0  # full system snapshot
```

Or browse `legacy/` for code that's still in this branch but inert.
