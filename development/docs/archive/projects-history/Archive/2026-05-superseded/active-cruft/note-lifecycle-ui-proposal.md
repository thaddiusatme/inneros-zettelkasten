---
type: ui-proposal
created: 2025-10-26
audience: ux-team, product-team
tags: [ui-design, note-lifecycle, dashboard, automation-visibility]
related: note-lifecycle-ux-impact.md
---

# Note Lifecycle UI Proposal

**For**: UX Team, Product Team  
**Date**: 2025-10-26  
**Context**: UI design for visualizing note promotion and lifecycle management

---

## 🎯 Current State

### Existing Web UI
- ✅ **Flask web app** at `localhost:5001`
- ✅ **Pages**: Dashboard, Analytics, Weekly Review, Settings, Onboarding
- ✅ **Metrics**: Real-time automation metrics, workflow runs, success rates
- 🔴 **Missing**: Note lifecycle visibility, promotion status, stuck note detection

### Current User Interaction (CLI-Only)
```bash
# Users currently interact via command line
python scripts/repair_orphaned_notes.py /path/to/vault          # Preview stuck notes
python scripts/repair_orphaned_notes.py /path/to/vault --apply  # Fix them
```

**Problem**: No visual feedback, requires terminal knowledge, not discoverable

---

## 💡 Proposed UI Components

### 1. **Note Lifecycle Dashboard Widget** (Priority: HIGH)

**Location**: Main Dashboard (`/dashboard`)  
**Size**: Full-width card, collapsible  
**Update Frequency**: Real-time (WebSocket) or every 30s

#### Visual Design

```
╔═══════════════════════════════════════════════════════════╗
║  📊 Note Lifecycle Health                        [Expand] ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  ┌─────────────┬──────────────┬──────────────┬─────────┐ ║
║  │   📥 Inbox  │ 📝 Permanent │ 📚 Literature│ 💭 Fleeting│ ║
║  │     5       │     142      │      38      │    67    │ ║
║  │  ━━━━━━━━  │  ━━━━━━━━━━ │  ━━━━━━━━━━ │ ━━━━━━━ │ ║
║  │  All Ready  │   +3 today   │   +1 today   │  +2 today│ ║
║  └─────────────┴──────────────┴──────────────┴─────────┘ ║
║                                                           ║
║  🚨 Attention Needed:                                    ║
║  • 0 stuck notes (all clear! ✅)                        ║
║  • Last auto-promotion: 2 min ago                       ║
║                                                           ║
║  📈 This Week:                                           ║
║  • 24 notes promoted automatically                      ║
║  • 98% success rate (1 manual intervention)             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

#### Component Breakdown

**Folder Status Cards**:
- Count of notes in each directory
- Visual progress bar showing "health" (green = all good)
- Today's activity ("+3 today" = 3 notes promoted today)
- Click to filter note list view

**Attention Section**:
- 🚨 Red badge when stuck notes detected
- 🟢 Green checkmark when all clear
- Shows count of notes needing attention
- Click to see details/fix

**Weekly Summary**:
- Promotion activity metrics
- Success rate percentage
- Trends (up/down indicators)

---

### 2. **Stuck Notes Alert** (Priority: HIGH)

**Trigger**: When orphaned notes detected (status/location mismatch)  
**Type**: Toast notification + dashboard banner  
**Action**: Click to review and fix

#### When Stuck Notes Exist

```
╔═══════════════════════════════════════════════════════════╗
║  🚨 13 Notes Need Attention                     [Review] ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Some notes have been processed but weren't moved to     ║
║  their correct folders. This usually happens when        ║
║  automation was interrupted.                             ║
║                                                           ║
║  Breakdown:                                              ║
║  • 11 notes: Status says "promoted" but still in Inbox  ║
║  • 2 notes: Processed by AI but status not updated      ║
║                                                           ║
║  [Review & Fix]  [Learn More]  [Dismiss]                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

#### Click "Review & Fix" → Modal Dialog

