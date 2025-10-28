# Backlink Preservation During File Moves

## Overview

InnerOS uses Obsidian-style wiki-link syntax (`[[note-title]]`) which is **title-based, not path-based**. This means links are preserved automatically when files move between directories.

## How Wiki-Links Work

### ✅ Safe File Moves
When a note moves from `Inbox/my-note.md` to `Permanent Notes/my-note.md`:

**Before move:**
```markdown
<!-- In another-note.md -->
See related concept in [[my-note]]
```

**After move:**
```markdown
<!-- Links still work! -->
See related concept in [[my-note]]
```

The link continues to work because:
1. Filename remains: `my-note.md`
2. Wiki-links match on filename, not path
3. No backlink updates needed

### Link Formats Supported

| Format | Example | Path-Sensitive? | Auto-Preserved? |
|--------|---------|-----------------|-----------------|
| Wiki-link | `[[note-title]]` | ❌ No | ✅ Yes |
| Wiki-link with alias | `[[note-title\|Alias]]` | ❌ No | ✅ Yes |
| Wiki-link with heading | `[[note-title#Section]]` | ❌ No | ✅ Yes |
| Image embed | `![[image.png]]` | ❌ No | ✅ Yes |
| Markdown link | `[Link](../path/file.md)` | ✅ Yes | ❌ No |

## NoteLifecycleManager Guarantees

When using `NoteLifecycleManager.promote_note()`:

1. ✅ **Filename preserved** - `note.md` stays `note.md`
2. ✅ **Status updated** - Frontmatter `status: promoted`
3. ✅ **Timestamp added** - `processed_date: YYYY-MM-DD HH:MM`
4. ✅ **Type-based routing** - Moves to correct directory based on `type:` field
5. ✅ **Atomic operation** - Uses `shutil.move()` for safe file relocation

## Backlink Integrity Verification

To verify no broken links after moves:

```bash
# Check for broken wiki-links (should return empty)
grep -r '\[\[.*\]\]' . --include="*.md" | \
  grep -v '\.automation' | \
  python check_broken_links.py

# Or use Obsidian's built-in "Broken links" view
```

## Edge Cases

### ⚠️ When Backlink Updates ARE Needed

If your vault uses markdown-style relative paths:
```markdown
[Link to note](../Inbox/note.md)  <!-- Path-sensitive! -->
```

These would break on file moves. **Solution**: Standardize on wiki-links.

### ⚠️ Duplicate Note Titles

If two notes have the same filename in different directories:
- `Inbox/concepts.md`
- `Permanent Notes/concepts.md`

Wiki-links like `[[concepts]]` become ambiguous. **Solution**: Use unique filenames or include full path.

## Migration Safety Checklist

Before running `repair_orphaned_notes.py --apply`:

- [ ] Backup created automatically (default)
- [ ] Dry-run preview reviewed
- [ ] No duplicate filenames exist
- [ ] All links use wiki-link format (not relative paths)
- [ ] Vault tested with Obsidian/PKM tool after migration

## References

- **Standard**: Obsidian wiki-link documentation
- **Implementation**: `src/ai/note_lifecycle_manager.py::promote_note()`
- **Testing**: `tests/unit/test_note_lifecycle_manager.py`
- **Repair Script**: `scripts/repair_orphaned_notes.py`

## Summary

**No backlink updates needed** when using wiki-link format. The NoteLifecycleManager preserves note filenames and wiki-links match on filenames, ensuring link integrity is maintained automatically during file moves.
