# Retro Terminal UI Design Manifest

**Created**: 2025-10-10  
**Status**: 📋 **PLANNED** - Awaiting Quality Audit Completion  
**Priority**: P1 - After workflows validated  
**Timeline**: 1 week (after audit)

---

## 🎯 Vision

**Goal**: Single entry point for all InnerOS workflows with nostalgic, ASCII-based terminal interface.

**Philosophy**: Retro computing aesthetic - simple, functional, keyboard-driven. Think MS-DOS era, BBS systems, early Unix tools.

**User**: Personal tool for daily knowledge management workflows.

---

## 🎨 Design Aesthetic

### **Retro Style Elements**

**Visual Style**:
- ASCII box-drawing characters (├─┤ │ ╭╮╰╯)
- ANSI colors (16-color palette, no fancy gradients)
- Monospace fonts only
- Character-based "graphics"
- Minimal animations (typing effect, simple spinners)

**Interaction Style**:
- Keyboard-driven (arrow keys, numbers, letters)
- Clear visual feedback
- Status messages in classic style
- Progress indicators with ASCII art

**Inspiration**:
- MS-DOS applications (Norton Commander, Turbo Pascal IDE)
- BBS interfaces (ANSI art menus)
- Midnight Commander, htop (modern retro)
- Early Unix menu systems

---

## 📋 Core Interface Design

### **Main Menu**

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗███╗   ██╗███╗   ██╗███████╗██████╗  ██████╗ ███████╗  ║
║   ██║████╗  ██║████╗  ██║██╔════╝██╔══██╗██╔═══██╗██╔════╝  ║
║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝██║   ██║███████╗  ║
║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║╚════██║  ║
║   ██║██║ ╚████║██║ ╚████║███████╗██║  ██║╚██████╔╝███████║  ║
║   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝  ║
║                                                               ║
║              Knowledge Management System v0.2.0              ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  What would you like to do?                                  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │  1. 📋 Weekly Review           [Last: 2 days ago]       │ ║
║  │  2. 🎥 Process YouTube Videos  [3 pending]              │ ║
║  │  3. 🔗 Discover Connections    [128 notes analyzed]     │ ║
║  │  4. 🏷️  Enhance Tags            [45 improvements found]  │ ║
║  │  5. 📝 Organize Notes           [12 misplaced]          │ ║
║  │  6. 💾 Backup & Restore         [Last: Today 09:15]     │ ║
║  │  7. 📊 View Analytics           [Dashboard]             │ ║
║  │  8. ⚙️  Settings                [Configure]             │ ║
║  │  9. 📖 Help & Documentation     [Commands]              │ ║
║  │                                                          │ ║
║  │  q. Quit                                                │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  Select option [1-9, q]:                                     ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║ Status: ✓ All systems operational | 680/775 tests passing   ║
╚═══════════════════════════════════════════════════════════════╝
```

**Features**:
- ASCII art logo (optional, can be minimal)
- Numbered options (1-9)
- Status indicators (last run, pending items)
- Quick stats on main menu
- System health at bottom

---

### **Workflow Execution Screen**

**Example: Weekly Review**

```
╔═══════════════════════════════════════════════════════════════╗
║ InnerOS > Weekly Review                              [RUNNING]║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Analyzing your knowledge vault...                           ║
║                                                               ║
║  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░ 75%     ║
║                                                               ║
║  ✓ Scanned 128 notes                                         ║
║  ✓ Analyzed quality scores                                   ║
║  ✓ Identified 15 promotion candidates                        ║
║  ⏳ Generating recommendations...                            ║
║                                                               ║
║  Elapsed: 8s | Estimated: 3s remaining                       ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║ Press 'x' to cancel | Status: Processing...                  ║
╚═══════════════════════════════════════════════════════════════╝
```

**Features**:
- Clear workflow title
- Progress bar (ASCII blocks)
- Step-by-step updates
- Time estimates
- Cancelable operations

---

### **Results Display**

**Example: Weekly Review Results**

```
╔═══════════════════════════════════════════════════════════════╗
║ InnerOS > Weekly Review                            [COMPLETE] ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ✓ Weekly Review Complete (12 seconds)                       ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ READY TO PROMOTE (Quality > 0.7)                        │ ║
║  ├─────────────────────────────────────────────────────────┤ ║
║  │                                                          │ ║
║  │  1. fleeting-ai-strategy-framework (0.85)               │ ║
║  │     → Suggest: Move to Permanent Notes                  │ ║
║  │                                                          │ ║
║  │  2. lit-zettelkasten-method-book (0.79)                 │ ║
║  │     → Suggest: Move to Literature Notes                 │ ║
║  │                                                          │ ║
║  │  3. fleeting-automation-ideas (0.81)                    │ ║
║  │     → Suggest: Move to Permanent Notes                  │ ║
║  │                                                          │ ║
║  │  [+12 more...]                                          │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  📊 Statistics:                                              ║
║     • Total Notes: 128                                       ║
║     • Avg Quality: 0.64                                      ║
║     • Promotion Ready: 15                                    ║
║     • Needs Work: 23                                         ║
║                                                               ║
║  Actions:                                                     ║
║    [s] Save report    [o] Organize now    [m] Main menu     ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║ Review saved to: .automation/review_queue/                   ║
╚═══════════════════════════════════════════════════════════════╝
```

**Features**:
- Clear success indicator
- Results in organized sections
- Actionable next steps
- Quick actions (save, organize, etc.)
- File paths for reference

---

## 🎹 Interaction Patterns

### **Navigation**

**Keyboard Shortcuts**:
- `↑` `↓` - Navigate menu items
- `1-9` - Direct number selection
- `Enter` - Confirm/Execute
- `Esc` / `q` - Back/Quit
- `h` - Help (context-sensitive)
- `Ctrl+C` - Emergency exit

**Visual Feedback**:
```
Selected item:   > [ 1. Weekly Review ]
Unselected:        2. YouTube Processing
Disabled:          3. Connections (analyzing...)
```

---

### **Progress Indicators**

**Spinner** (for quick tasks):
```
Processing... ⠋
Processing... ⠙
Processing... ⠹
Processing... ⠸
```

**Progress Bar** (for long tasks):
```
[▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░] 50% - Analyzing notes...
```

**Multi-step** (for complex workflows):
```
[✓] Step 1: Scan files
[✓] Step 2: Extract metadata
[⏳] Step 3: AI analysis
[ ] Step 4: Generate report
```

---

## 🛠️ Technical Implementation

### **Tech Stack**

**Framework**: `Rich` (Python library)
- Lightweight, no external dependencies beyond pip
- ANSI color support
- Progress bars, tables, layouts
- Retro aesthetic achievable with minimal styling

**Alternative**: `Textual` (if Rich too limited)
- More powerful, modern TUI framework
- Still supports retro aesthetic
- Reactive components, layouts

**Decision**: Start with Rich (simpler), upgrade to Textual if needed

---

### **Architecture**

```
inneros.py (main entry point)
├── ui/
│   ├── menu.py           # Main menu renderer
│   ├── workflows.py      # Workflow execution screens
│   ├── results.py        # Results display
│   ├── components.py     # Reusable UI elements
│   └── theme.py          # Retro color scheme
├── commands/
│   ├── weekly_review.py  # Wrapper for workflow_demo.py
│   ├── youtube.py        # Wrapper for youtube_cli.py
│   ├── connections.py    # Wrapper for connections_demo.py
│   └── ...
└── cli/
    └── [existing CLI tools remain unchanged]
