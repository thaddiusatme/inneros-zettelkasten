---
type: project-manifest
created: 2025-10-26 15:24
updated: 2025-10-29 08:35
status: active
priority: P1
tags: [project-tracking, priorities, workflow-automation, ci-cd, post-beta]
---

# InnerOS Zettelkasten - Project Todo v5.0

**Last Updated**: 2025-10-29 08:35 PDT
**Status**: ✅ **v0.1.0-beta SHIPPED** - CI/CD resolved, repo public, unlimited minutes
**Scope**: Entire InnerOS (Solopreneur Edition)
**Previous Version**: `project-todo-v4.md` (619 lines archived)

---

## 🎯 Product Vision (Unchanged)

**Core Purpose**: Personal knowledge management tool for a solo developer power user

- CLI-first, local files, safety-first automation
- Teachable and shippable: clear docs, one-command dev, small but real tests
- Closed beta for a few power users without breakage or data loss

---

## 🏗️ Architectural Health

**Status**: ✅ Improving — hygiene bundle applied, CI aligned to Makefile, daemon registry corrected

### Stable

- Safety/backup workflows
- Weekly review analytics
- CI-Lite pattern (ruff/black/pyright/pytest via `make test`)

### In-Flux / Next Refactors

- `WorkflowManager` decomposition (ConnectionManager, AnalyticsCoordinator, PromotionEngine)
- Web UI scope and feature flags

---

## ✅ Recently Completed (Oct 26-29, 2025)

### Oct 28-29: CI/CD Resolution & v0.1.0-beta Ship

**Duration**: ~4 hours across 3 sessions

**Deliverables**:

- ✅ **Ubuntu CI Switch** (Oct 27): Switched from macOS to Ubuntu runners (10x cheaper)
- ✅ **CI Quality Gates** (Oct 27): PR #7 merged - lint, format, type checking
- ✅ **Test Collection Fixes** (Oct 27): Fixed psutil import, 1872 tests discoverable (was 1788)
- ✅ **v0.1.0-beta Shipped** (Oct 28): PR #8 merged, tag pushed
- ✅ **Dual-Repo Sync** (Oct 28): Created `scripts/sync-repos.sh` (superseded Oct 29)
- ✅ **Repo Made Public** (Oct 29): Removed `knowledge/` (473 files), changed visibility to PUBLIC
- ✅ **Unlimited CI/CD** (Oct 29): No more 2,000 min/month limit

**Impact**: v0.1.0-beta shipped, CI/CD unlimited, privacy protected, dual-repo strategy replaced by single public repo

**Note**: Dual-repo strategy (Oct 28) was superseded <24h later by making main repo public.

### Oct 26: Repo Hygiene Bundle

- Makefile (`test`, `cov`, `run`, `ui`)
- CI-Lite calls `make test`
- Daemon registry path fixes (3/3 daemons)
- .gitignore tightened (`.automation/metrics/`, cache|logs|tmp, `reports/`)
- Docs skeleton: ARCHITECTURE, HOWTOs (weekly review, inbox)
- ADRs: 0001 provider policy (local-first), 0002 prompt storage (draft)
- Observability HOWTOs: daemon health (uses AutomationStatusCLI), metrics export (`/api/metrics`)
- Intake persisted: `Projects/ACTIVE/PROJECT-INTAKE.md` (13-point, full InnerOS)

**Impact**: One-command dev, cleaner CI, safer automation visibility, repeatable setup

**See**: `Projects/COMPLETED-2025-10/` for detailed completion docs (180+ files)

---

## ✅ RESOLVED: CI/CD Infrastructure (Oct 29, 2025)

**Status**: ✅ **COMPLETE** - Repo is now public with unlimited CI/CD

### What We Did

1. **Removed `knowledge/` from git** (473 personal files)
   - Files still exist locally for personal use
   - `.gitignore` prevents re-adding
   - No personal/business content in public repo ✅

2. **Made repo public** (Oct 29, 08:30 PDT)
   - Changed `thaddiusatme/inneros-zettelkasten` visibility to PUBLIC
   - Unlocked unlimited GitHub Actions minutes
   - All existing CI workflows now run for free

### Benefits Achieved

