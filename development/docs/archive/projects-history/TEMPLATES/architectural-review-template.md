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

**Summary**:
- **Critical** (>500 LOC or >20 methods): [Count] classes
- **Warning** (>400 LOC or >15 methods): [Count] classes
- **Healthy** (<400 LOC and <15 methods): [Count] classes

---

## Responsibility Audit

### Classes Requiring Attention

**[ClassName]**:
- **Current Purpose**: [Try to state in <10 words]
- **Domains Detected**: [List different responsibility domains]
- **Split Recommendation**: [How to split - e.g., Analytics vs. AI vs. Connections]
- **Priority**: P0 | P1 | P2
- **Estimated Effort**: [hours/days/weeks]

**[ClassName]**:
- **Current Purpose**: [Try to state in <10 words]
- **Domains Detected**: [List different responsibility domains]
- **Split Recommendation**: [How to split]
- **Priority**: P0 | P1 | P2
- **Estimated Effort**: [hours/days/weeks]

---

## Coupling Audit

### High-Coupling Classes
```bash
# Find highly coupled classes
for file in development/src/ai/*.py; do
    count=$(grep -r "from.*$(basename $file .py) import" development/ | wc -l)
    echo "$count imports: $(basename $file)"
done | sort -rn | head -10
```

### Findings

| Class | Import Count | Threshold | Status | Action |
|-------|--------------|-----------|--------|--------|
| workflow_manager | 17 | 10 | ⚠️ HIGH | Consider interface extraction |
| example_class | 8 | 10 | ✅ OK | Monitor |

**Recommendations**:
- Classes imported >10 times should consider interface-based architecture
- High coupling indicates potential for extraction/modularization

---

## God Class Warning Signs

### Structural Indicators Detected
- [ ] Multiple unrelated responsibilities (list domains mixed)
- [ ] Method names from different domains
- [ ] Large private helper sections (>5 helpers)
- [ ] Tests require extensive mocking
- [ ] "And" or "Or" in class description

### Behavioral Indicators Detected
- [ ] New features always go to same class
- [ ] PRs consistently modify same file
- [ ] Merge conflicts frequent
- [ ] Difficulty naming single purpose
- [ ] Developers avoid modifying (complexity fear)

**Notes**: [Describe any detected patterns]

---

## Action Items

### Immediate (This Week)
- [ ] [Action 1 - e.g., Create ADR for WorkflowManager split]
- [ ] [Action 2 - e.g., Extract utilities from ClassName]

### Short Term (This Month)
- [ ] [Action 1 - e.g., Begin WorkflowManager refactoring sprint]
- [ ] [Action 2 - e.g., Schedule team review of architecture]

### Medium Term (This Quarter)
- [ ] [Action 1 - e.g., Complete all P1 refactoring]
- [ ] [Action 2 - e.g., Implement architectural tests in CI/CD]

---

## Refactoring Queue

| Class | Effort | Priority | Scheduled | Owner | Status |
|-------|--------|----------|-----------|-------|--------|
| WorkflowManager | 4 weeks | P1 | Oct 6-Nov 2 | Team | 🔄 In Progress |
| [ClassName] | [Time] | P2 | [Date] | [Name] | 📋 Planned |
| [ClassName] | [Time] | P3 | [Date] | [Name] | 📋 Planned |

---

## Success Metrics

### Current Month
- **Classes >500 LOC**: [Count] (Target: 0)
- **Classes >20 methods**: [Count] (Target: 0)
- **ADRs Created This Month**: [Count]
- **Refactorings Completed**: [Count]
- **New Classes Added**: [Count]
- **Classes Approaching Limits** (>400 LOC): [Count]

### Trend Analysis
- **LOC Growth Rate**: [Increasing/Stable/Decreasing]
- **Method Count Growth**: [Increasing/Stable/Decreasing]
- **Refactoring Velocity**: [Number of classes refactored per month]

### Health Score
- ✅ **Excellent**: All classes <400 LOC, <15 methods
- 🟡 **Good**: Some classes 400-500 LOC, 15-20 methods, but tracked
- ⚠️ **Warning**: Classes >500 LOC exist with refactoring plan
- 🔴 **Critical**: Classes >500 LOC without refactoring plan

**Current Score**: [Score with justification]

---

## Lessons Learned

### What Worked Well
- [e.g., Utility extraction pattern reduced coupling]
- [e.g., Early detection prevented god class formation]

### What Needs Improvement
- [e.g., Need earlier intervention on growing classes]
- [e.g., Better documentation of design decisions]

### Process Improvements
- [e.g., Add pre-commit hooks for class size]
- [e.g., More frequent architectural check-ins]

---

## Next Review

**Date**: [First Monday of next month]  
**Focus Areas**: 
- [Any specific classes to watch]
- [Any specific patterns to track]
- [Any upcoming refactoring to validate]

**Preparation**:
- [ ] Run class size audit script
- [ ] Review recent commits for architectural changes
- [ ] Check ADR updates
- [ ] Validate refactoring queue progress
