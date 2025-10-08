# Quick Fill Checklist

> **Ultra-fast reference**: 2-minute prompt generation  
> **Use this**: When you're in a hurry  
> **Full template**: See `prompt.md` for complete version

---

## ✅ Minimum Viable Prompt (5 Required Fields)

**At end of iteration, fill these 5 fields:**

```
1. What I just completed: ___________________________________
   Commit hash: ___________

2. Key learning: __________________________________________

3. Next task: ____________________________________________

4. Working in file: ______________________________________
   Function: ______________

5. Test to write: ________________________________________
   Expected to fail with: _______________
```

**Then paste into new chat:**

```markdown
# TDD Iteration: [FEATURE_NAME]

## Status
Completed: [FIELD 1] ([COMMIT])
Learning: [FIELD 2]

## Next Task
Goal: [FIELD 3]
File: [FIELD 4]:[FUNCTION]

## RED Phase
Test: [FIELD 5]
Expected: [FAILURE TYPE]

Ready to start RED phase?
```

---

## 🗺️ Add Code Map (Bonus +30 seconds)

**If you have 30 extra seconds, add this at the top:**

```markdown
## Code Map Request
Show architecture: [SYSTEM YOU'RE WORKING ON]
Trace: "What happens when [USER ACTION]?"
```

---

## 📊 Full Template (When You Have 3-5 Minutes)

**Use `prompt.md` and fill these sections in order:**

### Priority 1 (Required)
- [ ] What just completed + commit
- [ ] Key learning
- [ ] Next P0 task + goal
- [ ] Working file + function
- [ ] RED test name + expected failure

### Priority 2 (Recommended)
- [ ] Code map context (system + user action)
- [ ] 3 files to load in parallel
- [ ] P0 steps (1, 2, 3)
- [ ] GREEN strategy

### Priority 3 (Optional)
- [ ] Current blocker
- [ ] Refactor opportunities
- [ ] P1 next priority
- [ ] Memory to create

---

## 💡 Common Patterns

### Code Map Questions
```
# For daemon work:
"AutomationDaemon startup and handler registration"
Trace: "What happens when daemon.start() is called?"

# For event processing:
"File event processing pipeline"
Trace: "What happens when a file is created in Inbox?"

# For CLI work:
"CLI command execution flow"
Trace: "What happens when user runs 'inneros workflow --status'?"
```

### Key Learnings
```
# Pattern discoveries:
"[PATTERN NAME] solves [PROBLEM] by [APPROACH]"

# Architecture insights:
"[COMPONENT A] must initialize before [COMPONENT B] because [REASON]"

# Performance findings:
"[OPTIMIZATION] reduced [METRIC] by [PERCENTAGE]"
```

### P0 Goals
```
# Feature completion:
"Complete [FEATURE] integration with [SYSTEM]"

# Bug fixes:
"Fix [BUG] in [COMPONENT] causing [SYMPTOM]"

# Refactoring:
"Extract [FUNCTIONALITY] from [GOD_CLASS] to [NEW_CLASS]"
```

---

## 🎯 Field Lookup Table

| If you're stuck on... | Write this... |
|----------------------|---------------|
| **USER_ACTION** | Describe what user/system does: "user adds screenshot", "cron job triggers" |
| **KEY_LEARNING** | Most important insight from last iteration - one sentence |
| **P0_GOAL** | What this iteration delivers - complete the sentence: "Enable..." |
| **RED_EXPECTED_FAILURE** | Error type: AttributeError, ImportError, AssertionError, etc. |
| **GREEN_STRATEGY** | Minimal implementation approach - 1-2 sentences |
| **REFACTOR_OPPORTUNITY** | What could be cleaner - extract, rename, simplify |

---

## 🚀 Time Comparison

| Method | Time | When to Use |
|--------|------|-------------|
| Minimum 5 fields | 1-2 min | Quick iteration, familiar territory |
| Full template | 3-5 min | Complex feature, new territory |
| Custom prompt | 10-15 min | Special cases (not recommended) |

---

## 📝 Example: Ultra-Fast Fill

**Scenario**: Just finished FileWatcher integration, need to start handler registration

**Fill 5 fields** (90 seconds):
```
1. FileWatcher integration with debouncing | a1b2c3d
2. Dual-layer debouncing prevents AI spam during edits
3. Complete feature handler registration system
4. development/src/automation/daemon.py | _setup_feature_handlers
5. test_handlers_initialize_from_config | AttributeError
```

**Paste this** (30 seconds):
```markdown
# TDD Iteration: automation-daemon-integration

## Status
Completed: FileWatcher integration with debouncing (a1b2c3d)
Learning: Dual-layer debouncing prevents AI spam during edits

## Next Task
Goal: Complete feature handler registration system
File: development/src/automation/daemon.py:_setup_feature_handlers

## RED Phase
Test: test_handlers_initialize_from_config
Expected: AttributeError

Ready to start RED phase?
```

**Total time**: 2 minutes → Start coding immediately

---

## ✨ Power User Tips

### Tip 1: Keep Template Open
- Open `prompt.md` in a dedicated editor window
- Fill as you work through iteration
- Copy at end of session

### Tip 2: Use Snippets
Create text expansion shortcuts:
- `pminvp` → Minimum viable prompt structure
- `pmcode` → Code map request format
- `pmred` → RED phase structure

### Tip 3: Archive Pattern
```bash
# After filling prompt.md
cp .windsurf/prompt.md .windsurf/archive/prompt-iteration-4.md
# Now prompt.md is your template for iteration 5
```

### Tip 4: Parallel Fill
While tests are running:
- Fill COMPLETED_TASK + KEY_LEARNING
- Tests finish → Fill next task
- Total overhead: 30 seconds

---

## 🎓 Learning Curve

**Iteration 1**: 5-7 minutes (learning template)
**Iteration 2**: 4-5 minutes (getting comfortable)
**Iteration 3+**: 2-3 minutes (muscle memory)

**ROI**: After 3 iterations, you've saved 20+ minutes vs. manual prompts

---

**Remember**: The template is a tool, not a prison. Skip fields, add fields, modify as needed. The goal is **faster context transfer**, not template compliance.

---

**Last Updated**: 2025-10-07
