# Issue #119 — Target Module Design for `development/src/ai/`

**Status:** Revised — incorporating team feedback (2026-05-12). Ready for final approval before #120 begins.  
**Scope:** Map ~50 source files in `development/src/ai/` into 10 target modules (no code changes)

> **Change from initial draft:** `connections.py` split into `connections_discovery.py` + `connections_insertion.py` per team feedback (different test surfaces, different failure modes). `batch.py` split into `batch.py` (user-invoked ops) + `automation.py` (file watching + scheduled pipeline). Total modules: 8 → 10.

---

## Module Map (Revised)

| # | Target Module | Responsibility | Files In |
|---|---|---|---|
| 1 | `llm_client.py` | Raw Ollama API calls, embedding cache, shared type aliases | 3 |
| 2 | `enrichment.py` | Per-note AI: tagging, summarization, content enhancement, metadata repair | 5 |
| 3 | `tags.py` | Tag lifecycle: generation, RAG-ready tagging, AI-tag prevention, cleanup | 8 |
| 4 | `connections_discovery.py` | Semantic graph: embedding similarity, scored candidate ranking, in-memory model | 8 |
| 5 | `connections_insertion.py` | Filesystem mutations: write wiki-links, preserve backlinks, rollback, orphan remediation | 7 |
| 6 | `lifecycle.py` | Note state machine: status transitions, promotion, triage, import/validation | 7 |
| 7 | `batch.py` | User-invoked orchestration: workflow coordination, batch processing, reporting | 8 |
| 8 | `automation.py` | Daemon concerns: file watching, daily pipeline, scheduled triggers | 2 |
| 9 | `analytics.py` | Pure-Python metrics: quality scoring, stale/orphan detection, vault analytics | 3 |
| 10 | `media.py` | Atomic image processing, integrity monitoring, rollback | 5 |

**Total source files: 56** (all accounted for, excludes `__init__.py`)

---

## Module Details

### 1. `llm_client.py` (3 files)
Thin wrapper over Ollama HTTP API. No business logic. Every other module that needs LLM calls imports from here — nothing imports from `enrichment` or `tags` to get an LLM handle.

| Source File | Role |
|---|---|
| `ollama_client.py` | Ollama REST client, health check, model selection |
| `embedding_cache.py` | Disk-backed embedding cache (avoids re-embedding identical content) |
| `types.py` | Shared type aliases (`AnalyticsResult`, `WorkflowResult`, etc.) |

---

### 2. `enrichment.py` (5 files)
Per-note AI enhancement pipeline. Takes a note path, returns enriched frontmatter/content.

**Import boundary:** imports from `llm_client` and `tags`. Does NOT import from `connections_*`. Does NOT import from `tags` — both `enrichment` and `tags` import independently from `llm_client` to avoid circular deps.

| Source File | Role |
|---|---|
| `tagger.py` | LLM-powered tag generation (`AITagger`) |
| `summarizer.py` | LLM-powered summarization (`AISummarizer`) |
| `enhancer.py` | Content quality assessment and improvement suggestions (`AIEnhancer`) |
| `ai_enhancement_manager.py` | Orchestrates tagger + summarizer with 3-tier LLM fallback |
| `metadata_repair_engine.py` | Repairs malformed frontmatter fields |

---

### 3. `tags.py` (8 files)
Tag domain: generation strategies, quality enforcement, RAG-readiness, bulk cleanup. Tag prevention logic (blocking AI-style tags) lives here, not in enrichment.

**Import boundary:** imports from `llm_client` only. Does NOT import from `enrichment` (circular dep risk flagged by team).

| Source File | Role |
|---|---|
| `advanced_tag_enhancement.py` | `SmartTagEnhancer`, `TagSuggestionGenerator` core logic |
| `advanced_tag_enhancement_utils.py` | Support utilities for above |
| `ai_tagging_prevention.py` | Detects and blocks AI-style tag patterns |
| `ai_tagging_prevention_utils.py` | Support utilities for above |
| `rag_ready_tag_engine.py` | Generates RAG-optimized tags for retrieval |
| `rag_tag_utils.py` | Support utilities for RAG tag engine |
| `enhanced_ai_features.py` | `EnhancedSuggestionEngine`, `QualityScoringRecalibrator` (tag-specific) |
| `enhanced_ai_tag_cleanup_deployment.py` | Deployment wrapper for bulk tag cleanup runs |

