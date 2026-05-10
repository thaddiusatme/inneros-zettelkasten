# Simplification Plan — InnerOS Zettelkasten Repivot

**Created**: 2026-05-10
**Branch**: `refactor/simplify-knowledgebase` (off `main`)
**Supersedes**: `inneros-manifest-v3.md`, `SPRINT-MAKE-IT-USABLE.md`, `PROJECT-STATUS-FEB-2026.md`
**Status**: Plan approved — ready to execute

---

## 1. Repivot Statement

InnerOS is no longer "an AI knowledge platform with RAG, agents, multi-device capture, and a web UI." It is:

> **A well-tended Zettelkasten with AI-augmented inbox triage and weekly review.**

Read-first, capture-second, AI as a *helper for maintenance*, not a feature surface.

---

## 2. North-Star Daily Loop

1. **Read** — Browse notes in Obsidian. Reading experience matters.
2. **Capture** — New notes land in `Inbox/` (any device, any method).
3. **Review** — AI augments inbox notes (auto-tag, quality score, suggested links, triage recommendation).
4. **Promote / Archive** — Weekly review CLI surfaces what to do with each note.
5. **Connect** — Linking happens during promote step.

Anything that doesn't serve this loop gets cut.

---

## 3. What Stays / What Goes

### Stays (the maintenance toolkit)

