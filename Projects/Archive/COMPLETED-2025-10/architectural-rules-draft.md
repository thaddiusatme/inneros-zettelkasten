# Architectural Rules - DRAFT for .windsurf/rules/

**Instructions**: Review these and add to `.windsurf/rules/` directory

---

## File 1: architectural-constraints.md

```markdown
# Architectural Constraints

**Purpose**: Prevent god classes and architectural debt  
**Enforcement**: Pre-commit checks, code review, CI/CD  
**Last Updated**: 2025-10-05

---

## Class Size Limits

### Hard Limits (MUST NOT EXCEED)
- **Max LOC per class**: 500 lines
- **Max methods per class**: 20 methods
- **Max constructor parameters**: 5 parameters

### Soft Limits (REVIEW REQUIRED)
- **Warning LOC**: 400 lines (start planning extraction)
- **Warning methods**: 15 methods (start planning extraction)
- **Warning imports**: Class imported by >10 files (high coupling)

---

## Refactoring Triggers

**STOP adding features and refactor if ANY are true**:

- [ ] Class exceeds 500 LOC
- [ ] Class has >20 methods
- [ ] Class name contains "Manager", "Handler", "Controller" AND is >300 LOC
- [ ] Adding new method would exceed thresholds
- [ ] User reports "code smell" or complexity concerns
- [ ] Difficulty explaining class purpose in <10 words

---

## God Class Warning Signs

### Structural Indicators
- Multiple unrelated responsibilities (analytics + AI + connections)
- Method names from different domains
- Large private helper method sections (>5 helpers)
- Tests require extensive mocking of unrelated features
- "And" or "Or" in class description (e.g., "Handles workflows AND analytics")

### Behavioral Indicators
- New features always go to same class
- PRs consistently modify same file
- Merge conflicts frequent in same class
- Difficulty naming the class's single purpose
- Developers avoid modifying the class (complexity fear)

---

## Required Actions When Threshold Exceeded

### Immediate (Before Next Commit)
1. **STOP** adding features to the class
2. **MEASURE**: Run metrics (LOC, methods, coupling)
3. **ASSESS**: Single Responsibility violated?

### Short Term (Within 1 Week)
1. **CREATE** Architecture Decision Record (ADR)
2. **DESIGN** split strategy:
   - Domain separation (analytics vs. AI vs. connections)
   - Utility extraction (helper methods → utility classes)
   - Manager hierarchy (core vs. specialized managers)
3. **ESTIMATE** refactoring effort (hours/days/weeks)

### Medium Term (Within Sprint/Iteration)
1. **IMPLEMENT** refactoring via TDD:
   - RED: Write tests for new architecture
   - GREEN: Extract classes to pass tests
   - REFACTOR: Migrate existing code
2. **VALIDATE**: All tests pass, no regressions
3. **DOCUMENT** lessons learned

---

## Pre-Development Checklist

**Before starting ANY new feature**:

```bash
# 1. Check target class size
wc -l development/src/ai/target_class.py

# 2. Check method count
grep -c "^    def " development/src/ai/target_class.py

# 3. Check import coupling
grep -r "from.*target_class import" development/ | wc -l
```

**Decision Matrix**:

| Current Size | Action |
|--------------|--------|
| <300 LOC, <10 methods | ✅ Add feature to class |
| 300-400 LOC, 10-15 methods | ⚠️ Consider utility extraction |
| 400-500 LOC, 15-20 methods | 🔴 Extract utilities FIRST, then add |
| >500 LOC, >20 methods | 🚫 BLOCKED - Refactor required |

---

## Architectural Tests

**Add to test suite**:

```python
def test_class_size_constraints():
    """Prevent god classes - fail if any class too large."""
    import os
    from pathlib import Path
    
    src_path = Path("development/src")
    violations = []
    
    for py_file in src_path.rglob("*.py"):
        if py_file.name.startswith("test_"):
            continue
            
        content = py_file.read_text()
        loc = len(content.split('\n'))
        methods = content.count('\n    def ')
        
        if loc > 500:
            violations.append(f"{py_file.name}: {loc} LOC (max 500)")
        if methods > 20:
            violations.append(f"{py_file.name}: {methods} methods (max 20)")
    
    assert not violations, f"God class violations:\n" + "\n".join(violations)
