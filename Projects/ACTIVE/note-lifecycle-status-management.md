# Note Lifecycle & Status Management

**Created**: 2025-10-13  
**Priority**: 🔴 **CRITICAL** - Notes accumulating in inbox without status updates  
**Issue**: AI processing completes but `status` field remains unchanged

---

## 🐛 Root Cause Identified

### **The Problem**
Notes are being AI-processed (tags, quality scores, connections added) but their `status` field is **not being updated**, causing them to:
- ✅ Get AI enhancements successfully
- ❌ Still show `status: inbox` 
- ❌ Continue appearing in weekly review scans
- ❌ Accumulate in Inbox/ directory indefinitely

### **Code Location**
`development/src/ai/workflow_manager.py::process_inbox_note()`
- **Lines 250-400**: Adds AI tags, quality scores, connections, summaries
- **Missing**: `frontmatter["status"] = "promoted"` update
- **Result**: Notes processed but never marked as "promoted"

---

## 📊 Complete Note Lifecycle States

### **Status Field Values (5-State System)**

```yaml
status: inbox      # Initial capture, needs AI processing
status: promoted   # AI-processed, ready for review/promotion
status: draft      # In development, not ready for permanent
status: published  # Moved to Permanent Notes/, fully integrated
status: archived   # No longer active, preserved for reference
```

---

## 🔄 Complete Note Lifecycle Pathways

### **Pathway 1: Quick Capture → Fleeting → Permanent**
```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEETING NOTE PATHWAY                         │
└─────────────────────────────────────────────────────────────────┘

1. CAPTURE (User creates note)
   Location: Inbox/
   Type: fleeting
   Status: inbox ← INITIAL STATE
   Action: Quick thought captured

2. AI PROCESSING (--process-inbox)
   Location: Inbox/ (stays)
   Type: fleeting (unchanged)
   Status: inbox → promoted ⚠️ MISSING UPDATE
   Action: AI adds tags, quality, connections
   
   🐛 CURRENT BUG: Status stays "inbox"
   ✅ SHOULD BE: Status becomes "promoted"

3. TRIAGE (--fleeting-triage)
   Location: Inbox/
   Type: fleeting
   Status: promoted (after fix)
   Action: AI analyzes readiness for promotion

4. PROMOTION (--promote-note)
   Location: Inbox/ → Fleeting Notes/
   Type: fleeting
   Status: promoted → published
   Action: Move to Fleeting Notes/ directory

5. MATURATION (7-30 days)
   Location: Fleeting Notes/
   Type: fleeting
   Status: published
   Action: Note develops, links strengthen

6. PERMANENT PROMOTION (--promote-note --to permanent)
   Location: Fleeting Notes/ → Permanent Notes/
   Type: fleeting → permanent
   Status: published (already)
   Action: Move to Permanent Notes/
```

### **Pathway 2: Literature Notes (Articles/Books)**
```
┌─────────────────────────────────────────────────────────────────┐
│                   LITERATURE NOTE PATHWAY                        │
└─────────────────────────────────────────────────────────────────┘

1. IMPORT (--import reading-list)
   Location: Inbox/
   Type: literature
   Status: inbox ← INITIAL STATE
   Action: Import from reading list

2. AI PROCESSING (--process-inbox)
   Location: Inbox/
   Type: literature
   Status: inbox → promoted ⚠️ MISSING UPDATE
   Action: AI extracts key concepts
   
   🐛 CURRENT BUG: Status stays "inbox"
   ✅ SHOULD BE: Status becomes "promoted"

3. MANUAL ENHANCEMENT (User adds notes)
   Location: Inbox/
   Type: literature
   Status: promoted (after fix)
   Action: User adds claims, quotes, analysis

4. PROMOTION (--promote-note --to literature)
   Location: Inbox/ → Literature/
   Type: literature
   Status: promoted → published
   Action: Move to Literature/ directory
```