---

### 4. `connections_discovery.py` (8 files)
**Pure compute — no filesystem writes.** Builds the semantic similarity graph, scores candidates, returns ranked suggestions. Test surface is pure functions against an in-memory model; no I/O mocking needed.

| Source File | Role |
|---|---|
| `connections.py` | Core `AIConnections` class — embedding similarity, connection scoring |
| `connection_manager.py` | Higher-level discovery management with config |
| `connection_coordinator.py` | Coordinates the discovery workflow |
| `enhanced_connections.py` | Enhanced variant of `AIConnections` |
| `enhanced_connection_utils.py` | Utilities for enhanced connection scoring |
| `link_suggestion_engine.py` | Generates ranked link suggestions for a note |
| `link_suggestion_utils.py` | Support utilities for suggestion engine |
| `suggestion_utils.py` | Generic suggestion utilities shared across engines |

---

### 5. `connections_insertion.py` (7 files)
**Filesystem I/O with rollback.** Takes suggestions from `connections_discovery` and writes them into note files. Preserves `[[wiki-links]]`, handles backlinks, supports dry-run. Test surface requires file fixtures and rollback assertions.

| Source File | Role |
|---|---|
| `link_insertion_engine.py` | Writes wiki-links into note bodies |
| `link_insertion_utils.py` | Support utilities for link insertion |
| `end_to_end_link_processor.py` | Full pipeline: suggest → insert → validate |
| `real_connection_integration_engine.py` | Integration engine against real vault notes |
| `real_note_connection_processor.py` | Processes connections against actual vault notes |
| `connection_integration_utils.py` | Integration helpers for connection pipeline |
| `orphan_remediation_coordinator.py` | Detects orphaned notes, inserts bidirectional links to fix them |

---

### 6. `lifecycle.py` (7 files)
Note state machine: `inbox → processed → promoted → archived`. Also handles import because import is the entry point to the lifecycle — kept together, but the module docstring will explain the grouping explicitly (per team feedback).

| Source File | Role |
|---|---|
| `note_lifecycle_manager.py` | Status transitions with validation and timestamps |
| `promotion_engine.py` | Promotes notes between directories by quality threshold |
| `fleeting_note_coordinator.py` | Coordinates fleeting note operations |
| `fleeting_analysis_coordinator.py` | AI-powered analysis of fleeting notes for triage |
| `review_triage_coordinator.py` | Weekly review candidate scanning + fleeting triage |
| `import_manager.py` | CSV import adapter — entry point to the lifecycle (`CSVImportAdapter`) |
| `import_schema.py` | `ImportItem` schema + row validation |

---

### 7. `batch.py` (8 files)
**User-invoked orchestration only.** Drives multi-note workflows when a human (or CLI command) kicks them off. Does not own the event loop — that belongs to `automation.py`.

| Source File | Role |
|---|---|
| `core_workflow_manager.py` | Top-level orchestrator: coordinates Analytics, Enrichment, Connections |
| `workflow_manager.py` | Integrates all AI features end-to-end |
| `workflow_manager_adapter.py` | Backward-compat adapter — evaluate for deletion during #120 |
| `workflow_integration_utils.py` | Shared utilities for workflow integration |
| `workflow_reporting_coordinator.py` | Generates workflow run reports |
| `batch_inbox_processor.py` | Processes inbox notes in batch |
| `batch_processing_coordinator.py` | Coordinates batch operations across note sets |
| `note_processing_coordinator.py` | Per-note processing coordination — #121 CLI target, likely deleted there |

---

### 8. `automation.py` (2 files)
**Daemon concerns only.** Long-running file watcher and scheduled daily pipeline trigger. Calls into `batch.py` for the actual work — does not contain processing logic itself.

| Source File | Role |
|---|---|
| `auto_processor.py` | File watcher (`watchdog`) + automatic processing trigger |
| `daily_content_pull.py` | ADR-010 Stage 0: selects notes modified in last 24h for daily pipeline |

---