```

---

## Exception Process

**If you must exceed limits** (rare):

1. **Document WHY** in ADR
2. **Get approval** from team/reviewer
3. **Create refactoring ticket** with deadline
4. **Add TODO** comment with ticket reference
5. **Schedule refactoring** within 2 sprints

**Valid exceptions** (still require ADR):
- Generated code (mark with `# Generated - DO NOT EDIT`)
- Migration code (temporary, with deletion date)
- Legacy integration (with modernization plan)

---

## Monthly Architectural Review

**Schedule**: First Monday of each month  
**Duration**: 30 minutes  
**Attendees**: Developer + AI (Cascade)

**Agenda**:
1. Run class size audit (find large classes)
2. Review god class warning signs
3. Prioritize refactoring queue
4. Update architectural health tracking

**Output**: `Projects/ACTIVE/architectural-review-YYYY-MM.md`

---

## Success Metrics

**Track in project-todo**:

- [ ] Zero classes >500 LOC
- [ ] Zero classes >20 methods
- [ ] <3 classes in refactoring queue
- [ ] Monthly reviews completed on time
- [ ] ADRs created for all major decisions

---

## References

- **Lessons Learned**: `Projects/COMPLETED-2025-10/god-class-prevention-lessons-learned.md`
- **Refactor Example**: `Projects/ACTIVE/workflow-manager-refactor-tdd-manifest.md`
- **Technical Assessment**: `Projects/REFERENCE/technical-health-assessment-oct-2025.md`
```

---

## File 2: tdd-methodology-architectural-additions.md

**Add this section to existing `.windsurf/rules/tdd-methodology.md`**:

```markdown
## TDD with Architectural Safeguards

### RED Phase - Architectural Checks

**BEFORE writing failing tests for new features**:

#### Step 1: Target Class Assessment
```bash
# Check current size
wc -l development/src/ai/target_class.py

# Check method count
grep -c "^    def " development/src/ai/target_class.py

# Check coupling
grep -r "from.*target_class import" development/ | wc -l
```

#### Step 2: Decision Point

**If >400 LOC or >15 methods**:
- ❌ DO NOT add to existing class
- ✅ Propose extracting utility class FIRST
- ✅ OR propose new manager class
- ✅ Document decision in iteration plan

**If <400 LOC and <15 methods**:
- ✅ Proceed with feature addition
- 📝 Document: "Adding to [ClassName] (current: XXX LOC, XX methods)"

#### Step 3: Write Architectural Test

**Always include**:
```python
def test_[class]_size_constraint():
    """Prevent god class - fail if too large."""
    from pathlib import Path
    
    source = Path("src/ai/[class].py").read_text()
    loc = len(source.split('\n'))
    methods = source.count('\n    def ')
    
    assert loc < 500, f"[Class] too large: {loc} LOC (max 500)"
    assert methods < 20, f"[Class] too many methods: {methods} (max 20)"
```

---

### GREEN Phase - Size Monitoring

**AFTER implementing to pass tests**:

1. **Re-check class size** (may have grown during implementation)
   ```bash
   wc -l development/src/ai/target_class.py
   ```

2. **If exceeded threshold**:
   - Extract utilities immediately
   - Update tests for new architecture
   - DO NOT commit bloated class

3. **If approaching threshold** (>400 LOC):
   - Add TODO comment: `# TODO: Extract [domain] logic to utility class (approaching 500 LOC limit)`
   - Create refactoring ticket
   - Schedule extraction within 2 iterations

---

### REFACTOR Phase - Mandatory Architecture Review

**AFTER passing tests, BEFORE committing**:

#### Checklist
- [ ] Class size within limits (<500 LOC, <20 methods)
- [ ] Single responsibility maintained
- [ ] If >3 helpers added: Extract to utility class
- [ ] If responsibilities mixed: Consider domain separation
- [ ] Architectural tests passing
- [ ] ADR updated if architectural decisions made

