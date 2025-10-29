---
type: project-manifest
created: 2025-10-26 15:24
updated: 2025-10-29 08:20
status: active
priority: P0
tags: [project-tracking, priorities, workflow-automation, ci-cd, dual-repo, shipping]
---

# InnerOS Zettelkasten - Project Todo v5.0

**Last Updated**: 2025-10-29 08:30 PDT
**Status**: ✅ **CI/CD RESOLVED** - Repo now public, unlimited GitHub Actions minutes
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

### Oct 28-29: CI/CD Infrastructure & Dual-Repo Sync

**Duration**: ~3 hours across 2 sessions

**Deliverables**:

- ✅ **Ubuntu CI Switch** (Oct 27): Switched from macOS to Ubuntu runners (conserve free tier: 10x cheaper)
- ✅ **CI Quality Gates** (Oct 27): PR #7 merged - lint, format, type checking in `.github/workflows/ci.yml`
- ✅ **Test Collection Fixes** (Oct 27): Fixed psutil import, 1872 tests now discoverable (was 1788)
- ✅ **Dual-Repo Sync** (Oct 28): `scripts/sync-repos.sh` + git alias `sync-all`
  - Private: `thaddiusatme/inneros-zettelkasten` (billing limits: 2000 min/month Ubuntu)
  - Public: `thaddiusatme/inneros-zettelkasten-public` (unlimited CI/CD)
- ✅ **TDD Workflow v4.0** (Oct 28): Updated `.windsurf/workflows/tdd-git-workflow.md` with CI/CD automation docs
- ✅ **Markdown Linting** (Oct 28): Fixed 30+ MD022/MD032 violations across workflows

**Impact**: CI/CD infrastructure functional, dual-repo strategy in place, documentation updated

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

## 🔴 P0: Ship v0.1.0-beta (Unblocked!)

**Prerequisites**: ✅ CI/CD resolved - repo now public

### Pre-Beta Checklist

- [x] CI/CD strategy implemented (repo made public)
- [ ] PR #8 CI checks passing (`chore/repo-hygiene-bundle-and-lifecycle-fixes`)
- [ ] Merge PR #8 to main
- [ ] Tag `v0.1.0-beta -m "Post-beta quality infrastructure + note lifecycle fixes"`
- [ ] Push tag to public repo

### Post-Beta Improvements

- [ ] Nightly coverage job (GitHub Actions schedule → `make cov` at 07:23 UTC)
- [ ] Enhanced CONTRIBUTING.md (CI/CD workflow, testing requirements)
- [ ] Bug report template (`.github/ISSUE_TEMPLATE/bug_report.md` exists, needs update)
- [ ] Open backlog issues from hygiene plan (P1/P2 items)
- [ ] Link `knowledge-starter-pack/` from README
- [ ] Web UI feature flags for unfinished pages
- [ ] Remove `workflow_demo.py` (ADR-004) + update CLI-REFERENCE
- [ ] Security scanning: CodeQL + Dependabot alerts

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