### **Pathway 3: Direct to Permanent (High Quality)**
```
┌─────────────────────────────────────────────────────────────────┐
│                  DIRECT PERMANENT PATHWAY                        │
└─────────────────────────────────────────────────────────────────┘

1. CAPTURE (Well-formed note created)
   Location: Inbox/
   Type: permanent (or fleeting)
   Status: inbox
   Action: Complete thought captured

2. AI PROCESSING (--process-inbox)
   Location: Inbox/
   Type: permanent
   Status: inbox → promoted ⚠️ MISSING UPDATE
   Quality: >0.7 (high quality)
   
   🐛 CURRENT BUG: Status stays "inbox"
   ✅ SHOULD BE: Status becomes "promoted"

3. WEEKLY REVIEW (--weekly-review)
   Location: Inbox/
   Type: permanent
   Status: promoted (after fix)
   Action: AI recommends immediate promotion

4. PROMOTION (--promote-note --to permanent)
   Location: Inbox/ → Permanent Notes/
   Type: permanent
   Status: promoted → published
   Action: Move to Permanent Notes/
```

### **Pathway 4: Archive (Low Value)**
```
┌─────────────────────────────────────────────────────────────────┐
│                      ARCHIVE PATHWAY                             │
└─────────────────────────────────────────────────────────────────┘

1. CAPTURE
   Location: Inbox/
   Status: inbox

2. AI PROCESSING (--process-inbox)
   Location: Inbox/
   Status: inbox → promoted ⚠️ MISSING UPDATE
   Quality: <0.4 (low quality)

3. TRIAGE (--fleeting-triage)
   Location: Inbox/
   Status: promoted
   Action: AI recommends archiving

4. ARCHIVE (User decision)
   Location: Inbox/ → Archive/
   Status: promoted → archived
   Action: Move to Archive/
```

---

## 🔧 Required Status Update Points

### **1. After AI Processing** ⚠️ **CRITICAL MISSING**
```python
# File: workflow_manager.py::process_inbox_note()
# Location: After line ~400 (after all AI processing)

if not results.get("error"):
    frontmatter["status"] = "promoted"
    frontmatter["processed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Write updated frontmatter back to file
```

### **2. After Manual Promotion** ✅ **ALREADY IMPLEMENTED**
```python
# File: workflow_manager.py::promote_note()
# Location: Line 542 (already working)

frontmatter["status"] = "promoted" if target_type == "permanent" else "draft"
```

### **3. After Fleeting Promotion** ✅ **ALREADY IMPLEMENTED**
```python
# File: workflow_manager.py::promote_fleeting_note()
# Updates status to "published" when moving to Permanent Notes/
```

### **4. After Archive** ⚠️ **NEEDS IMPLEMENTATION**
```python
# File: workflow_manager.py::archive_note()
# TO BE IMPLEMENTED

frontmatter["status"] = "archived"
frontmatter["archived_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
```

---

## 📋 Status Transition Matrix

| From Status | To Status | Trigger | Location Change | Type Change |
|-------------|-----------|---------|-----------------|-------------|
| `inbox` | `promoted` | AI processing completes | No | No |
| `promoted` | `published` | Move to Fleeting Notes/ | Yes | No |
| `promoted` | `published` | Move to Literature/ | Yes | No |
| `promoted` | `published` | Move to Permanent Notes/ | Yes | Maybe |
| `inbox` | `draft` | Manual "work in progress" | No | No |
| `draft` | `promoted` | User marks ready | No | No |
| `published` | `published` | Fleeting → Permanent | Yes | Yes |
| `*` | `archived` | User archives | Yes | No |

---

## 🧑‍💻 User Stories

### P0 — Status Update & Tests
- As a knowledge worker processing inbox notes, I want the system to automatically set `status: promoted` with a `processed_date` after successful AI processing so that weekly review can distinguish processed from unprocessed notes.
- As a maintainer, I want offline-safe unit tests that fail if status or timestamp are missing so that regressions are caught in CI without network/AI calls.

Acceptance Criteria:
- Running `--process-inbox` in fast-mode on a note in `Inbox/` with `status: inbox` results in frontmatter containing `status: promoted` and a `processed_date` timestamp, persisted to disk.
- Unit tests pass locally and in CI with no external network calls and complete in under 2 seconds.