#### Utility Extraction Pattern

**If added >3 helper methods**:

```python
# BEFORE (in main class)
class WorkflowManager:
    def process_note(self):
        result = self._helper1()
        result = self._helper2()
        result = self._helper3()
        return result
    
    def _helper1(self): ...
    def _helper2(self): ...
    def _helper3(self): ...

# AFTER (extracted to utility)
# File: workflow_manager_utils.py
class WorkflowProcessorUtils:
    @staticmethod
    def helper1(): ...
    
    @staticmethod
    def helper2(): ...
    
    @staticmethod
    def helper3(): ...

# File: workflow_manager.py
from .workflow_manager_utils import WorkflowProcessorUtils

class WorkflowManager:
    def process_note(self):
        result = WorkflowProcessorUtils.helper1()
        result = WorkflowProcessorUtils.helper2()
        result = WorkflowProcessorUtils.helper3()
        return result
```

---

### Post-Iteration Review

**Required questions**:

1. **Size**: Is target class within limits?
2. **Responsibility**: Can you state class purpose in <10 words?
3. **Coupling**: Is class imported by <10 files?
4. **Tests**: Do architectural tests pass?
5. **Documentation**: Is ADR updated if needed?

**If any answer is NO**:
- [ ] Create refactoring ticket
- [ ] Add to architectural review queue
- [ ] Schedule fix within 2 iterations
```

---

## File 3: Monthly Review Template

**Create**: `Projects/TEMPLATES/architectural-review-template.md`

```markdown
# Architectural Review - [Month Year]

**Date**: YYYY-MM-DD  
**Reviewer**: [Name]  
**Status**: In Progress | Complete

---

## Class Size Audit

### Report Generation
```bash
# Generate size report
find development/src -name "*.py" -exec wc -l {} \; | sort -rn | head -20
```

### Findings

| File | LOC | Methods | Status | Action |
|------|-----|---------|--------|--------|
| workflow_manager.py | 2,374 | 59 | 🔴 CRITICAL | P1 Refactor (4 weeks) |
| example_class.py | 450 | 18 | ⚠️ WARNING | Monitor |
| another_class.py | 250 | 10 | ✅ HEALTHY | None |

---

## Responsibility Audit

### Classes Requiring Attention

**[ClassName]**:
- **Current Purpose**: [Trying to state in <10 words]
- **Domains Detected**: [List different responsibility domains]
- **Split Recommendation**: [How to split]
- **Priority**: P0 | P1 | P2

---

## Coupling Audit

### High-Coupling Classes
```bash
# Find highly coupled classes
for file in development/src/ai/*.py; do
    count=$(grep -r "from.*$(basename $file .py) import" development/ | wc -l)
    echo "$count imports: $(basename $file)"
done | sort -rn
```

### Findings
- **[ClassName]**: Imported by XX files (threshold: 10) → Consider interface extraction

---

## Action Items

### Immediate (This Week)
- [ ] [Action 1]
- [ ] [Action 2]

### Short Term (This Month)
- [ ] [Action 1]
- [ ] [Action 2]

### Medium Term (This Quarter)
- [ ] [Action 1]
- [ ] [Action 2]

---

## Refactoring Queue

| Class | Effort | Priority | Scheduled | Owner |
|-------|--------|----------|-----------|-------|
| WorkflowManager | 4 weeks | P1 | Oct 6-Nov 2 | Team |
| [ClassName] | [Time] | P2 | [Date] | [Name] |

---

## Success Metrics

- **Classes >500 LOC**: [Count] (Target: 0)
- **Classes >20 methods**: [Count] (Target: 0)
- **ADRs Created This Month**: [Count]
- **Refactorings Completed**: [Count]

---

## Next Review

**Date**: [First Monday of next month]  
**Focus**: [Any specific areas to watch]
```

---

**NEXT STEPS**:

1. Review these drafts
2. Move to `.windsurf/rules/` directory (manually, as I can't write there)
3. Update existing TDD methodology rule
4. Create first architectural review using template
