# InnerOS Daily Workflow

**Updated**: 2025-12-15

---

## Start of day (30 seconds)

```bash
make up
make status
```

If `make` isn’t available (or you’re debugging), run the underlying CLIs directly:

```bash
PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py daemon start
PYTHONPATH=development python3 development/src/cli/inneros_status_cli.py
```

---

## During the day (capture)

- Put new notes in `knowledge/Inbox/` (or subfolders).
- Screenshots/YouTube workflows may run via automation (depending on what’s enabled).

---

## End of day / quick triage (2–5 minutes)

```bash
make review
make fleeting
```

Manual equivalents:

```bash
PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py --vault knowledge weekly-review --preview
PYTHONPATH=development python3 development/src/cli/fleeting_cli.py --vault knowledge fleeting-health
```

---

## Weekly review (10–20 minutes)

1. Run the weekly review.
2. Export a report if you want to work from a checklist.

```bash
PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py --vault knowledge weekly-review --export review.md
```

---

## Stop automation (optional)

```bash
make down
```

Manual equivalent:

```bash
PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py daemon stop
```
