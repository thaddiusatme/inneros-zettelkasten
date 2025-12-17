# GitHub Issue: P1 Smart Link Filtering Improvements

**Title**: P1: Improve Smart Link similarity filtering to reduce false positives

**Labels**: `enhancement`, `P1`, `smart-link`

---

## Problem

Smart Link connection discovery returns surface-level matches that don't reflect true semantic relationships.

### Evidence from Manual Testing (2025-12-03)

Tested `leadership-principles.md` against 513-note corpus:

| Match | Score | Issue |
|-------|-------|-------|
| zettelkasten-entry-logic | 69.3% | ❌ Different domain (note-taking vs leadership) |
| ai-notebook-strategy | 69.0% | ❌ Different domain (AI tools vs leadership) |
| burnout-out-prompts | 66.3% | ✅ Should be HIGHER - shares self-regulation theme |

**Root Cause**: Embedding model matches document structure and vocabulary patterns rather than deep semantic meaning.

---

## Proposed Improvements

### 1. Filter Archive/Backup Duplicates

**Problem**: Results include notes from `Archive/Backups/` paths, inflating connection counts with duplicates.

**Solution**:
- Add path-based filtering in `load_note_corpus()`
- Exclude patterns: `Archive/`, `Backups/`, `.backup`, `*_backup_*`
- Make exclusion patterns configurable

**Files**: `development/src/cli/connections_demo.py`, `development/src/ai/connections.py`

### 2. Boost Notes with Matching Tags

**Problem**: Notes with overlapping tags (e.g., `emotional-intelligence`) should rank higher but currently don't.

**Solution**:
- Extract tags from YAML frontmatter during corpus loading
- Calculate tag overlap score between source and candidate notes
- Combine: `final_score = (embedding_similarity * 0.7) + (tag_overlap * 0.3)`
- Configurable weights

**Files**: `development/src/ai/connections.py`, `development/src/automation/feature_handler_utils.py`

---

## Acceptance Criteria

- [ ] Archive/Backup paths excluded from similarity search by default
- [ ] Tag overlap boosts similarity score for notes with shared tags
- [ ] Configurable exclusion patterns and boost weights
- [ ] Unit tests for new filtering logic
- [ ] Re-run leadership-principles test showing burnout-prompts ranks higher

---

## Context

- **Sprint**: Make InnerOS Usable - Phase 2
- **Related**: Smart Link E2E tests (10/10 passing)
- **Branch**: `feat/phase2-smart-link-workflow-e2e`
- **Discovered during**: Manual demo testing with real vault data

---

## Quick Submit

```bash
# Re-authenticate if needed
gh auth login

# Then create issue
gh issue create \
  --title "P1: Improve Smart Link similarity filtering to reduce false positives" \
  --body-file Projects/ACTIVE/github-issue-smart-link-filtering-p1.md \
  --label "enhancement,P1,smart-link"
```
