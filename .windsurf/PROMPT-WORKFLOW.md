# Windsurf-Optimized Prompt Workflow

> **Quick Reference**: How to use the prompt template system  
> **Files**: `prompt.md` (template), `prompt-example.md` (example)  
> **Updated**: 2025-10-07

---

## 🎯 The 3-Step Workflow

### **Step 1: End of Current Iteration** ⏹️

When you finish your current TDD cycle:

1. Open `.windsurf/prompt.md`
2. Fill in the template variables (15 fields)
3. Keep the file open for Step 2

**Time**: 3-5 minutes

---

### **Step 2: Generate Next Prompt** 📤

1. Copy everything under "OUTPUT: Generated Prompt for Next Chat"
2. Save to clipboard
3. (Optional) Archive filled template as `prompt-iteration-N.md`

**Time**: 30 seconds

---

### **Step 3: Start New Chat** 🆕

1. Click "New Chat" in Windsurf
2. Paste the generated prompt
3. Wait for code map and context loading
4. Begin RED phase

**Time**: 1 minute

---

## 📋 Template Variables Cheat Sheet

### Quick Fill Order (Most Important First)

1. **What I just completed**: COMPLETED_TASK, COMMIT_HASH, KEY_LEARNING
2. **Where I am now**: IN_PROGRESS_TASK, WORKING_FILE, WORKING_FUNCTION
3. **What I'm doing next**: P0_TASK_NAME, P0_GOAL, P0_STEP_1/2/3
4. **For code map**: SYSTEM_COMPONENT, USER_ACTION
5. **For TDD**: RED_TEST_NAME, RED_EXPECTED_FAILURE, GREEN_STRATEGY

### Optional Fields (Can Skip)

- CURRENT_BLOCKER (if none, write "None")
- P1_TASK (for future reference)
- MEMORY_* fields (if no pattern discovered)

---

## 🎨 Example Usage

### Scenario: You Just Finished FileWatcher Integration

**End of iteration checklist**:
- ✅ All tests passing
- ✅ Git commit made: `7f3a2b9`
- ✅ Ready for next task

**Open prompt.md and fill**:
```markdown
COMPLETED_TASK: FileWatcher integration with debouncing
COMMIT_HASH: 7f3a2b9
KEY_LEARNING: Dual-layer debouncing prevents duplicate processing

IN_PROGRESS_TASK: Feature handler registration
WORKING_FILE: development/src/automation/daemon.py
WORKING_FUNCTION: _setup_feature_handlers

P0_TASK_NAME: Complete feature handler registration system
P0_GOAL: Enable conditional handler initialization via config
...
```

**Copy output section** → **Paste in new chat** → **Start coding**

---

## 💡 Pro Tips

### Code Map Questions

Fill `USER_ACTION` with actual user scenarios:
- ✅ "a new screenshot is added to OneDrive"
- ✅ "user runs weekly review command"
- ✅ "file is modified in Inbox directory"
- ❌ "the system processes things" (too vague)

### Key Learning Capture

Write learnings as actionable insights:
- ✅ "Dual-layer debouncing prevents API spam during rapid edits"
- ✅ "Config validation must happen before daemon.start() to fail fast"
- ❌ "Made some improvements" (not actionable)

### P0 Steps

Break tasks into 3 specific steps:
- Each step should be 1-2 sentences
- Each step should be testable
- Steps should build on each other

### Batch File Loading

List 3-5 most relevant files:
- Primary working file
- Test file
- Related integration files
- Utility/config files

---

## 🚀 Benefits Over Old Approach

| Old Way | New Way | Benefit |
|---------|---------|---------|
| Manually write prompt each time | Fill template → Copy output | **3x faster** |
| Forget to request code map | Auto-included in template | **Saves 10 min** |
| Sequential file reads | Batch loading built-in | **Parallel execution** |
| Lose context between sessions | Structured handoff | **Zero context loss** |
| Inconsistent prompts | Standardized structure | **Cascade knows what to expect** |

---

## 🔄 Workflow Integration

### With `/complete-feature-development`

- **Phase 1**: Use template for engine iterations
- **Phase 2**: Use template for CLI iterations
- **Phase 3**: Use template for automation iterations (current!)
- **Phase 4**: Use template for monitoring iterations

### With Git Workflow

```bash
# After GREEN phase passes
git add .
git commit -m "GREEN: Feature handler registration - tests passing"
git push

# Open prompt.md
# Fill variables
# Copy output
# Start new chat
```

### With Lessons Learned

- Fill `KEY_LEARNING` from lessons-learned.md
- Use `MEMORY_*` fields to preserve patterns
- Archive filled prompts with iteration numbers

---

## 📁 File Organization

```
.windsurf/
├── prompt.md                    # Template (always keep clean)
├── prompt-example.md            # Reference example
├── PROMPT-WORKFLOW.md          # This guide
└── archive/                     # Optional
    ├── prompt-iteration-1.md   # Filled templates
    ├── prompt-iteration-2.md
    └── prompt-iteration-3.md
```

---

## ❓ FAQ

**Q: Do I need to fill every field?**  
A: No! Focus on the "Quick Fill Order" section. Optional fields can be skipped.

**Q: Should I archive filled templates?**  
A: Optional but recommended. Helps track your progression and reasoning.

**Q: What if I don't know what to put for code map?**  
A: Use the example! Copy the pattern and adjust to your feature.

**Q: Can I modify the template?**  
A: Yes! This is your template. Add/remove fields as you discover what works.

**Q: How do I request a code map mid-iteration?**  
A: Just ask naturally: "Create code map showing X, Y, Z" - no template needed.

---

## 🎯 Success Metrics

After 3-4 iterations, you should notice:
- ✅ Less time writing prompts (5 min → 2 min)
- ✅ Faster context loading in new chats
- ✅ Fewer clarification questions from Cascade
- ✅ More consistent workflow adherence
- ✅ Better handoffs between sessions

---

## 🆘 Troubleshooting

**"I don't know what to put for P0_STEP_1/2/3"**
→ Break your goal into 3 concrete actions. Each should be independently testable.

**"Code map request seems too complex"**
→ Simplify to: "Show how [A] connects to [B] and where [C] integrates"

**"Template feels too long"**
→ Skip optional sections. Minimum viable prompt needs:
- COMPLETED_TASK + KEY_LEARNING
- P0_TASK_NAME + P0_GOAL
- RED_TEST_NAME + GREEN_STRATEGY

**"Cascade isn't loading files in parallel"**
→ Make sure "Read in parallel:" is on one line, with bullet list below

---

## 📚 Related Resources

- `.windsurf/workflows/complete-feature-development.md` - 4-phase methodology
- `.windsurf/workflows/tdd-git-workflow.md` - Git commit patterns
- `Projects/COMPLETED-*/lessons-learned.md` - Pattern library

---

**Last Updated**: 2025-10-07  
**Maintained by**: Development team  
**Feedback**: Update this guide as you discover improvements