```

**Design Principle**: TUI is a wrapper/facade over existing CLI tools
- Don't rewrite workflows - call existing scripts
- Parse output and format for TUI
- Add progress tracking and cancellation
- Existing CLIs still work standalone

---

### **Menu System**

```python
# Pseudo-code structure

class RetroMenu:
    def __init__(self):
        self.options = [
            MenuItem("1", "Weekly Review", self.run_weekly_review),
            MenuItem("2", "YouTube Processing", self.run_youtube),
            # ...
        ]
    
    def display(self):
        # Render ASCII menu with Rich
        
    def run_weekly_review(self):
        # Show progress screen
        # Execute: python3 development/src/cli/workflow_demo.py knowledge/ --weekly-review
        # Parse output
        # Display results screen
        
    def get_status_info(self):
        # Check last run times
        # Count pending items
        # Return for main menu display
```

---

## 📊 Screen Specifications

### **Main Menu**
- Width: 67 columns (fits 80-column terminals with margin)
- Height: Dynamic (fits content)
- Sections: Header, Options, Status Bar
- Updates: Real-time status on load

### **Execution Screen**
- Shows: Current step, progress, time estimate
- Interactive: Cancelable (Ctrl+C, 'x' key)
- Logging: Can toggle verbose mode

### **Results Screen**
- Shows: Summary, detailed results, statistics
- Actions: Save, continue, back to menu
- Export: Can save full report to file

---

## 🎨 Color Scheme (16-color ANSI)

```
Primary:   Cyan (titles, borders)
Success:   Green (✓, completed items)
Warning:   Yellow (⚠, warnings)
Error:     Red (✗, errors)
Info:      Blue (ℹ, information)
Muted:     Gray (inactive, help text)
Highlight: Bright White (selected items)
```

**Accessibility**: Always include text indicators, not just color

---

## 🚀 Implementation Plan

### **Phase 1: Basic Menu** (Day 1-2)

**Deliverables**:
- Main menu with 8 workflow options
- Number/letter selection working
- Exit functionality
- Basic ASCII styling

**Test**: Can launch TUI and navigate menu

---

### **Phase 2: Workflow Integration** (Day 3-4)

**Deliverables**:
- Execute existing CLI commands from menu
- Capture output and display
- Basic progress indicators
- Error handling

**Test**: Can run each workflow from TUI successfully

---

### **Phase 3: Progress & Feedback** (Day 5-6)

**Deliverables**:
- Real-time progress bars
- Step-by-step status updates
- Time estimates
- Cancelable operations

**Test**: User gets clear feedback during long operations

---

### **Phase 4: Results & Polish** (Day 6-7)

**Deliverables**:
- Formatted results screens
- Quick actions (save, organize, etc.)
- Status bar with system info
- Help system

**Test**: Complete workflow feels smooth and informative

---

## ✅ Success Criteria

### **Must Have**

- ✅ Single `inneros` command launches TUI
- ✅ All 8 workflows accessible from menu
- ✅ Clear progress indicators
- ✅ Results displayed in organized format
- ✅ Keyboard-only navigation
- ✅ Graceful error handling

### **Should Have**

- ✅ Retro aesthetic (ASCII art, boxes, ANSI colors)
- ✅ Status indicators (last run, pending items)
- ✅ Time estimates for operations
- ✅ Context-sensitive help
- ✅ Cancelable operations

### **Nice to Have**

- ✅ ASCII art logo/splash screen
- ✅ Sound effects (system beeps for complete/error)
- ✅ Themes (different retro color schemes)
- ✅ Command history (recently used workflows)

---

## 🐛 Known Challenges

### **Output Parsing**

**Issue**: Existing CLIs output to stdout with various formats
**Solution**: 
- Add `--json` flag to CLIs for structured output
- Parse existing text output as fallback
- Standardize output format gradually

### **Progress Tracking**

**Issue**: Some workflows don't report progress
**Solution**:
- Add progress callbacks to workflow functions
- Show spinner when progress unavailable
- Estimate based on typical execution time

### **Error Handling**

**Issue**: Need to capture and display errors gracefully
**Solution**:
- Try/except around all workflow calls
- Display errors in styled error boxes
- Offer recovery options (retry, skip, exit)

---

## 📁 Deliverables

### **Code**

1. **`inneros.py`** - Main TUI entry point
2. **`ui/` module** - All UI components
3. **`commands/` module** - Workflow wrappers
4. **Tests** - TUI component tests

### **Documentation**

1. **User Guide** - How to use TUI
2. **Developer Guide** - How to add new workflows
3. **Screenshots** - ASCII art examples (in markdown)

### **Configuration**

1. **`.innerosrc`** - User preferences (theme, defaults)
2. **Workflow metadata** - Icons, descriptions, categories

---

## 🔄 Iteration Strategy

**Start Simple**: 
- Week 1: Functional menu, basic workflow execution
- Get feedback from personal use
- Identify pain points

**Iterate Based on Use**:
- Add features that save the most time
- Polish workflows used most often
- Defer rarely-used features

**Don't Over-engineer**:
- Personal tool, not enterprise software
- ASCII art is decoration, not requirement
- Focus on workflows working reliably

---

## 📚 Related Documents

- **Quality Audit**: `quality-audit-manifest.md` (prerequisite)
- **Workflow Docs**: `CLI-REFERENCE.md`
- **Current State**: `CURRENT-STATE-2025-10-08.md`
- **Master TODO**: `project-todo-v3.md`

---

**Status**: Awaiting quality audit completion  
**Dependencies**: All workflows validated and documented  
**Next Action**: Begin after audit Phase 4 complete (Oct 14-15)

---

**Last Updated**: 2025-10-10  
**Target Start**: Oct 14, 2025 (after audit)  
**Estimated Completion**: Oct 21, 2025
