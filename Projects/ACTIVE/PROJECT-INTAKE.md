# InnerOS Zettelkasten – Project Intake (Solopreneur Edition)

Status: Draft (Scope confirmed: Entire InnerOS)
Date: 2025-10-26

---

## 1) Product and scope
- **Value proposition**: Local‑first, AI‑assisted Zettelkasten that captures, organizes, and connects notes with safety‑first automation.
- **MVP must‑haves**
  - AI‑assisted workflows: inbox processing, weekly review, link suggestions.
  - Safety: timestamped backups, dry‑run, rollback.
  - Dedicated CLIs (ADR‑004) + CI‑Lite gates.
  - Observability: JSON metrics endpoint and reports.
- **Out of scope**: multi‑user auth, hosted cloud backend, advanced RBAC, mobile app.
- **Primary users**: solo operator now; closed beta for power users next.

## 2) Repository map (high level)
- development/ (src, tests, demos). Primary code lives here.
- .automation/ (config, cron, scripts, backups, logs, metrics – gitignored).
- web_ui/ (Flask app + metrics API).
- Projects/ (ACTIVE, REFERENCE, COMPLETED‑YYYY‑MM).
- knowledge/ (private vault, excluded via .gitignore). knowledge-starter-pack/ is public safe sample.
- .github/workflows/ (ci-lite.yml, youtube-integration-tests.yml).

## 3) Architecture overview
- Core modules: `ai/*` (analytics, workflow), `cli/*` (dedicated CLIs), `utils/*` (safety), `monitoring/*` (metrics), `web_ui/*` (Flask UI).
- Boundaries: CLI (primary), Flask API/UI, background automation via `.automation/`.
- Stability: safety/backup and weekly review stable; web UI scope evolving; daemonization patterns in progress.

## 4) Data, configs, secrets
- Stores: Markdown in knowledge/, JSON/CSV exports in gitignored `.automation/metrics/`.
- Configs: CLI args, env vars, YAML in `.automation/config/` (e.g., `daemon_registry.yaml`).
- Secrets: env (`YOUTUBE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`). No secrets in git.

## 5) Models and AI components
- Providers: Default local Ollama (`llama3:latest`). Optional OpenAI/Anthropic when enabled.
- IO: text in → JSON/text suggestions out. Prefer JSON where supported.
- Constraints: VRAM/latency for local; rate/cost for cloud; feature‑flag cloud.
- Prompts: begin storing in `docs/prompts/` (ADR‑0002). Inline prompts remain until migrated.

## 6) Build, run, deploy
- Install: `pip install -r requirements.txt`
- One‑command gates: `make test`
- Coverage: `make cov`
- CLIs: `python3 development/src/cli/weekly_review_cli.py weekly-review`
- Web UI: `python3 web_ui/app.py` (http://localhost:8081)
- Deploy: local‑first. CI‑Lite on PRs. Rollback = git revert + backups.

## 7) Testing and quality gates
- CI‑Lite: ruff (E/F/W, ignore E501), black --check, pyright, unit pytest.
- Local: `make test` mirrors CI. Coverage with `make cov`.
- Known slow/flaky: network/YouTube; keep out of CI‑Lite.

## 8) Observability
- Metrics endpoint: `/api/metrics` via `web_ui/web_metrics_utils.py` + `monitoring/*`.
- Destinations: Flask JSON responses, terminal, files in `.automation/metrics/`.
- Blind spots: daemon crash surfacing, cross‑process error aggregation.

## 9) Security and compliance
- External calls: YouTube API, optional OpenAI/Anthropic, local Ollama HTTP.
- Local filesystem only; API keys via env; `.env` not committed.
- License: MIT; dependencies are standard OSS.

## 10) Performance and costs
- Targets (README): summarization <10s; similarity <5s; weekly review <5s (medium vault).
- Bottlenecks: embedding/similarity, OCR/vision, API quotas.
- Costs: local = $0; cloud = pay‑as‑you‑go behind flags; batch + cache.

## 11) Documentation plan
- Existing: README, INSTALLATION, CLI‑REFERENCE, Projects/REFERENCE, ADR‑004, `.windsurf/rules/`.
- New: ARCHITECTURE.md (Mermaid), HOWTOs (weekly‑review, inbox, daemon‑health, metrics‑export), ADR‑0001/0002, prompts dir.

## 12) Project management
- Next milestones
  - Retire legacy `workflow_demo.py` (ADR‑004); enforce dedicated CLIs.
  - Automation hardening: daemon registry coverage + surface health in UI.
  - Evening screenshots integration polish + metrics.
- DoD: tests passing (CI‑Lite), docs updated, safety (backup/dry‑run), observability (JSON output/metrics), daemon registered where relevant.
- Labels: type:feature/bug, area:cli/ui/automation, priority:p0‑p2, status:blocked/ready.

## 13) Risks and decisions
- Top risks: link integrity during moves; template token leaks; daemon visibility; provider lock‑in.
- ADR needs: default AI provider (ADR‑0001), prompt storage (ADR‑0002), UI scope and metrics retention.
- Deprecations: remove `workflow_demo.py`; consolidate generated artifacts under gitignored locations.

---

## Exact commands
```bash
# Install
pip install -r requirements.txt

# Lint/format/type (included in make test)
ruff check development/src development/tests --select=E,F,W --ignore=E501
black --check development/src development/tests
pyright development/src || true

# Tests
make test
make cov

# Batch inbox processing
make inbox-safe  # dry-run (no changes); uses VAULT=knowledge by default
make inbox       # process eligible $(VAULT)/Inbox/*.md notes

# Web UI
python3 web_ui/app.py  # http://localhost:8081
```

## Validation checklist
- make test exits 0
- Coverage prints a report
- UI serves at http://localhost:8081
- No untracked files outside ignored paths
