# Architecture Simplification — Team Feedback Request

**Project:** InnerOS Zettelkasten — `development/` module  
**Issue:** #116  
**Date:** 2026-05-12  
**Author:** Thaddius  
**Status:** Design phase — feedback requested before implementation begins

---

## Mission

Build a maintainable, AI-powered Zettelkasten automation layer that a single developer (or small team) can confidently extend, debug, and ship. The system processes personal knowledge notes using local LLMs (Ollama) to generate tags, surface connections, promote notes through a lifecycle, and keep the vault healthy.

---

## Goal of This Refactor

The `development/src/ai/` directory has grown to **~50 Python files** through iterative feature additions. Many files overlap in responsibility, several exist only for backward compatibility, and the CLI has accumulated **34 entry points** — most unused.

**The goal is to collapse this into a clean 8-module structure and a 5-command CLI**, reducing cognitive overhead, eliminating dead code, and making the system testable end-to-end.

**Success looks like:**
- A new contributor can understand the full `ai/` layer in under 30 minutes
- Every module has a clear single responsibility
- The CLI has five obvious commands that cover all real use cases
- Test coverage exists for each of the 8 modules before any code is merged

---

## Current State (Before Refactor)

| Area | Now | Target |
|---|---|---|
| `development/src/ai/` source files | ~50 | 8 modules |
| CLI entry points | 34 | 5 commands |
| Test coverage | Partial, scattered | Full coverage per module (TDD) |
| Legacy code in `legacy/` | Present | Archived or deleted |
| Embedding cache gitignored | Yes (already done) | — |

---

## Execution Plan — 6-Step Sequence

Steps must be completed in order. Each is a discrete, reviewable PR.

### Step 1 — `#117`: Gitignore `.embedding_cache/` ✅ Already done
`.embedding_cache/` was added to `.gitignore` in a prior commit. No cache directories are tracked. **Closed.**

---

### Step 2 — `#118`: Archive / delete `legacy/`
**What:** The `legacy/` directory contains old modules moved during prior simplification phases (YouTube pipeline, dashboards, daemon CLIs, screenshot pipeline). They are no longer imported anywhere in the active codebase.

**Action:** Delete `legacy/` from the repo. Keep the git history as the safety net.

**Risk:** Low. No active code imports from `legacy/`. Confirm with a grep before deletion.

**Feedback requested:**
- Is there anything in `legacy/` worth preserving in a different form before deletion?
- Should we archive to a separate branch instead of deleting?

---

### Step 3 — `#119`: Design the 8 target modules (no code) ✅ Draft complete
**What:** A mapping table and one-line responsibility per module, showing which of the ~50 source files collapses into which target module.

**See:** `development/docs/issue-119-module-design.md` for the full draft.

**The 8 modules:**

| Module | Responsibility |
|---|---|
| `llm_client.py` | Raw Ollama API calls, embedding cache, shared types |
| `enrichment.py` | Per-note AI: tagging, summarization, enhancement, metadata repair |
| `tags.py` | Tag lifecycle: generation, RAG-ready tagging, AI-tag prevention, cleanup |
| `connections.py` | Link graph: semantic discovery, suggestion/insertion, orphan remediation |
| `lifecycle.py` | Note state machine: status transitions, promotion, triage, import |
| `batch.py` | Orchestration: workflow coordination, batch ops, file watching, daily pipeline |
| `analytics.py` | Pure-Python metrics: quality scoring, stale/orphan detection, reporting |
| `media.py` | Atomic image processing, integrity monitoring, rollback |

**Feedback requested:**
- Does the module boundary between `enrichment` and `tags` make sense? (Tags is its own domain because it has prevention logic and RAG-specific concerns.)
- `connections.py` collapses 15 files into 1. Is that too large? Would you split it further (e.g., `connections_discovery.py` + `connections_insertion.py`)?
- Any module name that's too generic or misleading?

---

### Step 4 — `#120`: Collapse `development/src/ai/` → 8 modules
**What:** Write tests first (TDD), then collapse the ~50 files into the 8 modules approved in #119. The public interface of each module is defined by the tests before any implementation is merged.

**Approach:**
1. For each target module, write characterization tests against the existing files.
2. Collapse files into the target module, keeping tests green throughout.
3. Delete the originals.

**Blocked on:** #119 approval  
**Risk:** Medium. This is the largest single change. Mitigated by TDD — tests must be green before each file is deleted.

---

### Step 5 — `#121`: Reduce CLI from 34 → 5 commands
**What:** The 34 CLI entry points map down to five real use cases:

| Command | What it does |
|---|---|
| `process` | Run AI enrichment on one or more notes |
| `triage` | Score and triage fleeting notes |
| `connect` | Find and insert wiki-links |
| `review` | Generate weekly review candidates |
| `repair` | Fix metadata, tags, orphaned notes |

**Blocked on:** #120  
**Risk:** Medium. Some entry points may be used in Make targets or scripts — audit before removing.

**Feedback requested:**
- Do these 5 commands cover your actual workflows? Anything missing?
- Should `repair` be split into `repair-metadata` and `repair-links`?

---

### Step 6 — `#122`: Enforce `development/` isolation (or split into its own repo)
**What:** The `development/` directory houses Python automation tooling that is conceptually separate from the `knowledge/` vault content. Options:

**Option A (Recommended):** Keep in the same repo but enforce strict isolation via `.gitignore`, path rules in CLAUDE.md, and separate `pyproject.toml`.

**Option B:** Split `development/` into its own git repo and reference it as a submodule or external tool.

**Blocked on:** #120, #121  
**Risk:** Low for Option A. Option B is more disruptive but cleaner long-term.

**Feedback requested:**
- Do you prefer same-repo isolation or full repo split?
- Does the team have opinions on monorepo vs. split given this is currently a solo project?

---

## What We Are NOT Doing

- No new features until #116 is closed.
- `#114` (wire LLM triage into CLI) is hard-blocked until #121 ships — it targets files that #120 will eliminate.
- No changes to `knowledge/` vault content as part of this refactor.

---

## What We Need From You

1. **Review the #119 module design** (`development/docs/issue-119-module-design.md`) and flag any boundary decisions you'd draw differently.
2. **Answer the open questions** embedded in each step above.
3. **Flag any workflows** you rely on that touch the 34-entry-point CLI — we want to make sure the 5-command target doesn't break your usage.
4. **Optional:** Review and comment on the GitHub issues (#117–#122) directly.

---

## Timeline Estimate

| Step | Estimate |
|---|---|
| #117 | Done |
| #118 | ~30 min |
| #119 | Design drafted — awaiting approval |
| #120 | 2–4 hours (TDD adds time but prevents regressions) |
| #121 | 1–2 hours |
| #122 | 1 hour (Option A) / 2–3 hours (Option B) |
| **Total remaining** | **~5–10 hours of focused work** |

---

*Questions or comments? Reply to this doc or comment on the GitHub issues.*
