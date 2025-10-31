# Automation Revival Sprint - Project Board Guide

**Project**: https://github.com/users/thaddiusatme/projects/2

---

## 🎯 **Current Organization**

All 9 issues are in **"Todo"** status and organized by existing labels:

### **By Priority (Using Labels)**

**🔴 P0 - Critical** (Must Do This Week) - 6 issues:
- #29 Fix YouTube Rate Limiting (`priority:p0`, `type:bug-fix`, 2h)
- #30 Fix File Watching Loop Bug (`priority:p0`, `type:bug-fix`, 2h)
- #31 Test Screenshot Import (`priority:p0`, `type:testing`, 2h)
- #32 Test Inbox Processing (`priority:p0`, `type:testing`, 2h)
- #34 Staged Cron Re-enablement (`priority:p0`, `type:deployment`, 2h)
- #36 48-Hour Stability (`priority:p0`, `type:monitoring`, 4h)

**🟠 P1 - High Priority** (Nice to Have) - 3 issues:
- #33 Test Health Monitor (`priority:p1`, `type:testing`, 1h)
- #35 Automation Visibility (`priority:p1`, `type:monitoring`, 3h)
- #37 Sprint Retrospective (`priority:p1`, `type:documentation`, 2h)

### **By Type (Using Labels)**

- **Bug Fixes** (`type:bug-fix`): #29, #30
- **Testing** (`type:testing`): #31, #32, #33
- **Deployment** (`type:deployment`): #34
- **Monitoring** (`type:monitoring`): #35, #36
- **Documentation** (`type:documentation`): #37

---

## 📊 **How to Use the Board**

### **1. View by Status (Kanban)**

In the project:
1. Click **"View"** dropdown (top right)
2. Select **"Board"** layout
3. Click **"Group by"** → Select **"Status"**
4. You'll see three columns:
   - **Todo** (all 9 issues currently here)
   - **In Progress** (empty)
   - **Done** (empty)

### **2. View by Priority (Using Labels)**

In the project:
1. Click **"View"** dropdown
2. Select **"Table"** layout
3. Click **"Filter"** → Add filter: `label:priority:p0`
4. See only P0 critical items
5. Change to `label:priority:p1` for P1 items

### **3. View by Type (Using Labels)**

Filter by:
- `label:type:bug-fix` - Bug fixes (#29, #30)
- `label:type:testing` - Testing tasks (#31, #32, #33)
- `label:type:deployment` - Deployment (#34)
- `label:type:monitoring` - Monitoring (#35, #36)
- `label:type:documentation` - Docs (#37)

### **4. View by Size (Using Labels)**

Filter by:
- `label:size:small` - 1-2 hour tasks
- `label:size:medium` - 2-4 hour tasks
- `label:size:large` - 4-8 hour tasks

---

## 🚀 **Working with the Board**

### **Starting Work on an Issue**

**In Browser**:
1. Drag issue from **"Todo"** to **"In Progress"**
2. Assign it to yourself (click issue → Assignees)
3. Click issue to open details

**Via CLI**:
```bash
# View issue
gh issue view 29

# Assign to yourself
gh issue edit 29 --add-assignee @me

# Update status (requires item ID)
# Easier to drag in web UI
```

### **Completing an Issue**

**In Browser**:
1. Drag from **"In Progress"** to **"Done"**
2. Close the issue (the board will update automatically)

**Via CLI**:
```bash
# Close issue
gh issue close 29 --comment "Completed! Rate limiting working correctly."
```

---

## 📋 **Recommended Views to Create**

### **View 1: Kanban Board**
- Layout: **Board**
- Group by: **Status**
- Sort by: **Priority** (using labels)
- Name: "Kanban Board"

### **View 2: Priority Focus**
- Layout: **Table**
- Filter: `label:priority:p0 is:open`
- Sort by: **Sprint Day**
- Name: "P0 Items Only"

### **View 3: Daily Plan**
- Layout: **Board**
- Group by: **Sprint Day** (custom field)
- Filter: `is:open`
- Name: "Daily Timeline"

### **View 4: My Work**
- Layout: **Board**
- Group by: **Status**
- Filter: `assignee:@me`
- Name: "My Tasks"

---

## 🔧 **CLI Commands**

### **View Project**
```bash
# In browser
gh project view 2 --owner @me --web

# In terminal
gh project view 2 --owner @me

# List items
gh project item-list 2 --owner @me
```

### **Work with Issues**
```bash
# List sprint issues
gh issue list --label 'sprint:automation-revival'

# List P0 only
gh issue list --label 'priority:p0,sprint:automation-revival'

# View specific issue
gh issue view 29

# Start working
git checkout -b fix/youtube-rate-limiting
gh issue edit 29 --add-assignee @me
```

### **Move Items** (Easier in Web UI)
```bash
# Get item ID first
gh project item-list 2 --owner @me --format json | \
  jq '.items[] | select(.content.number == 29) | .id'

# Then use gh project item-edit with field IDs
# (Complex - use web UI drag-and-drop instead)
```

---

## 💡 **Pro Tips**

1. **Use Labels for Filtering**: The existing labels (`priority:p0`, `type:bug-fix`, etc.) are perfect for organizing. No need for duplicate custom fields!

2. **Drag and Drop**: Easiest way to move items between Status columns

3. **Bulk Actions**: Select multiple issues → Set status/assignee at once

4. **Keyboard Shortcuts**: 
   - `e` - Edit item
   - `c` - Close item
   - `Ctrl+K` - Quick search

5. **Automation**: GitHub Projects can auto-move items when issues are closed

---

## 📈 **Sprint Progress Tracking**

### **Daily Check-in** (Morning)
```bash
# What's in progress?
gh issue list --label 'sprint:automation-revival' --assignee @me

# What's done today?
gh issue list --label 'sprint:automation-revival' --state closed
```

### **Weekly Review** (End of Sprint)
```bash
# Total completed
gh issue list --label 'sprint:automation-revival' --state closed | wc -l

# Total remaining
gh issue list --label 'sprint:automation-revival' --state open | wc -l

# Burndown: 9 total - X done = Y remaining
```

---

## 🎯 **Next Steps**

1. **Open project**: Already open in browser!
2. **Explore views**: Try different groupings (Status, Labels, etc.)
3. **Start Issue #29**: 
   ```bash
   gh issue view 29 --web
   git checkout -b fix/youtube-rate-limiting
   ```

**Project**: https://github.com/users/thaddiusatme/projects/2