### 9. `analytics.py` (3 files)
Pure metrics — no AI calls in the core manager. Safe to run cheaply at any time without Ollama running.

| Source File | Role |
|---|---|
| `analytics.py` | Vault-wide analytics with optional matplotlib/networkx visualization |
| `analytics_manager.py` | Pure-Python quality scoring, orphan/stale detection, review candidates |
| `analytics_coordinator.py` | Coordinates analytics workflow steps |

---

### 10. `media.py` (5 files)
Atomic image operations with guaranteed rollback. Fully isolated from the note AI pipeline.

| Source File | Role |
|---|---|
| `safe_image_processor.py` | Atomic image ops with session management (`SafeImageProcessor`) |
| `safe_image_processor_utils.py` | `ImageBackupManager`, `AtomicOperationEngine`, `ImageExtractor`, etc. |
| `safe_image_processing_coordinator.py` | Coordinates safe image processing workflow |
| `image_integrity_monitor.py` | Monitors image integrity post-processing |
| `image_integrity_utils.py` | Support utilities for integrity checks |

---

## File Count Verification

| Module | Count |
|---|---|
| `llm_client.py` | 3 |
| `enrichment.py` | 5 |
| `tags.py` | 8 |
| `connections_discovery.py` | 8 |
| `connections_insertion.py` | 7 |
| `lifecycle.py` | 7 |
| `batch.py` | 8 |
| `automation.py` | 2 |
| `analytics.py` | 3 |
| `media.py` | 5 |
| **Total** | **56** |

---

## Import Dependency Rules

These rules prevent circular imports and keep the layer cake clean:

```
llm_client      ← no internal imports (base layer)
analytics       ← llm_client (optional, for AI-assisted analysis)
tags            ← llm_client only (NOT enrichment)
enrichment      ← llm_client only (NOT tags)
connections_discovery  ← llm_client
connections_insertion  ← connections_discovery (reads suggestions, writes files)
lifecycle       ← enrichment, tags (for quality-gated promotion)
batch           ← all of the above
automation      ← batch only
media           ← llm_client (optional)
```

---

## CLI Impact (#121 Preview)

Per team feedback, `repair` becomes a subcommand group using the `git`/`kubectl` pattern:

| Command | Maps to |
|---|---|
| `process <path>` | `batch.py` — run enrichment on one or more notes |
| `triage` | `lifecycle.py` — score and triage fleeting notes |
| `connect` | `connections_discovery` + `connections_insertion` — find and insert wiki-links |
| `review` | `analytics.py` + `lifecycle.py` — generate weekly review candidates |
| `repair metadata` | `enrichment.py` — fix malformed frontmatter |
| `repair links` | `connections_insertion.py` — fix broken/missing wiki-links |
| `repair orphans` | `connections_insertion.py` — remediate orphaned notes |

Help text for `process` vs `triage` must explicitly state: **`process` enriches content (tags, summary, enhancement); `triage` scores and routes fleeting notes by lifecycle stage.**

---

## Pre-#120 Checklist (from team feedback)

Before writing any characterization tests, do a per-file TODO/issue scan to avoid green-locking known bugs:

- [ ] Grep each source file for `TODO`, `FIXME`, `HACK`, `XXX`
- [ ] Cross-reference any open GitHub issues that name specific files in `src/ai/`
- [ ] Flag `workflow_manager_adapter.py` for deletion evaluation (not collapse)
- [ ] Confirm `pre-simplification-v1.0` git tag exists before #118 `rm -rf legacy/`
- [ ] Grep for `workflow_demo.py` across: `Makefile`, CI config, shell scripts, `.windsurf/`, `README.md`, `CLAUDE.md`, ADRs

---

## Revised Timeline Estimate

Per team feedback, the original 2–4 hour estimate for #120 was optimistic.

| Step | Revised Estimate |
|---|---|
| #118 — delete `legacy/` | 1 hour (audit + delete) |
| #119 — design approval | ~0 (this doc) |
| #120 — collapse 56 → 10 (TDD) | 8–12 hours |
| #121 — CLI 34 → 5+subcommands | 2–3 hours |
| #122 — repo isolation (Option A) | 1 hour |
| **Total remaining** | **12–17 hours** |
