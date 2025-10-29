# Copy Instructions for Protected Rules Files

**Created**: 2025-10-23  
**Purpose**: Replace protected rules files with updated versions

---

## Quick Copy Commands

```bash
# From project root:
cd /Users/thaddius/repos/inneros-zettelkasten

# Copy updated files:
cp .windsurf/rules-updates/README.md .windsurf/rules/README.md
cp .windsurf/rules-updates/updated-session-context.md .windsurf/rules/updated-session-context.md

# Verify changes:
git diff .windsurf/rules/README.md | head -50
git diff .windsurf/rules/updated-session-context.md | head -50
```

---

## What Changed

### README.md Updates:
1. **Date**: 2025-10-07 → 2025-10-23
2. **File sizes**: Updated with actual byte counts
3. **New section**: Consolidated Development Guides reference
4. **Footer**: Updated totals and added guides total

### updated-session-context.md Updates:
1. **Metadata**: Date, branch, commit updated
2. **Recent work**: Added Oct 21-23 consolidation work
3. **Priorities**: Added Git Branch Cleanup as P2
4. **NOT Next**: Added consolidation to completed list
5. **Guide references**: Already present, no changes needed

---

## Commit After Copying

```bash
git add .windsurf/rules/README.md .windsurf/rules/updated-session-context.md
git commit -m "Meta: Update protected rules files with current info

- Rules README: Current file sizes + guide references  
- Session context: Update date/branch/commit + Oct 23 work

Completes .windsurf configuration review (see CONFIG-FIXES-COMPLETE.md)"
```

---

## Files Ready to Copy

- `.windsurf/rules-updates/README.md` → `.windsurf/rules/README.md`
- `.windsurf/rules-updates/updated-session-context.md` → `.windsurf/rules/updated-session-context.md`

**Total Time**: ~30 seconds to copy + verify + commit