### P1 — Draft/Archive Transitions
- As a writer, I want to mark a note as `draft` and later `promoted` via `mark_as_draft()` and `mark_ready()` so that I can control work-in-progress state.
- As an organizer, I want `archive_note()` to set `status: archived` with `archived_date` so that inactive notes are excluded from active workflows.

Acceptance Criteria:
- `mark_as_draft()` and `mark_ready()` update status fields correctly and are covered by unit tests.
- `archive_note()` updates status and timestamp; archived notes are excluded from weekly review and auto-promotion.

### P2 — Status Validation & Repair
- As an operator, I want `--validate-status` to list inconsistent notes (e.g., `ai_processed: true` but `status: inbox`) so that I can see what needs repair.
- As an operator, I want `--fix-status` to repair common inconsistencies safely so that stuck notes progress automatically.
- As a template user, I want new note templates to include a default `status` so that all new notes enter the lifecycle consistently.

Acceptance Criteria:
- `--validate-status` outputs a concise report and proper exit code; `--fix-status` repairs targeted cases with dry-run and backup support.
- Templates include `status: inbox` by default and tests verify template metadata.

## 🎯 Implementation Priority

### **P0: Fix Critical Bug** (Immediate)
1. ✅ Update `process_inbox_note()` to set `status: promoted` after AI processing
2. ✅ Add `processed_date` timestamp
3. ✅ Write tests for status update
4. ✅ Verify with real inbox notes

### **P1: Implement Missing Transitions** (This Week)
1. Add `archive_note()` method with `status: archived`
2. Add `mark_as_draft()` method for work-in-progress
3. Add `mark_ready()` method to move draft → promoted

### **P2: Validation & Cleanup** (Next Sprint)
1. Add `--validate-status` command to find inconsistent notes
2. Add `--fix-status` command to repair orphaned statuses
3. Update all workflow diagrams with status transitions
4. Add status field to all note templates

---

## 🔍 Detection & Repair Script

```bash
#!/bin/bash
# Find notes with ai_processed but still status:inbox

# Find processed notes without status update
rg --type md -l "ai_processed: true" knowledge/Inbox/ | \
while read file; do
    if rg -q "status: inbox" "$file"; then
        echo "ORPHANED: $file (processed but still inbox status)"
    fi
done

# Count by status
echo "Status Distribution:"
rg "^status:" knowledge/ --type md | cut -d: -f3 | sort | uniq -c
```

---

## 📊 Expected Status Distribution (After Fix)

```
Healthy Vault Status Distribution:
- inbox: 5-10% (new captures awaiting processing)
- promoted: 10-20% (processed, awaiting review/promotion)
- published: 60-70% (active permanent knowledge)
- draft: 5-10% (work in progress)
- archived: 5-15% (completed/obsolete)
```

---

## 🚨 Current Impact (Before Fix)

**Problem Symptoms**:
- ✅ Notes get AI tags, quality scores, connections
- ❌ Still appear in `--weekly-review` as "needing attention"
- ❌ Accumulate in Inbox/ indefinitely
- ❌ No way to distinguish processed vs unprocessed
- ❌ Weekly review shows same notes repeatedly

**User Impact**:
- Cognitive load: Can't tell what needs attention
- Workflow broken: Processed notes treated as new
- Time waste: Reviewing same notes repeatedly
- Loss of trust: "AI is processing but nothing happens"

---

## ✅ Expected Behavior (After Fix)

**After AI Processing**:
1. Note gets AI enhancements ✅
2. Status updates to "promoted" ✅
3. Appears in weekly review with "Ready for promotion" ✅
4. User can distinguish processed from new ✅
5. Clear path through workflow ✅

**Weekly Review Output**:
```markdown
## Ready for Promotion (status: promoted, quality >0.7)
- ✅ note-1.md (quality: 0.85, 5 links) - Ready to promote
- ✅ note-2.md (quality: 0.78, 3 links) - Ready to promote

## Needs Processing (status: inbox)
- ⚠️ new-capture.md - Not yet processed
```

---

**Next Steps**:
1. Implement status update in `process_inbox_note()`
2. Add tests for status transitions
3. Create repair script for orphaned notes
4. Update workflow diagrams
5. Document status field in templates
