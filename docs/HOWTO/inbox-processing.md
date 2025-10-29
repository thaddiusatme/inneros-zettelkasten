# Inbox Processing

## Purpose
Move raw captures into the vault safely with metadata and links.

## Command or script

```bash
.automation/scripts/supervised_inbox_processing.sh
```

## Steps

1) Stage files in `Inbox/`
2) Run supervised script to classify and tag
3) Review console diff
4) Confirm to apply
