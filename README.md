# InnerOS Zettelkasten

A personal Zettelkasten in `knowledge/` (Obsidian vault), with a small Python toolkit in `development/` for AI-assisted inbox triage and weekly review.

> **Recovery anchor**: git tag `pre-simplification-v1.0` on `main` holds the previous full-featured system (agents, RAG, daemons, YouTube/screenshot pipelines, web UI).

---

## What this is

| Is | Is not |
| --- | --- |
| A maintained personal knowledge base | A multi-user platform |
| A handful of AI-assisted CLIs that help you triage notes | An autonomous agent runtime |
| Obsidian-friendly Markdown notes with structured frontmatter | A web dashboard / SaaS product |
| Backed up locally and to git | A RAG system, transcript pipeline, or OCR processor |

If you need the deprecated pieces, check out the recovery tag: `git checkout pre-simplification-v1.0`.

---

## Quick start

```bash
# 1. Clone and enter the repo
git clone https://github.com/thaddiusatme/inneros-zettelkasten.git
cd inneros-zettelkasten

# 2. Open knowledge/ in Obsidian
#    File → Open folder as vault → Select the knowledge/ directory

# 3. (Optional) Set up the Python toolkit for AI-assisted maintenance
make setup           # creates .venv and installs requirements
make review          # generate a weekly review preview
make fleeting        # show fleeting-note health
make inbox-safe      # dry-run scan of Inbox/
```

The vault stands on its own — the Python toolkit is optional sugar for inbox triage and weekly review.

---

## Repo layout

```
inneros-zettelkasten/
├── knowledge/          # Obsidian vault (gitignored except CLAUDE.md)
├── development/
│   ├── src/ai/         # tagger, summarizer, connections, enhancer, workflow_manager
│   ├── src/cli/        # surviving CLIs (workflow_demo, analytics_demo, connections_demo, ...)
│   └── src/utils/      # directory_organizer, frontmatter helpers
├── Projects/
│   ├── ACTIVE/         # current sprint (≤ 5 files)
│   ├── REFERENCE/      # START-HERE.md + a few essentials
│   └── Archive/        # everything else
├── Makefile            # 18 targets (vault maintenance + dev)
└── pytest.ini          # scoped to development/tests
```

---

## Daily loop

1. **Capture** — drop new notes in `knowledge/Inbox/` with `type: fleeting`, `status: inbox`.
2. **Read & link** — open `knowledge/` in Obsidian, browse, link, think.
3. **Triage weekly** — `make review` to see promotion candidates; `make fleeting` for fleeting-note health.
4. **Process inbox** — `make inbox-safe` (dry-run) or `make inbox` (apply).
5. **Promote** — move ready notes to `Permanent Notes/` (the directory organizer can fix type/folder mismatches).

The invariant: a note's `type:` frontmatter field must match its folder. Anything else is drift.

---

## Documentation

- **`Projects/REFERENCE/START-HERE.md`** — single source of truth for the project (rewritten 2026-05).
- **`knowledge/CLAUDE.md`** — assistant-facing guide for vault navigation.
- **`CLI-REFERENCE.md`** — every surviving CLI flag, with examples.
- **`INSTALLATION.md`** — detailed setup beyond `make setup`.
- **`CONTRIBUTING.md`** — pull-request guidelines.

---

## Tests

```bash
make test-fast    # CI subset, ~30s
make test-unit    # full unit suite, ~4 min
make cov          # with coverage report
```

Pre-commit pytest is configured to scope to `development/tests/` only.

---

## Recovery

If you need anything from the pre-simplification era:

```bash
git checkout pre-simplification-v1.0   # full-featured snapshot
```

---

**License**: MIT