```
╔═══════════════════════════════════════════════════════════╗
║  Fix Stuck Notes                                    [×]  ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Preview of changes:                                     ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Type       Issue             Note Title        Action│ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ fleeting   needs move        daily-screenshots →    │ ║
║  │                               Fleeting Notes/        │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ literature needs status+move OpenAI DevDay... →     │ ║
║  │                               Literature Notes/      │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ ...        ...               ...                     │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ✅ Automatic backup will be created before changes     ║
║  ✅ You can undo if something goes wrong                ║
║                                                           ║
║  [Cancel]                    [Fix 13 Notes →]           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

### 3. **Note Lifecycle Detail View** (Priority: MEDIUM)

**Location**: New page `/notes/lifecycle` or expandable dashboard section  
**Purpose**: Deep dive into note promotion history and status

```
╔═══════════════════════════════════════════════════════════╗
║  Note Lifecycle Explorer                                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Filters: [All Statuses ▼] [All Types ▼] [Last 7 Days ▼]║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Status     Type      Note Title           Last Action│ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ 📥 inbox   fleeting  Morning standup      Just now  │ ║
║  │                      notes                           │ ║
║  │                      Status: Awaiting AI processing  │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ ✅ promoted permanent Deep Work review    2 hrs ago │ ║
║  │                                                      │ ║
║  │                      📍 Permanent Notes/             │ ║
║  │                      Status: Promoted successfully   │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ 🚨 stuck   literature YouTube transcript  3 days ago│ ║
║  │                                                      │ ║
║  │                      ⚠️ Still in Inbox/              │ ║
║  │                      [Fix Now]                       │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

### 4. **Real-Time Promotion Notifications** (Priority: MEDIUM)

**Type**: Toast notifications (bottom-right corner)  
**Duration**: 5 seconds (dismissible)  
**Trigger**: When notes are automatically promoted

#### Success Notification

```
┌─────────────────────────────────────┐
│ ✅ Note Promoted                   │
├─────────────────────────────────────┤
│ "Deep Work principles" moved to    │
│ Permanent Notes/                   │
│                                     │
│ Quality: 0.87 • Type: permanent    │
│                                     │
│ [View] [Undo]                 [×]  │
└─────────────────────────────────────┘
```

#### Batch Promotion Summary

```
┌─────────────────────────────────────┐
│ 🎉 3 Notes Promoted                │
├─────────────────────────────────────┤
│ • 2 → Fleeting Notes/              │
│ • 1 → Literature Notes/            │
│                                     │
│ [View Details]                [×]  │
└─────────────────────────────────────┘
```

---

### 5. **Note Status Badge** (Priority: LOW)

**Location**: Wherever individual notes are displayed  
**Purpose**: Quick visual indicator of note state

Visual badges:

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ 📥 Inbox │  │ ✅ Ready │  │ 🚀 Promoted│  │ 🚨 Stuck │
└──────────┘  └──────────┘  └──────────┘  └──────────┘

┌──────────────┐  ┌──────────────┐
│ 🤖 Processing│  │ ⏸️ Paused    │
└──────────────┘  └──────────────┘
```

**Color Coding**:
- 📥 **Inbox** (Gray): New, awaiting processing
- ✅ **Ready** (Green): AI processed, ready to promote
- 🚀 **Promoted** (Blue): Successfully moved to folder
- 🚨 **Stuck** (Red): Needs attention/manual intervention
- 🤖 **Processing** (Yellow): Currently being analyzed by AI
- ⏸️ **Paused** (Orange): User-paused automation

---

## 🎨 Design System

### Color Palette

**Status Colors**:
- **Success/Promoted**: `#10B981` (green)
- **Warning/Ready**: `#F59E0B` (amber)
- **Error/Stuck**: `#EF4444` (red)
- **Info/Inbox**: `#6B7280` (gray)
- **Processing**: `#3B82F6` (blue)

**Note Type Colors**:
- **Permanent**: `#8B5CF6` (purple) - lasting knowledge
- **Literature**: `#EC4899` (pink) - external sources
- **Fleeting**: `#14B8A6` (teal) - quick captures

### Icons

```
📥 Inbox           (fa-inbox)
📝 Permanent       (fa-bookmark)
📚 Literature      (fa-book)
💭 Fleeting        (fa-lightbulb)
✅ Success         (fa-check-circle)
🚨 Error           (fa-exclamation-triangle)
🚀 Promoted        (fa-rocket)
🤖 AI Processing   (fa-robot)
⏸️ Paused          (fa-pause-circle)
```

---

## 🔌 Technical Implementation

### Backend API Endpoints Needed

```python
# Get lifecycle status summary
GET /api/lifecycle/status
Response: {
  "inbox": {"count": 5, "ready": 3, "stuck": 0},
  "permanent": {"count": 142, "today": 3},
  "literature": {"count": 38, "today": 1},
  "fleeting": {"count": 67, "today": 2},
  "stuck_notes": []
}

# Get stuck notes (orphaned)
GET /api/lifecycle/stuck
Response: {
  "count": 13,
  "notes": [
    {
      "path": "Inbox/daily-screenshots-2025-09-30.md",
      "type": "fleeting",
      "issue": "needs_file_move",
      "title": "Daily screenshots",
      "status": "promoted"
    }
  ]
}

# Fix stuck notes
POST /api/lifecycle/repair
Body: {"apply": true, "backup": true}
Response: {
  "success": true,
  "fixed": 12,
  "errors": 1,
  "backup_path": "~/backups/..."
}

# Get promotion history
GET /api/lifecycle/history?days=7
Response: {
  "promotions": [
    {
      "timestamp": "2025-10-26T14:30:00Z",
      "note": "Deep Work principles",
      "from": "Inbox",
      "to": "Permanent Notes",
      "type": "permanent",
      "quality": 0.87
    }
  ]
}
```

