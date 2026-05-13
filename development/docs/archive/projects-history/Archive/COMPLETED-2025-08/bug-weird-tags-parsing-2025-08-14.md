# Bug: Tag parsing/normalization produces stray tokens and malformed metadata

- Status: Open
- Priority: High
- Reported: 2025-08-14 17:46 (local)
- Area: Workflow CLI weekly review, tag extraction/normalization, metadata repair
- Related: templates timestamp fix, metadata repair scripts

## Summary
Tags in some notes are being parsed/generated as stray single-character tokens and punctuation (e.g., "", " ", "-", "/", digits), and malformed metadata keys appear (e.g., `"{ date": "YYYY-MM-DD HH:mm }":`). This indicates issues in tag extraction/normalization and legacy frontmatter cleanup.

## Impact
- Pollutes tag taxonomy, harms analytics and recommendations
- Breaks metadata schema expectations (kebab-case tags)
- Increases noise in weekly review and quality scoring

## Evidence
Observed via weekly review dry-run JSON (`.venv/bin/python development/src/cli/workflow_demo.py . --weekly-review --dry-run --format json`):

```json
{
  "tags": ["", " ", "-", "/", "0", "2", "8", "contact-information"],
  "metadata": {
    "type": "literature",
    "created": "",
    "status": "inbox",
    "tags": ["", " ", "-", "/", "0", "2", "8", "contact-information"],
    "ai_processed": "2025-08-14T17:39:12.478777",
    "\"{ date": "YYYY-MM-DD HH:mm }\":",  
    "visibility": "private"
  }
}
```

Also observed legacy placeholder `created: {{date:YYYY-MM-DD HH:mm}}` present in some notes.

## Suspected Causes
- Legacy template placeholders and malformed YAML previously written into frontmatter
- Tag extraction/tokenization admitting empty strings, punctuation, and single-character tokens
- Repair script treating non-list `tags` or malformed strings too permissively

## Scope
- Affects subset of Inbox/Fleeting notes scanned during weekly review (13 candidates; several with malformed tags)

## Steps to Reproduce
1. Run: `.venv/bin/python development/src/cli/workflow_demo.py . --weekly-review --dry-run --format json`
2. Inspect recommendations[].metadata.tags for stray tokens

## Expected vs Actual
- Expected: tags are normalized kebab-case strings, length >= 2, free of whitespace/punctuation-only entries
- Actual: tags include empty strings, punctuation, digits-only tokens, and stray YAML remnants

## Proposed Fix
- Implement centralized tag normalization and filtering:
  - Trim whitespace; lowercase; kebab-case conversion
  - Drop empty entries; drop tokens that are punctuation-only or digits-only
  - Enforce regex: `^[a-z0-9][a-z0-9-]*$` (min length 2) with allowlist for known short tags if needed
- Update AI tag extraction path in `WorkflowManager.process_inbox_note()` to use sanitizer
- Harden `.automation/scripts/repair_metadata.py` to:
  - Parse non-list `tags` safely; split on commas/newlines; sanitize with same rules
  - Remove invalid/malformed keys that leaked from old templates
  - Ensure `created` is `YYYY-MM-DD HH:mm` or repaired to a valid timestamp
- Add unit tests:
  - Sanitizer behavior for edge cases (empty, punctuation, digits)
  - Repair script transforms malformed tags into clean sets
  - Weekly review output contains only valid tags

## Acceptance Criteria
- Weekly review JSON contains only normalized tags (no empty/punctuation/digits-only)
- Validator passes for affected notes after repair (no malformed keys)
- Performance unchanged (<5s for 100+ notes)

## Action Items
- [ ] Add tag_sanitize() utility and apply in WorkflowManager processing
- [ ] Enhance repair_metadata.py to normalize tags and scrub malformed keys
- [ ] Write tests (unit + CLI) covering malformed tags and legacy placeholders
- [ ] Run repair (dry-run, then apply) on Inbox and Fleeting Notes
- [ ] Verify weekly review dry-run outputs clean tags

## Notes
- Templates have been fixed to use Templater timestamp; remaining malformed data likely from older notes.
