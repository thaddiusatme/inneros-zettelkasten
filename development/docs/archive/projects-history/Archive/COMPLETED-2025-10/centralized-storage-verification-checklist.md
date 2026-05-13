# Samsung Capture Centralized Storage - Verification Checklist

**Date**: 2025-10-02  
**Feature**: TDD Iteration 11 - Centralized Image Storage  
**Status**: ✅ Deployed to Production

---

## When to Use This Checklist

Use this checklist the **first time** you process Samsung screenshots after deploying TDD Iteration 11 to verify the centralized storage is working correctly.

---

## Pre-Processing Check

### 1. Verify You Have New Screenshots

- [ ] Take a screenshot on your Samsung phone (or use existing recent screenshots)
- [ ] Wait for OneDrive sync to complete
- [ ] Confirm screenshot file exists in OneDrive folder

**Expected filename format**: `Screenshot_YYYYMMDD_HHMMSS_AppName.jpg`

---

## Processing Steps

### 2. Run Your Normal Screenshot Workflow

Choose one of these methods:

**Option A: Automated Workflow** (Recommended)
```bash
# From repo root
.automation/scripts/process_inbox_workflow.sh
```

**Option B: Manual Processing**
```bash
# From repo root
cd development
python3 src/cli/workflow_demo.py ../knowledge --process-screenshots --limit 1
```

**Note**: Use `--limit 1` first time to test with just one screenshot

---

## Verification Checklist

### 3. Check Centralized Storage Created

- [ ] **Folder exists**: `knowledge/attachments/YYYY-MM/` (current month)
- [ ] **File copied**: Screenshot exists in centralized location
- [ ] **Correct naming**: File named `samsung-YYYYMMDD-HHMMSS.jpg`

**How to check**:
```bash
# From repo root
ls -lh knowledge/attachments/$(date +%Y-%m)/
```

**Expected output**:
```
samsung-20251002-120000.jpg    1.2M Oct  2 12:00
samsung-20251002-143000.jpg    956K Oct  2 14:30
```

### 4. Check Note Generation

- [ ] **Note created**: New note in `knowledge/Inbox/`
- [ ] **Filename format**: `capture-YYYYMMDD-HHMM-description.md`
- [ ] **Note opens correctly**: Can view in Obsidian

**How to check**:
```bash
# Find most recent capture note
ls -lt knowledge/Inbox/capture-*.md | head -1
```

### 5. Verify Image Path in Note

- [ ] **Open the note** in Obsidian or text editor
- [ ] **Find image reference**: Look for `![Screenshot](...)`
- [ ] **Check path format**: Should be `../attachments/YYYY-MM/samsung-*.jpg`
- [ ] **Image displays**: Screenshot shows correctly in Obsidian preview

**Expected markdown syntax**:
```markdown
![Screenshot_20251002_120000_Chrome.jpg](../attachments/2025-10/samsung-20251002-120000.jpg)
```

**NOT this** (old scattered format):
```markdown
![Screenshot](/Users/thaddius/OneDrive/Screenshots/Screenshot_20251002_120000_Chrome.jpg)
```

### 6. Verify Original Cleanup

- [ ] **Original file deleted**: Screenshot no longer in OneDrive folder
- [ ] **Only centralized copy exists**: File only in `attachments/YYYY-MM/`

**How to check**:
```bash
# Check OneDrive folder (should not find recently processed screenshots)
# Replace path with your actual OneDrive screenshot path
ls ~/Library/CloudStorage/OneDrive-Personal/Screenshots/Screenshot_$(date +%Y%m%d)*.jpg 2>/dev/null
```

**Expected**: "No such file or directory" (files cleaned up)

### 7. Verify Image Quality

- [ ] **Open image in Obsidian**: Should display clearly
- [ ] **Compare file size**: Should match original (no compression)
- [ ] **Check file permissions**: Should be readable

**How to check**:
```bash
# From repo root
cd knowledge/attachments/$(date +%Y-%m)/
file samsung-*.jpg              # Should show: JPEG image data
ls -lh samsung-*.jpg            # Check file size (should match original)
```

---

## Success Criteria

✅ **All checks passed** = Centralized storage working perfectly!

If everything above works, you can confidently:
- Process all your screenshots normally
- Trust the automated workflows
- Rely on centralized storage going forward

---

## Troubleshooting

### Issue: Centralized folder not created

**Check**:
```bash
# Verify attachments root exists
ls -ld knowledge/attachments/
```

**Fix**: Create manually if needed:
```bash
mkdir -p knowledge/attachments/
```

### Issue: Original files not deleted

**Possible causes**:
- Permission error (check logs)
- OneDrive sync locked files
- Processing error before cleanup step

**Check logs**:
```bash
# Look for cleanup messages
grep "Cleaned up original" /path/to/log/file
```

### Issue: Image paths wrong in notes

**Check**:
- Path should start with `../attachments/`
- Path should be relative, not absolute
- Month folder should be current month (YYYY-MM)

**Example correct path**:
```markdown
../attachments/2025-10/samsung-20251002-120000.jpg
```

### Issue: Images not displaying in Obsidian

**Check**:
1. Obsidian settings → Files & Links → Use relative paths ✅
2. File exists: `ls knowledge/attachments/2025-10/samsung-*.jpg`
3. Path syntax correct in markdown

---

## Quick Visual Test

**Before** (old scattered approach):
```
OneDrive/Screenshots/
  └── Screenshot_20251002_120000_Chrome.jpg  ← Original location
  
knowledge/Inbox/
  └── capture-20251002-1200.md              ← References OneDrive path
```

**After** (new centralized approach):
```
knowledge/
  ├── attachments/
  │   └── 2025-10/
  │       └── samsung-20251002-120000.jpg   ← Centralized copy
  └── Inbox/
      └── capture-20251002-1200.md          ← References ../attachments/...

OneDrive/Screenshots/
  └── (empty - originals cleaned up)        ← Original deleted
```

---

## Additional Verification (Optional)

### Test Device Prefix Detection

If you have **iPad screenshots** too, verify they get the correct prefix:

- [ ] iPad screenshots named: `ipad-YYYYMMDD-HHMMSS.png`
- [ ] Samsung screenshots named: `samsung-YYYYMMDD-HHMMSS.jpg`

**How to check**:
```bash
ls -1 knowledge/attachments/$(date +%Y-%m)/
```

**Expected output**:
```
ipad-20251002-090000.png
samsung-20251002-120000.jpg
samsung-20251002-143000.jpg
```

### Test Backward Compatibility

If you have **old scattered screenshots** already referenced in notes:

- [ ] Old notes still display images correctly
- [ ] Old scattered files NOT moved or deleted
- [ ] Only NEW screenshots use centralized storage

---

## Report Issues

If any checks fail, create an issue with:

1. **Which step failed**: Checklist item number
2. **Error message**: Copy exact error if any
3. **Screenshot details**: Filename and expected location
4. **Logs**: Relevant log output

---

## Once Verified

After successful verification:

- ✅ Mark this checklist as complete
- ✅ Delete or archive this document
- ✅ Continue normal screenshot processing workflows
- ✅ Enjoy automatic centralized storage!

---

**Next Update**: No action needed - system works automatically from now on!
