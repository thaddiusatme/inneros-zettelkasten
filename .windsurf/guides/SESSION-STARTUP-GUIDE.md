# Session Startup Guide - Using Consolidated Wisdom

**Purpose**: Quick reference for Windsurf AI to load relevant patterns at session start  
**Created**: 2025-10-23  
**Status**: Active

---

## 🚀 Session Startup Checklist

### 1. Identify Task Type

**TDD Iteration?**
→ Load: `.windsurf/guides/tdd-methodology-patterns.md`

**AI Integration?**
→ Load: `.windsurf/guides/ai-integration-patterns.md`

**Test Remediation?**
→ Load: `.windsurf/guides/test-remediation-patterns.md`

**CLI Development?**
→ Load: Both TDD + AI guides (CLI builds on both)

**Maintenance/Refactoring?**
→ Load: TDD guide (REFACTOR patterns)

### 2. Reference Relevant Patterns

**Starting TDD?**
- RED Phase: Sections on test coverage (10-25 tests)
- GREEN Phase: Minimal implementation strategy
- REFACTOR Phase: Utility extraction (3-5 classes)
- Time box: 30-90 minutes

**Integrating AI?**
- Mock-first development (4 stages)
- Caching strategy (file hash-based)
- Quality gates for output validation
- Error handling & circuit breakers

### 3. Check for Similar Work

**Before implementing**:
- Search `Projects/COMPLETED-2025-*/` for similar features
- Check specific lessons-learned for implementation details
- Reuse proven patterns from guides

---

## 📚 Guide Reference Map

### When to Use Each Guide

| Task | Primary Guide | Secondary Guide | Specific Lessons-Learned |
|------|---------------|----------------|-------------------------|
| **New TDD Feature** | TDD Methodology | - | Feature-specific docs |
| **AI Service Integration** | AI Integration | TDD Methodology | Samsung OCR, Tag Prevention |
| **Test Remediation** | Test Remediation | TDD Methodology | Sprint 1 Retrospective |
| **CLI Command** | TDD Methodology | - | CLI extraction iterations |
| **Performance Optimization** | AI Integration | - | Batch processing examples |
| **Bug Fix** | TDD Methodology | Test Remediation | Template fix, backup fix |
| **Refactoring** | TDD Methodology | - | ADR-002, ADR-004 |

---

## 🎯 Pattern Quick Reference

### TDD Patterns (Most Used)

**Test Setup**:
```python
# Use tmp_path fixture
def test_feature(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
```

**Import Path Fix**:
```python
# At top of test file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
```

**Utility Extraction Threshold**:
- >20 lines AND reusable
- Used 3+ times in codebase
- Clear single responsibility

### AI Patterns (Most Used)

**Graceful Degradation**:
```python
try:
    result = ai_service.analyze(content)
except APIError:
    result = fallback_analysis(content)
```

**File Hash Caching**:
```python
cache_key = hashlib.sha256(file_path.read_bytes()).hexdigest()
if cache_key in cache:
    return cache[cache_key]
```

**Quality Gate**:
```python
if len(tag) > 50 or has_prohibited_pattern(tag):
    return False, "Tag validation failed"
```

---

## 💡 Common Scenarios

### Scenario 1: Starting TDD Iteration

**Load**:
- `.windsurf/guides/tdd-methodology-patterns.md`
- Sections: RED Phase Patterns, GREEN Phase Patterns

**Reference**:
- Test count: 10-25 tests
- Time box: 30-90 minutes
- Import path fix if needed

### Scenario 2: AI Service Failing

**Load**:
- `.windsurf/guides/ai-integration-patterns.md`
- Section: Error Handling Patterns

**Check**:
- Graceful degradation implemented?
- Circuit breaker in place?
- Fallback strategy defined?

### Scenario 3: Performance Issues

**Load**:
- `.windsurf/guides/ai-integration-patterns.md`
- Section: Performance Optimization Patterns

**Check**:
- Caching implemented? (85-95% hit rate target)
- Batch processing used?
- Parallel processing appropriate?

### Scenario 4: Over-Engineering in GREEN Phase

**Load**:
- `.windsurf/guides/tdd-methodology-patterns.md`
- Section: GREEN Phase - Minimal Implementation

**Intervention**:
- Set 45-min timer
- Ask: "Is this REQUIRED to pass tests?"
- Move "nice to have" to REFACTOR

---

## 🔍 Finding Specific Patterns

### Quick Pattern Lookup

