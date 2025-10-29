---
type: project-manifest
created: 2025-10-26 15:24
updated: 2025-10-29 08:20
status: active
priority: P0
tags: [project-tracking, priorities, workflow-automation, ci-cd, dual-repo, shipping]
---

# InnerOS Zettelkasten - Project Todo v5.0

**Last Updated**: 2025-10-29 08:20 PDT
**Status**: 🟡 **CI/CD INFRASTRUCTURE ISSUES** - Quality gates working, but billing/deployment strategy needs resolution
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

## 🔴 P0: CI/CD Infrastructure Resolution (This Week)

**Status**: 🟡 **BLOCKED** - Dual-repo strategy in place, but not yet operational

### Current State

- ✅ Private repo: CI working with Ubuntu runners (2000 min/month limit)
- ✅ Public repo: Synced via `scripts/sync-repos.sh`
- ❌ Public repo: CI/CD **NOT configured** (no workflows pushed)
- ❌ Deployment strategy: Unclear

### Issues to Resolve

**1. GitHub Actions Billing Constraints** 🔴

- Private repo limited to 2,000 Ubuntu minutes/month
- Already using Ubuntu (10x cheaper than macOS)
- Risk: Hitting limits with PR-based development

**2. Public Repo CI/CD Not Configured** 🟡

- Public repo has unlimited CI/CD minutes
- Workflows exist in private repo but not synced to public
- Need to decide: Mirror all workflows? Subset?

**3. Deployment Strategy Undefined** 🟡

- Where should PRs be opened? Private? Public? Both?
- Which repo should run expensive CI jobs (coverage, CodeQL)?
- How to handle security scanning on public repo?

### Options

#### Option A: Primary Development on Public Repo (Recommended)

- Move all development to public repo
- Unlimited CI/CD minutes
- Great for portfolio
- Private repo becomes backup/personal notes
- **Action**: Copy all workflows to public, update README, switch development

#### Option B: Dual-PR Workflow

- Open PRs on both repos
- Light CI on private (lint/format only)
- Full CI on public (tests, coverage, security)
- **Action**: Configure public repo workflows, update CONTRIBUTING.md

#### Option C: Stay Private + Add Payment

- Add credit card to GitHub account
- Set spending limit (e.g., $5/month)
- Continue as-is
- **Action**: Update billing settings

### Immediate Tasks (Choose Option First)

- [ ] **DECISION**: Choose Option A, B, or C
- [ ] Update `.github/workflows/` in chosen repo(s)
- [ ] Configure branch protection rules
- [ ] Update CONTRIBUTING.md with CI/CD workflow
- [ ] Test PR workflow end-to-end

**Blocked Until**: CI/CD strategy decision made

---

## 🟡 P1: Ship v0.1.0-beta (After CI/CD Resolution)

**Prerequisites**: P0 CI/CD strategy resolved

### Pre-Beta Checklist

- [ ] CI/CD strategy implemented (Option A/B/C)
- [ ] PR #8 CI checks passing (`chore/repo-hygiene-bundle-and-lifecycle-fixes`)
- [ ] Merge PR #8 to main
- [ ] Tag `v0.1.0-beta -m "Post-beta quality infrastructure + note lifecycle fixes"`
- [ ] Push tag to chosen repo(s)

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
