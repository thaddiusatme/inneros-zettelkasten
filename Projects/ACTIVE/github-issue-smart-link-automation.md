# GitHub Issue: Smart Link Automation

> **Copy this to create a GitHub issue when `gh auth login` is configured**

---

## Title

Smart Link Automation: Implement Vault Corpus Loading

## Labels

`enhancement`, `automation`, `P1`

## Body

### Summary

The Smart Link automation handler passes an empty corpus to `AIConnections.find_similar_notes()`, making it impossible to find similar notes. The manual CLI (`connections_demo.py`) works correctly because it loads the vault corpus.

### Current State

| Component | Status | Issue |
|-----------|--------|-------|
| Manual CLI | ✅ Works | Loads vault with `load_note_corpus()` |
| Automation | ❌ Broken | Passes `note_corpus={}` (empty) |
| Config | ⚠️ Disabled | `enabled: false` in `daemon_test_config.yaml` |

### Root Cause

```python
# feature_handler_utils.py line 218
similar_notes = self.ai_connections.find_similar_notes(
    target_note=note_content,
    note_corpus={},  # Empty corpus - GREEN phase stub
)
```

### Required Changes

**P0: Core Fix**
1. Add `_load_vault_corpus()` method to `SmartLinkEngineIntegrator`
2. Port logic from `connections_demo.py:load_note_corpus()`
3. Pass real corpus to `find_similar_notes()`
4. Enable in config: `smart_link_handler.enabled: true`

**P1: Output Mechanism**
- Log suggestions to `.automation/logs/smart_link_suggestions.log`
- Or queue to `.automation/review_queue/` for user review

**P2: Performance**
- Cache embeddings per file hash
- Incremental corpus updates (only scan changed files)

### Acceptance Criteria

- [ ] SmartLinkEventHandler finds >0 suggestions for notes with related content
- [ ] E2E test validates suggestions are generated
- [ ] Suggestions logged or queued for review
- [ ] Performance: <5 seconds per note processing

### Files to Modify

- `development/src/automation/feature_handler_utils.py` - Add corpus loading
- `.automation/config/daemon_test_config.yaml` - Enable handler
- `development/tests/integration/test_smart_link_workflow_e2e.py` - Add real corpus test

### Related

- **Manifest**: `Projects/ACTIVE/smart-link-automation-manifest.md`
- **Working CLI**: `development/src/cli/connections_demo.py`
- **Discovery**: Sprint "Make InnerOS Usable" Phase 4 Day 2

### Effort Estimate

8-12 hours total (2-3h core fix, 2-3h output, 4-6h performance)

---

## Create Command

```bash
gh issue create \
  --title "Smart Link Automation: Implement Vault Corpus Loading" \
  --label "enhancement,automation,P1" \
  --body-file Projects/ACTIVE/github-issue-smart-link-automation.md
```