**Use CMD+F in guides**:
- "import path" → TDD guide
- "graceful degradation" → AI guide
- "circuit breaker" → AI guide
- "utility extraction" → TDD guide
- "mock-first" → AI guide
- "quality gate" → AI guide

### Cross-References

**TDD Guide References**:
- `.windsurf/rules/updated-development-workflow.md` (high-level)
- `.windsurf/rules/architectural-constraints.md` (design limits)
- `Projects/Archive/completed-2025-09/` (detailed examples)

**AI Guide References**:
- Samsung Screenshot iterations (OCR integration)
- Tag Prevention iterations (quality gates)
- Fleeting Triage iterations (batch processing)

---

## 📊 Success Patterns

### High-Velocity Iterations

**Pattern**: Follow strict TDD, use guides
- Auto-Promotion Subdirectory: 15 min (50% under target)
- AI Tag Prevention: 12 min (exceptional)
- Fleeting Triage Phase 1: 7 min (record)

**Common Factor**: Referenced relevant guide patterns

### Zero-Regression Features

**Pattern**: Comprehensive test coverage + refactor phase
- 34/34 iterations: Zero regressions
- Key: REFACTOR phase cleanup + regression testing

**Reference**: TDD guide, Success Metrics section

### Production-Ready AI

**Pattern**: Mock-first + quality gates + caching
- Samsung OCR: Mock→Real in 60 min
- Tag Prevention: 82% bad output reduction
- Connection Discovery: 85-95% cache hit rate

**Reference**: AI guide, Foundation Patterns

---

## ⚠️ Anti-Patterns to Avoid

### Don't Rediscover Patterns

❌ **Anti-pattern**: "Let me figure out how to structure tests..."
✅ **Pattern**: Reference TDD guide, test coverage patterns

❌ **Anti-pattern**: "How should I handle AI failures?"
✅ **Pattern**: Reference AI guide, graceful degradation

### Don't Skip Guide Sections

❌ **Anti-pattern**: Jump straight to coding
✅ **Pattern**: 5-min guide review → implement

❌ **Anti-pattern**: "I remember something about mocks..."
✅ **Pattern**: CMD+F "mock-first" in AI guide

### Don't Over-Engineer

❌ **Anti-pattern**: Perfect code before tests pass
✅ **Pattern**: Minimal GREEN → REFACTOR polish

---

## 🔄 Updating Guides

### When to Propose Updates

**Add pattern if**:
1. Appears in 3+ iterations
2. Solves recurring challenge  
3. Provides measurable improvement
4. Generalizable across features

**Process**:
1. Note pattern in session
2. Document with metrics
3. Add to relevant guide
4. Reference source iterations

### What NOT to Add

❌ Feature-specific logic
❌ One-off solutions
❌ Temporary workarounds
❌ Unproven approaches

---

## 📈 Tracking Guide Effectiveness

### Monitor These Metrics

**Context Loading Time**:
- Target: <10 min per session
- Before guides: 15-30 min
- After guides: 5-10 min (target achieved)

**Pattern Reuse**:
- Target: 80% of iterations reference guides
- Track: Count "see guide" in lessons-learned

**Development Velocity**:
- Target: Maintain 3-5x TDD efficiency
- Track: Time to first passing test

---

## 🎓 Learning Path

### For New Sessions

**First 3 Sessions**:
1. Read TDD Methodology guide (full read)
2. Read AI Integration guide (full read)
3. Practice referencing during development

**Sessions 4-10**:
1. Quick guide review (5 min)
2. Reference specific patterns as needed
3. Note any missing patterns

**Sessions 10+**:
1. Guide reference becomes automatic
2. Muscle memory for common patterns
3. Contribute new patterns back

---

## 📞 Quick Help

**Stuck on imports?**
→ TDD guide, Pattern 3: Import Path Setup

**AI service down?**
→ AI guide, Pattern 2: Graceful Degradation

**Tests taking too long?**
→ TDD guide, Time Management Patterns

**Need utilities?**
→ TDD guide, Pattern 1: Utility Extraction Strategy

**Performance issues?**
→ AI guide, Performance Optimization Patterns

**Over-engineering?**
→ TDD guide, Challenge 4: Over-Engineering in GREEN Phase

---

**Quick Start**: Load relevant guide → Skim headers → CMD+F for pattern → Implement → Update if new pattern emerges

**Remember**: Guides extract wisdom from 34+ iterations. Trust the patterns.