### Frontend Components (React/Vue)

```javascript
// Main dashboard widget
<NoteLifecycleWidget 
  refreshInterval={30000}  // 30 seconds
  showStuckAlert={true}
  showWeeklySummary={true}
/>

// Stuck notes modal
<StuckNotesModal
  notes={stuckNotes}
  onFix={handleRepair}
  onDismiss={handleDismiss}
/>

// Real-time notifications
<PromotionToast
  note={promotedNote}
  duration={5000}
  position="bottom-right"
  showUndo={true}
/>
```

### WebSocket Events (Real-Time Updates)

```javascript
// Subscribe to lifecycle events
socket.on('note:promoted', (data) => {
  showToast(`Note promoted: ${data.title}`)
  updateDashboard()
})

socket.on('note:stuck_detected', (data) => {
  showAlert(`${data.count} notes need attention`)
  updateStuckCount(data.count)
})

socket.on('promotion:batch_complete', (data) => {
  showToast(`${data.count} notes promoted`)
})
```

---

## 📱 Responsive Design

### Desktop (1200px+)
- Full dashboard with all widgets visible
- Side-by-side comparison views
- Expanded note details in modal

### Tablet (768px - 1199px)
- Stacked widgets (2 columns)
- Collapsible sections
- Simplified filters

### Mobile (< 768px)
- Single column layout
- Bottom sheet modals instead of centered
- Swipe gestures for actions
- Simplified metrics (show counts only)

---

## 🚀 Implementation Phases

### Phase 1: Minimum Viable UI (Week 1)
- [ ] Dashboard widget showing note counts
- [ ] Stuck notes alert banner
- [ ] Basic repair modal with preview
- [ ] Success/error toast notifications

**Goal**: Users can see stuck notes and fix them via UI

### Phase 2: Enhanced Visibility (Week 2)
- [ ] Real-time promotion notifications
- [ ] Weekly summary section
- [ ] Note status badges throughout app
- [ ] Lifecycle history view

**Goal**: Users understand what's happening automatically

### Phase 3: Advanced Features (Week 3)
- [ ] WebSocket real-time updates
- [ ] Note detail drill-down
- [ ] Batch promotion controls
- [ ] Undo functionality

**Goal**: Power users can manage lifecycle manually

---

## 🎯 Success Metrics

### User Engagement
- **Dashboard widget views**: Target 80%+ of sessions
- **Stuck note repairs via UI**: Target 90%+ (vs CLI)
- **Time to discover stuck notes**: < 30 seconds (vs manual hunting)

### User Satisfaction
- **Confidence in automation**: "I trust the system" survey rating
- **Anxiety reduction**: "I know what's happening" survey rating
- **Cognitive load**: Time spent checking note locations

### Technical Performance
- **Dashboard load time**: < 500ms
- **Real-time notification latency**: < 1 second
- **Repair operation success**: 95%+ (matching CLI)

---

## 💬 Open Questions for UX Team

1. **Notification Frequency**: How often should we show promotion toasts?
   - Every single note? (could be noisy)
   - Batch summary every N minutes?
   - Only when user is actively watching?

2. **Stuck Note Severity**: When should we interrupt the user?
   - Immediately when detected?
   - Only if stuck > 24 hours?
   - Weekly digest?

3. **Undo Granularity**: What should "Undo" revert?
   - Single note promotion?
   - Entire batch?
   - Time-based (last 5 minutes)?

4. **Mobile Priority**: Do users need full features on mobile?
   - Or just view-only dashboard?
   - Or critical alerts only?

5. **Dark Mode**: Should lifecycle status colors change in dark mode?
   - Use same semantic colors?
   - Muted versions?

---

## 📎 Related Documents

- `note-lifecycle-ux-impact.md` - UX impact analysis
- `project-todo-v4.md` - Technical implementation details
- `web_ui/templates/dashboard.html` - Current dashboard implementation
- `.windsurf/rules/automation-monitoring-requirements.md` - Automation requirements

---

**Next Steps**:
1. Review with UX team
2. Create high-fidelity mockups (Figma)
3. Validate with user testing
4. Begin Phase 1 implementation