- **Vault**: `knowledge/` as the Obsidian vault
- **Maintenance CLIs** (all in `development/src/cli/` or kept; we'll prune the rest):
  - `directory_organizer.py` — fix inbox/folder mismatch
  - `workflow_demo.py --process-inbox` — AI augmentation on inbox notes
  - `workflow_demo.py --weekly-review` — weekly promotion candidates
  - `workflow_demo.py --fleeting-triage` — fleeting note health
  - `analytics_demo.py` — vault health metrics
  - `connections_demo.py` — link suggestions (if it still works post-pruning; fix or drop)
- **AI core** (`development/src/ai/`): tagging, quality scoring, summarization, connection discovery — kept because the inbox triage needs them
- **Templates**: `knowledge/Templates/Core/*`, `Templates/Reviews/weekly.md`
- **Content Pipeline** (`knowledge/Content Pipeline/`): kept, but cleaned (see §6)
- **CLAUDE.md** at vault root (assistant guide)
- **Makefile targets**: keep `make status`, `make inbox`, `make review` only

### Goes to `legacy/` (preserved but deprecated)

- Agent RAG: `development/src/ai/agent/`, vector store, embedding service, vault indexer, librarian agent
- YouTube automation: handlers, transcripts daemon, official API integration
- Screenshot pipeline: OneDrive watchers, OCR, daily screenshot rollups
- Quality Scoring epic work (issue #86/#88 lineage)
- Daemons: health monitor, screenshot processor, youtube watcher, agent event handler, smart link daemon
- All web-UI / dashboard prototypes
- `Projects/ACTIVE/inneros-rag-layer-v1-manifest.md`, `gpt-oss-20b-note-feedback-manifest.md`, etc.

### Deleted outright (true clutter)

- `knowledge/knowledge/` (nested empty duplicate)
- `knowledge/Users/thaddius/`, `knowledge/Test-Inbox/`, `knowledge/Untitled/`, `knowledge/temp_workflow_diagrams/`
- `knowledge/scripts/` (code in vault)
- All `*.canvas` files at vault root that are empty (2 bytes)
- `.obsidian-backup-20250805-155425/` (408K)
- All `.bak*` files in `Permanent Notes/` and root
- Loose images at vault root (`ChatGPT Image*.png`, `Pasted image*.png`, UUID png)

---

## 4. Target Vault Structure

```
knowledge/
├── Inbox/                  # staging only, < 30 files steady-state
├── Fleeting Notes/         # quick captures
├── Literature Notes/       # source-based notes
├── Permanent Notes/        # atomic evergreens
├── Reviews/                # daily, weekly, retros (absorbs Reports/)
├── Projects/               # active work only (sprint board)
├── Content Pipeline/       # drafts + campaigns (cleaned, see §6)
├── Archive/                # retired content
├── Media/                  # images, transcripts
├── Templates/              # Obsidian templates
├── CLAUDE.md               # assistant operating guide
├── Home Note.md            # rewritten navigation hub
└── README.md               # how to use this vault
```

Removed from vault: `Clippings/`, `People/`, `attachments/`, `Reports/`, all MOC files at root (merged into `Home Note.md`), `Test-Inbox/`, `temp_workflow_diagrams/`, `Untitled/`, `Users/`, `scripts/`, `perplexity_outputs_real/`, `knowledge/knowledge/`.

---

## 5. Target Repo Structure

```
inneros-zettelkasten/
├── knowledge/              # the vault (see §4)
├── development/            # CLIs + AI core that survive
│   ├── src/cli/            # only the maintenance CLIs
│   ├── src/ai/             # tagging, scoring, summarization, connections
│   ├── src/utils/          # directory_organizer + helpers
│   └── tests/              # tests for the above
├── legacy/                 # everything deprecated (see §3)
│   ├── agent-rag/
│   ├── youtube/
│   ├── screenshots/
│   ├── daemons/
│   └── README.md           # explains what's here and why it's frozen
├── Projects/
│   ├── ACTIVE/             # SIMPLIFICATION-PLAN.md + current sprint only
│   ├── REFERENCE/          # START-HERE.md (the new single source of truth)
│   └── Archive/            # everything else dated
├── .windsurf/              # AI assistant rules (slimmed)
├── .automation/            # only what surviving CLIs need
├── Makefile                # 3 targets: status, inbox, review
├── README.md               # rewritten, paths verified
└── INSTALLATION.md
```

---

## 6. Content Pipeline Cleanup

Current: 126 files across `Content Pipeline/mustaphas-harissa-campaign/`, `Pre-Production/`, `Idea Backlog/`.

Action:

- Keep `Idea Backlog/` if it has live ideas
- Move `mustaphas-harissa-campaign/` to `Archive/Campaigns/` if the campaign is done; otherwise compress its 60+ Perplexity research files into a single `research-notes.md` summary
- Merge `Pre-Production/` content into `Idea Backlog/` or `Projects/` per status
- Target: `Content Pipeline/` < 30 files

---

## 7. In-Flight Work Disposition

### Open PRs

- **#84** (YouTube fix), **#85** (pip-audit security) → merge before the cut (they're harmless and ready)
- **#73** (CI coverage) → close as superseded
- **#74** (LogAggregator) → close, references daemon code we're deprecating

### Open issues

- **#18** (YouTube test failures), **#83** (YouTube prompts) → close as out-of-scope (YouTube → legacy)
- **#22** (Templates/screenshots extract), **#28** (Lifecycle UI), **#104** (daemon health), **#105** (review UI) → close as out-of-scope or convert to a `deferred` milestone for resurrection if/when needed
- **#106, #107, #108** (housekeeping P0/P1/P2) → **keep** — they're the simplification cleanup work

### New issue (this plan)

- Create umbrella issue **"Repivot: simplify to maintained Zettelkasten"** linked to this doc, with #106/107/108 as sub-issues

---

## 8. Execution Sequence (8 phases)

Each phase ends with a commit, a status check, and explicit user approval before proceeding.

### Phase 0 — Pre-flight (no destructive changes)

- [ ] Push current 11 unpushed commits on `main` to `origin/main`
- [ ] Merge ready PRs (#84, #85); close stale PRs (#73, #74)
- [ ] Tag `pre-simplification-v1.0` on `main` as the recovery anchor
- [ ] Create branch `refactor/simplify-knowledgebase`
- [ ] Create umbrella GitHub issue linking this plan; close out-of-scope issues with a comment pointing here

### Phase 1 — Vault P0 cleanup (issue #106)

- [ ] Run directory organizer dry-run on the 124 stranded inbox files
- [ ] Apply moves; verify
- [ ] Delete `.bak*`, empty `.canvas`, root images, empty stray dirs, `.obsidian-backup-*/`
- [ ] Rename `.md.md` → `.md`
- [ ] Commit, close #106

### Phase 2 — Vault P1 cleanup (issue #107)

- [ ] Move 38 `daily-screenshots-*.md` to `Reviews/Daily-Screenshots/`
- [ ] Delete `Test-Inbox/`, `temp_workflow_diagrams/`, `Users/`, `knowledge/knowledge/`
- [ ] Move `scripts/` to `development/scripts/` or delete
- [ ] Move `perplexity_outputs_real/` to `Content Pipeline/mustaphas-harissa-campaign/research/` (then compress in Phase 5)
- [ ] Run fleeting-triage on the 107 Fleeting notes; archive low-quality
- [ ] Commit, close #107

### Phase 3 — Code repivot: move to `legacy/`

- [ ] Create `legacy/` with subdirs per §3
- [ ] Move Agent RAG, YouTube, screenshots, daemons, web-UI prototypes
- [ ] Update Python imports in surviving CLIs to drop legacy dependencies
- [ ] Run surviving test suite; expect breaks, fix only what blocks the maintenance CLIs
- [ ] Delete daemons from `.automation/config/daemon_registry.yaml`
- [ ] Commit

### Phase 4 — Slim the docs

- [ ] Archive `inneros-manifest-v3.md`, `SPRINT-MAKE-IT-USABLE.md`, `PROJECT-STATUS-FEB-2026.md` to `Projects/Archive/2026-05-superseded/`
- [ ] Write `Projects/REFERENCE/START-HERE.md` as the new single source of truth
- [ ] Reduce `Projects/ACTIVE/` to ≤ 5 files (this plan + current sprint)
- [ ] Trim `.windsurf/rules/` — keep `updated-file-organization.md`, `content-standards.md`, `privacy-security.md`; archive automation/monitoring/AI-integration heavy rules
- [ ] Commit

### Phase 5 — Vault P2 (issue #108) + Content Pipeline

- [ ] Normalize frontmatter in `Permanent Notes/` (type/status/folder alignment)
- [ ] Run tag-cleanup tooling dry-run; apply
- [ ] Rewrite `Home Note.md` reflecting today's vault; fold root MOC files into it
- [ ] Clean `Content Pipeline/` per §6
- [ ] Commit, close #108

### Phase 6 — README + Makefile

- [ ] Rewrite `README.md`: 1 paragraph what-it-is, daily loop, 3 commands, links to `START-HERE.md` and `CLAUDE.md`
- [ ] Slim `Makefile` to `status`, `inbox`, `review` targets only; remove daemon/agent targets
- [ ] Verify every command in the README works (CI-able later)
- [ ] Commit

### Phase 7 — Merge & follow-up

- [ ] Open PR: `refactor/simplify-knowledgebase` → `main`
- [ ] Self-review against this plan's exit criteria
- [ ] Merge
- [ ] Tag `simplified-v1.0`
- [ ] Close umbrella issue + remaining housekeeping issues

---

## 9. Exit Criteria

The branch is mergeable when **all** of these are true:

- [ ] Vault `Inbox/` has < 30 files
- [ ] Vault root has only the files listed in §4 (no canvas, no images, no `.bak`)
- [ ] No daemons referenced in `daemon_registry.yaml`
- [ ] `development/` contains only code paths used by the surviving CLIs
- [ ] `legacy/` README explains everything frozen there
- [ ] `Projects/ACTIVE/` has ≤ 5 files
- [ ] `README.md` commands all execute without error
- [ ] A new person can read README + START-HERE in < 10 minutes and know what this project is

---

## 10. Non-Goals (explicit, to prevent scope creep)

- ❌ Building any RAG system
- ❌ Resurrecting screenshots, YouTube, agent, quality scoring during this refactor
- ❌ Adding any new feature
- ❌ Rewriting any AI logic — only pruning
- ❌ Touching `.obsidian/` config beyond what's needed
- ❌ Multi-user / Phase 6 work

If any of these come up mid-refactor, defer to a future issue.

---

## 11. Open Questions (to revisit after Phase 4)

- Does `connections_demo.py` still work after legacy pruning? If not, drop it from the surviving set.
- Is the `quality_score` field worth keeping in frontmatter if the full quality scoring epic is in `legacy/`? Probably yes (the inbox processor still writes it) but verify.
- After cleanup, is the Templates/ directory still using Templater EJS? If Templater plugin is heavy/broken, consider plain markdown templates.

---

*This plan is the new single source of truth for the simplification effort. It supersedes manifest-v3 and the make-it-usable sprint doc on merge.*
