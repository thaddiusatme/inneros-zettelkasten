# How to run a Weekly Review

## Prereqs

- Python 3.11
- Vault path default: `knowledge/`

## Commands

```bash
make run
# or explicitly
PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py weekly-review --format json --dry-run
```

## Outputs

- JSON metrics in `.automation/metrics/weekly/`
- Console summary

## Safety

- Use `--dry-run` first
- Backups in `.automation/backups/` if enabled
