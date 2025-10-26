# Daemon Health

## Purpose

Check automation daemon status, logs, and last runs using the registry.

## Prereqs

- macOS terminal
- Repo root as CWD
- Registry at `.automation/config/daemon_registry.yaml`

## One‑time permissions

```bash
chmod +x .automation/scripts/automated_screenshot_import.sh \
         .automation/scripts/health_monitor.sh
```

## Validate registry schema (tests)

```bash
cd development
pytest tests/unit/cli/test_automation_status_cli.py -q
```

## Quick status snapshot (no code changes)

```bash
PYTHONPATH=development python3 - <<'PY'
from pathlib import Path
from cli.automation_status_cli import AutomationStatusCLI
ws = Path('.').resolve()
reg = ws/'.automation/config/daemon_registry.yaml'
cli = AutomationStatusCLI(reg, ws)
resp = cli.status()
print(cli.formatter.format_summary(resp['daemon_statuses']))
PY
```

## Logs and last run

Tail logs (paths from registry):

```bash
# Update names if you change registry entries
for n in screenshot_processor health_monitor youtube_watcher; do
  log=".automation/logs/${n}.log"; echo "==> $log"; [ -f "$log" ] && tail -n 20 "$log" || echo "(missing)"; echo;
done
```

Check a daemon's last run via CLI helper:

```bash
PYTHONPATH=development python3 - <<'PY'
from pathlib import Path
from cli.automation_status_cli import AutomationStatusCLI
ws = Path('.')
reg = ws/'.automation/config/daemon_registry.yaml'
cli = AutomationStatusCLI(reg, ws)
print(cli.last_run('screenshot_processor'))
PY
```

## Pass criteria

- Status summary prints N/N daemons
- Logs exist under `.automation/logs/`
- No untracked files outside ignored paths
