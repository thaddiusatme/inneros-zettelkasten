# Quick Add: New Daemon to Registry

**⚡ 2-Minute Guide** | See `DAEMON-REGISTRY-MAINTENANCE.md` for details

## 1. Add Entry to `daemon_registry.yaml`

```yaml
  - name: your_daemon_name          # Lowercase, underscores, unique
    script_path: .automation/scripts/your_script.py
    log_path: .automation/logs/your_daemon_name.log
    pid_file: .automation/logs/your_daemon_name.pid
    description: What this daemon does (present tense, under 80 chars)
```

## 2. Validate

```bash
cd development && pytest tests/unit/cli/test_automation_status_cli.py -k validate -v
```

## 3. Test

```bash
cd development && python3 -c "
from pathlib import Path
from src.cli.automation_status_cli import AutomationStatusCLI
cli = AutomationStatusCLI(
    registry_path=Path('../.automation/config/daemon_registry.yaml'),
    workspace_root=Path('..')
)
print(f'Total: {cli.status()[\"total_daemons\"]} daemons')
"
```

## 4. Commit

```bash
git add .automation/config/daemon_registry.yaml
git commit -m "config: Add [daemon_name] to daemon registry"
```

---

✅ **Done!** Your daemon is now monitored by the automation visibility CLI.
