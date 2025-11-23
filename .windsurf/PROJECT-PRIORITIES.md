# InnerOS Zettelkasten - Current Priorities

**Last Updated**: 2025-11-19 19:41 PST
**Single Source of Truth**: [GitHub Issues](https://github.com/thaddiusatme/inneros-zettelkasten/issues)

---

## 🎯 Current Sprint (Nov 11 - Nov 18, 2025)

### P0 - Must Do This Week

- **[#21](https://github.com/thaddiusatme/inneros-zettelkasten/issues/21)** Web UI Feature Flags
  - Status: ✅ Completed (feature flags implemented & verified via Web UI + tests)
  - Estimated: 2-3 hours (actual within range)
  - Impact: Production safety (7 routes now gated by flags)

### P1 - High Priority Next

- **[#25](https://github.com/thaddiusatme/inneros-zettelkasten/issues/25)** Inbox Metadata Repair (⚡ Quick Win)
  - Status: ✅ Completed (TDD iteration with real-note fixtures + integration tests)
  - Estimated: 30 minutes
  - Impact: Auto-promotion enabled for previously blocked notes

- **[#39](https://github.com/thaddiusatme/inneros-zettelkasten/issues/39)** Migrate Automation Scripts to Dedicated CLIs
  - Status: In progress (integration testing complete)
  - Estimated: 4-6 hours remaining
  - Impact: Complete CLI architecture migration

- **[#50](https://github.com/thaddiusatme/inneros-zettelkasten/issues/50)** Automation CLI and status UX epic
  - Status: In progress (shared system health and inneros-status implemented)
  - Estimated: 4-8 hours remaining (inneros-up, AI workflow CLIs, Web UI status)
  - Impact: Unifies automation start, health checks, and visibility

- **[#19](https://github.com/thaddiusatme/inneros-zettelkasten/issues/19)** WorkflowManager Decomposition
  - Status: Not started
  - Estimated: 8-12 hours (can be phased)
  - Impact: Reduce god-class technical debt (~812 LOC)

- **[#20](https://github.com/thaddiusatme/inneros-zettelkasten/issues/20)** Automation Visibility UX
  - Status: In progress (shared check_all + CLI; Web UI status pending)
  - Estimated: 3-5 hours remaining
  - Impact: Surface daemon health consistently in CLI and Web UI

- **[#26](https://github.com/thaddiusatme/inneros-zettelkasten/issues/26)** Pre-commit Hooks
  - Status: Iterations 1–2 ✅ Completed (baseline hooks + CI alignment)
  - Estimated: 1-2 hours (initial scope)
  - Impact: Prevent CI failures locally; remaining performance tuning tracked in #48

- **[#48](https://github.com/thaddiusatme/inneros-zettelkasten/issues/48)** Pre-commit all-files run is too slow
  - Status: In progress (config + tests updated; `pytest-unit-fast` moved to push-stage, `make precommit-fast` added)
  - Estimated: 1-2 hours remaining (monitoring + follow-up tweaks)
  - Impact: Keeps pre-commit as a fast CI predictor without full CI runtimes

- **[#27](https://github.com/thaddiusatme/inneros-zettelkasten/issues/27)** pip-audit Security Scanning
  - Status: Not started
  - Estimated: 1 hour
  - Impact: Security hardening

- **[#49](https://github.com/thaddiusatme/inneros-zettelkasten/issues/49)** Developer automation helper script and runbook
  - Status: Not started
  - Estimated: 1-2 hours
  - Impact: Faster onboarding and easier day to day automation use

### P2 - Backlog

- **[#18](https://github.com/thaddiusatme/inneros-zettelkasten/issues/18)** YouTube Integration Architecture (255 test failures)
- **[#22](https://github.com/thaddiusatme/inneros-zettelkasten/issues/22)** Templates & Evening Screenshots
- **[#23](https://github.com/thaddiusatme/inneros-zettelkasten/issues/23)** CLI-REFERENCE.md Update
- **[#28](https://github.com/thaddiusatme/inneros-zettelkasten/issues/28)** Note Lifecycle UI Web Dashboard

---

## ✅ Recent Completions (Nov 1-11, 2025)

### November 9, 2025

- **[#24](https://github.com/thaddiusatme/inneros-zettelkasten/issues/24)** Git Branch Cleanup ✅
  - 129 → 20 branches (84% reduction)
  - **Action Required**: Close issue on GitHub
  
- **[#47](https://github.com/thaddiusatme/inneros-zettelkasten/issues/47)** CLI Syntax Mismatch Bug ✅
  - Fixed in `feat/cli-integration-tests` branch
  - 8 integration tests added
  - **Action Required**: Create PR, close issue

### November 1-4, 2025 - P0 Sprint

- **[#41](https://github.com/thaddiusatme/inneros-zettelkasten/issues/41)** P0-1: WorkflowManager promotion logic (16 tests) ✅
- **[#42](https://github.com/thaddiusatme/inneros-zettelkasten/issues/42)** P0-2: CLI Safe Workflow Utils (14 tests) ✅
- **[#43](https://github.com/thaddiusatme/inneros-zettelkasten/issues/43)** P0-3: Enhanced AI CLI Integration (15 tests) ✅
- **[#44](https://github.com/thaddiusatme/inneros-zettelkasten/issues/44)** P0-4: PromotionEngine return format (5 tests) ✅
- **[#45](https://github.com/thaddiusatme/inneros-zettelkasten/issues/45)** Vault configuration centralization ✅

### October 31, 2025

- **[#29](https://github.com/thaddiusatme/inneros-zettelkasten/issues/29)** YouTube Rate Limiting (global 60s cooldown) ✅
- **[#30](https://github.com/thaddiusatme/inneros-zettelkasten/issues/30)** File Watching Loop Bug ✅

---

## 📊 Project Health

- **Status**: v0.1.0-beta SHIPPED ✅
- **CI/CD**: Unlimited (public repo)
- **Test Suite**: 1,384 passing, 255 YouTube failures (known issue #18)
- **Automation Suite**: 178/178 (100%) ✅
- **Known Blockers**: None

---

## 🔄 Sync Instructions

**For AI Assistants**: At session start, check if GitHub Issues have changed:

1. Run: `gh issue list --limit 20 --json number,title,state,labels`
2. If P0/P1 issues completed or created, suggest updating this file
3. Keep updates minimal - just sprint priorities (top 5-7 issues)

**For Developers**: Update this file when:

- Sprint changes (weekly/bi-weekly)
- P0 priority shifts
- Major milestones completed
- New blocking issues emerge

**Don't track here**:

- Issue progress details (that's in GitHub)
- All issues (just top priorities)
- Historical context (archived in Projects/)

---

**Last Sprint Update**: 2025-10-30 (Initial creation with 11 GitHub issues)
**Next Review**: 2025-11-06 (Weekly sprint planning)
