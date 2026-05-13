---
title: "Issue #93: Stale PR Triage — Lessons Learned"
created: 2025-02-15
completed: 2025-02-15
issue: 93
type: housekeeping
branch: chore/triage-stale-prs-issue-93
---

# Issue #93: Stale PR Triage — Lessons Learned

## Summary

Triaged and resolved all 13 open PRs in a single session. Zero open PRs remain.

## Results

### Merged (6 PRs)
| PR | Change | Method |
|----|--------|--------|
| #10 | `actions/upload-artifact` v4→v5 | Direct merge |
| #11 | `github/codeql-action` v3→v4 | Direct merge |
| #12 | `actions/setup-python` v5→v6 | Direct merge |
| #14 | `pyyaml` 6.0.2→6.0.3 | Direct merge |
| #16 | `flask` 3.1.0→3.1.2 | Direct merge |
| #15 | `psutil` 5.9.8→7.1.2 | Closed PR, applied manually (merge conflict) |

### Closed with Rationale (7 PRs)
| PR | Reason |
|----|--------|
| #13 | `openai` v1→v2 major bump; only used in 1 file, Ollama is primary |
| #17 | `anthropic` 0.39→0.72; dead dependency (not imported anywhere) |
| #7  | 4mo old, 51 commits, CONFLICTING, superseded by current CI |
| #65 | 2mo old, 77 commits, kitchen-sink branch, impractical to rebase |
| #70 | 2mo old, CONFLICTING; re-implement from clean main (issue #39) |
| #71 | 2mo old, CONFLICTING; re-implement from clean main (issue #67) |
| #74 | 2mo old, CONFLICTING; re-implement from clean main (issue #67) |

## Key Insights

### 1. Batch Dependabot PRs by risk tier
Grouping into GH Actions → safe deps → breaking deps allowed fast, confident merges for the safe ones and thoughtful rejection for the risky ones.

### 2. Sequential requirements.txt merges cause cascading conflicts
PRs #14, #15, #16 all touched `requirements.txt`. After merging #14 and #16, #15 had a conflict. **Fix**: When multiple Dependabot PRs touch the same file, merge them in order and be ready to apply the last one manually.

### 3. Dead dependencies create noise
`anthropic` is pinned in `requirements.txt` but never imported. This generated a Dependabot PR for nothing. **Action**: Remove dead dependencies proactively.

### 4. Kitchen-sink branches are un-mergeable
PRs #7 (51 commits) and #65 (77 commits) accumulated changes across many sessions. By the time they're reviewed, they have massive conflicts and mixed concerns. **Prevention**: Keep PRs small and single-purpose; merge frequently.

### 5. Feature PRs that stall >1 month should be closed
PRs #70, #71, #74 were small and focused but 2 months of drift made them conflict-ridden. The work is better re-done from a clean main. Close stale PRs with good comments so the context isn't lost.

### 6. CI failures on Dependabot PRs were pre-existing
All 8 Dependabot PRs showed CI failures, but these were from the repo's known 53 unit test failures — not from the PR changes. Don't let pre-existing CI noise block safe merges.

## Follow-up Items
- [ ] Remove `anthropic` from `requirements.txt` (dead dependency)
- [ ] Revisit issues #39, #67 — closed PRs #70/#71/#74 may contain useful fixes
- [ ] Consider Dependabot grouping config to reduce PR volume
- [ ] Tackle the 53 pre-existing unit test failures to make CI signal meaningful

## Duration
~30 minutes for full triage of 13 PRs.