- ✅ **Unlimited CI/CD**: No more 2,000 min/month limit
- ✅ **Privacy Protected**: Personal knowledge folder removed
- ✅ **Portfolio Ready**: Public repo showcases development practices
- ✅ **Cost-Free**: All workflows (lint, test, coverage, security) run free

### Current State

- **Repo**: `thaddiusatme/inneros-zettelkasten` → PUBLIC ✅
- **CI Runners**: Ubuntu (all workflows)
- **Monthly Limit**: Unlimited (public repo benefit)
- **Personal Data**: Protected (knowledge/ removed from git)

---

## ✅ SHIPPED: v0.1.0-beta (Oct 28, 2025)

**Status**: ✅ **COMPLETE** - Tag pushed before CI/CD resolution

### What Shipped

- ✅ PR #8 merged (Oct 28, 5:20pm PDT)
- ✅ Tag `v0.1.0-beta` created and pushed (commit 6bb232f)
- ✅ Test infrastructure: 1872 tests, 0 collection errors
- ✅ Note lifecycle fixes included
- ✅ CI quality gates enforced

**Subsequent improvement (Oct 29)**: CI/CD limits removed by making repo public

---

## 🔴 P0: Post-Beta Improvements (Nov 2025)

### ✅ Completed (5/8)

- [x] **Nightly coverage job** - `.github/workflows/nightly-coverage.yml` runs daily at 07:23 UTC
- [x] **Enhanced CONTRIBUTING.md** - Comprehensive 276-line guide with CI/CD, TDD, testing requirements
- [x] **Link knowledge-starter-pack/** - Referenced in README.md lines 37, 78
- [x] **Security scanning: CodeQL** - `.github/workflows/codeql.yml` runs weekly + on PRs
- [x] **Dependabot alerts** - `.github/dependabot.yml` configured (see open PRs #11, #12, #15)

### 🟡 Remaining (3/8)

- [ ] **Bug report template** - `.github/ISSUE_TEMPLATE/bug_report.md` exists but needs post-beta update
- [ ] **Open backlog issues** - No GitHub issues created from hygiene plan P1/P2 items
- [ ] **Web UI feature flags** - No feature flag system in `web_ui/app.py` (7 routes fully exposed)

---

### 📝 Optional/Deferred

- [x] **Remove workflow_demo.py** - ADR-004 completed Oct 11! File deprecated, 10 dedicated CLIs extracted
  - Note: File still exists at `development/src/cli/workflow_demo.py` but all functionality moved to dedicated CLIs
  - CLI-REFERENCE.md still references it in examples (needs update)

---

## 🟡 P1: WorkflowManager Decomposition (Nov 2025)

- [ ] Extract ConnectionManager (~300 LOC)
- [ ] Extract AnalyticsCoordinator (~400 LOC)
- [ ] Extract PromotionEngine (~200 LOC)

Success: Reduced god-class risk; clearer unit boundaries

---

## 🟡 P1: Automation Visibility UX

- [ ] Integrate `AutomationStatusCLI` insights into `./inneros` wrapper or a small TUI
- [ ] Surface daemon health summary in Web UI (read-only)

---

## 🟢 P2: Templates & Evening Screenshots

- [ ] Templater-driven workflow triggers (design + MVP)
- [ ] Extract Evening Screenshots to `evening_screenshots_cli.py` with summary output

---

## 📊 Success Metrics

- Tests: CI-Lite green on PRs; local `make test` < 2 min
- UX: Weekly review runs end-to-end with `--dry-run` + backup; daemon status visible in <5s
- Docs: 2+ HOWTOs discoverable; architecture diagram present
- Release: v0.1.0-beta tagged after PR merge

---

## 🔗 References

- CI: `.github/workflows/ci-lite.yml`
- Docs: `docs/ARCHITECTURE.md`, `docs/HOWTO/*`, `docs/adr/*`
- Observability: `web_ui/app.py` (`/api/metrics`), `development/src/monitoring/*`
- Automation: `.automation/config/daemon_registry.yaml`, `development/src/cli/automation_status_cli.py`
- Intake: `Projects/ACTIVE/PROJECT-INTAKE.md`
