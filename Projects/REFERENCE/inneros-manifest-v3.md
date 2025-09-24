# InnerOS Zettelkasten – Project Manifest v3.0

**Updated**: 2025-09-18 16:36 PDT  
**Owner**: Thaddius • Assistant: Cascade  
**Source of Truth**: `.windsurf/rules/windsurfrules-v4-concise.md` (v4.0)

---

## 🎯 Vision & Purpose

InnerOS Zettelkasten is a local-first, AI-augmented knowledge system that preserves human decision-making while automating analysis, triage, and connectivity discovery.

Core Promise: "Capture any thought in under 15 seconds, and let AI transform it into connected knowledge that compounds over time."

---

## 🏁 Current State Summary (v3)

- Major foundational systems are production-ready (Phase 5 complete)
- Template System: fixed and validated, unblocking Reading Intake
- Directory Organization P0+P1: production-ready with backup/rollback
- Fleeting Lifecycle (Phase 5.6): health, triage, promotion complete
- Focus now shifts to Phase 6 and system integrity issues

---

## 🚨 Active Priorities

- Image Linking System bug (media preservation during automation)
- Reading Intake Pipeline integration (Phase 5 extension)
- Phase 6 preparation (multi-user + UI)

---

## 🤖 AI Capabilities (Phase 5 Complete)

- Smart Tagging: Context-aware auto-tagging (3-8 tags/note)
- Quality Scoring: 0-1 scale with actionable feedback
- Summarization: Abstractive (AI) + extractive methods, YAML-aware
- Connection Discovery: Embedding-based similarity, link suggestions
- Weekly Review: Candidate identification with rationale
- Enhanced Metrics: Orphaned/stale detection, link density, productivity insights

### Performance Benchmarks

- Summarization: <10s for 1000+ words
- Similarity: <5s per comparison
- Weekly Review: <5s for 100+ notes
- Enhanced Metrics: <5s for 76+ notes
- Connection Mapping: <20s (full network)

### Key CLI Commands

```bash
# Analytics dashboard
python3 src/cli/analytics_demo.py . --interactive

# Workflow management
python3 src/cli/workflow_demo.py . --status --process-inbox --weekly-review --enhanced-metrics

# Connection discovery
python3 src/cli/connections_demo.py .
```

---

## 📁 Information Architecture

### Directory Workflow

| Stage | Directory | Status | AI Features |
|------|-----------|--------|-------------|
| Capture | `Inbox/` | `status: inbox` | Auto-tagging, quality assessment |
| Process | `Fleeting Notes/` | `inbox → promoted` | Semantic analysis, connections |
| Permanent | `Permanent Notes/` | `draft → published` | Summarization, link prediction |
| Archive | `Archive/` | `archived` | Compression, historical analysis |

### Templates (Obsidian Templater)

- `knowledge/Templates/fleeting.md` — quick capture
- `knowledge/Templates/permanent.md` — structured permanent
- `knowledge/Templates/literature.md` — literature/reference
- Rituals: `daily.md`, `weekly-review.md`, `sprint-review.md`, `sprint-retro.md`

Usage:

- Requires Obsidian Templater. EJS syntax is used, e.g., `<% tp.date.now("YYYY-MM-DD HH:mm") %>`
- Starts with `type: fleeting`, `status: inbox`

### YAML Schema (Required)

```yaml
type: permanent | fleeting | literature | MOC
created: YYYY-MM-DD HH:mm
status: inbox | promoted | draft | published | archived
visibility: private | shared | team | public
tags: [kebab-case, hierarchical]
linked_notes: [[note-name]]
quality_score: 0.0-1.0
ai_tags: [auto-generated, contextual]
```

### Reading Intake Extensions

```yaml
source:
  url: https://example.com
  title: "Article Title"
  author: "Author Name"
  published_at: "2025-08-07"
  duration: 540
saved_at: YYYY-MM-DD HH:mm
claims: [key-assertions]
quotes: ["important quotes"]
```

---

## 📚 Reading Intake Pipeline (Phase 5 Extension)

Approach: Integration-first. Leverage existing AI workflows and schema.

- Schema: Extend with `source:` and `saved_at` fields
- Templates: Use updated Templater-ready forms
- CLI: Add import + processing to existing workflow demo
- Performance target: <30s per item triage

Reference: `Projects/reading-intake-integration-analysis.md`

---

## 🚀 Phase 6 Roadmap (Multi-User & UI)

### 6.1 Multi-User Foundations

- Authentication scaffolding; user identity model (local-first)
- Visibility/Audit: per-user actions, share states
- Team workflows: collaborative inbox processing, review queues

### 6.2 API & Integrations

- Read-only REST API for analytics and note metadata
- Mutation endpoints gated by role/visibility (opt-in)
- Webhooks/local events for status transitions

### 6.3 Visualization & Web UI

- Interactive knowledge graph (local web UI) with community detection
- Network metrics (degree, betweenness, clustering)
- Health dashboards: orphaned/stale, AI adoption, productivity

---

## 🔐 Ethics, Privacy & Quality

- Local AI by default; explicit opt-in for external calls
- Non-destructive: backups and dry-run for structural ops
- Visibility respected; logged transitions
- TDD required; 66/66 baseline tests remain passing

---

## 📊 Success Metrics & Status

- Notes processed: 212+ validated
- Test coverage: 66/66 passing; performance targets met
- Connectivity targets: reduce orphaned notes; increase avg links/note

---

## 📝 Decision Log (Newest First)

- 2025-09-18: Directory Organization P0+P1 marked production-ready; Fleeting Lifecycle v1 complete; v3 manifest created
- 2025-09-17: Template Processing System fixed; repair script shipped; Reading Intake unblocked
- 2025-08-10: v2 manifest with connectivity targets

---

Manifest Version: 3.0  
Next Review: 2025-09-25  
Status: Production Ready → Phase 6 Preparation
